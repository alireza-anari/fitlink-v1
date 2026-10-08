"""Actual session-authenticated HTTP defines the owned quarantine boundary."""

from datetime import timedelta
from uuid import uuid4

import pytest

from apps.assets.models import Asset
from apps.governance.audit_models import AuditEvent
from apps.governance.outbox_models import OutboxEvent

from .upload_helpers import (
    PNG,
    PREFIX,
    begin,
    body,
    finalize,
    owner,
    post,
    shared_store,
)

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def test_finalize_quarantines_not_ready(monkeypatch):
    s = owner()
    dto, payload = begin(s)
    store = shared_store(monkeypatch)
    row = Asset.objects.get(pk=dto["id"])
    assert row.state == "pending_upload" and row.owner == s.user
    assert (
        s.user.phone not in row.source_key and str(s.profile.id) not in row.source_key
    )
    response = body(s, dto)
    assert response.status_code == 200
    uploaded = response.json()
    assert store.read(row.source_key) == PNG
    operation = uuid4()
    response = finalize(s, uploaded, operation)
    assert response.status_code == 202
    assert response.json()["state"] == "quarantined"
    row.refresh_from_db()
    assert row.accepted_at and row.finalized_at and row.sha256
    assert row.classification == "private_source"
    assert row.state != "ready" and row.derivatives.count() == 0
    assert finalize(s, uploaded, operation).json() == response.json()
    assert post(s, "begin/", payload).json()["id"] == dto["id"]
    assert AuditEvent.objects.filter(action="asset.finalized").count() == 1
    event = OutboxEvent.objects.get(event_type="asset.processing_requested")
    assert event.payload == {
        "asset_uuid": str(row.id),
        "user_uuid": str(s.user.public_id),
    }
    assert set(response.json()) == {
        "id",
        "version",
        "state",
        "purpose",
        "upload_expires_at",
    }
    assert response["Cache-Control"] == "no-store"


def test_receive_source_once(monkeypatch):
    s = owner()
    dto, _ = begin(s)
    store = shared_store(monkeypatch)
    assert body(s, dto).status_code == 200
    assert body(s, dto, b"changed").status_code == 409
    row = Asset.objects.get(pk=dto["id"])
    assert store.read(row.source_key) == PNG
    assert AuditEvent.objects.filter(action="asset.uploaded").count() == 1


@pytest.mark.parametrize(
    "defect",
    ["missing", "size", "hash", "foreign", "foreign_identical", "type", "oversized"],
)
def test_finalization_rejects_wrong_storage_facts(defect, monkeypatch):
    s = owner()
    dto, _ = begin(s)
    store = shared_store(monkeypatch)
    response = body(s, dto)
    assert response.status_code == 200
    dto = response.json()
    row = Asset.objects.get(pk=dto["id"])
    if defect == "missing":
        store.delete(row.source_key)
    elif defect in {"foreign", "foreign_identical"}:
        foreign = "quarantine/foreign"
        store.put(
            foreign,
            PNG if defect == "foreign_identical" else b"z" * len(PNG),
            "image/png",
        )
        Asset.objects.filter(pk=row.pk).update(source_key=foreign)
    else:
        value = (
            b"z" * len(PNG)
            if defect == "hash"
            else PNG + b"extra"
            if defect == "size"
            else b"x" * 10_000_001
            if defect == "oversized"
            else PNG
        )
        store.put(
            row.source_key, value, "text/html" if defect == "type" else "image/png"
        )
    assert finalize(s, dto).status_code in {409, 503}
    row.refresh_from_db()
    assert row.accepted_at is None and row.state != "ready"
    assert not OutboxEvent.objects.filter(
        event_type="asset.processing_requested"
    ).exists()


def test_finalization_rejects_new_operation_and_changed_replay(monkeypatch):
    s = owner()
    dto, _ = begin(s)
    shared_store(monkeypatch)
    response = body(s, dto)
    assert response.status_code == 200
    uploaded, operation = response.json(), uuid4()
    accepted = finalize(s, uploaded, operation)
    assert accepted.status_code == 202
    assert finalize(s, uploaded).status_code == 409
    assert finalize(s, accepted.json(), operation).status_code == 409
    assert (
        OutboxEvent.objects.filter(event_type="asset.processing_requested").count() == 1
    )


