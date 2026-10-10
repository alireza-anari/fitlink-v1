from uuid import uuid4

import pytest
from django.db import DatabaseError, connection, transaction
from django.utils import timezone

from apps.governance.audit_models import AuditEvent
from apps.governance.outbox_models import OutboxEvent
from apps.professionals.contracts import ProfileConflict, ProfileNotFound
from apps.professionals.models import (
    ProfessionalRoleRestriction,
    RoleRestrictionHistory,
    VerificationDecision,
)

from .test_verification_decisions import approved, eligibility, facts, mutate_evidence
from .verification_helpers import command

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def revoke(s, kind="coach", *, captured=None, approval=None, operation=None):
    case, target, binding = captured or facts(s, kind)
    approval = (
        approval
        or VerificationDecision.objects.get(target=target, decision="approve").id
    )
    return command(
        "revoke_verification_target",
        s.staff.actor,
        case.id,
        target.id,
        approval,
        case.version,
        target.version,
        binding,
        s.staff.step,
        "evidence_revoked",
        "Synthetic private revocation",
        operation or uuid4(),
        timezone.now(),
    )


def restriction_facts(s, kind):
    case, _, binding = facts(s, kind)
    role = s.profile.roles.get(role=kind)
    return case, role, binding.restriction_token


def restrict(s, kind="nutritionist", *, release=False, captured=None, operation=None):
    case, role, token = captured or restriction_facts(s, kind)
    return command(
        "release_professional_role_restriction"
        if release
        else "restrict_professional_role",
        s.staff.actor,
        case.id,
        role.id,
        case.version,
        role.version,
        token,
        s.staff.step,
        "restriction_removed" if release else "role_restricted",
        operation or uuid4(),
        timezone.now(),
    )


def test_role_revocation_immediately_excludes_only_affected_role(settings):
    s = approved(settings)
    revoke(s)
    result = eligibility(s)
    assert result.identity_verified and result.eligible
    assert result.verified_roles == ("nutritionist",)
    original = VerificationDecision.objects.get(
        profile=s.profile, target_kind="coach", decision="approve"
    )
    row = VerificationDecision.objects.get(
        profile=s.profile, target_kind="coach", decision="revoke"
    )
    assert (
        row.revoked_approval_id == original.id and row.target_id == original.target_id
    )
    assert original.decision == "approve"


def test_coach_revocation_preserves_nutritionist(settings):
    test_role_revocation_immediately_excludes_only_affected_role(settings)


def test_identity_revocation_preserves_role_facts(settings):
    s = approved(settings)
    revoke(s, "identity")
    result = eligibility(s)
    assert not result.identity_verified and not result.eligible
    assert result.verified_roles == ("coach", "nutritionist")


def test_wrong_target_approval_denied(settings):
    s = approved(settings)
    wrong = VerificationDecision.objects.get(
        profile=s.profile, target_kind="nutritionist", decision="approve"
    )
    with pytest.raises((ProfileConflict, ProfileNotFound)):
        revoke(s, approval=wrong.id)
    assert VerificationDecision.objects.count() == 3


def test_revocation_replay_and_changed_payload(settings):
    s = approved(settings)
    captured, operation = facts(s, "coach"), uuid4()
    first = revoke(s, captured=captured, operation=operation)
    counts = (
        VerificationDecision.objects.count(),
        AuditEvent.objects.count(),
        OutboxEvent.objects.count(),
    )
    assert revoke(s, captured=captured, operation=operation) == first
    assert counts == (
        VerificationDecision.objects.count(),
        AuditEvent.objects.count(),
        OutboxEvent.objects.count(),
    )
    with pytest.raises(ProfileConflict):
        revoke(s, captured=captured, operation=operation, approval=uuid4())
    with pytest.raises(ProfileConflict):
        revoke(s)


def test_temporary_role_restriction_is_local(settings):
    s = approved(settings)
    role = s.profile.roles.get(role="nutritionist")
    before = (role.evidence_revision, role.decision_version, role.declaration_version)
    restrict(s)
    role.refresh_from_db()
    assert before == (
        role.evidence_revision,
        role.decision_version,
        role.declaration_version,
    )
    assert eligibility(s).verified_roles == ("coach",)
    assert eligibility(s).identity_verified and eligibility(s).eligible
    assert VerificationDecision.objects.count() == 3
    assert RoleRestrictionHistory.objects.get().event == "applied"


