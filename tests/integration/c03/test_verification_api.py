"""Assigned staff projections and real-session command transport, never auth mocks."""

from dataclasses import fields
from datetime import timedelta
from uuid import uuid4

import pytest
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from apps.governance.staff_models import StaffStepUpGrant
from apps.professionals.verification_selectors import assigned_verification_detail

from .profile_helpers import make_actor
from .test_verification_decisions import approved, decision, mutate_evidence, review
from .test_verification_revocation import restrict, revoke
from .verification_helpers import assign

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def detail(s, actor=None, step=None):
    return assigned_verification_detail(
        actor or s.staff.actor,
        s.case.id,
        step or s.staff.step,
        "verification_review",
        timezone.now(),
    )


def context(result, kind):
    assert hasattr(result, "review_targets"), "Missing assigned staff read context"
    return next(t for t in result.review_targets if t.target == kind)


def test_assigned_projection_role_refs_identity_and_case_history(settings):
    s = review(settings)
    result = detail(s)
    identity = context(result, "identity")
    assert identity.role_uuid is None and identity.role_version is None
    for kind in ("coach", "nutritionist"):
        role = s.profile.roles.get(role=kind)
        target = context(result, kind)
        assert (target.role_uuid, target.role_version) == (role.id, role.version)
        assert target.effective_approval_uuid is None
    assert result.history and len(result.history) <= 25
    assert {f.name for f in fields(result.history[0])} == {
        "event",
        "target_uuid",
        "at",
        "reason_code",
        "prior_version",
        "new_version",
    }
    assert [h.event for h in result.history] == ["submit", "assign", "start_review"]
    assert all(h.target_uuid is None for h in result.history)


def test_effective_approval_exact_target_and_role(settings):
    from apps.professionals.models import VerificationDecision

    s = approved(settings)
    result = detail(s)
    approvals = {
        kind: VerificationDecision.objects.get(
            profile=s.profile, target_kind=kind, decision="approve"
        ).id
        for kind in ("identity", "coach", "nutritionist")
    }
    for kind, identifier in approvals.items():
        assert context(result, kind).effective_approval_uuid == identifier
    assert len(set(approvals.values())) == 3
    restrict(s, "coach")
    assert context(detail(s), "coach").effective_approval_uuid == approvals["coach"]
    revoke(s, "coach")
    result = detail(s)
    assert context(result, "coach").effective_approval_uuid is None
    assert (
        context(result, "nutritionist").effective_approval_uuid
        == approvals["nutritionist"]
    )


def test_rejected_and_stale_projection_has_no_fake_approval(settings):
    s = review(settings)
    decision(s, "coach", "reject")
    mutate_evidence(s, "nutritionist")
    result = detail(s)
    assert context(result, "coach").effective_approval_uuid is None
    assert context(result, "nutritionist").effective_approval_uuid is None


@pytest.mark.parametrize(
    "fault", ["reassigned", "crosscase", "expired", "auth", "superuser", "self"]
)
def test_extended_projection_has_no_lower_authority(settings, fault):
    s = review(settings)
    actor, step = s.staff.actor, s.staff.step
    if fault == "reassigned":
        other = next_reviewer(s)
        s.case = assign(s, other, detail(s).version)
    elif fault == "crosscase":
        StaffStepUpGrant.objects.filter(pk=step).update(case_uuid=uuid4())
    elif fault == "expired":
        StaffStepUpGrant.objects.filter(pk=step).update(
            verified_at=timezone.now() - timedelta(minutes=10),
            expires_at=timezone.now() - timedelta(seconds=1),
        )
    elif fault == "auth":
        s.staff.user.auth_version += 1
        s.staff.user.save(update_fields=["auth_version"])
    elif fault == "self":
        actor = s.actor
    else:
        other = make_actor("+989123456784")
        other.user.is_superuser = True
        other.user.save(update_fields=["is_superuser"])
        actor = other.actor
    with pytest.raises((PermissionDenied, PermissionError)):
        detail(s, actor, step)


def next_reviewer(s):
    from django.db import transaction

    from apps.governance.staff import MockStepUpProvider, issue_mock_step_up
    from apps.governance.staff_models import StaffCapabilityGrant

    other = make_actor("+989123456783")
    issuer = s.staff.grant.granted_by
    other.grant = StaffCapabilityGrant.objects.create(
        user=other.user,
        capability="professional_verification",
        granted_by=issuer,
        reason_code="staff_assigned",
        valid_from=other.at - timedelta(seconds=1),
        valid_until=other.at + timedelta(hours=1),
    )
    provider = MockStepUpProvider()
    assertion = provider.prepare(
        other.user.public_id, "professional_verification", s.case.id, other.at
    )
    with transaction.atomic():
        other.step = issue_mock_step_up(
            other.user,
            "professional_verification",
            s.case.id,
            assertion.raw_assertion,
            issuer,
            other.at,
            provider,
        )
    return other


