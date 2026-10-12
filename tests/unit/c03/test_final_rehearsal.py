"""Final Task 14 orchestration must retain every required source/service gate."""

import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit
ROOT = Path(__file__).resolve().parents[3]

REQUIRED = (
    "docker/c03_baseline.py",
    "sh docker/verify_c02.sh",
    "/probe.py prepare",
    "/probe.py verify",
    "upgraded_capabilities probe replay",
    "upgraded_constraints probe constraints",
    "docker/c03_upgrade_probe.py clean",
    "manage.py makemigrations --check --dry-run",
    "manage.py showmigrations",
    "pytest tests/unit tests/integration",
    "tests/integration/test_minio_storage.py",
    "tests/integration/c03/test_scanner_service.py",
    "tests/integration/test_celery_roundtrip.py",
    "tests/e2e/c02 tests/e2e/test_foundation_smoke.py",
    "restart_probe prepare",
    "restart_probe start",
    "restart_probe verify",
    "restart_probe fault",
    "kill -s SIGKILL worker",
    "restart redis minio scanner",
    "clean_project=fitlink-c03-task14-clean",
    "docker/c03_timeout_probe.py",
    "--task11-owner",
    "--task12-staff",
    "tests/unit/c03/test_exact_baseline.py",
    "tests/unit/c03/test_final_rehearsal.py",
    "tests/integration/c03/test_upgrade_from_c02.py",
)


def final_gates_valid(source):
    return all(item in source for item in REQUIRED) and all(
        item not in source for item in ("--reuse-db", "--deselect", "continue-on-error")
    )


def test_final_gates_include_all_c02_and_real_c03_services_browser():
    source = (ROOT / "docker/verify_c03.sh").read_text()
    assert final_gates_valid(source), "Task 14 actual final rehearsal is omitted"
    for item in REQUIRED:
        assert not final_gates_valid(source.replace(item, "omitted"))


def test_final_stage_propagates_early_function_failure(tmp_path):
    source = (ROOT / "docker/verify_c03.sh").read_text()
    function = source[source.index("run_step() {") : source.index("original_c02() (")]
    private = tmp_path / "private"
    evidence = tmp_path / "evidence"
    private.mkdir()
    evidence.mkdir()
    script = (
        "set -eu\nprivate='"
        + str(private)
        + "'\nevidence='"
        + str(evidence)
        + "'\n"
        + function
        + "fixture() { false; printf 'EARLY_FAILURE_SWALLOWED'; }\n"
        + "run_step synthetic fixture\n"
    )
    result = subprocess.run(
        ["sh", "-c", script], cwd=ROOT, capture_output=True, timeout=10
    )
    assert result.returncode != 0, "Final verifier swallowed an earlier gate failure"
    assert "EARLY_FAILURE_SWALLOWED" not in (private / "synthetic.log").read_text()


def test_private_rehearsal_diagnostics_never_export_exception_text_or_sessions(
    tmp_path,
):
    import json

    from docker.c03_upgrade_probe import private_log_metadata

    path = tmp_path / "private.log"
    sentinel = "PRIVATE-SNAPSHOT-SESSION-AND-OTP-SENTINEL"
    path.write_text(
        'File "/app/config/settings/env.py", line 17, in invalid\n'
        "ImproperlyConfigured: " + sentinel + " +989123000001\n"
        "FAILED tests/unit/c02/test_security_config.py::test_unsafe_config["
        + sentinel
        + "] - "
        + sentinel
        + "\n"
        "3 passed, 1 failed\n"
    )
    result = private_log_metadata(path)
    assert result["exceptions"] == ["ImproperlyConfigured"]
    assert result["counts"]["passed"] == [3]
    assert result["counts"]["failed"] == [1]
    assert result["locations"] == [{"file": "env.py", "line": 17}]
    assert sentinel not in json.dumps(result)
    assert "+989123000001" not in json.dumps(result)
