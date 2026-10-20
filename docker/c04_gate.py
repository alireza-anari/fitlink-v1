"""Fail a C04 pytest command on required skips or expected failures."""

import errno
import importlib
import json
import math
import os
import sys
import tempfile
from pathlib import Path
from uuid import uuid4

import pytest


def evidence_folder(root):
    folder = root / ".runtime/c04-gate-evidence" / uuid4().hex
    try:
        folder.mkdir(parents=True, mode=0o700)
    except OSError as error:
        if not isinstance(error, PermissionError) and error.errno != errno.EROFS:
            raise
        # Non-root checks use a host-owned bind mount. Keep checkout permissions
        # intact and create a private, atomically unique folder in writable tmp.
        folder = Path(tempfile.mkdtemp(prefix="fitlink-c04-gate-"))
    return folder


class RequiredEvidence:
    counts = None

    def __init__(self):
        self.query_plans = []
        self.invalid_plan = False

    def pytest_runtest_logreport(self, report):
        if report.when != "call":
            return
        for name, value in report.user_properties:
            if name != "c04_query_plan":
                continue
            expected = (
                "tests/integration/c04/test_search_query_plans.py::"
                "test_real_bounded_fts_trigram_query_plan"
            )
            fields = {
                "rows",
                "returned",
                "index_nodes",
                "planning_ms",
                "execution_ms",
                "buffer_blocks",
            }
            if (
                report.nodeid != expected
                or report.outcome != "passed"
                or not isinstance(value, dict)
                or set(value) != fields
                or any(
                    type(v) not in (int, float)
                    or not math.isfinite(v)
                    or not 0 <= v <= 1e9
                    for v in value.values()
                )
                or any(
                    type(value[k]) is not int
                    for k in ("rows", "returned", "index_nodes", "buffer_blocks")
                )
                or value["rows"] < 30000
                or value["returned"] > 100
                or value["index_nodes"] < 2
                or value["execution_ms"] >= 2000
                or value["buffer_blocks"] > 2000
            ):
                self.invalid_plan = True
            else:
                self.query_plans.append(value)

    def pytest_sessionfinish(self, session):
        terminal = session.config.pluginmanager.get_plugin("terminalreporter")
        if terminal:
            self.counts = {
                key: len(terminal.stats.get(key, ()))
                for key in (
                    "passed",
                    "failed",
                    "error",
                    "skipped",
                    "xfailed",
                    "xpassed",
                    "deselected",
                )
            }
        if (
            self.invalid_plan
            or (
                os.environ.get("C04_SEARCH_EVIDENCE") == "1"
                and len(self.query_plans) != 1
            )
            or not terminal
            or not terminal.stats.get("passed")
            or any(
                terminal.stats.get(k)
                for k in (
                    "failed",
                    "error",
                    "skipped",
                    "xfailed",
                    "xpassed",
                    "deselected",
                )
            )
        ):
            session.exitstatus = 1


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root))
    folder = evidence_folder(root)
    os.environ["C03_FOUNDATION_TRIAGE"] = "1"
    os.environ["C03_TRIAGE_EVIDENCE_FILE"] = str(folder / "reports.jsonl")
    triage = importlib.import_module("docker.c03_pytest_triage")
    evidence = RequiredEvidence()
    # Raw pytest/internal-error/capture output can contain synthetic private
    # payloads. Keep it in an unlinked private file; emit existing finite triage.
    sys.stdout.flush()
    sys.stderr.flush()
    saved = (os.dup(1), os.dup(2))
    code = 3
    runner_error = None
    try:
        with tempfile.TemporaryFile(dir=folder) as private:
            os.dup2(private.fileno(), 1)
            os.dup2(private.fileno(), 2)
            try:
                code = int(
                    pytest.main(
                        [*sys.argv[1:], "--basetemp", str(folder / "tmp")],
                        plugins=[evidence, triage],
                    )
                )
            except BaseException as error:
                from docker.c03_storage_errors import error_category

                runner_error = error_category(error)
            finally:
                try:
                    sys.stdout.flush()
                    sys.stderr.flush()
                finally:
                    os.dup2(saved[0], 1)
                    os.dup2(saved[1], 2)
    finally:
        os.close(saved[0])
        os.close(saved[1])
    for metrics in evidence.query_plans:
        print("C04_QUERY_PLAN " + json.dumps(metrics, sort_keys=True), flush=True)
    if runner_error:
        print("C04_RUNNER_ERROR " + json.dumps({"category": runner_error}), flush=True)
    if code == 0 and (
        not evidence.counts
        or not evidence.counts["passed"]
        or any(
            evidence.counts[key]
            for key in (
                "failed",
                "error",
                "skipped",
                "xfailed",
                "xpassed",
                "deselected",
            )
        )
    ):
        code = 1
    for path in folder.glob("*.jsonl"):
        for line in path.read_text().splitlines():
            event = json.loads(line)
            if event.get("event") in {"test_report", "pytest_internalerror"} and (
                event.get("outcome") not in {None, "passed"}
                or event.get("event") == "pytest_internalerror"
            ):
                print("C04_FAILURE " + json.dumps(event, sort_keys=True), flush=True)
    print(
        "C04_REQUIRED_COUNTS "
        + json.dumps({"counts": evidence.counts, "exit_code": code}, sort_keys=True),
        flush=True,
    )
    if os.environ.get("C04_MEDIA_GATE") == "1":
        # Existing triage already strips captures, values and exception text.
        # The outer supervisor discards arbitrary stdout; persist only these
        # finite records to the dedicated, non-secret evidence directory.
        target = root / ".runtime/c03-triage/c04-media.jsonl"
        with target.open("a") as destination:
            for source in folder.glob("*.jsonl"):
                for line in source.read_text().splitlines():
                    record = json.loads(line)
                    if record.get("event") in {"test_report", "pytest_internalerror"}:
                        destination.write(json.dumps(record, sort_keys=True) + "\n")
            destination.write(
                json.dumps(
                    {
                        "event": "required_counts",
                        "counts": evidence.counts,
                        "exit_code": code,
                    },
                    sort_keys=True,
                )
                + "\n"
            )
    raise SystemExit(code)
