"""Mandatory actual private MinIO ingress; no storage or authorization mocks."""

import re
from io import BytesIO
from uuid import uuid4

import httpx
import pytest
from django.utils import timezone

from apps.assets.models import Asset
from apps.assets.storage import S3PrivateStore

from .upload_helpers import PNG, PREFIX, begin, body, finalize, owner, post

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
            assert (
                client.get(
                    f"{store.backend.endpoint_url}/{store.backend.bucket_name}?list-type=2"
                ).status_code
                == 403
            )
            for origin in ("https://foreign.invalid", "http://localhost:8000", "null"):
                preflight = client.options(
                    url,
                    headers={
                        "Origin": origin,
                        "Access-Control-Request-Method": "PUT",
                    },
                )
                assert "access-control-allow-origin" not in preflight.headers
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


def test_real_minio_http_owned_private_source(settings):
    settings.STORAGE_BACKEND = "s3"
    s, foreign = owner(), owner("+989123456781")
    store = S3PrivateStore()
    dto, declaration = begin(s)
    row = Asset.objects.get(pk=dto["id"])
    key = row.source_key
    try:
        assert re.fullmatch(r"quarantine/[0-9a-f]{32}", key)
        assert str(s.user.public_id) not in key and str(s.profile.id) not in key
        assert post(s, "begin/", {**declaration, "source_key": key}).status_code == 400
        response = body(s, dto)
        assert response.status_code == 200
        uploaded = response.json()
        assert set(uploaded) == {
            "id",
            "version",
            "state",
            "purpose",
            "upload_expires_at",
        }
        assert store.head(key).size == len(PNG)
        assert store.read_limited(key, 10_000_000) == PNG
        assert body(s, dto).status_code == 409
        operation = uuid4()
        response = finalize(s, uploaded, operation)
        assert response.status_code == 202
        assert finalize(s, uploaded, operation).json() == response.json()
        assert finalize(s, uploaded).status_code == 409
        row.refresh_from_db()
        assert row.state == "quarantined" and row.finalized_at is not None
        assert row.source_key == key and row.derivatives.count() == 0
        assert row.classification == "private_source"
        assert store.backend.default_acl is None
        # This is an unsigned object URL, never a browser upload grant.
        url = f"{store.backend.endpoint_url}/{store.backend.bucket_name}/{key}"
        with httpx.Client(
            timeout=5, trust_env=False, limits=httpx.Limits(max_keepalive_connections=0)
        ) as client:
            assert client.get(url).status_code == 403
            assert client.put(url, content=PNG).status_code == 403
        for caller in (s, foreign):
            for identifier in (row.id, uuid4()):
                assert (
                    caller.client.get(PREFIX + f"{identifier}/source/").status_code
                    == 404
                )
                assert (
                    caller.client.get(
                        f"/api/v1/staff/profile-assets/{identifier}/source/"
                    ).status_code
                    == 404
                )
        assert finalize(foreign, uploaded).status_code == 404
        from config.use_cases import profile_assets

        for actor in (s.actor, foreign.actor, None):
            with pytest.raises(LookupError):
                profile_assets.authorized_profile_download(
                    actor, row.id, "avatar", timezone.now(), staff_context=object()
                )
        assert store.read_limited(key, 10_000_000) == PNG
    finally:
        store.delete(key)


@pytest.mark.parametrize("defect", ["missing", "size", "type", "foreign"])
def test_real_minio_http_rejects_changed_storage_facts(defect, settings):
    settings.STORAGE_BACKEND = "s3"
    s = owner()
    store = S3PrivateStore()
    dto, _ = begin(s)
    row = Asset.objects.get(pk=dto["id"])
    keys = {row.source_key}
    try:
        response = body(s, dto)
        assert response.status_code == 200
        uploaded = response.json()
        if defect == "missing":
            store.delete(row.source_key)
        elif defect == "size":
            store.put(row.source_key, PNG + b"x", "image/png")
        elif defect == "type":
            store.put(row.source_key, PNG, "image/jpeg")
        else:
            other_key = "quarantine/" + uuid4().hex
            keys.add(other_key)
            store.put_stream(other_key, BytesIO(PNG), "image/png", 10_000_000)
            Asset.objects.filter(pk=row.pk).update(source_key=other_key)
        assert finalize(s, uploaded).status_code == 409
        row.refresh_from_db()
        assert row.finalized_at is None and row.accepted_at is None
        assert row.state == "quarantined"
    finally:
        for key in keys:
            store.delete(key)
