"""C04 test failures retain useful locations without private exception payloads."""

import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit
ROOT = Path(__file__).resolve().parents[3]


def test_required_gate_redacts_failure_payload_and_retains_failure(tmp_path):
    source = tmp_path / "test_synthetic_failure.py"
    source.write_text(
        "def test_synthetic_failure():\n"
        "    raise ValueError('synthetic-private-health-token')\n"
    )
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "docker/c04_gate.py"),
            str(source),
            "-q",
            "--strict-markers",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 1
    assert "synthetic-private-health-token" not in result.stdout + result.stderr
    assert (
        "C04_FAILURE" in result.stdout and '"exception": "ValueError"' in result.stdout
    )


def test_collect_only_cannot_be_reported_as_runtime_acceptance(tmp_path):
    source = tmp_path / "test_synthetic_collection.py"
    source.write_text("def test_synthetic_collection():\n    assert True\n")
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "docker/c04_gate.py"),
            str(source),
            "-q",
            "--collect-only",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode != 0


def test_deselected_required_cases_cannot_be_reported_as_runtime_acceptance(tmp_path):
    source = tmp_path / "test_synthetic_selection.py"
    source.write_text(
        "def test_first():\n    assert True\ndef test_second():\n    assert True\n"
    )
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "docker/c04_gate.py"),
            str(source),
            "-q",
            "-k",
            "test_first",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode != 0
