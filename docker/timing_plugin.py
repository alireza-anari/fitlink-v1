"""Read-only primary-pytest observations. No SQL, parameters or failure text."""

import ast
import bisect
import functools
import hashlib
import json
import os
import re
import threading
import time
from pathlib import Path

import pytest
from timing_profile import (
    Tracker,
    calibration,
    install_lifecycle,
    install_migrations,
    restore,
)

OUT = Path("/evidence")
STATE = None
CLASSES = (
    "SELECT",
    "INSERT",
    "UPDATE",
    "DELETE",
    "TRUNCATE",
    "CREATE",
    "ALTER",
    "DROP",
    "TRANSACTION",
    "OTHER",
)
BINS = (1_000_000, 5_000_000, 20_000_000, 100_000_000, 1_000_000_000)


def sql_class(sql):
    if not isinstance(sql, str):
        return "OTHER"
    match = re.match(r"\s*([A-Za-z]+)\b", sql[:128])
    first = match[1].upper() if match else "OTHER"
    if first in {"BEGIN", "COMMIT", "ROLLBACK", "SAVEPOINT", "RELEASE", "SET"}:
        return "TRANSACTION"
    return first if first in CLASSES else "OTHER"


def empty_classes():
    return {k: {"count": 0, "ns": 0, "bins": [0] * 6} for k in CLASSES}


class Observer:
    def __init__(self, folder):
        self.file = (folder / "pytest.jsonl").open("x", buffering=1)
        self.rows = self.bytes = self.hook_ns = self.sql_count = self.sql_ns = 0
        self.sql_observer_ns = 0
        self.lock = threading.Lock()
        self.write_lock = threading.Lock()
        self.stop = threading.Event()
        self.thread = None
        self.previous = (0, 0)
        self.ordinal = self.completed = 0
        self.nodes = set()
        self.fault = self.truncated = False
        self.originals = []
        self.enabled = os.environ.get("CAUSAL_MODE", "full") == "full"
        self.classes = empty_classes()
        self.previous_classes = empty_classes()
        self.timing = Tracker(self.enabled)
        self.timing_calibration = None

    def emit(self, event, **values):
        with self.write_lock:
            self._emit(event, **values)

    def heartbeat(self):
        try:
            while not self.stop.wait(5):
                with self.lock:
                    count, ns, overhead = (
                        self.sql_count,
                        self.sql_ns,
                        self.sql_observer_ns,
                    )
                self.emit(
                    "counters",
                    sql_count=count if self.enabled else None,
                    sql_ns=ns if self.enabled else None,
                    sql_counter_observed_ns=overhead if self.enabled else None,
                    hook_observed_ns=self.hook_ns,
                )
        except Exception:
            self.fault = True

    def _emit(self, event, **values):
        started = time.monotonic_ns()
        try:
            line = (
                json.dumps(
                    {"event": event, "mono_ns": started, **values},
                    sort_keys=True,
                    allow_nan=False,
                )
                + "\n"
            )
            if self.rows >= 12000 or self.bytes + len(line) > 16 * 1024 * 1024:
                self.truncated = True
                return
            self.file.write(line)
            self.rows += 1
            self.bytes += len(line)
        except Exception:
            self.fault = True
        finally:
            self.hook_ns += time.monotonic_ns() - started

    def wrap(self, original):
        @functools.wraps(original)
        def observed(cursor, *args, **kwargs):
            observer_entered = time.monotonic_ns()
            category = sql_class(args[0] if args else kwargs.get("sql"))
            entered = time.monotonic_ns()
            try:
                return original(cursor, *args, **kwargs)
            finally:
                returned = time.monotonic_ns()
                # Lock only the numeric update, never query execution.
                with self.lock:
                    self.sql_count += 1
                    self.sql_ns += returned - entered
                    item = self.classes[category]
                    item["count"] += 1
                    item["ns"] += returned - entered
                    item["bins"][bisect.bisect_right(BINS, returned - entered)] += 1
                    self.sql_observer_ns += (
                        time.monotonic_ns() - returned + entered - observer_entered
                    )

        return observed


def allowed_nodes(root):
    """Derive finite source-symbol allowlist from verified public test source."""
    nodes = set()

    def visit(body, prefix):
        for node in body:
            if isinstance(node, ast.ClassDef):
                visit(node.body, prefix + "::" + node.name)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name.startswith("test_"):
                    nodes.add(prefix + "::" + node.name)

    for directory in ["tests/unit", "tests/integration"]:
        for path in (root / directory).rglob("*.py"):
            visit(ast.parse(path.read_text()).body, path.relative_to(root).as_posix())
    return nodes


def pytest_configure(config):
    global STATE
    # Children inherit PYTEST_PLUGINS but must not become observers or write
    # primary evidence. Exclusive empty sentinel is outside application source.
    try:
        with (OUT / "primary.lock").open("x"):
            pass
    except OSError:
        return
    try:
        from django.db.backends.utils import CursorWrapper

        STATE = Observer(OUT)
        for name in ["execute", "executemany"]:
            original = getattr(CursorWrapper, name)
            STATE.originals.append((CursorWrapper, name, original))
            if os.environ.get("CAUSAL_MODE", "full") == "full":
                setattr(CursorWrapper, name, STATE.wrap(original))
        # Estimate per-call timer/counter overhead without a DB or test query.
        noop = STATE.wrap(lambda *args, **kwargs: None)
        start = time.monotonic_ns()
        for _ in range(10000):
            noop(None)
        elapsed = time.monotonic_ns() - start
        STATE.sql_count = STATE.sql_ns = STATE.sql_observer_ns = 0
        STATE.classes = empty_classes()
        STATE.timing_calibration = calibration()
        if STATE.enabled:
            STATE.originals.extend(install_migrations(STATE.timing))
        STATE.thread = threading.Thread(target=STATE.heartbeat, daemon=True)
        STATE.thread.start()
        STATE.emit(
            "configured",
            calibration_calls=10000,
            calibration_total_ns=elapsed,
            acceptance=False,
            observer_mode="minimal"
            if os.environ.get("CAUSAL_MODE") == "minimal"
            else "full",
        )
    except Exception:
        if STATE:
            STATE.fault = True


