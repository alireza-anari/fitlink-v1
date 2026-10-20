"""Ownership refusal remains mandatory and explains only finite safe metadata."""

import json
import sys
from collections import deque

import pytest

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("available", [False, True])
def test_fresh_runner_refusal_distinguishes_unavailable_from_owned_collision(
    tmp_path, monkeypatch, available
):
    from docker import c03_gate_diagnostics as diag

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(diag, "QUERY_FAILURES", deque(maxlen=8))
    rows = (
        [{"project": "fitlink-c03-private-storage", "id": "PRIVATE-ID"}]
        if available
        else None
    )
    monkeypatch.setattr(diag, "containers", lambda: rows)
    assert (
        diag.watch(
            "storage", [sys.executable, "-c", "raise SystemExit(0)"], acceptance=True
        )
        == 1
    )
    text = next((tmp_path / ".runtime/c03-diagnostics").glob("*.jsonl")).read_text()
    event = json.loads(text)
    assert event["reason"] == "fresh_runner_ownership_unavailable"
    assert event["baseline_available"] is available
    assert event["conflicting_projects"] == (
        ["fitlink-c03-private-storage"] if available else []
    )
    assert "PRIVATE-ID" not in text


def test_metadata_timeout_is_finite_and_kills_only_its_owned_query(monkeypatch):
    from docker import c03_gate_diagnostics as diag

    monkeypatch.setattr(diag, "QUERY_FAILURES", deque(maxlen=8))
    assert (
        diag.query([sys.executable, "-c", "import time;time.sleep(30)"], seconds=0.05)
        is None
    )
    record = diag.QUERY_FAILURES[-1]
    assert record["category"] == "metadata_command_timeout"
    assert record["returncode"] is None
    assert "time.sleep" not in json.dumps(record)
