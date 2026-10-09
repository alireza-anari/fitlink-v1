"""Real submitted snapshots, assigned review and current internal eligibility."""

from dataclasses import replace
from datetime import timedelta
from uuid import uuid4

import pytest
from django.core.exceptions import PermissionDenied
from django.db import DatabaseError, connection, transaction
from django.utils import timezone

from apps.governance.audit_models import AuditEvent
from apps.governance.outbox_models import OutboxEvent
from apps.professionals.contracts import ProfileConflict, ProfileNotFound
from apps.professionals.models import (
    Verification,
    VerificationDecision,
    VerificationTarget,
)
from config.use_cases.professional_profile import revise_credential, withdraw_credential

from .test_credential_revisions import payload
from .test_professional_setup import save
from .verification_helpers import assign, command, prepared, reviewer, selectors

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def review(settings, targets=("identity", "coach", "nutritionist")):
    s = prepared(targets)
    asset, dto = s.assets["nutritionist"]
    s.assets["nutritionist"] = (
        asset,
        revise_credential(
            s.actor,
            dto.id,
            payload(
                category="qualification",
                role="nutritionist",
                source_asset=asset.id,
                expires_on=timezone.now().date() + timedelta(days=1),
            ),
            dto.version,
            uuid4(),
            timezone.now(),
        ),
    )
    s.case = command(
        "submit_verification",
        s.actor,
        s.case.id,
        s.case.version,
        uuid4(),
        timezone.now(),
    )
    s.staff = reviewer(settings, s.case.id)
    s.case = assign(s, s.staff)
    s.case = command(
        "start_verification_review",
        s.staff.actor,
        s.case.id,
        s.case.version,
        s.staff.step,
        "verification_review",
        timezone.now(),
    )
    return s


def facts(s, kind):
    case = Verification.objects.get(pk=s.case.id)
    target = case.targets.get(target=kind)
    reader = selectors()
    assert callable(getattr(reader, "assigned_target_review_binding", None)), (
        "Missing review binding"
    )
    binding = reader.assigned_target_review_binding(
        s.staff.actor,
        case.id,
        target.id,
        s.staff.step,
        "verification_review",
        timezone.now(),
    )
    return case, target, binding


def decision(
    s, kind, value="approve", *, operation=None, captured=None, actor=None, at=None
):
    case, target, binding = captured or facts(s, kind)
    return command(
        "decide_verification_target",
        actor or s.staff.actor,
        case.id,
        target.id,
        value,
        case.version,
        target.version,
        binding,
        s.staff.step,
        "credentials_approved" if value == "approve" else "credentials_invalid",
        "Private synthetic explanation",
        operation or uuid4(),
        at or timezone.now(),
    )


def eligibility(s, at=None):
    from apps.professionals import selectors as reads

    assert callable(getattr(reads, "publication_eligibility", None)), (
        "Missing internal eligibility"
    )
    return reads.publication_eligibility(s.profile.id, at or timezone.now())


def approved(settings):
    s = review(settings)
    for kind in ("identity", "coach", "nutritionist"):
        decision(s, kind)
    assert eligibility(s).verified_roles == ("coach", "nutritionist")
    assert eligibility(s).eligible
    return s


def mutate_evidence(s, kind):
    asset, dto = s.assets[kind]
    return revise_credential(
        s.actor,
        dto.id,
        payload(
            category="identity" if kind == "identity" else "qualification",
            role=None if kind == "identity" else kind,
            source_asset=asset.id,
            title="Changed synthetic evidence",
        ),
        dto.version,
        uuid4(),
        timezone.now(),
    )


def test_coach_approve_nutritionist_reject(settings):
    s = review(settings)
    decision(s, "identity")
    decision(s, "coach")
    decision(s, "nutritionist", "reject")
    result = eligibility(s)
    assert result.identity_verified and result.eligible
    assert result.verified_roles == ("coach",)
    assert list(
        VerificationDecision.objects.filter(profile=s.profile)
        .order_by("decision_sequence", "target_kind")
        .values_list("target_kind", "decision")
    ) == [("coach", "approve"), ("identity", "approve"), ("nutritionist", "reject")]
    assert Verification.objects.get(pk=s.case.id).state == "decided"


def test_shared_identity_and_at_least_one_verified_role_required(settings):
    s = review(settings)
    decision(s, "coach")
    assert eligibility(s).verified_roles == ("coach",)
    assert not eligibility(s).eligible
    decision(s, "identity")
    assert eligibility(s).eligible
    save(s, "identity", {"roles": ["nutritionist"]})
    assert not eligibility(s).eligible


def test_nutritionist_expiry_preserves_coach(settings):
    s = approved(settings)
    result = eligibility(s, timezone.now() + timedelta(days=2))
    assert result.verified_roles == ("coach",)
    assert result.identity_verified and result.eligible