def pytest_collection_finish(session):
    if not STATE:
        return
    start = time.monotonic_ns()
    try:
        STATE.nodes = allowed_nodes(Path.cwd())
        nodes = [item.nodeid.split("[", 1)[0] for item in session.items]
        safe = [n if n in STATE.nodes else "other" for n in nodes]
        STATE.emit(
            "collection",
            count=len(nodes),
            sequence_sha256=hashlib.sha256("\n".join(safe).encode()).hexdigest(),
            unknown_nodes=sum(n == "other" for n in safe),
        )
    except Exception:
        STATE.fault = True
    finally:
        STATE.hook_ns += time.monotonic_ns() - start


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    if STATE:
        STATE.timing.context("setup", STATE.ordinal)


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_call(item):
    saved = []
    previous = None
    try:
        if STATE:
            STATE.timing.context("call", STATE.ordinal)
            if os.environ.get("TIMING_JOB") == "budget":
                saved, previous = STATE.timing.wrap(
                    "install", lambda: install_lifecycle(STATE.timing, item)
                )()
        yield
    finally:
        restore(saved)
        if previous is not None:
            item.funcargs["corpus"] = previous


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_teardown(item):
    if STATE:
        STATE.timing.context("teardown", STATE.ordinal)


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_logstart(nodeid, location):
    if STATE:
        STATE.ordinal += 1
        node = nodeid.split("[", 1)[0]
        STATE.emit(
            "start",
            ordinal=STATE.ordinal,
            node=node if node in STATE.nodes else "other",
        )


def pytest_runtest_logreport(report):
    if not STATE:
        return
    if report.when not in {"setup", "call", "teardown"}:
        STATE.fault = True
        return
    with STATE.lock:
        counters = (STATE.sql_count, STATE.sql_ns)
        delta = [counters[i] - STATE.previous[i] for i in range(2)]
        STATE.previous = counters
        classes = {
            k: {
                "count": v["count"] - STATE.previous_classes[k]["count"],
                "ns": v["ns"] - STATE.previous_classes[k]["ns"],
                "bins": [
                    a - b
                    for a, b in zip(
                        v["bins"], STATE.previous_classes[k]["bins"], strict=True
                    )
                ],
            }
            for k, v in STATE.classes.items()
        }
        STATE.previous_classes = {
            k: {"count": v["count"], "ns": v["ns"], "bins": list(v["bins"])}
            for k, v in STATE.classes.items()
        }
    if report.when == "teardown":
        STATE.completed += 1
    STATE.emit(
        "phase",
        ordinal=STATE.ordinal,
        phase=report.when,
        outcome=report.outcome
        if report.outcome in {"passed", "failed", "skipped"}
        else "other",
        seconds=round(report.duration, 6),
        sql_classes=classes if STATE.enabled else None,
        sql_count=delta[0] if STATE.enabled else None,
        sql_ns=delta[1] if STATE.enabled else None,
        sql_counter_observed_ns=STATE.sql_observer_ns if STATE.enabled else None,
        hook_observed_ns=STATE.hook_ns,
    )


def pytest_sessionfinish(session, exitstatus):
    if not STATE:
        return
    STATE.stop.set()
    if STATE.thread:
        STATE.thread.join(timeout=2)
    try:
        profile = STATE.timing.report()
        job = os.environ.get("TIMING_JOB")
        job = job if job in {"migration", "budget"} else "unknown"
        payload = json.dumps(
            {
                "acceptance": False,
                "job": job,
                "profile": profile,
                "calibration": STATE.timing_calibration,
            },
            sort_keys=True,
            allow_nan=False,
        )
        if len(payload) > 1_048_576:
            raise ValueError("timing_profile_limit")
        (OUT / "timing.json").write_text(payload + "\n")
        if profile["fault"]:
            STATE.fault = True
    except Exception:
        STATE.fault = True
    terminal = session.config.pluginmanager.get_plugin("terminalreporter")
    counts = {
        k: len(terminal.stats.get(k, [])) if terminal else None
        for k in [
            "passed",
            "failed",
            "error",
            "skipped",
            "xfailed",
            "xpassed",
            "deselected",
        ]
    }
    STATE.emit(
        "finish",
        exit_code=int(exitstatus),
        counts=counts,
        started=STATE.ordinal,
        completed=STATE.completed,
        sql_count=STATE.sql_count if STATE.enabled else None,
        sql_ns=STATE.sql_ns if STATE.enabled else None,
        sql_counter_observed_ns=STATE.sql_observer_ns if STATE.enabled else None,
        hook_observed_ns=STATE.hook_ns,
        truncated=STATE.truncated,
        observer_fault=STATE.fault,
    )
    for owner, name, original in STATE.originals:
        setattr(owner, name, original)
