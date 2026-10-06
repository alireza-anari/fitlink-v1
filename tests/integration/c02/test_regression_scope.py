import hashlib
import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration


def test_initial_user_migration_remains_exact_immutable_c01_source():
    manifest = json.loads(Path("docker/c01_source_manifest.json").read_text())
    entry = next(
        e
        for e in manifest["entries"]
        if e["path"] == "apps/accounts/migrations/0001_initial.py"
    )
    body = Path(entry["path"]).read_bytes()
    assert (
        hashlib.sha1(b"blob " + str(len(body)).encode() + b"\0" + body).hexdigest()
        == entry["sha"]
    )
