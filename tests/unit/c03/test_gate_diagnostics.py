"""Diagnostic output is bounded, private and preserves real failure status."""

import importlib.util
import json
import os
import signal
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit
ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "c03_gate_diagnostics", ROOT / "docker/c03_gate_diagnostics.py"
)
diag = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diag)


def test_process_command_does_not_expose_credentials_or_private_arguments():
    values = diag.safe_command(
        [
            "uv",
            "run",
            "pytest",
            "tests/integration/c03/test_upload_lifecycle.py",
            "--password=synthetic-secret",
            "+989000000000",
            "quarantine/private-source",
            "https://example.invalid/object?signature=synthetic-secret",
        ]
    )
    text = " ".join(values)
    assert "test_upload_lifecycle.py" in text
    for denied in ("synthetic-secret", "+989", "private-source", "signature"):
        assert denied not in text


def test_snapshot_without_proc_is_explicitly_unavailable(tmp_path):
    assert diag.process_rows(b"marker", tmp_path / "absent") is None


def test_container_process_arguments_are_sanitized(monkeypatch):
    monkeypatch.setattr(
        diag,
        "query",
        lambda command: (
            "PID PPID PGID SID STAT COMMAND\n"
            "123 1 123 123 S python -c synthetic-private-content\n"
        ),
    )
    rows = diag.container_processes(
        [{"id": "a" * 64, "status": "running", "project": next(iter(diag.PROJECTS))}]
    )
    assert rows[0]["processes"][0]["command"] == ["python", "-c", "<redacted>"]
    assert "synthetic-private-content" not in str(rows)


def test_stopped_container_does_not_hide_later_postgres_observation(monkeypatch):
    monkeypatch.setattr(diag, "query", lambda command: "123|active|Lock|relation|5|{9}")
    rows = diag.services(
        [
            {"status": "exited"},
            {"status": "running", "kind": "postgres", "service": "db", "id": "a"},
        ]
    )
    assert rows == [
        {"kind": "postgres_activity", "rows": ["123|active|Lock|relation|5|{9}"]}
    ]


def test_bounded_metadata_query_terminates_hung_command():
    assert diag.query([sys.executable, "-c", "import time;time.sleep(30)"], 0.1) is None


def test_watcher_preserves_failure_and_writes_only_sanitized_diagnostics(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "docker/c03_gate_diagnostics.py"),
            "postgresql",
            sys.executable,
            "-c",
            "raise SystemExit(7)",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 7
    assert '"returncode": 7' in result.stdout
    assert "raise SystemExit" not in result.stdout
    files = list((tmp_path / ".runtime/c03-diagnostics").glob("*.jsonl"))
    assert len(files) == 1
    assert "command_exited" in files[0].read_text()


def test_deadline_returns_evidence_and_kills_term_ignoring_owned_child(tmp_path):
    pid_file = tmp_path / "owned.pid"
    code = (
        "import os,signal,time;from pathlib import Path;"
        "signal.signal(signal.SIGTERM,signal.SIG_IGN);"
        f"Path({str(pid_file)!r}).write_text(str(os.getpid()));time.sleep(30)"
    )
    child = subprocess.Popen(
        [
            sys.executable,
            str(ROOT / "docker/c03_gate_diagnostics.py"),
            "postgresql",
            sys.executable,
            "-c",
            code,
        ],
        cwd=tmp_path,
        env={**os.environ, "C03_DIAGNOSTIC_SECONDS": "0.3"},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    try:
        stdout, _ = child.communicate(timeout=8)
        assert child.returncode != 0
        events = [
            json.loads(line)
            for line in next((tmp_path / ".runtime/c03-diagnostics").glob("*.jsonl"))
            .read_text()
            .splitlines()
        ]
        assert any(e["event"] == "final_snapshot" for e in events)
        assert events[-1]["event"] == "diagnostic_finished"
        assert events[-1]["reason"] == "observation_deadline"
        assert "time.sleep(30)" not in stdout
        with pytest.raises(ProcessLookupError):
            os.kill(int(pid_file.read_text()), 0)
    finally:
        if child.poll() is None:
            os.killpg(child.pid, signal.SIGKILL)
            child.wait(timeout=2)
        if pid_file.exists():
            try:
                os.kill(int(pid_file.read_text()), signal.SIGKILL)
            except ProcessLookupError:
                pass


def test_diagnostic_checkpoint_never_returns_pass_for_successful_command(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "docker/c03_gate_diagnostics.py"),
            "postgresql",
            sys.executable,
            "-c",
            "raise SystemExit(0)",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=8,
    )
    assert result.returncode != 0


def test_cleanup_excludes_unrelated_and_preexisting_containers(monkeypatch):
    foreign = {"id": "f" * 64, "project": "unrelated-project"}
    existing = {"id": "e" * 64, "project": "fitlink-c03-private-storage"}
    owned = {"id": "a" * 64, "project": "fitlink-c03-private-storage"}
    snapshots = iter([[foreign, existing, owned], [foreign, existing]])
    monkeypatch.setattr(diag, "containers", lambda: next(snapshots))
    commands = []
    monkeypatch.setattr(diag, "query", lambda command, **kw: commands.append(command))
    result = diag.stop_owned_containers("storage", {existing["id"]})
    assert result == {"owned_ids": [owned["id"]], "complete": True}
    assert commands == [
        ["docker", "stop", "--time", "1", owned["id"]],
        ["docker", "rm", "-f", owned["id"]],
    ]


def test_child_private_output_and_pytest_parameters_never_enter_artifact(tmp_path):
    line = (
        "tests/unit/c03/test_gate_diagnostics.py::"
        "test_snapshot_without_proc_is_explicitly_unavailable[synthetic-private-phone]"
    )
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "docker/c03_gate_diagnostics.py"),
            "postgresql",
            sys.executable,
            "-c",
            f"print('synthetic-secret');print({line!r})",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=8,
    )
    artifact = next((tmp_path / ".runtime/c03-diagnostics").glob("*.jsonl")).read_text()
    assert "test_snapshot_without_proc_is_explicitly_unavailable" in artifact
    assert "synthetic-secret" not in artifact + result.stdout
    assert "synthetic-private-phone" not in artifact + result.stdout
