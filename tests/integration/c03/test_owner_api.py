"""Real session HTTP contracts replacing only the two private preview absences."""

from uuid import uuid4

import pytest
from django.conf import settings
from django.test import Client

from apps.professionals.models import AssistantMembership, ProfessionalProfile

from .profile_helpers import make_actor
from .test_professional_setup import owner, save
from .test_verification_decisions import approved, decision, review
from .verification_helpers import submitted

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]
ROUTES = ("/professional/preview/", "/api/v1/professional/preview/")


def session_client(s):
    client = Client(enforce_csrf_checks=True)
    client.cookies[settings.SESSION_COOKIE_NAME] = s.request.session.session_key
    return client


def private(response):
    assert "no-store" in response.headers.get("Cache-Control", "")
    assert response.headers.get("X-Robots-Tag") == "noindex, nofollow"


@pytest.mark.parametrize("route", ROUTES)
@pytest.mark.parametrize(
    "state", ["unverified", "submitted", "under_review", "partial", "verified"]
)
def test_preview_owner_only_private_in_all_verification_states(settings, route, state):
    if state == "unverified":
        s = owner()
        save(
            s,
            "identity",
            {
                "display_name": "Owner title",
                "identity_name": "Private identity",
                "roles": ["coach"],
            },
        )
    elif state == "submitted":
        s = submitted()
    elif state == "verified":
        s = approved(settings)
    else:
        s = review(settings)
        if state == "partial":
            decision(s, "identity")
            decision(s, "coach")
    response = session_client(s).get(route)
    assert response.status_code == 200
    private(response)
    body = response.content.decode()
    assert s.profile.display_name in body
    assert s.profile.identity_name not in body
    for forbidden in (
        "source_key",
        "storage_key",
        "snapshot_hash",
        "evidence_binding",
        "Private synthetic explanation",
        "assignment_uuid",
        "signed_url",
        "staff_explanation",
        "publication_url",
    ):
        assert forbidden not in body


@pytest.mark.parametrize("route", ROUTES)
def test_preview_cross_owner_and_assistant_cannot_select_owner(route):
    s = owner()
    save(
        s,
        "identity",
        {
            "display_name": "Owner title",
            "identity_name": "Private identity",
            "roles": ["coach"],
        },
    )
    stranger = make_actor("+989123456789")
    AssistantMembership.objects.create(profile=s.profile, assistant=stranger.user)
    foreign_client = session_client(stranger)
    denied = foreign_client.get(route)
    assert denied.status_code == 404
    private(denied)
    missing = foreign_client.get(route, {"profile_uuid": str(uuid4())})
    guessed = foreign_client.get(route, {"profile_uuid": str(s.profile.id)})
    assert guessed.status_code == missing.status_code
    assert guessed.content == missing.content
    assert s.profile.display_name not in guessed.content.decode()
    ProfessionalProfile.objects.create(user=stranger.user, display_name="Other owner")
    own = foreign_client.get(route)
    assert own.status_code == 200
    private(own)
    assert "Other owner" in own.content.decode()
    assert s.profile.display_name not in own.content.decode()


@pytest.mark.parametrize("route", ROUTES)
@pytest.mark.parametrize("fault", ["auth_version", "restricted", "suspended"])
def test_preview_rechecks_current_account_and_auth_version(route, fault):
    s = owner()
    client = session_client(s)
    if fault == "auth_version":
        s.user.auth_version += 1
        s.user.save(update_fields=["auth_version"])
    else:
        s.user.state = fault
        s.user.is_active = fault != "suspended"
        s.user.save(update_fields=["state", "is_active"])
    response = client.get(route)
    assert response.status_code in ({403} if route.startswith("/api/") else {302, 403})
    private(response)


def post(client, route, data, token=None):
    return client.post(
        route,
        data,
        content_type="application/json",
        **({"HTTP_X_CSRFTOKEN": token} if token else {}),
    )


