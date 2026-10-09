from datetime import timedelta
from uuid import uuid4

import pytest
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from apps.governance.staff_models import StaffStepUpGrant
from apps.professionals.models import Verification

from .profile_helpers import make_actor
from .verification_helpers import assign, command, reviewer, selectors, submitted

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]
DENIED = (PermissionDenied, PermissionError, LookupError)


def test_reassignment_invalidates_old_reviewer(settings):
    s = submitted()
    staff = reviewer(settings, s.case.id)
    dto = assign(s, staff)
    other = make_actor("+989123456783")
    from apps.governance.staff_models import StaffCapabilityGrant

    StaffCapabilityGrant.objects.create(
        user=other.user,
        granted_by=staff.user,
        capability="professional_verification",
        reason_code="staff_assigned",
        valid_from=staff.at,
        valid_until=staff.at + timedelta(hours=1),
    )
    command(
        "assign_verification",
        staff.actor,
        s.case.id,
        other.user.public_id,
        dto.version,
        staff.step,
        "case_conflict",
        timezone.now(),
    )
    with pytest.raises(DENIED):
        selectors().assigned_verification_detail(
            staff.actor, s.case.id, staff.step, "verification_review", timezone.now()
        )


@pytest.mark.parametrize(
    "fault",
    [
        "capability",
        "assignment",
        "expired",
        "wrong_case",
        "auth",
        "reason",
        "superuser",
    ],
)
def test_staff_without_capability_assignment_fresh_stepup_or_nonself_denied(
    settings, fault
):
    s = submitted()
    staff = reviewer(settings, s.case.id)
    if fault != "assignment":
        assign(s, staff)
    if fault in {"capability", "superuser"}:
        staff.grant.revoked_at = timezone.now()
        staff.grant.save()
    if fault == "superuser":
        staff.user.is_staff = staff.user.is_superuser = True
        staff.user.save()
    if fault == "expired":
        StaffStepUpGrant.objects.filter(pk=staff.step).update(
            expires_at=staff.at + timedelta(seconds=1)
        )
    if fault == "wrong_case":
        StaffStepUpGrant.objects.filter(pk=staff.step).update(case_uuid=uuid4())
    if fault == "auth":
        staff.user.auth_version += 1
        staff.user.save()
    at = staff.at + timedelta(seconds=2) if fault == "expired" else timezone.now()
    with pytest.raises(DENIED):
        selectors().assigned_verification_detail(
            staff.actor,
            s.case.id,
            staff.step,
            "" if fault == "reason" else "verification_review",
            at,
        )


def test_start_review_requires_assignment_and_preserves_snapshots(settings):
    s = submitted()
    staff = reviewer(settings, s.case.id)
    case = assign(s, staff)
    dto = command(
        "start_verification_review",
        staff.actor,
        s.case.id,
        case.version,
        staff.step,
        "verification_review",
        timezone.now(),
    )
    assert dto.state == "under_review"
    assert {t.state for t in dto.targets} == {"under_review"}


def test_queue_minimal_and_bounded(settings):
    s = submitted()
    staff = reviewer(settings, None)
    queue = selectors().submitted_verification_queue(
        staff.actor, staff.step, "verification_review", None, timezone.now()
    )
    assert len(queue.items) == 1 and len(queue.items) <= 25
    assert set(queue.items[0].__dataclass_fields__) == {
        "id",
        "state",
        "submitted_at",
        "requested_targets",
    }
    with pytest.raises(DENIED):
        selectors().assigned_verification_detail(
            staff.actor, s.case.id, staff.step, "verification_review", timezone.now()
        )


def test_audit_failure_prevents_evidence_read(settings, monkeypatch):
    s = submitted()
    staff = reviewer(settings, s.case.id)
    assign(s, staff)
    calls = []

    def fail(*args, **kwargs):
        raise RuntimeError("Injected audit failure")

    monkeypatch.setattr("apps.governance.audit.append_event", fail)
    from apps.assets.storage import FakePrivateStore

    monkeypatch.setattr(FakePrivateStore, "read_limited", lambda *args: calls.append(1))
    with pytest.raises(RuntimeError):
        selectors().assigned_verification_evidence(
            staff.actor,
            s.case.id,
            s.assets["identity"][0].id,
            staff.step,
            "verification_review",
            timezone.now(),
        )
    assert calls == []
    assert Verification.objects.get(pk=s.case.id).state == "submitted"
