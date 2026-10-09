from uuid import uuid4

import pytest
from django.db import DatabaseError, transaction
from django.utils import timezone

from apps.professionals.contracts import ProfileConflict
from apps.professionals.models import (
    Verification,
    VerificationEvidence,
    VerificationTarget,
)

from .test_professional_setup import save
from .verification_helpers import command, prepared, submitted

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def test_submit_freezes_relational_identity_and_each_role_snapshot():
    s = submitted()
    assert s.case.state == "submitted"
    targets = list(VerificationTarget.objects.filter(verification_id=s.case.id))
    assert {t.target for t in targets} == {"identity", "coach", "nutritionist"}
    assert (
        VerificationEvidence.objects.filter(target__verification_id=s.case.id).count()
        == 3
    )
    for target in targets:
        assert target.state == "submitted" and len(target.target_snapshot_hash) == 64
        with pytest.raises(DatabaseError), transaction.atomic():
            VerificationTarget.objects.filter(pk=target.id).update(
                target_snapshot_hash="f" * 64
            )
        with pytest.raises(DatabaseError), transaction.atomic():
            VerificationEvidence.objects.filter(target=target).update(
                category="qualification" if target.target == "identity" else "identity"
            )
    assert not any(
        asset.classification != "private_source" for asset, _ in s.assets.values()
    )


def test_inflight_requested_role_or_evidence_edit_is_stale():
    s = submitted()
    old = VerificationTarget.objects.get(
        verification_id=s.case.id, target="nutritionist"
    )
    digest = old.target_snapshot_hash
    save(s, "identity", {"roles": ["coach"]})
    old.refresh_from_db()
    assert old.state == "stale" and old.target_snapshot_hash == digest
    assert (
        VerificationTarget.objects.get(verification_id=s.case.id, target="coach").state
        == "submitted"
    )


def test_unrelated_role_edit_preserves_pending_target():
    s = submitted(("identity", "coach"))
    save(s, "identity", {"roles": ["coach"]})
    assert set(
        VerificationTarget.objects.filter(verification_id=s.case.id).values_list(
            "state", flat=True
        )
    ) == {"submitted"}


def test_duplicate_submission_and_new_resubmission_bundle():
    s = prepared()
    op, version = uuid4(), s.case.version
    first = command(
        "submit_verification", s.actor, s.case.id, version, op, timezone.now()
    )
    again = command(
        "submit_verification", s.actor, s.case.id, version, op, timezone.now()
    )
    assert first == again
    with pytest.raises(ProfileConflict):
        command(
            "prepare_verification",
            s.actor,
            ("identity", "coach"),
            s.profile.version,
            uuid4(),
            timezone.now(),
        )
    for t in VerificationTarget.objects.filter(verification_id=first.id).order_by("id"):
        row = Verification.objects.get(pk=first.id)
        command(
            "withdraw_verification_target",
            s.actor,
            first.id,
            t.id,
            row.version,
            uuid4(),
            timezone.now(),
        )
    row.refresh_from_db()
    assert Verification.objects.get(pk=first.id).state == "withdrawn"
    next_case = command(
        "prepare_verification",
        s.actor,
        ("identity", "coach"),
        s.profile.version,
        uuid4(),
        timezone.now(),
    )
    assert next_case.id != first.id and next_case.sequence == 2


@pytest.mark.parametrize("fault", ["expired", "withdrawn", "revoked", "unready"])
def test_submission_denies_current_invalid_evidence(fault):
    s = prepared()
    asset, dto = s.assets["coach"]
    from apps.professionals.models import Credential

    if fault == "expired":
        # Source metadata is immutable; expire by evaluating after its date.
        at = timezone.now().replace(year=2031)
        from apps.accounts.security_models import AccountSessionControl

        AccountSessionControl.objects.filter(pk=s.actor.control_id).update(
            expires_at=at.replace(year=2032)
        )
    else:
        at = timezone.now()
        if fault == "withdrawn":
            Credential.objects.filter(pk=dto.id).update(withdrawn_at=at)
        else:
            asset.state = "revoked" if fault == "revoked" else "quarantined"
            asset.save(update_fields=["state"])
    with (
        pytest.raises(ValueError, match="expired")
        if fault == "expired"
        else pytest.raises((ValueError, LookupError, PermissionError))
    ):
        command("submit_verification", s.actor, s.case.id, s.case.version, uuid4(), at)
    assert Verification.objects.get(pk=s.case.id).state == "draft"


