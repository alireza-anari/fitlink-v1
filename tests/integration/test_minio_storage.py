import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import httpx
import pytest

from apps.assets.storage import S3PrivateStore

pytestmark = pytest.mark.integration


def test_private_minio_signed_roundtrip():
    store = S3PrivateStore()
    key = "tests/" + uuid.uuid4().hex
    try:
        store.put(key, b"private-probe", "text/plain")
        assert store.read(key) == b"private-probe"
        url = store.signed_read_url(key, 60)
        with httpx.Client(timeout=5, trust_env=False) as client:
            assert client.get(url).content == b"private-probe"
            assert client.get(url.split("?")[0]).status_code == 403
            # Sign as an expired request; MinIO must reject the signature now.
            with patch(
                "botocore.auth.get_current_datetime",
                return_value=datetime.now(UTC) - timedelta(minutes=10),
            ):
                expired = store.signed_read_url(key, 1)
            assert client.get(expired).status_code == 403
    finally:
        store.delete(key)
    assert not store.backend.exists(key)
