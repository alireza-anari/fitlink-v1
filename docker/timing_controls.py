import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

HERE = Path(__file__).parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


class Controls(unittest.TestCase):
    def test_delegation_preserves_args_identity_return_and_exact_exception(self):
        p = load("timing_profile")
        t = p.Tracker()
        calls = []
        secret = object()
        error = ValueError("PRIVATE")

        def original(*args, **kwargs):
            calls.append((args, kwargs))
            return secret

        self.assertIs(t.wrap("state_clone", original)(secret, token=secret), secret)
        self.assertEqual(calls, [((secret,), {"token": secret})])

        def fail(*args, **kwargs):
            calls.append("fail")
            raise error

        with self.assertRaises(ValueError) as caught:
            t.wrap("migration_apply", fail)("PRIVATE")
        self.assertIs(caught.exception, error)
        self.assertEqual(calls[-1], "fail")
        self.assertEqual(len(calls), 2)
        self.assertNotIn("PRIVATE", json.dumps(t.report()))
        self.assertEqual(sum(x["count"] for x in t.report()["rows"]), 2)

    def test_nested_recursion_and_thread_local_attribution(self):
        p = load("timing_profile")
        t = p.Tracker()
        t.context("call", 1)
        inner = t.wrap("state_clone", lambda: 17)
        outer = t.wrap("migration_execute", lambda: inner())
        self.assertEqual(outer(), 17)
        rows = t.report()["rows"]
        self.assertEqual(len(rows), 2)
        for r in rows:
            self.assertEqual(r["count"], 1)
            self.assertLessEqual(r["self_wall_ns"], r["wall_ns"])
            self.assertLessEqual(r["self_cpu_ns"], r["cpu_ns"])
        self.assertFalse(t.fault)

    def test_bookkeeping_failure_does_not_replace_original_behavior(self):
        p = load("timing_profile")
        t = p.Tracker()
        t.stats = None
        self.assertEqual(t.wrap("search", lambda: 19)(), 19)
        self.assertTrue(t.fault)

    def test_unknown_label_phase_and_bound_are_explicit(self):
        p = load("timing_profile")
        t = p.Tracker()
        with self.assertRaises(ValueError):
            t.wrap("PRIVATE", lambda: None)
        t.context("PRIVATE", 1)
        self.assertTrue(t.fault)
        self.assertNotIn("PRIVATE", json.dumps(t.report()))

    def test_clock_fault_and_original_exception_are_not_masked(self):
        p = load("timing_profile")
        t = p.Tracker()
        calls = []
        with patch.object(p.time, "monotonic_ns", side_effect=ValueError("PRIVATE")):
            self.assertEqual(t.wrap("search", lambda: calls.append(1) or 23)(), 23)
        self.assertEqual(calls, [1])
        self.assertTrue(t.fault)
        t = p.Tracker()
        t.stats = None
        error = RuntimeError("PRIVATE")

        def fail():
            raise error

        with self.assertRaises(RuntimeError) as caught:
            t.wrap("search", fail)()
        self.assertIs(caught.exception, error)
        self.assertTrue(t.fault)

    def test_recursive_and_concurrent_delegation_stays_balanced(self):
        from concurrent.futures import ThreadPoolExecutor

        p = load("timing_profile")
        t = p.Tracker()
        t.context("call", 1)

        def original(n):
            return recursive(n - 1) + 1 if n else 0

        recursive = t.wrap("state_clone", original)
        self.assertEqual(recursive(3), 3)
        wrapped = t.wrap("search", lambda n: n + 1)
        with ThreadPoolExecutor(max_workers=2) as executor:
            self.assertEqual(list(executor.map(wrapped, range(20))), list(range(1, 21)))
        rows = {r["label"]: r for r in t.report()["rows"]}
        self.assertEqual(rows["state_clone"]["count"], 4)
        self.assertEqual(rows["search"]["count"], 20)
        self.assertFalse(t.fault)

    def test_minimal_mode_emits_missing_not_measured_zero(self):
        p = load("timing_profile")
        t = p.Tracker(False)
        calls = []
        self.assertEqual(t.wrap("corpus", lambda: calls.append(1) or 21)(), 21)
        self.assertEqual(calls, [1])
        self.assertIsNone(t.report()["rows"])
        self.assertIsNone(t.report()["bookkeeping_cpu_ns"])

    def test_lifecycle_binding_restores_and_calls_exactly_once(self):
        p = load("timing_profile")
        t = p.Tracker()
        calls = []

        def f(*args, **kwargs):
            calls.append(1)
            return 29

        publication = SimpleNamespace(
            prepare_publication=f, confirm_publication=f, unpublish_profile=f
        )
        market = SimpleNamespace(
            refresh_public_projection=f,
            search_public_professionals=f,
            reconcile_publications=f,
        )
        helpers = SimpleNamespace(coach_approved=f)
        modules = {
            "config.use_cases.publication": publication,
            "config.use_cases.marketplace": market,
            "tests.integration.c04.search_helpers": helpers,
        }

        def original():
            return 31

        item = SimpleNamespace(funcargs={"corpus": original})
        with patch("importlib.import_module", side_effect=lambda name: modules[name]):
            saved, previous = p.install_lifecycle(t, item)
        self.assertEqual(publication.unpublish_profile("PRIVATE"), 29)
        self.assertEqual(calls, [1])
        self.assertEqual(item.funcargs["corpus"](), 31)
        p.restore(saved)
        item.funcargs["corpus"] = previous
        self.assertIs(publication.unpublish_profile, f)
        self.assertIs(item.funcargs["corpus"], original)
        self.assertNotIn("PRIVATE", json.dumps(t.report()))

    def test_hook_restores_bindings_when_original_test_raises(self):
        p = load("timing_plugin")
        profile = load("timing_profile")
        tracker = profile.Tracker()

        def f(*args, **kwargs):
            return 7

        publication = SimpleNamespace(
            prepare_publication=f, confirm_publication=f, unpublish_profile=f
        )
        market = SimpleNamespace(
            refresh_public_projection=f,
            search_public_professionals=f,
            reconcile_publications=f,
        )
        helpers = SimpleNamespace(coach_approved=f)
        modules = {
            "config.use_cases.publication": publication,
            "config.use_cases.marketplace": market,
            "tests.integration.c04.search_helpers": helpers,
        }
        item = SimpleNamespace(funcargs={"corpus": f})
        p.STATE = SimpleNamespace(timing=tracker, ordinal=1)
        error = RuntimeError("PRIVATE")
        with (
            patch.dict("os.environ", {"TIMING_JOB": "budget"}),
            patch("importlib.import_module", side_effect=lambda name: modules[name]),
        ):
            hook = p.pytest_runtest_call(item)
            next(hook)
            self.assertEqual(item.funcargs["corpus"](), 7)
            with self.assertRaises(RuntimeError) as caught:
                hook.throw(error)
        self.assertIs(caught.exception, error)
        self.assertIs(item.funcargs["corpus"], f)
        self.assertIs(publication.unpublish_profile, f)

    def test_controller_rejects_missing_profile_fault_and_wrong_counts(self):
        with patch.dict("os.environ", {"TIMING_JOB": "migration"}):
            r = load("timing_run")
        p = load("timing_profile")
        t = p.Tracker()
        t.context("call", 1)
        for label in ["state_clone", "model_render", "migration_execute"]:
            t.wrap(label, lambda: None)()
        sampler = {
            "errors": 0,
            "thread_stopped": True,
            "samples": 1,
            "clock_sync": {"common_origin_verified": True},
        }
        rows = [
            {
                "event": "collection",
                "unknown_nodes": 0,
                "count": 2,
                "sequence_sha256": "a" * 64,
            },
            {
                "event": "finish",
                "exit_code": 0,
                "started": 2,
                "completed": 2,
                "observer_fault": False,
                "truncated": False,
                "counts": {
                    "passed": 2,
                    "failed": 0,
                    "error": 0,
                    "skipped": 0,
                    "xfailed": 0,
                    "xpassed": 0,
                    "deselected": 0,
                },
            },
        ]
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d)
            (folder / "pytest.jsonl").write_text(
                "".join(json.dumps(x) + "\n" for x in rows)
            )
            self.assertFalse(r.evidence_check(folder, sampler)["valid"])
            record = {
                "mono_start_ns": 1,
                "mono_end_ns": 2,
                "host": {
                    "cpu_count": 4,
                    "cpu_ticks": [1] * 8,
                    "memory_kib": {"MemAvailable": 100},
                },
                "postgres": {
                    k: 0
                    for k in [
                        "active",
                        "lock_wait",
                        "io_wait",
                        "lwlock_wait",
                        "ungranted_locks",
                    ]
                },
                "containers": {
                    k: {"running": True}
                    for k in [
                        "db",
                        "redis",
                        "minio",
                        "scanner",
                        "web",
                        "worker",
                        "beat",
                        "checks",
                    ]
                },
            }
            (folder / "host.jsonl").write_text(json.dumps(record) + "\n")
            value = {
                "job": "migration",
                "profile": t.report(),
                "calibration": {"calls": 10000, "wall_ns": 1, "fault": False},
            }
            path = folder / "timing.json"
            path.write_text(json.dumps(value))
            self.assertTrue(r.evidence_check(folder, sampler)["valid"])
            value["profile"]["fault"] = True
            path.write_text(json.dumps(value))
            self.assertFalse(r.evidence_check(folder, sampler)["valid"])
            value["profile"]["fault"] = False
            value["profile"]["rows"] = []
            path.write_text(json.dumps(value))
            self.assertFalse(r.evidence_check(folder, sampler)["valid"])

    def test_clock_probe_only_running_and_bounded_retry(self):
        m = load("timing_metrics")
        s = m.Sampler()
        with patch.object(m, "capture", return_value=None) as cap:
            s.probe_clock({"checks": {"running": False}}, {"checks": "STATIC"})
            self.assertEqual(s.clock_attempts, 0)
            cap.assert_not_called()
            s.probe_clock({"checks": {"running": True}}, {"checks": "STATIC"})
            self.assertEqual(s.clock_attempts, 1)
            self.assertFalse(s.clock_sync["common_origin_verified"])
        with patch.object(
            m, "capture", side_effect=lambda *args, **kwargs: str(m.time.monotonic_ns())
        ) as cap:
            s.probe_clock({"checks": {"running": True}}, {"checks": "STATIC"})
            self.assertTrue(s.clock_sync["common_origin_verified"])
            self.assertEqual(s.clock_attempts, 2)
            s.probe_clock({"checks": {"running": True}}, {"checks": "STATIC"})
            self.assertEqual(cap.call_count, 1)
        s = m.Sampler()
        with patch.object(m, "capture", return_value=None) as cap:
            for _ in range(5):
                s.probe_clock({"checks": {"running": True}}, {"checks": "STATIC"})
            self.assertEqual(cap.call_count, 3)

    def test_resource_journal_missing_is_not_zero(self):
        r = load("timing_run")
        with tempfile.TemporaryDirectory() as d:
            self.assertFalse(r.resource_evidence(Path(d), 1)["valid"])
            value = {
                "mono_start_ns": 1,
                "mono_end_ns": 2,
                "host": None,
                "postgres": None,
                "containers": None,
            }
            (Path(d) / "host.jsonl").write_text(json.dumps(value) + "\n")
            result = r.resource_evidence(Path(d), 1)
            self.assertFalse(result["valid"])
            self.assertEqual(result["missing_postgres_samples"], 1)

    def test_cleanup_refuses_missing_or_mismatched_ownership(self):
        r = load("timing_run")
        with tempfile.TemporaryDirectory() as d:
            r.m.PRIVATE = Path(d)
            r.m.PROJECT = "STATIC_PROJECT"
            with patch.object(r.subprocess, "run") as command:
                result = {}
                r.cleanup(result)
                self.assertFalse(result["cleanup_complete"])
                command.assert_not_called()
                (Path(d) / "owned").write_text("OTHER_PROJECT")
                result = {}
                r.cleanup(result)
                self.assertFalse(result["cleanup_complete"])
                command.assert_not_called()

    def test_actual_job_selection_and_subset_bounds(self):
        import ast

        r = load("timing_run")
        self.assertEqual(len(r.MIGRATION_TESTS), 2)
        self.assertEqual(len(r.BUDGET_TESTS), 1)
        self.assertTrue(all("::test_" in n for n in r.MIGRATION_TESTS + r.BUDGET_TESTS))
        tree = ast.parse((HERE / "timing_run.py").read_text())
        calls = [
            n
            for n in ast.walk(tree)
            if isinstance(n, ast.Call)
            and isinstance(n.func, ast.Name)
            and n.func.id == "shell_stage"
            and len(n.args) > 2
            and isinstance(n.args[1], ast.Constant)
            and n.args[1].value == "matched_subset"
        ]
        self.assertEqual(len(calls), 1)
        bound = calls[0].args[-1]
        self.assertIsInstance(bound, ast.IfExp)
        self.assertEqual(bound.body.value, 300)
        self.assertEqual(bound.orelse.value, 600)

    def test_calibration_and_all_migration_bindings_restore(self):
        p = load("timing_profile")
        t = p.Tracker()
        from django.db.migrations.state import ProjectState

        original = ProjectState.clone
        saved = p.install_migrations(t)
        try:
            state = ProjectState()
            cloned = state.clone()
            self.assertIsNot(cloned, state)
            self.assertEqual(cloned.models, state.models)
        finally:
            p.restore(saved)
        self.assertIs(ProjectState.clone, original)
        c = p.calibration()
        self.assertEqual(c["calls"], 10000)
        self.assertFalse(c["fault"])
        self.assertGreater(c["wall_ns"], 0)


if __name__ == "__main__":
    unittest.main()
