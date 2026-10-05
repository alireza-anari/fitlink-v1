import os
import subprocess
import sys

import pytest

pytestmark = pytest.mark.unit


def test_direct_healthcheck_boots_project_and_fails_quietly_without_db():
    result = subprocess.run(
        [sys.executable, "docker/healthcheck.py", "db"],
        env={
            **{key: value for key, value in os.environ.items() if key == "PATH"},
            "DJANGO_SETTINGS_MODULE": "config.settings.test",
            "POSTGRES_PORT": "1",
        },
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 1
    assert result.stderr == "" and result.stdout == ""
