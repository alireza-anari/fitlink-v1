"""A bounded outer budget must permit the complete nested Foundation command."""

import json
import sys

import pytest

from docker import c03_gate_diagnostics as observer

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("seconds", [1300, 1800])
def test_complete_command_can_exit_naturally_within_reviewed_budget(
    monkeypatch, tmp_path, seconds
):
    # Metadata adapters are synthetic here; actual service/cleanup acceptance
    # remains mandatory in the full hosted gate.
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("C03_DIAGNOSTIC_SECONDS", str(seconds))
    monkeypatch.setattr(observer, "containers", lambda: [])
    monkeypatch.setattr(observer, "container_processes", lambda rows: [])
    monkeypatch.setattr(observer, "services", lambda rows: [])
    monkeypatch.setattr(observer, "enable_subreaper", lambda: True)
    monkeypatch.setattr(observer, "terminate_owned", lambda child, marker: True)
    monkeypatch.setattr(
        observer,
        "stop_owned_containers",
        lambda *args: {"complete": True, "owned_ids": []},
    )
    assert (
        observer.watch(
            "foundation", [sys.executable, "-c", "raise SystemExit(0)"], acceptance=True
        )
        == 0
    )
    journal = next((tmp_path / ".runtime/c03-diagnostics").glob("*.jsonl"))
    events = [json.loads(line) for line in journal.read_text().splitlines()]
    assert events[0]["observation_seconds"] == seconds
    assert events[-1]["reason"] == "command_exited"
    assert events[-1]["observed_returncode"] == 0


@pytest.mark.parametrize("seconds", ["1800.1", "nan", "inf", "-1"])
def test_budget_cannot_be_extended_arbitrarily(monkeypatch, seconds):
    monkeypatch.setenv("C03_DIAGNOSTIC_SECONDS", seconds)
    with pytest.raises(ValueError, match="bounded diagnostic observation window"):
        observer.watch("foundation", [sys.executable, "-c", "raise SystemExit(0)"])
