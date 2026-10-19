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


def test_readonly_checkout_uses_private_writable_evidence(monkeypatch, tmp_path):
    import tempfile

    from docker.c04_gate import evidence_folder

    checkout = tmp_path / "readonly-checkout"
    checkout.mkdir()
    original = Path.mkdir

    def denied(path, *args, **kwargs):
        if path.is_relative_to(checkout):
            raise PermissionError("Readonly synthetic checkout")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "mkdir", denied)
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
    folder = evidence_folder(checkout)
    assert folder.is_dir() and not folder.is_relative_to(checkout)
    assert folder.stat().st_mode & 0o777 == 0o700
    assert list(checkout.iterdir()) == []


def test_evidence_collision_never_overwrites_existing_work(monkeypatch, tmp_path):
    from types import SimpleNamespace

    from docker import c04_gate

    monkeypatch.setattr(c04_gate, "uuid4", lambda: SimpleNamespace(hex="a" * 32))
    existing = tmp_path / ".runtime/c04-gate-evidence" / ("a" * 32)
    existing.mkdir(parents=True)
    note = existing / "preserved.txt"
    note.write_text("legitimate-work")
    with pytest.raises(FileExistsError):
        c04_gate.evidence_folder(tmp_path)
    assert note.read_text() == "legitimate-work"