@pytest.mark.parametrize("kind", ["identity", "coach", "nutritionist"])
@pytest.mark.parametrize("fault", ["withdrawn", "quarantined", "revoked", "rejected"])
def test_expired_withdrawn_or_quarantined_evidence_denies_only_affected_target(
    settings, kind, fault
):
    s = approved(settings)
    asset, dto = s.assets[kind]
    if fault == "withdrawn":
        withdraw_credential(s.actor, dto.id, dto.version, uuid4(), timezone.now())
    elif fault == "revoked":
        asset.revoked_at = timezone.now()
        asset.save(update_fields=["revoked_at"])
    else:
        asset.state = "quarantined" if fault == "quarantined" else "rejected"
        asset.save(update_fields=["state"])
    result = eligibility(s)
    assert result.verified_roles == tuple(
        r for r in ("coach", "nutritionist") if r != kind
    )
    assert result.identity_verified == (kind != "identity")
    assert result.eligible == (kind != "identity")
    assert (
        VerificationDecision.objects.filter(
            profile=s.profile, decision="approve"
        ).count()
        == 3
    )


def test_decision_replay_vs_changed_payload(settings):
    s = review(settings)
    captured, operation = facts(s, "coach"), uuid4()
    first = decision(s, "coach", captured=captured, operation=operation)
    counts = (
        VerificationDecision.objects.count(),
        AuditEvent.objects.count(),
        OutboxEvent.objects.count(),
    )
    assert decision(s, "coach", captured=captured, operation=operation) == first
    assert counts == (
        VerificationDecision.objects.count(),
        AuditEvent.objects.count(),
        OutboxEvent.objects.count(),
    )
    with pytest.raises(ProfileConflict):
        decision(s, "coach", "reject", captured=captured, operation=operation)


def test_rejection_history_retained_resubmit_new_bundle(settings):
    s = review(settings)
    decision(s, "identity")
    decision(s, "coach")
    decision(s, "nutritionist", "reject")
    old = VerificationDecision.objects.get(
        profile=s.profile, target_kind="nutritionist"
    )
    s.profile.refresh_from_db()
    s.case = command(
        "prepare_verification",
        s.actor,
        ("nutritionist",),
        s.profile.version,
        uuid4(),
        timezone.now(),
    )
    assert s.case.id != old.target.verification_id
    s.case = command(
        "submit_verification",
        s.actor,
        s.case.id,
        s.case.version,
        uuid4(),
        timezone.now(),
    )
    # Fresh case requires a new case-bound step-up.
    from apps.governance.staff import MockStepUpProvider, issue_mock_step_up

    provider = MockStepUpProvider()
    at = timezone.now()
    assertion = provider.prepare(
        s.staff.user.public_id, "professional_verification", s.case.id, at
    )
    with transaction.atomic():
        s.staff.step = issue_mock_step_up(
            s.staff.user,
            "professional_verification",
            s.case.id,
            assertion.raw_assertion,
            s.user,
            at,
            provider,
        )
    s.case = assign(s, s.staff)
    s.case = command(
        "start_verification_review",
        s.staff.actor,
        s.case.id,
        s.case.version,
        s.staff.step,
        "verification_review",
        timezone.now(),
    )
    decision(s, "nutritionist")
    old.refresh_from_db()
    assert old.decision == "reject"
    assert eligibility(s).verified_roles == ("coach", "nutritionist")


def test_add_declared_role_preserves_other_approval(settings):
    s = review(settings, ("identity", "coach"))
    save(s, "identity", {"roles": ["coach"]})
    decision(s, "identity")
    decision(s, "coach")
    before = s.profile.roles.get(role="coach")
    save(s, "identity", {"roles": ["coach", "nutritionist"]})
    after = s.profile.roles.get(role="coach")
    assert (
        before.evidence_revision,
        before.decision_version,
        before.declaration_version,
    ) == (after.evidence_revision, after.decision_version, after.declaration_version)
    assert eligibility(s).verified_roles == ("coach",)


def test_deactivate_role_preserves_other_approval(settings):
    s = approved(settings)
    save(s, "identity", {"roles": ["nutritionist"]})
    assert eligibility(s).verified_roles == ("nutritionist",)
    save(s, "identity", {"roles": ["coach", "nutritionist"]})
    assert eligibility(s).verified_roles == ("coach", "nutritionist")
    assert VerificationDecision.objects.count() == 3


@pytest.mark.parametrize("change", ["evidence", "declaration"])
def test_inflight_requested_role_or_evidence_edit_is_stale(settings, change):
    s = review(settings)
    captured = facts(s, "coach")
    if change == "evidence":
        mutate_evidence(s, "coach")
    else:
        save(s, "identity", {"roles": ["nutritionist"]})
    with pytest.raises(ProfileConflict):
        decision(s, "coach", captured=captured)
    assert VerificationTarget.objects.get(pk=captured[1].id).state == "stale"
    assert (
        VerificationTarget.objects.get(pk=captured[1].id).target_snapshot_hash
        == captured[1].target_snapshot_hash
    )
    decision(s, "nutritionist")
    assert eligibility(s).verified_roles == ("nutritionist",)


