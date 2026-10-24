"""Offline privacy/observer controls; no local Docker or database execution."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Controls(unittest.TestCase):
    def setUp(self):
        self.host = load("causal_metrics")
        self.plugin = load("causal_plugin")
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)

    def observer(self):
        observer = self.plugin.Observer(self.folder)
        self.addCleanup(observer.file.close)
        return observer

    def test_delegate_exact_once_return_and_exception_without_private_values(self):
        observer = self.observer()
        calls = []

        def execute(cursor, sql, params):
            calls.append((sql, params))
            return 17

        result = observer.wrap(execute)(None, "PRIVATE_SQL", {"PRIVATE": "SECRET"})
        self.assertEqual(result, 17)
        self.assertEqual(len(calls), 1)

        def fail(*args):
            raise ValueError("PRIVATE_EXCEPTION")

        with self.assertRaises(ValueError):
            observer.wrap(fail)(None, "PRIVATE_SQL")
        self.assertEqual(observer.sql_count, 2)
        observer.emit("counters", count=observer.sql_count, ns=observer.sql_ns)
        self.assertNotIn("PRIVATE", (self.folder / "pytest.jsonl").read_text())

    def test_known_symbol_strips_parameters_unknown_symbol_not_exported(self):
        observer = self.observer()
        self.plugin.STATE = observer
        observer.nodes = {"tests/unit/test_x.py::test_public"}
        self.plugin.pytest_runtest_logstart(
            "tests/unit/test_x.py::test_public[PRIVATE_SECRET]", None
        )
        self.plugin.pytest_runtest_logstart("PRIVATE_PATH::PRIVATE_TEST", None)
        self.plugin.pytest_runtest_logreport(
            SimpleNamespace(when="call", outcome="PRIVATE_FAILURE", duration=0.1)
        )
        data = (self.folder / "pytest.jsonl").read_text()
        self.assertNotIn("PRIVATE", data)
        rows = [json.loads(x) for x in data.splitlines()]
        self.assertEqual(rows[0]["node"], "tests/unit/test_x.py::test_public")
        self.assertEqual(rows[1]["node"], "other")
        self.assertEqual(rows[2]["outcome"], "other")

    def test_children_do_not_patch_or_write_primary_evidence(self):
        self.plugin.OUT = self.folder
        (self.folder / "primary.lock").touch()
        self.plugin.pytest_configure(None)
        self.assertIsNone(self.plugin.STATE)
        self.assertFalse((self.folder / "pytest.jsonl").exists())

    def test_bound_does_not_interrupt_tests(self):
        observer = self.observer()
        observer.rows = 12000
        observer.emit("fixed", count=1)
        self.assertTrue(observer.truncated)
        self.assertEqual((self.folder / "pytest.jsonl").read_text(), "")

    def test_finite_ast_symbol_allowlist(self):
        path = self.folder / "tests/unit/test_x.py"
        path.parent.mkdir(parents=True)
        path.write_text(
            "class TestExample:\n"
            " def test_public(self): pass\n def private(self): pass\n"
        )
        self.assertEqual(
            self.plugin.allowed_nodes(self.folder),
            {"tests/unit/test_x.py::TestExample::test_public"},
        )

    def db_record(self):
        return {
            "active": 1,
            "test_active": 1,
            "service_active": 0,
            "other_active": 0,
            "lock_wait": 0,
            "io_wait": 0,
            "lwlock_wait": 0,
            "client_wait": 0,
            "other_wait": 0,
            "ungranted_locks": 0,
            "io_timing_enabled": False,
            "database": None,
            "io_cluster": None,
        }

    def test_database_missing_is_not_zero(self):
        with patch.object(self.host, "capture", return_value=None):
            self.assertIsNone(self.host.database("internal"))
        record = self.db_record()
        with patch.object(self.host, "capture", return_value=json.dumps(record)):
            self.assertEqual(self.host.database("internal"), record)

    def test_database_rejects_arbitrary_messages_keys_nested_or_nonfinite(self):
        records = []
        for value in ["PRIVATE_SQL", {"PRIVATE_SQL": 1}, float("nan")]:
            record = self.db_record()
            record["database"] = value
            records.append(record)
        record = self.db_record()
        record["PRIVATE_SECRET"] = 1
        records.append(record)
        record = self.db_record()
        record["active"] = "PRIVATE_VALUE"
        records.append(record)
        for record in records:
            with patch.object(self.host, "capture", return_value=json.dumps(record)):
                self.assertIsNone(self.host.database("internal"))

    def test_missing_cgroup_metrics_are_null(self):
        value = self.host.cgroup(self.folder / "missing")
        self.assertIsNone(value["cpu"])
        self.assertIsNone(value["io"])
        self.assertIsNone(value["pressure"]["cpu"])

    def test_cleanup_cannot_acquire_ownership_from_missing_marker(self):
        self.host.PRIVATE = self.folder
        with patch.object(
            self.host.subprocess, "run", side_effect=AssertionError("must not execute")
        ):
            self.assertEqual(self.host.emergency_cleanup(), 0)

    def test_thread_open_failure_is_finite_and_does_not_print_traceback(self):
        import contextlib
        import io

        self.host.OUT = self.folder / "missing"
        sampler = self.host.Sampler()
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            sampler.run()
        self.assertEqual(sampler.errors, 1)
        self.assertEqual(stderr.getvalue(), "")

    def test_post_deadline_cases_are_not_in_terminal_counts(self):
        events = [
            {"mono_ns": 899, "event": "phase"},
            {"mono_ns": 900, "event": "phase"},
            {"mono_ns": 901, "event": "finish"},
            {"event": "unknown"},
        ]
        self.assertEqual(self.host.window_events(events, 900), events[:2])

    def test_cluster_waits_include_auxiliary_database_without_exporting_names(self):
        self.assertIn("pid<>pg_backend_pid()", self.host.SQL)
        for field in ["lock_wait", "io_wait", "lwlock_wait", "other_wait"]:
            part = self.host.SQL.split("'" + field + "'", 1)[1].split(
                "'test_active'", 1
            )[0]
            self.assertNotIn("datname='test_fitlink'", part)

    def test_monitor_query_has_own_server_side_timeouts(self):
        with patch.object(self.host, "capture", return_value=None) as capture:
            self.host.database("internal")
        command = capture.call_args.args[0]
        self.assertIn(
            "PGOPTIONS=-c statement_timeout=1000 -c lock_timeout=500", command
        )
        self.assertIn("PGCONNECT_TIMEOUT=2", command)

    def test_exact_selection_and_original_deadline(self):
        import ast

        tree = ast.parse((ROOT / "causal_metrics.py").read_text())
        values = [
            n.value
            for n in ast.walk(tree)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)
        ]
        self.assertIn("900s", values)
        for arg in [
            "tests/unit",
            "tests/integration",
            "-q",
            "--strict-markers",
            "--tb=no",
            "--show-capture=no",
        ]:
            self.assertIn(arg, values)
        self.assertNotIn("--deselect", values)
        self.assertNotIn("--lf", values)


if __name__ == "__main__":
    unittest.main()