def token_for(client):
    client.get("/accounts/entry/")
    return client.cookies[settings.CSRF_COOKIE_NAME].value


def ready_media(monkeypatch):
    from hashlib import sha256

    from apps.assets.storage import FakePrivateStore
    from config.use_cases import profile_assets

    from .test_credential_revisions import ready

    s = owner()
    s.asset = ready(s, "avatar")
    s.derivative = s.asset.derivatives.get()
    s.content = b"\x89PNG\r\n\x1a\nsynthetic sanitized derivative"
    s.derivative.sha256 = sha256(s.content).hexdigest()
    s.derivative.save(update_fields=["sha256"])
    s.store = FakePrivateStore()
    s.store.put(s.derivative.key, s.content, "image/png")
    monkeypatch.setattr(profile_assets, "get_private_store", lambda: s.store)
    return s


def test_owner_status_and_only_sanitized_content(monkeypatch):
    from django.utils import timezone

    from config.use_cases import profile_assets

    s = ready_media(monkeypatch)
    client = session_client(s)
    status = client.get(f"/api/v1/profile-assets/{s.asset.id}/status/")
    assert status.status_code == 200
    assert set(status.json()) == {
        "id",
        "version",
        "state",
        "purpose",
        "upload_expires_at",
    }
    response = client.get(f"/api/v1/profile-assets/{s.asset.id}/content/")
    assert response.status_code == 200
    assert response.content == s.content and response["Content-Type"] == "image/png"
    assert "no-store" in response["Cache-Control"]
    from apps.assets.contracts import AssetNotFound

    with pytest.raises(AssetNotFound):
        profile_assets.authorized_profile_download(
            s.actor, s.asset.id, "avatar", timezone.now()
        )


@pytest.mark.parametrize(
    "fault",
    [
        "quarantined",
        "processing",
        "rejected",
        "revoked",
        "derivative_version",
        "derivative_purpose",
        "integrity",
        "assistant",
        "auth_version",
        "hold_restricted",
    ],
)
def test_owner_asset_release_fails_closed_before_storage(fault, monkeypatch):
    from django.utils import timezone

    from apps.assets.contracts import AssetNotFound
    from apps.assets.models import Asset, AssetDerivative
    from config.use_cases import profile_assets

    s = ready_media(monkeypatch)
    actor = s.actor
    if fault in {"quarantined", "processing", "rejected", "revoked"}:
        Asset.objects.filter(pk=s.asset.id).update(state=fault)
    elif fault == "derivative_version":
        AssetDerivative.objects.filter(pk=s.derivative.id).update(processing_version=2)
    elif fault == "derivative_purpose":
        AssetDerivative.objects.filter(pk=s.derivative.id).update(
            purpose="evidence_preview"
        )
    elif fault == "integrity":
        AssetDerivative.objects.filter(pk=s.derivative.id).update(sha256="a" * 64)
    elif fault == "assistant":
        stranger = make_actor("+989123456789")
        AssistantMembership.objects.create(profile=s.profile, assistant=stranger.user)
        actor = stranger.actor
    elif fault == "auth_version":
        s.user.auth_version += 1
        s.user.save(update_fields=["auth_version"])
    else:
        from apps.governance.privacy_models import RecordHold

        RecordHold.objects.create(
            subject_kind="profile_asset",
            subject_uuid=s.asset.id,
            owner_uuid=s.user.public_id,
            subject_version=1,
            case_uuid=uuid4(),
            authorized_by=s.user,
            purpose="security",
            created_at=timezone.now(),
            updated_at=timezone.now(),
            review_at=timezone.now() + __import__("datetime").timedelta(hours=1),
            expires_at=timezone.now() + __import__("datetime").timedelta(hours=2),
            reason_code="retention_due",
        )
        s.user.state = "restricted"
        s.user.save(update_fields=["state"])
    reads = []
    original = s.store.read_limited

    def counted(key, maximum):
        reads.append(key)
        return original(key, maximum)

    monkeypatch.setattr(s.store, "read_limited", counted)
    with pytest.raises((AssetNotFound, PermissionError)):
        profile_assets.authorized_profile_download(
            actor, s.asset.id, "owner_preview", timezone.now()
        )
    assert reads == ([s.derivative.key] if fault == "integrity" else [])