@pytest.mark.parametrize(
    "state", ["pending_upload", "receiving", "rejected", "revoked"]
)
def test_finalization_rejects_invalid_lifecycle_transition(state, monkeypatch):
    s = owner()
    dto, _ = begin(s)
    store = shared_store(monkeypatch)
    Asset.objects.filter(pk=dto["id"]).update(state=state)
    assert finalize(s, dto).status_code == 409
    assert store.objects == {}
    assert not OutboxEvent.objects.filter(
        event_type="asset.processing_requested"
    ).exists()


def test_finalization_receipt_does_not_bypass_current_authority(monkeypatch):
    s = owner()
    dto, _ = begin(s)
    shared_store(monkeypatch)
    response = body(s, dto)
    assert response.status_code == 200
    uploaded, operation = response.json(), uuid4()
    assert finalize(s, uploaded, operation).status_code == 202
    s.profile.state = "archived"
    s.profile.save(update_fields=["state"])
    assert finalize(s, uploaded, operation).status_code == 404


def test_body_requires_csrf_before_storage(monkeypatch):
    s = owner()
    dto, _ = begin(s)
    store = shared_store(monkeypatch)
    assert body(s, dto, csrf=False).status_code == 403
    assert store.objects == {}
    assert Asset.objects.get(pk=dto["id"]).state == "pending_upload"


@pytest.mark.parametrize(
    "name,media,data",
    [
        ("a.svg", "image/png", PNG),
        ("a.png", "text/html", PNG),
        ("a.png", "image/png", b"<html>"),
        ("a.png", "image/png", b"x" * 10_000_001),
    ],
)
def test_proxy_rejects_spoofed_or_oversized_body(name, media, data, monkeypatch):
    s = owner()
    dto, _ = begin(s)
    store = shared_store(monkeypatch)
    assert body(s, dto, data, name=name, media=media).status_code == 400
    assert store.objects == {}


def test_late_body_after_expiry_denied(monkeypatch):
    s = owner()
    dto, _ = begin(s)
    store = shared_store(monkeypatch)
    Asset.objects.filter(pk=dto["id"]).update(
        upload_expires_at=s.at - timedelta(seconds=1)
    )
    assert body(s, dto).status_code == 409
    assert store.objects == {}


def test_daily_and_pending_upload_quota(monkeypatch):
    s = owner()
    dto, _ = begin(s, declared_size=10_000_000)
    shared_store(monkeypatch)
    for _ in range(9):
        begin(s, declared_size=10_000_000)
    response = post(
        s,
        "begin/",
        {
            "purpose": "avatar",
            "subject_uuid": str(s.profile.id),
            "declared_size": 1,
            "declared_type": "image/png",
            "operation_id": str(uuid4()),
        },
    )
    assert response.status_code == 429
    Asset.objects.filter(owner=s.user).update(
        state="ready",
        accepted_at=s.at,
        finalized_at=s.at,
        actual_size=10_000_000,
        detected_type="image/png",
        sha256="a" * 64,
    )
    assert (
        post(
            s,
            "begin/",
            {
                "purpose": "avatar",
                "subject_uuid": str(s.profile.id),
                "declared_size": 1,
                "declared_type": "image/png",
                "operation_id": str(uuid4()),
            },
        ).status_code
        == 429
    )