def headers(s):
    return {
        "HTTP_X_VERIFICATION_STEP_UP": str(s.staff.step),
        "HTTP_X_VERIFICATION_REASON": "verification_review",
    }


def api_path(s, command=""):
    return f"/api/v1/staff/professional-verification/{s.case.id}/" + (
        command + "/" if command else ""
    )


def input_for(s, kind="coach"):
    from dataclasses import asdict

    from .test_verification_decisions import facts

    case, target, binding = facts(s, kind)
    return {
        "target_uuid": str(target.id),
        "expected_case_version": case.version,
        "expected_target_version": target.version,
        "expected_binding": asdict(binding),
        "step_up_id": str(s.staff.step),
        "reason_code": "credentials_approved",
        "explanation": "Synthetic bounded staff explanation",
        "operation_id": str(uuid4()),
        "decision": "approve",
    }


def normalize(value):
    from uuid import UUID

    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, dict):
        return {k: normalize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [normalize(v) for v in value]
    return value


def test_staff_api_decision_identical_replay_changed_payload_and_csrf(settings):
    from apps.professionals.models import VerificationDecision

    from .test_owner_api import post, session_client, token_for

    s = review(settings)
    client = session_client(s.staff)
    payload = normalize(input_for(s))
    assert post(client, api_path(s, "decide"), payload).status_code == 403
    assert VerificationDecision.objects.count() == 0
    token = token_for(client)
    assert post(client, api_path(s, "decide"), payload, token).status_code == 200
    assert post(client, api_path(s, "decide"), payload, token).status_code == 200
    assert VerificationDecision.objects.filter(target_kind="coach").count() == 1
    payload["explanation"] = "Changed bounded explanation"
    assert post(client, api_path(s, "decide"), payload, token).status_code == 409
    assert VerificationDecision.objects.filter(target_kind="nutritionist").count() == 0


@pytest.mark.parametrize(
    "fault",
    [
        "capability",
        "assignment",
        "expired",
        "crosscase",
        "auth",
        "superuser",
        "assistant",
    ],
)
def test_staff_api_live_detail_denials(settings, fault):
    from apps.professionals.models import AssistantMembership, VerificationAssignment

    from .test_owner_api import session_client

    s = review(settings)
    client = session_client(s.staff)
    if fault in {"capability", "superuser", "assistant"}:
        s.staff.grant.revoked_at = timezone.now()
        s.staff.grant.save(update_fields=["revoked_at"])
        if fault == "superuser":
            s.staff.user.is_superuser = s.staff.user.is_staff = True
            s.staff.user.save(update_fields=["is_superuser", "is_staff"])
        if fault == "assistant":
            AssistantMembership.objects.create(
                profile=s.profile, assistant=s.staff.user
            )
    elif fault == "assignment":
        VerificationAssignment.objects.filter(verification_id=s.case.id).update(
            ended_at=timezone.now()
        )
    elif fault == "expired":
        StaffStepUpGrant.objects.filter(pk=s.staff.step).update(
            verified_at=timezone.now() - timedelta(minutes=10),
            expires_at=timezone.now() - timedelta(seconds=1),
        )
    elif fault == "crosscase":
        StaffStepUpGrant.objects.filter(pk=s.staff.step).update(case_uuid=uuid4())
    else:
        s.staff.user.auth_version += 1
        s.staff.user.save(update_fields=["auth_version"])
    response = client.get(api_path(s), **headers(s))
    assert response.status_code == 403
    assert "no-store" in response["Cache-Control"]
    assert s.user.phone not in response.content.decode()


@pytest.mark.parametrize(
    "fault", ["case_version", "target_version", "binding", "unknown", "foreign_target"]
)
def test_staff_decision_stale_unknown_and_cross_target_denied(settings, fault):
    from apps.professionals.models import VerificationDecision

    from .test_owner_api import post, session_client, token_for

    s = review(settings)
    payload = normalize(input_for(s))
    if fault == "case_version":
        payload["expected_case_version"] += 1
    elif fault == "target_version":
        payload["expected_target_version"] += 1
    elif fault == "binding":
        payload["expected_binding"]["evidence_revision"] += 1
    elif fault == "unknown":
        payload["is_superuser"] = True
    else:
        payload["target_uuid"] = str(uuid4())
    client = session_client(s.staff)
    response = post(client, api_path(s, "decide"), payload, token_for(client))
    assert response.status_code == (
        400 if fault == "unknown" else 404 if fault == "foreign_target" else 409
    )
    assert VerificationDecision.objects.count() == 0
    assert "no-store" in response["Cache-Control"]


def test_staff_queue_minimal_bounded_and_capability_required(settings):
    from django.db import transaction

    from apps.governance.staff import MockStepUpProvider, issue_mock_step_up

    from .test_owner_api import session_client

    s = review(settings)
    provider = MockStepUpProvider()
    at = timezone.now()
    assertion = provider.prepare(
        s.staff.user.public_id, "professional_verification", None, at
    )
    with transaction.atomic():
        step = issue_mock_step_up(
            s.staff.user,
            "professional_verification",
            None,
            assertion.raw_assertion,
            s.staff.grant.granted_by,
            at,
            provider,
        )
    values = {
        "HTTP_X_VERIFICATION_STEP_UP": str(step),
        "HTTP_X_VERIFICATION_REASON": "verification_review",
    }
    # Trusted fixture rows exercise the actual PostgreSQL queue and cursor;
    # each belongs to a separate active owner, beyond the page boundary.
    from apps.professionals.models import ProfessionalProfile, Verification

    for index in range(27):
        owner = make_actor(f"+989120000{index:03}")
        profile = ProfessionalProfile.objects.create(user=owner.user)
        Verification.objects.create(
            profile=profile, sequence=1, state="submitted", submitted_at=at
        )
    client = session_client(s.staff)
    response = client.get("/api/v1/staff/professional-verification/queue/", **values)
    assert response.status_code == 200
    result = response.json()
    assert set(result) == {"items", "next_cursor"} and len(result["items"]) == 25
    import json

    second = client.get(
        "/api/v1/staff/professional-verification/queue/",
        **values,
        HTTP_X_VERIFICATION_CURSOR=json.dumps(result["next_cursor"]),
    )
    assert second.status_code == 200 and len(second.json()["items"]) == 2
    assert not {r["id"] for r in result["items"]} & {
        r["id"] for r in second.json()["items"]
    }
    assert all(
        set(row) == {"id", "state", "submitted_at", "requested_targets"}
        for row in result["items"]
    )
    s.staff.grant.revoked_at = timezone.now()
    s.staff.grant.save(update_fields=["revoked_at"])
    assert (
        client.get(
            "/api/v1/staff/professional-verification/queue/", **values
        ).status_code
        == 403
    )


def test_evidence_proxy_audit_failure_prevents_bytes_and_raw_denied(
    settings, monkeypatch
):
    from hashlib import sha256

    from django.db import DatabaseError

    from apps.assets.storage import FakePrivateStore
    from apps.governance import audit

    from .test_owner_api import session_client

    s = review(settings)
    asset = s.assets["coach"][0]
    derivative = asset.derivatives.get()
    clean = b"\x89PNG\r\n\x1a\nsynthetic clean derivative"
    derivative.sha256 = sha256(clean).hexdigest()
    derivative.save(update_fields=["sha256"])
    store = FakePrivateStore()
    store.put(derivative.key, clean, "image/png")
    monkeypatch.setattr("apps.assets.delivery.get_private_store", lambda: store)
    client = session_client(s.staff)
    path = api_path(s) + f"evidence/{asset.id}/"
    response = client.get(path, **headers(s))
    assert response.status_code == 200 and response.content == clean
    assert (
        response["Cache-Control"] == "private, no-store"
        and response["X-Content-Type-Options"] == "nosniff"
    )
    assert "source/" not in str(response.headers) and "derivative/" not in str(
        response.headers
    )

    def unavailable(*args, **kwargs):
        raise DatabaseError("Synthetic audit unavailable")

    monkeypatch.setattr(audit, "append_event", unavailable)
    assert client.get(path, **headers(s)).status_code == 503
    assert client.get(f"/api/v1/profile-assets/{asset.id}/content/").status_code in {
        403,
        404,
    }


def test_withdrawn_and_other_case_history_stay_case_local(settings):
    from apps.professionals.models import VerificationHistory

    from .verification_helpers import command

    s = review(settings)
    target = next(t for t in s.case.targets if t.target == "nutritionist")
    s.case = command(
        "withdraw_verification_target",
        s.actor,
        s.case.id,
        target.id,
        s.case.version,
        uuid4(),
        timezone.now(),
    )
    result = detail(s)
    assert context(result, "nutritionist").effective_approval_uuid is None
    exact = set(
        VerificationHistory.objects.filter(verification_id=s.case.id).values_list(
            "id", flat=True
        )
    )
    assert exact
    other_owner = make_actor("+989123456785")
    from apps.professionals.models import ProfessionalProfile, Verification

    other_profile = ProfessionalProfile.objects.create(user=other_owner.user)
    other_case = Verification.objects.create(profile=other_profile, sequence=1)
    VerificationHistory.objects.create(
        verification=other_case,
        actor=other_owner.user,
        event="submit",
        reason_code="verification_submitted",
        prior_version=1,
        new_version=2,
        at=timezone.now(),
    )
    assert detail(s).history == result.history
    for history in result.history:
        assert not {
            "actor",
            "explanation",
            "source_key",
            "derivative_key",
            "payload",
            "sha256",
        } & {f.name for f in fields(history)}
