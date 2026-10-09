"""Private storage never grants a browser origin cross-origin access."""

import fnmatch
import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit
ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(
    "origin",
    [
        "https://foreign.invalid",
        "http://localhost:8000",
        "https://app.invalid",
        "null",
    ],
)
def test_minio_policy_does_not_match_any_browser_origin(origin):
    source = (ROOT / "compose.yaml").read_text()
    service = source.split("  minio:\n", 1)[1].split("  minio-init:\n", 1)[0]
    setting = re.search(r"MINIO_API_CORS_ALLOW_ORIGIN: ['\"]?([^'\"\n]+)", service)
    # Pinned MinIO's absent/empty default is '*', not a deny-all policy.
    policy = setting[1].strip() if setting else "*"
    assert policy and not any(fnmatch.fnmatchcase(origin, v) for v in policy.split(","))
