"""Emit strictly finite per-phase pytest timing for the Task 7 fixture comparison.

This plugin never records SQL, request payloads, account IDs or exception text.
"""
from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path

RESULT = Path(os.environ["FITLINK_FIXTURE_PHASE_PATH"])
SOURCE_SHA = os.environ["FITLINK_FIXTURE_SOURCE_SHA"]
SOURCE_TREE = os.environ["FITLINK_FIXTURE_SOURCE_TREE"]
STAGES = {"setup", "call", "teardown"}
ROWS = {}
STARTED = 0.0
PROCESS_STARTED = 0.0
MAX_CASES = 40


def pytest_sessionstart(session):
    global STARTED, PROCESS_STARTED
    STARTED = time.perf_counter()
    PROCESS_STARTED = time.process_time()


def pytest_runtest_logreport(report):
    node = report.nodeid
    if not re.fullmatch(
        r"tests/integration/c04/test_(?:educational_posts|post_races)\.py::"
        r"test_[a-z0-9_]+(?:\[[a-z0-9_]+\])?",
        node,
    ):
        return
    if report.when not in STAGES:
        return
    if node not in ROWS and len(ROWS) >= MAX_CASES:
        return
    row = ROWS.setdefault(node, {"test": node, "status": "not_observed", "phases": {}})
    row["phases"][report.when] = round(max(0.0, float(report.duration)), 6)
    if report.failed:
        row["status"] = "failed"
    elif report.skipped and row["status"] != "failed":
        row["status"] = "skipped"
    elif report.when == "call" and report.passed and row["status"] == "not_observed":
        row["status"] = "passed"


def pytest_sessionfinish(session, exitstatus):
    rows = [ROWS[node] for node in sorted(ROWS)]
    statuses = {"passed": 0, "failed": 0, "skipped": 0, "not_observed": 0}
    for row in rows:
        statuses[row["status"]] += 1
    value = {
        "schema_version": 1,
        "acceptance": False,
        "source_sha": SOURCE_SHA,
        "source_tree": SOURCE_TREE,
        "pytest_exit_code": int(exitstatus),
        "status_counts": statuses,
        "cases": rows,
        "session_wall_seconds": round(max(0.0, time.perf_counter() - STARTED), 6),
        "session_process_cpu_seconds": round(max(0.0, time.process_time() - PROCESS_STARTED), 6),
        "phase_duration_source": "pytest TestReport.duration (wall clock)",
        "no_sql_or_sensitive_payloads_recorded": True,
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")