def test_c04_input_excludes_unverified_declarations(settings):
    s = review(settings)
    decision(s, "identity")
    decision(s, "coach")
    assert eligibility(s).verified_roles == ("coach",)
    assert eligibility(s).eligible


@pytest.mark.parametrize("kind", ["identity", "coach", "nutritionist"])
def test_bound_edit_preserves_history_and_only_affected_approval(settings, kind):
    s = approved(settings)
    mutate_evidence(s, kind)
    result = eligibility(s)
    assert result.verified_roles == tuple(
        r for r in ("coach", "nutritionist") if r != kind
    )
    assert result.identity_verified == (kind != "identity")
    assert result.eligible == (kind != "identity")
    assert VerificationDecision.objects.count() == 3


@pytest.mark.parametrize(
    "state",
    [
        "restricted",
        "suspended",
        "deletion_requested",
        "pending_deletion",
        "deleted",
        "auth_version",
    ],
)
def test_account_state_and_auth_change(settings, state):
    s = approved(settings)
    if state == "auth_version":
        s.staff.user.auth_version += 1
        s.staff.user.save(update_fields=["auth_version"])
        assert eligibility(s).eligible
    else:
        s.user.state = state
        s.user.is_active = state not in {"suspended", "deleted"}
        s.user.save(update_fields=["state", "is_active"])
        assert not eligibility(s).eligible
    with pytest.raises((PermissionDenied, PermissionError)):
        case, target, binding = facts(s, "coach")
        decision(s, "coach", captured=(case, target, binding))
    assert VerificationDecision.objects.count() == 3


def test_cosmetic_change_retains_eligibility_and_no_public_route(settings):
    from django.urls import Resolver404, resolve

    s = approved(settings)
    before = eligibility(s)
    save(
        s,
        "description",
        {
            "biography": "Cosmetic fixture",
            "specialties": ["Fitness"],
            "experience_years": 3,
        },
    )
    result = eligibility(s)
    assert result.eligible and result.verified_roles == before.verified_roles
    assert result.identity_verified
    for route in (
        "/professional/public/",
        "/api/v1/professional/eligibility/",
        "/marketplace/",
        "/professionals/fixture/",
    ):
        with pytest.raises(Resolver404):
            resolve(route)
    assert "Private synthetic explanation" not in repr(result)
    assert "Private Fixture" not in repr(result)
    assert "source/" not in repr(result)


@pytest.mark.parametrize(
    "fault",
    [
        "bare_superuser",
        "wrong_case",
        "stale_binding",
        "stale_target",
        "stale_case",
        "stale_actor",
    ],
)
def test_decision_authority_and_binding_fail_closed(settings, fault):
    s = review(settings)
    case, target, binding = facts(s, "coach")
    actor = s.staff.actor
    if fault == "bare_superuser":
        s.staff.grant.delete()
        s.staff.user.is_superuser = True
        s.staff.user.save(update_fields=["is_superuser"])
    elif fault == "wrong_case":
        case.id = uuid4()
    elif fault == "stale_binding":
        binding = replace(binding, evidence_revision=binding.evidence_revision + 1)
    elif fault == "stale_target":
        target.version += 1
    elif fault == "stale_case":
        case.version += 1
    else:
        actor = replace(actor, auth_version=actor.auth_version + 1)
    with pytest.raises(
        (ProfileConflict, ProfileNotFound, PermissionDenied, PermissionError)
    ):
        decision(s, "coach", captured=(case, target, binding), actor=actor)
    assert not VerificationDecision.objects.exists()


def test_decision_audit_failure_rolls_back(settings, monkeypatch):
    from config.use_cases import professional_verification

    s = review(settings)
    captured = facts(s, "coach")
    before = OutboxEvent.objects.count()

    def fail(*args, **kwargs):
        raise RuntimeError("synthetic audit unavailable")

    monkeypatch.setattr(professional_verification, "append_event", fail)
    with pytest.raises(RuntimeError):
        decision(s, "coach", captured=captured)
    assert not VerificationDecision.objects.exists()
    assert OutboxEvent.objects.count() == before
    assert VerificationTarget.objects.get(pk=captured[1].id).state == "under_review"


def test_direct_sql_immutable_decision_guards(settings):
    approved(settings)
    row = VerificationDecision.objects.first()
    for sql in (
        "UPDATE professionals_verificationdecision "
        "SET explanation = 'changed' WHERE id = %s",
        "DELETE FROM professionals_verificationdecision WHERE id = %s",
    ):
        with (
            pytest.raises(DatabaseError),
            transaction.atomic(),
            connection.cursor() as cursor,
        ):
            cursor.execute(sql, [row.id])
