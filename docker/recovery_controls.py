import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RecoveryControls(unittest.TestCase):
    def test_startup_classification_missing_empty_oversized_and_secret_redaction(self):
        p = load("startup_observer")
        cases = [
            (b"", "unclassified"),
            (
                b"PRIVATE https://secret:token@private port is already allocated",
                "networking",
            ),
            (b"Cannot connect to the Docker daemon at PRIVATE", "daemon_availability"),
            (b"PRIVATE manifest unknown", "image_retrieval"),
            (
                b"PRIVATE dependency failed to start: container x is unhealthy",
                "readiness_health",
            ),
            (b"PRIVATE permission denied", "permissions"),
        ]
        for raw, expected in cases:
            result = p.classify(1, raw, None, [])
            self.assertEqual(result["category"], expected)
            self.assertNotIn("PRIVATE", json.dumps(result))
            self.assertNotIn("secret", json.dumps(result))
        self.assertEqual(p.classify(0, b"", 0, [])["category"], "startup_succeeded")
        self.assertEqual(p.classify(1, None, None, [])["category"], "unclassified")
        self.assertEqual(
            p.classify(1, b"x" * 1048577, None, [])["category"], "unclassified"
        )

    def test_bounded_private_capture_preserves_exit_and_never_exports_raw(self):
        p = load("startup_observer")
        import sys

        with tempfile.TemporaryDirectory() as d:
            folder = Path(d)
            result = p.private_run(
                [
                    sys.executable,
                    "-c",
                    "import sys;sys.stdout.write('PRIVATE'*200000);"
                    "sys.stderr.write('PRIVATE');sys.exit(7)",
                ],
                folder,
                10,
            )
            self.assertEqual(result["exit_code"], 7)
            self.assertTrue(result["stdout_truncated"])
            self.assertLessEqual((folder / "stdout").stat().st_size, 1048576)
            self.assertNotIn("PRIVATE", json.dumps(result))
            self.assertGreaterEqual(result["end_ns"], result["start_ns"])

    def test_state_projection_drops_health_output_names_and_ids(self):
        p = load("startup_observer")
        raw = {
            "Config": {"Labels": {"com.docker.compose.service": "db"}},
            "Name": "PRIVATE",
            "Id": "PRIVATE",
            "State": {
                "Status": "running",
                "Running": True,
                "ExitCode": 0,
                "OOMKilled": False,
                "Health": {
                    "Status": "healthy",
                    "FailingStreak": 0,
                    "Log": [{"Output": "PRIVATE"}],
                },
            },
        }
        result = p.safe_state(raw)
        self.assertEqual(result["service"], "db")
        self.assertEqual(result["health"], "healthy")
        self.assertNotIn("PRIVATE", json.dumps(result))
        raw["Config"]["Labels"]["com.docker.compose.service"] = "PRIVATE"
        self.assertIsNone(p.safe_state(raw))

    def test_capture_then_snapshot_is_completed_before_observe_returns(self):
        from unittest.mock import patch

        p = load("startup_observer")
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d)
            events = []
            m = SimpleNamespace(PRIVATE=folder, SOURCE=folder)

            def capture(*args, **kwargs):
                events.append("capture")
                dest = args[1]
                dest.mkdir()
                (dest / "stdout").write_bytes(b"PRIVATE permission denied")
                (dest / "stderr").write_bytes(b"")
                return {"capture_complete": True, "exit_code": 13}

            def snapshot(*args):
                events.append("snapshot")
                return {"daemon_exit_code": 0, "services": []}

            with (
                patch.object(p, "private_run", side_effect=capture),
                patch.object(p, "snapshot", side_effect=snapshot),
            ):
                result = p.observe(m, ["STATIC"], 10, "services")
            self.assertEqual(events, ["capture", "snapshot"])
            self.assertEqual(result["capture"]["exit_code"], 13)
            self.assertEqual(result["classification"]["category"], "permissions")
            self.assertNotIn("PRIVATE", json.dumps(result))

    def test_per_migration_delegates_once_and_preserves_exact_exception(self):
        p = load("timing_profile")
        t = p.Tracker()
        self.assertTrue(
            hasattr(t, "migration_wrap"), "missing per-migration attribution"
        )
        t.migration_manifest = {("accounts", "0001_initial"): 1}
        migration = SimpleNamespace(
            app_label="accounts", name="0001_initial", operations=[object(), object()]
        )
        calls = []
        sentinel = object()
        wrapped = t.migration_wrap(
            "migration_apply", lambda *a, **kw: calls.append((a, kw)) or sentinel
        )
        self.assertIs(wrapped(migration, token=sentinel), sentinel)
        self.assertEqual(len(calls), 1)
        error = ValueError("PRIVATE")

        def fail(*a, **kw):
            calls.append(1)
            raise error

        with self.assertRaises(ValueError) as caught:
            t.migration_wrap("migration_unapply", fail)(migration)
        self.assertIs(caught.exception, error)
        self.assertEqual(len(calls), 2)
        report = t.report()
        self.assertEqual(len(report["migrations"]), 2)
        self.assertTrue(all(x["operation_count"] == 2 for x in report["migrations"]))
        self.assertNotIn("PRIVATE", json.dumps(report))
        self.assertFalse(t.fault)


if __name__ == "__main__":
    unittest.main()
