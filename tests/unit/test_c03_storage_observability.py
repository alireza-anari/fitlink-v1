"""Diagnostic-only boundary evidence must survive fast, private failures."""

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from django.db import OperationalError

pytestmark = pytest.mark.unit
ROOT = Path(__file__).resolve().parents[2]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "docker" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("boundary", ["migrate", "probe", "pytest"])
def test_gate_records_exact_failure_without_retry_and_still_cleans_up(
    tmp_path, boundary
):
    tools = tmp_path / "bin"
    tools.mkdir()
    python = tools / "python"
    python.write_text("#!/bin/sh\nexit 0\n")
    docker = tools / "docker"
    docker.write_text(
        f"#!{sys.executable}\n"
        "import os,sys,json\n"
        "from pathlib import Path\n"
        "args=sys.argv[1:]\n"
        "with Path(os.environ['COMMAND_LOG']).open('a') as f:\n"
        " f.write(json.dumps(args)+'\\n')\n"
        "phase=('migrate' if 'manage.py' in args else 'probe' if "
        "'docker/c03_storage_probe.py' in args else 'pytest' if 'pytest' in args "
        "else None)\n"
        "sys.exit(23 if phase==os.environ['FAIL_BOUNDARY'] else 0)\n"
    )
    for path in (python, docker):
        path.chmod(0o755)
    log = tmp_path / "commands.jsonl"
    result = subprocess.run(
        ["sh", str(ROOT / "docker/verify_c03_storage.sh")],
        cwd=tmp_path,
        env={
            **os.environ,
            "PATH": str(tools) + os.pathsep + os.environ["PATH"],
            "C03_STORAGE_GATE_CHILD": "1",
            "COMMAND_LOG": str(log),
            "FAIL_BOUNDARY": boundary,
        },
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode == 23
    phases = ["migrate", "probe", "pytest"]
    expected = []
    for phase in phases[: phases.index(boundary) + 1]:
        expected.append(f"C03_STORAGE_PHASE {phase} start")
        expected.append(
            f"C03_STORAGE_PHASE {phase} failure 23"
            if phase == boundary
            else f"C03_STORAGE_PHASE {phase} success"
        )
    assert result.stdout.splitlines() == expected
    commands = [json.loads(line) for line in log.read_text().splitlines()]
    assert commands[-1][-2:] == ["down", "--remove-orphans"]
    assert sum("manage.py" in c for c in commands) == 1
    assert sum("docker/c03_storage_probe.py" in c for c in commands) == (
        boundary != "migrate"
    )
    assert sum("pytest" in c for c in commands) == (boundary == "pytest")


def test_probe_setup_failure_reports_only_exception_class(monkeypatch, capsys):
    probe = load("c03_storage_probe")

    def fail():
        raise OperationalError("synthetic-secret https://private.invalid/?token=secret")

    monkeypatch.setattr(probe.django, "setup", fail)
    assert probe.main() == 1
    output = capsys.readouterr().out
    assert "C03_STORAGE_ERROR OperationalError" in output
    assert "synthetic-secret" not in output
    assert "private.invalid" not in output


@pytest.mark.parametrize(
    "error_type", ["OperationalError", "ClientError", "TimeoutError"]
)
def test_observer_classifies_traceback_without_relaying_message(error_type):
    diag = load("c03_gate_diagnostics")
    events = list(
        diag.progress_lines(f"{error_type}: synthetic-secret private-object-key\n")
    )
    assert events == [{"kind": "storage_error", "error_type": error_type}]


def test_unknown_error_and_untrusted_phase_are_not_relayed():
    diag = load("c03_gate_diagnostics")
    assert (
        list(
            diag.progress_lines(
                "PrivatePhoneError: synthetic-secret\n"
                "C03_STORAGE_PHASE private-object start\n"
                "C03_STORAGE_PHASE probe failure 1 synthetic-secret\n"
                "C03_STORAGE_ERROR private-object\n"
            )
        )
        == []
    )


def test_fast_child_preserves_every_phase_and_redacts_error_in_jsonl(tmp_path):
    code = (
        "print('C03_STORAGE_PHASE migrate start');"
        "print('C03_STORAGE_PHASE migrate success');"
        "print('C03_STORAGE_PHASE probe start');"
        "print('C03_STORAGE_ERROR ClientError');"
        "print('ClientError: synthetic-secret private-object-key');"
        "print('C03_STORAGE_PHASE probe failure 7');raise SystemExit(7)"
    )
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "docker/c03_gate_diagnostics.py"),
            "postgresql",
            sys.executable,
            "-c",
            code,
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=8,
    )
    assert result.returncode == 7
    artifact = next((tmp_path / ".runtime/c03-diagnostics").glob("*.jsonl"))
    text = artifact.read_text()
    events = [json.loads(line) for line in text.splitlines()]
    transitions = [e["progress"] for e in events if e["event"] == "storage_phase"]
    assert transitions == [
        {"kind": "storage_phase", "name": "migrate", "state": "start"},
        {"kind": "storage_phase", "name": "migrate", "state": "success"},
        {"kind": "storage_phase", "name": "probe", "state": "start"},
        {"kind": "storage_phase", "name": "probe", "state": "failure", "returncode": 7},
    ]
    errors = [e for e in events if e["event"] == "storage_error"]
    assert errors and all(e["progress"]["error_type"] == "ClientError" for e in errors)
    assert events[-1]["event"] == "diagnostic_finished"
    assert events[-1]["observed_returncode"] == 7
    assert events[-1]["reason"] == "command_exited"
    assert "synthetic-secret" not in text + result.stdout
    assert "private-object-key" not in text + result.stdout


def test_private_exception_class_uses_bounded_fallback():
    errors = load("c03_storage_errors")
    private_error = type("PrivateIdentifierError", (Exception,), {})
    assert errors.error_category(private_error("synthetic-secret")) == "OtherError"


@pytest.mark.parametrize(
    "line",
    [
        "C03_STORAGE_PHASE probe failure 0",
        "C03_STORAGE_PHASE probe failure 256",
        "C03_STORAGE_PHASE probe failure -1",
        "C03_STORAGE_PHASE probe failure 1234",
    ],
)
def test_invalid_phase_codes_are_not_retained(line):
    diag = load("c03_gate_diagnostics")
    assert list(diag.progress_lines(line)) == []