def historical_identity(settings, decision="approve"):
    # Imported historical outcome only: Task7 exposes no decision command.
    from apps.professionals.models import VerificationDecision

    from .verification_helpers import assign, reviewer

    s = submitted(("identity",))
    staff = reviewer(settings, s.case.id)
    assigned = assign(s, staff)
    command(
        "start_verification_review",
        staff.actor,
        s.case.id,
        assigned.version,
        staff.step,
        "verification_review",
        timezone.now(),
    )
    target = VerificationTarget.objects.get(verification_id=s.case.id)
    s.historical_decision = VerificationDecision.objects.create(
        target=target,
        profile=s.profile,
        target_kind="identity",
        actor=staff.user,
        decision=decision,
        reason_code="identity_verified"
        if decision == "approve"
        else "credentials_invalid",
        target_snapshot_hash=target.target_snapshot_hash,
        bound_evidence_revision=target.bound_evidence_revision,
        decision_sequence=1,
        decided_at=timezone.now(),
    )
    target.state = "approved" if decision == "approve" else "rejected"
    target.version += 1
    target.save(update_fields=["state", "version", "updated_at"])
    case = Verification.objects.get(pk=s.case.id)
    case.state, case.decided_at = "decided", timezone.now()
    case.version += 1
    case.save(update_fields=["state", "decided_at", "version", "updated_at"])
    s.profile.identity_decision_version += 1
    s.profile.save(update_fields=["identity_decision_version", "updated_at"])
    s.staff, s.identity_target = staff, target
    return s


def test_existing_identity_approval_reused_without_resubmission(settings):
    from apps.professionals.models import VerificationDecision

    s = historical_identity(settings)
    dto = command(
        "prepare_verification",
        s.actor,
        ("coach",),
        s.profile.version,
        uuid4(),
        timezone.now(),
    )
    assert tuple(t.target for t in dto.targets) == ("coach",)
    assert VerificationDecision.objects.count() == 1


@pytest.mark.parametrize("fault", ["rejected", "revoked", "expired"])
def test_invalid_historical_identity_cannot_be_reused(settings, fault):
    from apps.accounts.security_models import AccountSessionControl
    from apps.professionals.models import VerificationDecision

    s = historical_identity(settings, "reject" if fault == "rejected" else "approve")
    at = timezone.now()
    if fault == "revoked":
        VerificationDecision.objects.create(
            target=s.identity_target,
            profile=s.profile,
            target_kind="identity",
            actor=s.staff.user,
            decision="revoke",
            revoked_approval=s.historical_decision,
            reason_code="evidence_revoked",
            target_snapshot_hash=s.identity_target.target_snapshot_hash,
            bound_evidence_revision=s.identity_target.bound_evidence_revision,
            decision_sequence=2,
            decided_at=at,
        )
        s.profile.identity_decision_version += 1
        s.profile.save(update_fields=["identity_decision_version", "updated_at"])
    if fault == "expired":
        at = at.replace(year=2031)
        AccountSessionControl.objects.filter(pk=s.actor.control_id).update(
            expires_at=at.replace(year=2032)
        )
    with pytest.raises(ValueError, match="Shared identity review required"):
        command(
            "prepare_verification",
            s.actor,
            ("coach",),
            s.profile.version,
            uuid4(),
            at,
        )


@pytest.mark.parametrize(
    "targets", [(), ("identity", "identity"), ("other",), ("coach",)]
)
def test_request_targets_are_explicit_and_identity_required(targets):
    from .test_professional_setup import owner

    s = owner()
    with pytest.raises(ValueError):
        command(
            "prepare_verification",
            s.actor,
            targets,
            s.profile.version,
            uuid4(),
            timezone.now(),
        )


def test_submission_audit_failure_rolls_back_snapshot_and_outbox(monkeypatch):
    from apps.governance.outbox_models import OutboxEvent

    s = prepared()
    old_targets = list(
        VerificationTarget.objects.filter(verification_id=s.case.id).values_list(
            "id", flat=True
        )
    )
    old_events = OutboxEvent.objects.count()

    def fail(*args, **kwargs):
        raise RuntimeError("Injected audit failure")

    monkeypatch.setattr("apps.governance.audit.append_event", fail)
    with pytest.raises(RuntimeError):
        command(
            "submit_verification",
            s.actor,
            s.case.id,
            s.case.version,
            uuid4(),
            timezone.now(),
        )
    assert Verification.objects.get(pk=s.case.id).state == "draft"
    assert set(
        VerificationTarget.objects.filter(verification_id=s.case.id).values_list(
            "id", flat=True
        )
    ) == set(old_targets)
    assert OutboxEvent.objects.count() == old_events
