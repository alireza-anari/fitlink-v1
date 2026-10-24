import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


class Controls(unittest.TestCase):
    def test_evidence_requires_finish_health_and_zero_skips(self):
        r = load("causal_run")
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d)
            sampler = {
                "errors": 0,
                "thread_stopped": True,
                "samples": 1,
                "clock_sync": {"common_origin_verified": True},
            }
            self.assertFalse(r.evidence_check(folder, sampler)["valid"])
            rows = [
                {
                    "event": "collection",
                    "unknown_nodes": 0,
                    "count": 5,
                    "sequence_sha256": "a" * 64,
                },
                {
                    "event": "finish",
                    "exit_code": 0,
                    "started": 5,
                    "completed": 5,
                    "observer_fault": False,
                    "truncated": False,
                    "counts": {
                        "passed": 5,
                        "failed": 0,
                        "error": 0,
                        "skipped": 0,
                        "xfailed": 0,
                        "xpassed": 0,
                        "deselected": 0,
                    },
                },
            ]

            def save():
                (folder / "pytest.jsonl").write_text(
                    "".join(json.dumps(x) + "\n" for x in rows)
                )

            save()
            self.assertTrue(r.evidence_check(folder, sampler)["valid"])
            rows[-1]["truncated"] = True
            save()
            self.assertFalse(r.evidence_check(folder, sampler)["valid"])
            rows[-1]["truncated"] = False
            rows[-1]["counts"]["skipped"] = 1
            save()
            self.assertFalse(r.evidence_check(folder, sampler)["valid"])
            rows[-1]["counts"]["skipped"] = 0
            save()
            sampler["errors"] = 1
            self.assertFalse(r.evidence_check(folder, sampler)["valid"])

    def test_subset_bound_and_no_full_regression_selection(self):
        import ast

        r = load("causal_run")
        self.assertEqual(len(r.TESTS), 5)
        self.assertTrue(all("::test_" in x for x in r.TESTS))
        tree = ast.parse((HERE / "causal_run.py").read_text())
        matched = [
            n
            for n in ast.walk(tree)
            if isinstance(n, ast.Call)
            and isinstance(n.func, ast.Name)
            and n.func.id == "shell_stage"
            and len(n.args) > 2
            and isinstance(n.args[1], ast.Constant)
            and n.args[1].value == "matched_subset"
        ]
        self.assertEqual(len(matched), 1)
        self.assertEqual(matched[0].args[-1].value, 600)

    def test_fixture_closure_includes_all_conftests_and_test_helpers(self):
        r = load("causal_run")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for name, body in [
                (
                    "tests/integration/c02/conftest.py",
                    "from tests.shared import helper",
                ),
                ("tests/shared.py", "def helper(): pass"),
            ]:
                p = root / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(body)
            paths = r.fixture_closure(root)
            self.assertIn("tests/integration/c02/conftest.py", paths)
            self.assertIn("tests/shared.py", paths)

    def test_classification_uses_immediate_exits_not_elapsed(self):
        c = load("causal_classify")
        self.assertEqual(
            c.classify({"init_exit_code": 1, "operations": None}), "unobservable"
        )
        alias = []
        ready = []
        for _ in range(30):
            alias += [
                {"event": "start", "operation": "alias"},
                {"event": "end", "operation": "alias", "exit_code": 1},
            ]
            ready += [
                {"event": "start", "operation": "alias"},
                {"event": "end", "operation": "alias", "exit_code": 0},
                {"event": "start", "operation": "ready"},
                {"event": "end", "operation": "ready", "exit_code": 1},
            ]
        self.assertEqual(
            c.classify({"init_exit_code": 1, "operations": alias}),
            "alias_initialization_exhaustion",
        )
        self.assertEqual(
            c.classify({"init_exit_code": 1, "operations": ready}),
            "readiness_exhaustion",
        )
        self.assertEqual(
            c.classify(
                {
                    "init_exit_code": 1,
                    "operations": [
                        {"event": "start", "operation": "bucket"},
                        {"event": "end", "operation": "bucket", "exit_code": 1},
                    ],
                }
            ),
            "bucket_operation_failed",
        )
        self.assertEqual(
            c.classify(
                {"init_exit_code": 1, "operations": [], "container_exit_code": None}
            ),
            "docker_invocation_failed_underlying_unknown",
        )
        self.assertEqual(
            c.classify({"init_exit_code": 0, "operations": []}), "insufficient_evidence"
        )
        self.assertEqual(
            c.classify(
                {
                    "init_exit_code": 1,
                    "operations": [{"event": "start", "operation": "ready"}],
                }
            ),
            "incomplete_operation_observation",
        )

    def test_sql_class_has_no_dynamic_keys(self):
        p = load("causal_plugin")
        for sql, expected in [
            (" SELECT secret", "SELECT"),
            ("TRUNCATE secret", "TRUNCATE"),
            ("-- private\nSELECT token", "OTHER"),
            (object(), "OTHER"),
            ("BEGIN", "TRANSACTION"),
        ]:
            self.assertEqual(p.sql_class(sql), expected)

    def test_sql_delegate_result_exception_and_redaction(self):
        p = load("causal_plugin")
        with tempfile.TemporaryDirectory() as d:
            o = p.Observer(Path(d))
            try:
                self.assertEqual(
                    o.wrap(lambda *args, **kwargs: 71)(
                        None, "SELECT PRIVATE", ["SECRET"]
                    ),
                    71,
                )

                def fail(*args, **kwargs):
                    raise ValueError("PRIVATE_EXCEPTION")

                with self.assertRaises(ValueError):
                    o.wrap(fail)(None, "TRUNCATE PRIVATE")
                o.emit("classes", values=o.classes)
                self.assertNotIn("PRIVATE", (Path(d) / "pytest.jsonl").read_text())
                self.assertEqual(o.classes["SELECT"]["count"], 1)
                self.assertEqual(o.classes["TRUNCATE"]["count"], 1)
                self.assertEqual(sum(o.classes["SELECT"]["bins"]), 1)
            finally:
                o.file.close()

    def test_mc_operation_allowlist_never_echoes_arguments(self):
        m = load("mc_observe")
        for args, expected in [
            (["alias", "set", "SECRET"], "alias"),
            (["ready", "SECRET"], "ready"),
            (["admin", "user", "add", "SECRET"], "user"),
            (["admin", "policy", "attach", "SECRET"], "attach"),
            (["PRIVATE"], "unknown"),
        ]:
            self.assertEqual(m.operation(args), expected)

    def test_mc_exit_and_streams_preserved_numeric_log_only(self):
        m = load("mc_observe")
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "events"
            fake = Path(d) / "fake"
            fake.write_text("#!/bin/sh\nprintf CONTROL_OUTPUT\nexit 17\n")
            fake.chmod(0o755)
            with patch.object(m, "REAL", str(fake)), patch.object(m, "LOG", path):
                self.assertEqual(m.run(["admin", "user", "add", "PRIVATE"]), 17)
            records = [json.loads(x) for x in path.read_text().splitlines()]
            self.assertEqual([r["event"] for r in records], ["start", "end"])
            self.assertEqual(records[-1]["exit_code"], 17)
            self.assertNotIn("PRIVATE", path.read_text())
            self.assertGreaterEqual(records[-1]["mono_ns"], records[0]["mono_ns"])

    def test_mc_logging_failure_does_not_change_exit(self):
        m = load("mc_observe")
        with tempfile.TemporaryDirectory() as d:
            with (
                patch.object(m, "REAL", "/bin/true"),
                patch.object(m, "LOG", Path(d) / "missing" / "x"),
            ):
                self.assertEqual(m.run(["ready", "SECRET"]), 0)


if __name__ == "__main__":
    unittest.main()
