"""Final Task 14 orchestration must retain every required source/service gate."""

from pathlib import Path

import pytest

pytestmark = pytest.mark.unit
ROOT = Path(__file__).resolve().parents[3]

REQUIRED = (
    "docker/c03_baseline.py",
    "sh docker/verify_c02.sh",
    "docker/c03_upgrade_probe.py prepare",
    "docker/c03_upgrade_probe.py verify",
    "docker/c03_upgrade_probe.py replay",
    "docker/c03_upgrade_probe.py constraints",
    "docker/c03_upgrade_probe.py clean",
    "manage.py makemigrations --check --dry-run",
    "manage.py showmigrations",
    "docker/c03_foundation_evidence.py",
    "docker/c03_processing_evidence.py",
    "docker/c03_storage_slice.py",
    "docker/c03_asset_restart_probe.py run",
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
