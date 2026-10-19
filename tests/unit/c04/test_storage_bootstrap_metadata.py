"""Storage bootstrap triage preserves bounded commands and private credentials."""

import os
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit
ROOT = Path(__file__).resolve().parents[3]


@pytest.mark.parametrize(
    "failure", ["alias", "ready", "mb", "anonymous", "policy", "user", "attach", "none"]
)
def test_bootstrap_emits_only_failed_phase_and_preserves_exit(tmp_path, failure):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    mc = bin_dir / "mc"
    mc.write_text(
        "#!/bin/sh\n"
        'case "$1 $2" in\n'
        ' "alias set") phase=alias;;\n'
        ' "ready local") phase=ready;;\n'
        ' "mb --ignore-existing") phase=mb;;\n'
        ' "anonymous set") phase=anonymous;;\n'
        ' "admin policy") if [ "$3" = attach ]; then phase=attach;\n'
        " else phase=policy; fi;;\n"
        ' "admin user") phase=user;;\n'
        " *) exit 93;;\n"
        "esac\n"
        'printf "%s\\n" "$phase" >>"$BOOTSTRAP_TEST_LOG"\n'
        '[ "$phase" != "$FAILURE" ] || exit 7\n'
    )
    mc.chmod(0o755)
    sleep = bin_dir / "sleep"
    sleep.write_text("#!/bin/sh\nexit 0\n")
    sleep.chmod(0o755)
    env = {
        **os.environ,
        "PATH": str(bin_dir) + ":" + os.environ["PATH"],
        "FAILURE": failure,
        "BOOTSTRAP_TEST_LOG": str(tmp_path / "commands"),
        "MINIO_ROOT_USER": "private-root-user",
        "MINIO_ROOT_PASSWORD": "private-root-secret",
        "MINIO_APP_ACCESS_KEY": "private-access-key",
        "MINIO_APP_SECRET_KEY": "private-app-secret",
    }
    # Relocate only the ephemeral policy file for this restricted-host unit.
    source = (ROOT / "docker/minio-init.sh").read_text()
    assert source.count("/tmp/policy.json") == 3
    script = tmp_path / "minio-init.sh"
    script.write_text(source.replace("/tmp/policy.json", str(tmp_path / "policy.json")))
    result = subprocess.run(
        ["sh", str(script)],
        env=env,
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode == (
        0 if failure == "none" else 1 if failure in {"alias", "ready"} else 7
    )
    if failure == "none":
        assert "C04_STORAGE_BOOTSTRAP complete success 0" in result.stdout
    else:
        assert f"C04_STORAGE_BOOTSTRAP {failure} failure" in result.stdout
    commands = (tmp_path / "commands").read_text().splitlines()
    assert commands.count("alias") == (30 if failure in {"alias", "ready"} else 1)
    assert commands.count("ready") == (
        0 if failure == "alias" else 30 if failure == "ready" else 1
    )
    for secret in (env[k] for k in env if k.startswith("MINIO_")):
        assert secret not in result.stdout + result.stderr


def test_observer_retains_bootstrap_phase_without_child_payload():
    from docker.c03_gate_diagnostics import progress_lines

    assert list(progress_lines("C04_STORAGE_BOOTSTRAP alias failure 1")) == [
        {
            "kind": "storage_bootstrap",
            "phase": "alias",
            "state": "failure",
            "returncode": 1,
        }
    ]
    for unsafe in (
        "C04_STORAGE_BOOTSTRAP private-secret failure 1",
        "C04_STORAGE_BOOTSTRAP alias failure 1 private-secret",
        "C04_STORAGE_BOOTSTRAP alias failure 256",
    ):
        assert list(progress_lines(unsafe)) == []