def test_csrf_before_profile_and_upload_side_effect():
    from apps.assets.models import Asset
    from apps.athletes.models import AthleteProfile
    from apps.athletes.receipt_models import ProfileCommandReceipt as AthleteReceipt
    from apps.governance.audit_models import AuditEvent
    from apps.governance.outbox_models import OutboxEvent
    from apps.professionals.receipt_models import (
        ProfileCommandReceipt as ProfessionalReceipt,
    )

    s = owner()
    client = session_client(s)
    models = (
        AthleteProfile,
        ProfessionalProfile,
        Asset,
        AuditEvent,
        OutboxEvent,
        AthleteReceipt,
        ProfessionalReceipt,
    )
    before = [model.objects.count() for model in models]
    for route in (
        "/api/v1/athlete/profile/",
        "/api/v1/athlete/baseline/draft/",
        "/api/v1/professional/profile/",
        "/api/v1/professional/profile/steps/identity/",
        "/api/v1/profile-assets/begin/",
        f"/api/v1/profile-assets/{uuid4()}/body/",
        f"/api/v1/profile-assets/{uuid4()}/finalize/",
        f"/api/v1/profile-assets/{uuid4()}/abandon/",
        "/api/v1/professional/verification/draft/",
        "/athlete/setup/",
        "/professional/setup/",
        "/professional/verification/",
    ):
        response = post(client, route, {"operation_id": str(uuid4())})
        assert response.status_code == 403, route
        assert [model.objects.count() for model in models] == before


def test_unknown_owner_state_fields_denied():
    from apps.athletes.models import AthleteProfile

    s = owner()
    client = session_client(s)
    token = token_for(client)
    for forbidden in (
        "owner",
        "user_id",
        "state",
        "approved_roles",
        "source_key",
        "decision_version",
        "publication_eligibility",
        "health_history",
    ):
        response = post(
            client,
            "/api/v1/athlete/profile/",
            {"operation_id": str(uuid4()), forbidden: "unsafe"},
            token,
        )
        assert response.status_code == 400
        assert not AthleteProfile.objects.exists()


def test_api_no_store_uniform_403_404_409_503(monkeypatch):
    from django.db import DatabaseError

    from config.use_cases import athlete_profile

    s = owner()
    client = session_client(s)
    token = token_for(client)
    anonymous = Client().get("/api/v1/athlete/profile/")
    assert anonymous.status_code == 403 and anonymous.json() == {"status": "denied"}
    missing = client.get(f"/api/v1/athlete/baseline/{uuid4()}/")
    assert missing.status_code == 404 and missing.json() == {"status": "not_found"}
    created = post(
        client, "/api/v1/athlete/profile/", {"operation_id": str(uuid4())}, token
    )
    assert created.status_code == 201
    conflict = post(
        client,
        "/api/v1/athlete/baseline/draft/",
        {"expected_profile_version": 999, "operation_id": str(uuid4())},
        token,
    )
    assert conflict.status_code == 409 and conflict.json() == {"status": "conflict"}

    def outage(*args, **kwargs):
        raise DatabaseError("PRIVATE_INTERNAL_SENTINEL")

    monkeypatch.setattr(athlete_profile, "create_athlete_profile", outage)
    unavailable = post(
        client, "/api/v1/athlete/profile/", {"operation_id": str(uuid4())}, token
    )
    assert unavailable.status_code == 503 and unavailable.json() == {
        "status": "unavailable"
    }
    for response in (anonymous, missing, conflict, unavailable):
        assert "no-store" in response["Cache-Control"]
        assert "PRIVATE_INTERNAL_SENTINEL" not in response.content.decode()