def test_foreign_upload_binding_and_download_denied(monkeypatch):
    s, other = owner(), owner("+989123456781")
    dto, _ = begin(s)
    store = shared_store(monkeypatch)
    for target in (other.profile.id, uuid4()):
        response = post(
            s,
            "begin/",
            {
                "purpose": "avatar",
                "subject_uuid": str(target),
                "declared_size": len(PNG),
                "declared_type": "image/png",
                "operation_id": str(uuid4()),
            },
        )
        assert response.status_code == 404
    responses = [
        post(
            other,
            f"{identifier}/finalize/",
            {"expected_version": 1, "operation_id": str(uuid4())},
        )
        for identifier in (dto["id"], uuid4())
    ]
    assert [r.status_code for r in responses] == [404, 404]
    assert responses[0].content == responses[1].content
    from config.use_cases import profile_assets

    def forbidden(*args, **kwargs):
        pytest.fail("Unauthorized source I/O or signing")

    for method in ("read", "read_limited", "head", "signed_read_url"):
        monkeypatch.setattr(store, method, forbidden)
    for actor in (s.actor, other.actor):
        with pytest.raises(LookupError):
            profile_assets.authorized_profile_download(
                actor, uuid4() if actor == other.actor else dto["id"], "avatar", s.at
            )
    assert store.objects == {}


def test_abandon_is_idempotent_and_never_deletes_source(monkeypatch):
    s = owner()
    dto, _ = begin(s)
    store = shared_store(monkeypatch)
    response = body(s, dto)
    assert response.status_code == 200
    dto = response.json()
    command = {"expected_version": dto["version"], "operation_id": str(uuid4())}
    assert post(s, f"{dto['id']}/abandon/", command).json()["state"] == "abandoned"
    assert post(s, f"{dto['id']}/abandon/", command).status_code == 200
    assert finalize(s, dto).status_code == 409
    assert len(store.objects) == 1


@pytest.mark.parametrize("state", ["restricted", "suspended", "pending_deletion"])
def test_current_account_and_profile_loss_deny_finalization(state, monkeypatch):
    s = owner()
    dto, _ = begin(s)
    shared_store(monkeypatch)
    response = body(s, dto)
    assert response.status_code == 200
    s.user.state = state
    s.user.save(update_fields=["state"])
    assert finalize(s, response.json()).status_code == 403
    assert Asset.objects.get(pk=dto["id"]).accepted_at is None


def test_archived_profile_denies_existing_upload(monkeypatch):
    s = owner()
    dto, _ = begin(s)
    shared_store(monkeypatch)
    s.profile.state = "archived"
    s.profile.save(update_fields=["state"])
    assert body(s, dto).status_code == 404


def test_unauthenticated_ingress_is_denied():
    from django.test import Client

    client = Client(enforce_csrf_checks=True)
    assert (
        client.post(PREFIX + "begin/", {}, content_type="application/json").status_code
        == 403
    )


@pytest.mark.parametrize(
    "purpose", ["avatar", "cover", "logo", "identity_evidence", "credential_evidence"]
)
def test_only_current_owned_professional_purpose_bindings(purpose):
    from apps.professionals.credential_models import Credential
    from apps.professionals.profile_models import ProfessionalRole

    s = owner()
    subject = s.profile.id
    kind = "professional_profile"
    if purpose.endswith("evidence"):
        category = "identity" if purpose == "identity_evidence" else "qualification"
        role = (
            None
            if category == "identity"
            else ProfessionalRole.objects.create(profile=s.profile, role="coach")
        )
        credential = Credential.objects.create(
            profile=s.profile,
            role=role,
            category=category,
            type_code="synthetic",
            issuer="Fixture",
            title="Fixture",
        )
        subject, kind = credential.id, "professional_credential"
    dto, _ = begin(s, purpose=purpose, subject_uuid=str(subject))
    row = Asset.objects.get(pk=dto["id"])
    assert (
        row.purpose == purpose
        and row.subject_kind == kind
        and row.subject_uuid == subject
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("owner", "foreign"),
        ("source_key", "quarantine/foreign"),
        ("state", "ready"),
        ("purpose", "health_photo"),
    ],
)
def test_unknown_or_unapproved_ingress_payload_is_rejected(field, value):
    s = owner()
    payload = {
        "purpose": "avatar",
        "subject_uuid": str(s.profile.id),
        "declared_size": len(PNG),
        "declared_type": "image/png",
        "operation_id": str(uuid4()),
        field: value,
    }
    assert post(s, "begin/", payload).status_code == 400
    assert Asset.objects.count() == 0
