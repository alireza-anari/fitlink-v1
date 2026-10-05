import pytest

pytestmark = pytest.mark.unit


def test_fake_private_roundtrip():
    from apps.assets.storage import FakePrivateStore

    store = FakePrivateStore()
    store.put("tests/object", b"private", "text/plain")
    assert store.read("tests/object") == b"private"
    assert store.signed_read_url("tests/object", 60).startswith("fake://")
    store.delete("tests/object")
    with pytest.raises(FileNotFoundError):
        store.read("tests/object")


@pytest.mark.parametrize(
    "key", ["", "/absolute", "../secret", "a/../secret", "a\\secret", "a//b"]
)
def test_invalid_keys(key):
    from apps.assets.storage import FakePrivateStore

    with pytest.raises(ValueError):
        FakePrivateStore().put(key, b"payload", "text/plain")


@pytest.mark.parametrize("expiry", [0, 61, -1])
def test_expiry_bounded(expiry):
    from apps.assets.storage import FakePrivateStore

    with pytest.raises(ValueError):
        FakePrivateStore().signed_read_url("tests/key", expiry)


def test_s3_signing_private_without_service(settings):
    from apps.assets.storage import S3PrivateStore

    settings.S3_ENDPOINT_URL = "http://127.0.0.1:9000"
    settings.S3_BUCKET_NAME = "private-assets"
    settings.S3_ACCESS_KEY_ID = "unit-key"
    settings.S3_SECRET_ACCESS_KEY = "unit-secret"
    settings.S3_REGION = "us-east-1"
    settings.S3_ADDRESSING_STYLE = "path"
    store = S3PrivateStore()
    url = store.signed_read_url("tests/key", 60)
    assert "X-Amz-Expires=60" in url and "X-Amz-Signature=" in url
    assert store.backend.default_acl is None
    assert store.backend.querystring_auth is True
