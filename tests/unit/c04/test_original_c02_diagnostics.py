"""Behavioral checks for finite, private C02 prerequisite observations."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STAGES = (
    "original_c02_lock",
    "original_c02_sync",
    "original_c02_npm",
    "original_c02_css",
    "original_c02_js",
    "original_c02_static",
    "original_c02_lint",
    "original_c02_format",
    "original_c02_types",
    "original_c02_check",
    "original_c02_units",
    "original_c02_production",
    "original_c02_runtime",
)


class OriginalC02DiagnosticsTests(unittest.TestCase):
    def exercise(self, failure):
        source = (ROOT / "docker/verify_c03.sh").read_text()
        functions = source[
            source.index("run_step() {") : source.index(
                "# Invoke the immutable complete original"
            )
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            for name in ("private", "evidence", "baseline", "bin"):
                (path / name).mkdir()
            stub = path / "bin/uv"
            stub.write_text(
                "#!/bin/sh\n"
                'n=0; test ! -f "$OBSERVATION_COUNT" || '
                'read -r n < "$OBSERVATION_COUNT"\n'
                'n=$((n+1)); printf \'%s\\n\' "$n" > "$OBSERVATION_COUNT"\n'
                "printf 'PRIVATE-C02-OUTPUT-SENTINEL\\n'\n"
                'test "$n" -ne "$OBSERVATION_FAILURE" || exit 17\n'
            )
            stub.chmod(0o755)
            for name in ("npm", "sh"):
                (path / "bin" / name).symlink_to(stub)
            (path / "bin/python").symlink_to(sys.executable)
            script = (
                "set -eu\n"
                f"private='{path / 'private'}'\n"
                f"evidence='{path / 'evidence'}'\n"
                f"baseline='{path / 'baseline'}'\n"
                + functions
                + "\nrun_step exact_original_c02 original_c02\n"
            )
            environment = dict(
                os.environ,
                PATH=str(path / "bin"),
                OBSERVATION_COUNT=str(path / "count"),
                OBSERVATION_FAILURE=str(failure),
            )
            result = subprocess.run(
                ["/bin/sh", "-c", script],
                cwd=ROOT,
                env=environment,
                capture_output=True,
                text=True,
                timeout=30,
            )
            entries = [
                json.loads(line)
                for line in (path / "evidence/upgrade.jsonl").read_text().splitlines()
            ]
            return result, entries, int((path / "count").read_text())

    def test_failure_reports_exact_phase_and_never_runs_later_commands(self):
        for failure in (1, 3, 11, 13):
            with self.subTest(failure=failure):
                result, entries, count = self.exercise(failure)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(count, failure)
                self.assertEqual(
                    len(entries),
                    failure + 1,
                    "Each executed prerequisite needs its own result",
                )
                self.assertEqual(
                    entries[-2],
                    {"stage": STAGES[failure - 1], "exit_code": 17},
                )
                self.assertEqual(
                    entries[-1],
                    {"stage": "exact_original_c02", "exit_code": 17},
                )
                self.assertNotIn("PRIVATE-C02-OUTPUT-SENTINEL", result.stdout)
                self.assertNotIn("PRIVATE-C02-OUTPUT-SENTINEL", result.stderr)

    def test_success_executes_all_original_commands_and_preserves_parent_result(self):
        result, entries, count = self.exercise(0)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(count, len(STAGES))
        self.assertEqual(
            entries,
            [
                {"stage": stage, "exit_code": 0}
                for stage in (*STAGES, "exact_original_c02")
            ],
        )
        self.assertNotIn("PRIVATE-C02-OUTPUT-SENTINEL", result.stdout)


if __name__ == "__main__":
    unittest.main()
