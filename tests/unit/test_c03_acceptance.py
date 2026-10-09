"""A bounded gate may pass only after natural success and verified cleanup."""

import importlib.util
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit
ROOT = Path(__file__).resolve().parents[2]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "docker" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    "code,reason,host,containers,want",
    [
        (0, "command_exited", True, True, 0),
        (7, "command_exited", True, True, 7),
        (None, "observation_deadline", True, True, 1),
        (0, "observation_deadline", True, True, 1),
        (0, "command_exited", None, True, 1),
        (0, "command_exited", False, True, 1),
        (0, "command_exited", True, False, 1),
        (0, "diagnostic_error", True, True, 1),
    ],
)
def test_gate_acceptance_rejects_timeout_and_unknown_cleanup(
    code, reason, host, containers, want
):
    diag = load("c03_gate_diagnostics")
    assert hasattr(diag, "acceptance_status"), "Production gate result verifier absent"
    assert diag.acceptance_status(code, reason, host, containers) == want


def test_acceptance_mode_runs_real_child_and_preserves_diagnostic_default(
    tmp_path, monkeypatch
):
    diag = load("c03_gate_diagnostics")
    monkeypatch.chdir(tmp_path)
    # This sandbox cannot inspect /proc or Docker. Supply their external facts;
    # command/session creation, observation, waiting and JSONL remain real.
    monkeypatch.setattr(diag, "process_rows", lambda *a, **k: [])
    monkeypatch.setattr(diag, "containers", lambda: [])
    command = [sys.executable, "-c", "raise SystemExit(0)"]
    assert diag.watch("postgresql", command, acceptance=True) == 0
    assert diag.watch("postgresql", command) == 1


def test_missing_subreaper_fails_before_child_launch(tmp_path, monkeypatch):
    diag = load("c03_gate_diagnostics")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(diag, "containers", lambda: [])
    monkeypatch.setattr(diag, "enable_subreaper", lambda: False, raising=False)
    launched = []
    monkeypatch.setattr(diag.subprocess, "Popen", lambda *a, **k: launched.append(a))
    assert diag.watch("postgresql", [sys.executable], acceptance=True) == 1
    assert launched == []


def test_truncated_process_inventory_is_unknown():
    diag = load("c03_gate_diagnostics")

    class Inventory:
        def is_dir(self):
            return True

        def iterdir(self):
            return iter(Path(f"nonprocess-{i}") for i in range(4097))

    assert diag.process_rows(b"marker", proc=Inventory()) is None
