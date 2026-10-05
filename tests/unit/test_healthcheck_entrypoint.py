import json
import os
import subprocess
import sys

import pytest

pytestmark = pytest.mark.unit


def test_direct_healthcheck_boots_project_with_redacted_db_failure():
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
    assert result.stdout == ""
    event = json.loads(result.stderr)
    assert event["event"] == "dependency.unavailable"
    assert event["dependency"] == "postgresql"
    assert "password" not in result.stderr.lower()
