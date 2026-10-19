"""Fail a C04 pytest command on required skips or expected failures."""

import importlib
import json
import os
import sys
import tempfile
from pathlib import Path
from uuid import uuid4

import pytest


class RequiredEvidence:
    counts = None

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
            not terminal
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
    folder = root / ".runtime/c04-gate-evidence" / uuid4().hex
    folder.mkdir(parents=True, mode=0o700)
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
    raise SystemExit(code)
