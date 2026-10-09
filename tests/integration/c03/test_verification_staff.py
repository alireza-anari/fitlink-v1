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
    reassigned = command(
        "assign_verification",
        staff.actor,
        s.case.id,
        other.user.public_id,
        dto.version,
        staff.step,
        "case_conflict",
        timezone.now(),
    )
    assert reassigned.identity_name == "" and reassigned.evidence == ()
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
        "logout",
        "owner_inactive",
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
    if fault == "logout":
        from apps.accounts.security_models import AccountSessionControl

        AccountSessionControl.objects.filter(pk=staff.actor.control_id).update(
            revoked_at=timezone.now()
        )
    if fault == "owner_inactive":
        s.user.state, s.user.is_active = "suspended", False
        s.user.save(update_fields=["state", "is_active"])
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


def test_assigned_sanitized_read_audited_source_never_read(settings, monkeypatch):
    from hashlib import sha256

    from apps.assets.contracts import AssetNotFound
    from apps.assets.storage import FakePrivateStore
    from apps.governance.audit_models import AuditEvent

    s = submitted()
    staff = reviewer(settings, s.case.id)
    assign(s, staff)
    asset = s.assets["identity"][0]
    derivative = asset.derivatives.get()
    clean = b"synthetic sanitized derivative"
    derivative.sha256 = sha256(clean).hexdigest()
    derivative.save()
    store = FakePrivateStore()
    store.put(derivative.key, clean, derivative.mime_type)
    reads = []
    original = store.read_limited

    def read(key, limit):
        reads.append(key)
        return original(key, limit)

    monkeypatch.setattr(store, "read_limited", read)
    monkeypatch.setattr("apps.assets.delivery.get_private_store", lambda: store)
    result = selectors().assigned_verification_evidence(
        staff.actor,
        s.case.id,
        asset.id,
        staff.step,
        "verification_review",
        timezone.now(),
    )
    assert result.content == clean and reads == [derivative.key]
    assert AuditEvent.objects.filter(
        action="asset.read", actor_uuid=staff.user.public_id, subject_uuid=asset.id
    ).exists()
    from config.use_cases.profile_assets import authorized_profile_download

    with pytest.raises(AssetNotFound):
        authorized_profile_download(staff.actor, asset.id, "source", timezone.now())
    assert reads == [derivative.key]


def test_queue_cannot_open_production_verification_with_seeded_mfa(settings):
    submitted()
    staff = reviewer(settings, None)
    StaffStepUpGrant.objects.filter(pk=staff.step).update(method="verified_mfa")
    settings.SETTINGS_ENV = "production"
    with pytest.raises(DENIED):
        selectors().submitted_verification_queue(
            staff.actor, staff.step, "verification_review", None, timezone.now()
        )


def test_queue_cursor_returns_at_most_25_without_duplicate_cases(settings):
    from apps.professionals.models import ProfessionalProfile

    s = submitted()
    staff = reviewer(settings, None)
    for i in range(27):
        person = make_actor(f"+98912345{6900 + i:04d}")
        profile = ProfessionalProfile.objects.create(user=person.user)
        Verification.objects.create(
            profile=profile, sequence=1, state="submitted", submitted_at=s.at
        )
    queue = selectors().submitted_verification_queue(
        staff.actor, staff.step, "verification_review", None, timezone.now()
    )
    assert len(queue.items) == 25 and queue.next_cursor is not None
    next_page = selectors().submitted_verification_queue(
        staff.actor,
        staff.step,
        "verification_review",
        queue.next_cursor,
        timezone.now(),
    )
    assert len(next_page.items) == 3 and next_page.next_cursor is None
    assert not {x.id for x in queue.items} & {x.id for x in next_page.items}


def test_self_case_denied_with_real_capability_and_case_stepup(settings):
    from django.db import transaction

    from apps.governance.staff import MockStepUpProvider, issue_mock_step_up
    from apps.governance.staff_models import StaffCapabilityGrant

    s = submitted()
    staff = reviewer(settings, s.case.id)
    StaffCapabilityGrant.objects.create(
        user=s.user,
        granted_by=staff.user,
        capability="professional_verification",
        reason_code="staff_assigned",
        valid_from=s.at,
        valid_until=s.at + timedelta(hours=1),
    )
    provider = MockStepUpProvider()
    assertion = provider.prepare(
        s.user.public_id, "professional_verification", s.case.id, s.at
    )
    with transaction.atomic():
        step = issue_mock_step_up(
            s.user,
            "professional_verification",
            s.case.id,
            assertion.raw_assertion,
            staff.user,
            s.at,
            provider,
        )
    with pytest.raises(DENIED):
        command(
            "assign_verification",
            s.actor,
            s.case.id,
            staff.user.public_id,
            s.case.version,
            step,
            "staff_assigned",
            timezone.now(),
        )
    with pytest.raises(DENIED):
        selectors().assigned_verification_detail(
            s.actor, s.case.id, step, "verification_review", timezone.now()
        )


def test_unbound_evidence_denied_before_storage(settings, monkeypatch):
    from apps.assets.storage import FakePrivateStore

    from .test_credential_revisions import ready

    s = submitted()
    staff = reviewer(settings, s.case.id)
    assign(s, staff)
    asset = ready(s)
    reads = []
    monkeypatch.setattr(FakePrivateStore, "read_limited", lambda *args: reads.append(1))
    with pytest.raises(DENIED):
        selectors().assigned_verification_evidence(
            staff.actor,
            s.case.id,
            asset.id,
            staff.step,
            "verification_review",
            timezone.now(),
        )
    assert reads == []
