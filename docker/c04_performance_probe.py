"""Finite, non-acceptance ABBA measurements; never export SQL or pytest output."""

import argparse
import contextlib
import hashlib
import json
import os
import re
import sys
import threading
import time
from pathlib import Path

SELECTION = [
    "tests/unit/c02/test_inputs.py::test_exhaustive_supported_calendar_roundtrip",
    "tests/integration/c02/test_staff_authority.py",
    "tests/integration/c04/test_comparison.py",
    "tests/integration/c04/test_search_eligibility.py::"
    "test_candidate_budget_fails_without_partial_output_and_recovers",
]
WAIT_TYPES = {"Lock", "IO", "LWLock", "IPC", "Timeout", "Client", "Activity"}


def snapshot():
    result = {}
    try:
        fields = Path("/proc/stat").read_text().splitlines()[0].split()[1:9]
        result["cpu_ticks"] = [int(x) for x in fields]
        memory = dict(
            re.findall(
                r"^(MemAvailable|Dirty|Writeback):\s+(\d+)",
                Path("/proc/meminfo").read_text(),
                re.M,
            )
        )
        result["memory_kib"] = {k: int(v) for k, v in memory.items()}
        result["disk_free_bytes"] = os.statvfs(".").f_bavail * os.statvfs(".").f_frsize
        result["cpu_count"] = os.cpu_count()
        for key, filename in [
            ("cpu_pressure", "/proc/pressure/cpu"),
            ("io_pressure", "/proc/pressure/io"),
        ]:
            result[key] = [
                float(x)
                for x in re.findall(r"avg10=(\d+\.\d+)", Path(filename).read_text())
            ]
    except (OSError, ValueError, IndexError):
        result["unavailable"] = True
    return result


def monitor(stop, result):
    # A separate read-only connection samples aggregate counts, never queries,
    # PIDs, addresses, users, database names, lock keys or application values.
    try:
        import psycopg

        with psycopg.connect(
            host=os.environ["POSTGRES_HOST"],
            dbname="fitlink",
            user="fitlink",
            password=os.environ["POSTGRES_PASSWORD"],
            connect_timeout=3,
            autocommit=True,
            options="-c statement_timeout=1000",
        ) as connection:
            while not stop.is_set():
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT wait_event_type, count(*) FROM pg_stat_activity "
                        "WHERE datname = 'test_fitlink' AND state = 'active' "
                        "GROUP BY wait_event_type"
                    )
                    for kind, count in cursor.fetchall():
                        key = kind if kind in WAIT_TYPES else "running_or_other"
                        result[key] = max(result.get(key, 0), count)
                result["samples"] += 1
                stop.wait(2)
    except Exception:
        result["unavailable"] = True


class Evidence:
    def __init__(self):
        self.rows = []
        self.collection = {}
        self.sql = [0, 0.0]
        self.previous = [0, 0.0]
        self.lock = threading.Lock()
        self.counts = {}

    def pytest_collection_finish(self, session):
        # Parameter values never leave the process, including via hashes.
        nodes = [item.nodeid.split("[", 1)[0] for item in session.items]
        self.collection = {
            "count": len(nodes),
            "sequence_without_parameters_sha256": hashlib.sha256(
                "\n".join(nodes).encode()
            ).hexdigest(),
        }

    def pytest_runtest_logreport(self, report):
        with self.lock:
            sql = self.sql.copy()
        delta = [sql[0] - self.previous[0], round(sql[1] - self.previous[1], 6)]
        self.previous = sql
        # Only static known source paths and unparameterized test symbols.
        node = report.nodeid.split("[", 1)[0]
        if not any(
            node.startswith(path.split("::", 1)[0] + "::")
            for path in [
                *SELECTION,
                "tests/unit/c04/test_minio_baseline_diagnostics.py",
            ]
        ):
            node = "other"
        self.rows.append(
            {
                "node": node,
                "phase": report.when,
                "seconds": round(report.duration, 6),
                "sql": delta,
            }
        )
        key = (
            report.outcome
            if report.outcome in {"passed", "failed", "skipped"}
            else "other"
        )
        self.counts[key] = self.counts.get(key, 0) + 1

    def wrap(self, original):
        def measured(cursor, *args, **kwargs):
            started = time.monotonic()
            try:
                return original(cursor, *args, **kwargs)
            finally:
                with self.lock:
                    self.sql[0] += 1
                    self.sql[1] += time.monotonic() - started

        return measured


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("mode", choices=["collect", "minio", "sample"])
    parser.add_argument("output")
    args = parser.parse_args()
    source = Path(args.source).resolve()
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    os.chdir(source)
    sys.path.insert(0, str(source))
    evidence = Evidence()
    started, cpu = time.monotonic(), time.process_time()
    before = snapshot()
    waits = {"samples": 0}
    stop = threading.Event()
    observer = None
    code = 99
    # Capture all framework output, including collection and exception text.
    with (
        open(os.devnull, "w") as sink,
        contextlib.redirect_stdout(sink),
        contextlib.redirect_stderr(sink),
    ):
        try:
            from unittest.mock import patch

            import pytest
            from django.db.backends.utils import CursorWrapper

            selection = SELECTION
            if args.mode == "collect":
                selection = ["tests/unit", "tests/integration", "--collect-only"]
            elif args.mode == "minio":
                selection = ["tests/unit/c04/test_minio_baseline_diagnostics.py"]
            else:
                observer = threading.Thread(
                    target=monitor, args=(stop, waits), daemon=True
                )
                observer.start()
            with (
                patch.object(
                    CursorWrapper, "execute", evidence.wrap(CursorWrapper.execute)
                ),
                patch.object(
                    CursorWrapper,
                    "executemany",
                    evidence.wrap(CursorWrapper.executemany),
                ),
            ):
                code = int(
                    pytest.main(
                        [
                            *selection,
                            "-q",
                            "--strict-markers",
                            "--tb=no",
                            "--show-capture=no",
                            "--basetemp=" + str(output.with_suffix(".tmp")),
                        ],
                        plugins=[evidence],
                    )
                )
        except Exception:
            code = 99
        finally:
            stop.set()
            if observer:
                observer.join(timeout=5)
    report = {
        "acceptance": False,
        "mode": args.mode,
        "source_sha": os.environ["PROBE_SOURCE_SHA"],
        "exit_code": code,
        "wall_seconds": round(time.monotonic() - started, 6),
        "process_cpu_seconds": round(time.process_time() - cpu, 6),
        "before": before,
        "after": snapshot(),
        "wait_maxima": waits,
        "collection": evidence.collection,
        "reports": evidence.rows,
        "outcomes_by_phase": evidence.counts,
        "sql": evidence.sql,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "acceptance": False,
                "mode": args.mode,
                "exit_code": code,
                "wall_seconds": report["wall_seconds"],
            }
        )
    )
    return code


if __name__ == "__main__":
    raise SystemExit(main())
