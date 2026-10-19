"""Only finite infrastructure categories may leave a failing child process."""

import json

import pytest

from docker.c03_gate_diagnostics import progress_lines

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    ("message", "category"),
    [
        ("ERROR: failed to solve: process exited", "build_failed"),
        ("429 Too Many Requests", "rate_limited"),
        ("TLS handshake timeout", "tls_timeout"),
        ("no space left on device", "disk_full"),
        ("Temporary failure in name resolution", "dns_failure"),
        ("connection refused", "connection_refused"),
    ],
)
def test_build_failure_metadata_excludes_arbitrary_child_output(message, category):
    private = "secret-token private-source-url health-data"
    events = list(progress_lines(message + " " + private))
    assert {"kind": "infrastructure_error", "category": category} in events
    assert private not in json.dumps(events)
    assert message not in json.dumps(events)


def test_unrecognized_child_output_is_not_relayed():
    assert list(progress_lines("private-source-url health-data secret-token")) == []


def test_build_error_is_journaled_without_replacing_real_failure(tmp_path):
    import subprocess
    import sys
    from pathlib import Path

    observer = Path(__file__).resolve().parents[3] / "docker/c03_gate_diagnostics.py"
    result = subprocess.run(
        [
            sys.executable,
            str(observer),
            "--acceptance",
            "postgresql",
            sys.executable,
            "-c",
            "print('ERROR: failed to solve: private-source-url secret-token');"
            "raise SystemExit(17)",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 17
    journal = next((tmp_path / ".runtime/c03-diagnostics").glob("*.jsonl")).read_text()
    events = [json.loads(line) for line in journal.splitlines()]
    assert any(
        row["event"] == "infrastructure_error"
        and row["progress"]
        == {"kind": "infrastructure_error", "category": "build_failed"}
        for row in events
    )
    assert events[-1]["observed_returncode"] == 17
    assert "private-source-url" not in journal + result.stdout
    assert "secret-token" not in journal + result.stdout
