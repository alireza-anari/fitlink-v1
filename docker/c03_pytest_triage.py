"""Opt-in metadata-only pytest evidence; never record locals or payload text."""

import ast
import json
import os
import re
import sys
import threading
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TESTS = {}
for path in (ROOT / "tests").rglob("test_*.py"):
    TESTS[path.relative_to(ROOT).as_posix()] = {
        n.name
        for n in ast.walk(ast.parse(path.read_text()))
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def safe_node(node):
    node = node.split("[", 1)[0]
    parts = node.split("::")
    if len(parts) >= 2 and parts[-1] in TESTS.get(parts[0], set()):
        return node
    return "<redacted>"


def location(filename, function, line):
    try:
        path = Path(filename).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        path = "<external>"
        # Pytest's rewritten cache can retain the host compile-time filename
        # when mounted into a container. Normalize only known static test code.
        for known_file, functions in TESTS.items():
            if filename.endswith("/" + known_file) and function in functions:
                path = known_file
                break
        for package in ("_pytest", "pluggy", "django", "psycopg", "rest_framework"):
            if path == "<external>" and f"/{package}/" in filename:
                path = package + "/" + filename.split(f"/{package}/", 1)[1]
                break
        if Path(filename).name in {
            "subprocess.py",
            "threading.py",
            "selectors.py",
            "socket.py",
        }:
            path = Path(filename).name
    return {
        "file": path,
        "function": function if re.fullmatch(r"[\w<>.]+", function) else "<redacted>",
        "line": line,
    }


def stacks():
    result = []
    for identifier, frame in list(sys._current_frames().items())[:16]:
        rows = []
        while frame and len(rows) < 80:
            rows.append(
                location(frame.f_code.co_filename, frame.f_code.co_name, frame.f_lineno)
            )
            frame = frame.f_back
        result.append({"thread": identifier, "frames": rows})
    return result


class Journal:
    def __init__(self, path, cutoff=0.25, session_cutoff=120, terminate=False):
        self.output = Path(path).open("x")
        self.started = time.monotonic()
        self.case_started = None
        self.node = None
        self.last_node = None
        self.phase = "collection"
        self.cutoff = cutoff
        self.session_cutoff = session_cutoff
        self.terminate = terminate
        self.recorded = False
        self.session_recorded = False
        self.lock = threading.Lock()
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self.observe, daemon=True)
        self.thread.start()

    def emit(self, event, **values):
        with self.lock:
            self.output.write(
                json.dumps(
                    {
                        "event": event,
                        "elapsed_seconds": round(time.monotonic() - self.started, 3),
                        **values,
                    },
                    sort_keys=True,
                )
                + "\n"
            )
            self.output.flush()

    def begin(self, node):
        self.node = safe_node(node)
        self.last_node = self.node
        self.case_started = time.monotonic()
        self.recorded = False
        self.phase = "setup"
        self.emit("test_start", node=self.node)

    def snapshot(self, event):
        from docker.c03_gate_diagnostics import process_rows

        self.emit(
            event,
            active_node=self.node,
            phase=self.phase,
            case_seconds=round(time.monotonic() - self.case_started, 3)
            if self.case_started
            else None,
            stacks=stacks(),
            owned_processes=process_rows(b"C03_TRIAGE_OWNER=", owner_pid=os.getpid()),
        )

    def observe(self):
        while not self.stop.wait(0.02):
            if (
                self.case_started
                and not self.recorded
                and time.monotonic() - self.case_started >= self.cutoff
            ):
                self.recorded = True
                self.snapshot("case_cutoff")
            if (
                not self.session_recorded
                and time.monotonic() - self.started >= self.session_cutoff
            ):
                self.session_recorded = True
                self.snapshot(
                    "diagnostic_cutoff" if self.terminate else "session_snapshot"
                )
                if self.terminate:
                    os._exit(124)

    def finish(self):
        self.stop.set()
        self.thread.join(timeout=1)
        self.emit("observer_finished")
        self.output.close()


JOURNAL = None


def pytest_configure(config):
    global JOURNAL
    path = os.environ.get("C03_TRIAGE_EVIDENCE_FILE")
    if path:
        foundation = os.environ.get("C03_FOUNDATION_TRIAGE") == "1"
        JOURNAL = Journal(
            path,
            cutoff=30 if foundation else 0.05,
            session_cutoff=120,
            terminate=not foundation,
        )


@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_runtest_protocol(item, nextitem):
    if JOURNAL:
        JOURNAL.begin(item.nodeid)
    try:
        return (yield)
    finally:
        if JOURNAL:
            JOURNAL.emit(
                "test_end",
                node=JOURNAL.node,
                case_seconds=round(time.monotonic() - JOURNAL.case_started, 3),
            )
            JOURNAL.node = None
            JOURNAL.case_started = None


def pytest_runtest_setup(item):
    if JOURNAL:
        JOURNAL.phase = "setup"


def pytest_runtest_call(item):
    if JOURNAL:
        JOURNAL.phase = "call"


def pytest_runtest_teardown(item, nextitem):
    if JOURNAL:
        JOURNAL.phase = "teardown"


def failure_data(info):
    data = {"exception": info.type.__name__}
    data["traceback"] = [
        location(str(e.path), e.frame.code.name, e.lineno + 1) for e in info.traceback
    ]
    for entry in info.traceback:
        response = entry.frame.f_locals.get("response")
        if response is not None and type(getattr(response, "status_code", None)) is int:
            data["actual_http_status"] = response.status_code
            try:
                source = str(entry.statement)
            except (AssertionError, IndexError, OSError):
                # Optional source text can disappear or never exist for a frame.
                # Retain the original exception/status without replacing its verdict.
                source = ""
                known_file = location(
                    str(entry.path), entry.frame.code.name, entry.lineno
                )["file"]
                if known_file in TESTS:
                    try:
                        source = (
                            (ROOT / known_file).read_text().splitlines()[entry.lineno]
                        )
                    except (OSError, IndexError):
                        pass
            expected = re.search(r"assert response.status_code == ([0-9]{3})", source)
            if expected:
                data["expected_http_status"] = int(expected[1])
                data["assertion"] = "assert response.status_code == " + expected[1]
    return data


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    report = yield
    if JOURNAL:
        data = {
            "node": safe_node(item.nodeid),
            "phase": report.when,
            "outcome": report.outcome,
            "seconds": round(report.duration, 3),
        }
        if call.excinfo:
            data.update(failure_data(call.excinfo))
        JOURNAL.emit("test_report", **data)
    return report


def pytest_sessionfinish(session, exitstatus):
    if JOURNAL:
        JOURNAL.emit("pytest_exit", exitstatus=int(exitstatus))
        JOURNAL.finish()


def pytest_internalerror(excrepr, excinfo):
    if JOURNAL:
        # Never read exception text, frame locals or longrepr for a framework error.
        from docker.c03_storage_errors import error_category

        JOURNAL.emit(
            "pytest_internalerror",
            active_node=JOURNAL.node or JOURNAL.last_node,
            exception=error_category(excinfo.value),
            traceback=[
                location(str(e.path), e.frame.code.name, e.lineno + 1)
                for e in excinfo.traceback
            ],
        )