def test_restriction_removal_reuses_valid_approval(settings):
    s = approved(settings)
    restrict(s)
    restrict(s, release=True)
    assert eligibility(s).verified_roles == ("coach", "nutritionist")
    assert VerificationDecision.objects.count() == 3
    assert list(
        RoleRestrictionHistory.objects.order_by("at").values_list("event", flat=True)
    ) == ["applied", "released"]


def test_restriction_removal_cannot_undo_revocation(settings):
    s = approved(settings)
    restrict(s)
    revoke(s, "nutritionist")
    restrict(s, release=True)
    assert eligibility(s).verified_roles == ("coach",)
    assert VerificationDecision.objects.filter(decision="revoke").count() == 1


def test_restriction_release_cannot_restore_changed_evidence(settings):
    s = approved(settings)
    restrict(s)
    mutate_evidence(s, "nutritionist")
    restrict(s, release=True)
    assert eligibility(s).verified_roles == ("coach",)


def test_restriction_replay_duplicate_and_stale_token(settings):
    s = approved(settings)
    captured, operation = restriction_facts(s, "nutritionist"), uuid4()
    first = restrict(s, captured=captured, operation=operation)
    counts = (
        RoleRestrictionHistory.objects.count(),
        AuditEvent.objects.count(),
        OutboxEvent.objects.count(),
    )
    assert restrict(s, captured=captured, operation=operation) == first
    assert counts == (
        RoleRestrictionHistory.objects.count(),
        AuditEvent.objects.count(),
        OutboxEvent.objects.count(),
    )
    with pytest.raises(ProfileConflict):
        restrict(s, captured=captured)
    with pytest.raises(ProfileConflict):
        restrict(s)
    release = restriction_facts(s, "nutritionist")
    restrict(s, release=True)
    restrict(s)
    with pytest.raises(ProfileConflict):
        restrict(s, release=True, captured=release)
    assert (
        ProfessionalRoleRestriction.objects.filter(released_at__isnull=True).count()
        == 1
    )


def test_direct_sql_restriction_history_immutable(settings):
    s = approved(settings)
    restrict(s)
    row = RoleRestrictionHistory.objects.get()
    for sql in (
        "UPDATE professionals_rolerestrictionhistory "
        "SET reason_code = 'restriction_removed' WHERE id = %s",
        "DELETE FROM professionals_rolerestrictionhistory WHERE id = %s",
    ):
        with (
            pytest.raises(DatabaseError),
            transaction.atomic(),
            connection.cursor() as cursor,
        ):
            cursor.execute(sql, [row.id])


def rereview(s, kind):
    from apps.governance.staff import MockStepUpProvider, issue_mock_step_up

    from .verification_helpers import assign

    s.profile.refresh_from_db()
    s.case = command(
        "prepare_verification",
        s.actor,
        (kind,),
        s.profile.version,
        uuid4(),
        timezone.now(),
    )
    s.case = command(
        "submit_verification",
        s.actor,
        s.case.id,
        s.case.version,
        uuid4(),
        timezone.now(),
    )
    at = timezone.now()
    provider = MockStepUpProvider()
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


def test_new_authorized_reapproval_supersedes_revoke_and_preserves_history(settings):
    from .test_verification_decisions import decision

    s = approved(settings)
    revoke(s, "coach")
    old = VerificationDecision.objects.get(
        profile=s.profile, target_kind="coach", decision="revoke"
    )
    rereview(s, "coach")
    decision(s, "coach")
    result = eligibility(s)
    assert result.verified_roles == ("coach", "nutritionist") and result.eligible
    latest = (
        VerificationDecision.objects.filter(profile=s.profile, target_kind="coach")
        .order_by("-decision_sequence")
        .first()
    )
    assert latest.supersedes_decision_id == old.id
    old.refresh_from_db()
    assert old.decision == "revoke" and old.revoked_approval.decision == "approve"


def test_revoke_fences_older_pending_review_only_for_that_role(settings):
    from apps.professionals.models import VerificationTarget

    from .test_verification_decisions import decision

    s = approved(settings)
    old_case, old_step = s.case, s.staff.step
    old_facts = facts(s, "coach")
    rereview(s, "coach")
    pending_case, pending_step = s.case, s.staff.step
    pending = facts(s, "coach")
    s.case, s.staff.step = old_case, old_step
    revoke(s, captured=old_facts)
    s.case, s.staff.step = pending_case, pending_step
    with pytest.raises(ProfileConflict):
        decision(s, "coach", captured=pending)
    assert VerificationTarget.objects.get(pk=pending[1].id).state == "stale"
    assert eligibility(s).verified_roles == ("nutritionist",)
