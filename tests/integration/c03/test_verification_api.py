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
from .verification_helpers import assign, reviewer

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
        other = reviewer(settings, s.case.id, "+989123456783")
        s.case = assign(s, other, detail(s).version)
    elif fault == "crosscase":
        StaffStepUpGrant.objects.filter(pk=step).update(case_uuid=uuid4())
    elif fault == "expired":
        StaffStepUpGrant.objects.filter(pk=step).update(
            expires_at=timezone.now() - timedelta(seconds=1)
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
