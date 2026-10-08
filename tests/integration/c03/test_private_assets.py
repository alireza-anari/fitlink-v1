"""Mandatory actual private MinIO ingress; no storage or authorization mocks."""

from io import BytesIO
from uuid import uuid4

import httpx
import pytest
from django.utils import timezone

from apps.assets.models import Asset
from apps.assets.storage import S3PrivateStore

from .upload_helpers import PNG, begin, owner

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def test_real_minio_bounded_private_roundtrip_and_anonymous_denial():
    store = S3PrivateStore()
    key = "quarantine/" + uuid4().hex
    try:
        assert callable(getattr(store, "put_stream", None)), "Bounded ingress absent"
        store.put_stream(key, BytesIO(PNG), "image/png", 10_000_000)
        assert store.head(key).size == len(PNG)
        assert store.read_limited(key, 10_000_000) == PNG
        with pytest.raises(ValueError):
            store.put_stream(key, BytesIO(b"changed"), "image/png", 10_000_000)
        url = store.signed_read_url(key, 60).split("?")[0]
        with httpx.Client(
            timeout=5, trust_env=False, limits=httpx.Limits(max_keepalive_connections=0)
        ) as client:
            assert client.get(url).status_code == 403
            assert client.put(url, content=PNG).status_code == 403
        assert store.backend.default_acl is None
        assert store.read_limited(key, 10_000_000) == PNG
    finally:
        store.delete(key)


def test_real_minio_owned_quarantine_not_source_delivery(monkeypatch):
    s = owner()
    dto, _ = begin(s)
    from config.use_cases import profile_assets as commands

    store = S3PrivateStore()
    monkeypatch.setattr(commands, "get_private_store", lambda: store)
    row = Asset.objects.get(pk=dto["id"])
    try:
        result = commands.receive_profile_upload(
            s.actor, row.id, row.version, BytesIO(PNG), timezone.now()
        )
        assert result.state == "quarantined"
        result = commands.finalize_profile_upload(
            s.actor, row.id, result.version, uuid4(), timezone.now()
        )
        assert result.state == "quarantined"
        assert store.read_limited(row.source_key, 10_000_000) == PNG
        with pytest.raises(LookupError):
            commands.authorized_profile_download(
                s.actor, row.id, "avatar", timezone.now()
            )
    finally:
        store.delete(row.source_key)


def test_real_minio_missing_and_oversized_objects_fail_closed():
    store = S3PrivateStore()
    key = "quarantine/" + uuid4().hex
    assert callable(getattr(store, "read_limited", None)), "Bounded reader absent"
    with pytest.raises(FileNotFoundError):
        store.read_limited(key, 10_000_000)
    try:
        store.put(key, b"x" * 10_000_001, "image/png")
        with pytest.raises(ValueError):
            store.read_limited(key, 10_000_000)
    finally:
        store.delete(key)
