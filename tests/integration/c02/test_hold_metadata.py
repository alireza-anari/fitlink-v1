import importlib
from datetime import timedelta
from uuid import uuid4

import pytest
from django.apps import apps
from django.db import transaction
from django.utils import timezone
from test_phone_change import actor_for
from test_recovery_authorization import owner

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def contracts():
    assert importlib.util.find_spec("apps.governance.retention"), (
        "missing bounded hold services"
    )
    return importlib.import_module("apps.governance.retention")


def authority(settings, case):
    from dataclasses import replace

    from apps.governance.staff import MockStepUpProvider, issue_mock_step_up
    from apps.governance.staff_models import StaffCapabilityGrant

    settings.ACCOUNT_SECURITY = replace(
        settings.ACCOUNT_SECURITY, step_up_provider="mock"
    )
    user = owner("+989123456780")
    issuer = owner("+989123456781")
    at = timezone.now()
    StaffCapabilityGrant.objects.create(
        user=user,
        capability="privacy_operations",
        valid_from=at,
        valid_until=at + timedelta(hours=1),
        granted_by=issuer,
        reason_code="policy_approved",
    )
    provider = MockStepUpProvider()
    proof = provider.prepare(user.public_id, "privacy_operations", case, at)
    with transaction.atomic():
        step = issue_mock_step_up(
            user, "privacy_operations", case, proof.raw_assertion, issuer, at, provider
        )
    return actor_for(user)[0], step, timezone.now()


def subject():
    from config.use_cases.privacy import request_privacy

    module = contracts()
    user = owner()
    actor, _ = actor_for(user)
    at = timezone.now()
    case = request_privacy(actor, "export", uuid4(), at, confirmed=True)
    return (
        module,
        module.ValidatedRecordSubject("privacy_request", case, user.public_id, 1),
        case,
    )


def test_record_hold_is_bounded_reviewed_expiring_and_never_access_authority(settings):
    module, record, case = subject()
    actor, step, now = authority(settings, case)
    hold = module.apply_hold(
        actor,
        record,
        case,
        "security",
        "hold_applied",
        now + timedelta(minutes=5),
        now + timedelta(hours=1),
        step,
        now,
    )
    assert module.is_record_held(record, now)
    assert module.is_record_held(record, now + timedelta(minutes=5))
    assert not module.is_record_held(record, now + timedelta(hours=1))
    module.release_hold(actor, hold, 1, "hold_released", step, now)
    assert not module.is_record_held(record, now)
    assert (
        apps.get_model("accounts", "User")
        .objects.get(public_id=record.owner_uuid)
        .state
        == "active"
    )


@pytest.mark.parametrize(
    "defect",
    [
        "staff",
        "wrong_case",
        "unknown",
        "wrong_owner",
        "wrong_version",
        "review",
        "expiry",
        "purpose",
    ],
)
def test_hold_denies_unscoped_authority_and_invalid_subjects(settings, defect):
    from dataclasses import replace

    from django.core.exceptions import PermissionDenied

    module, record, case = subject()
    actor, step, now = authority(settings, case)
    if defect == "staff":
        apps.get_model("governance", "StaffCapabilityGrant").objects.all().update(
            revoked_at=now
        )
    if defect == "wrong_case":
        case = uuid4()
    if defect == "unknown":
        record = replace(record, kind="health")
    if defect == "wrong_owner":
        record = replace(record, owner_uuid=uuid4())
    if defect == "wrong_version":
        record = replace(record, version=9)
    with pytest.raises((PermissionError, PermissionDenied, ValueError)):
        module.apply_hold(
            actor,
            record,
            case,
            "blanket" if defect == "purpose" else "security",
            "hold_applied",
            now if defect == "review" else now + timedelta(minutes=5),
            now if defect == "expiry" else now + timedelta(hours=1),
            step,
            now,
        )
    assert not apps.get_model("governance", "RecordHold").objects.exists()


def test_hold_audit_failure_rolls_back(settings, monkeypatch):
    module, record, case = subject()
    actor, step, now = authority(settings, case)

    def fail(*args, **kwargs):
        raise RuntimeError("audit unavailable")

    monkeypatch.setattr(module, "append_event", fail)
    with pytest.raises(RuntimeError):
        module.apply_hold(
            actor,
            record,
            case,
            "security",
            "hold_applied",
            now + timedelta(minutes=5),
            now + timedelta(hours=1),
            step,
            now,
        )
    assert not apps.get_model("governance", "RecordHold").objects.exists()


def test_policy_remains_draft_without_approved_numeric_backup_metadata(settings):
    from django.core.exceptions import PermissionDenied

    module = contracts()
    policy_id = uuid4()
    actor, step, now = authority(settings, policy_id)
    result = module.create_policy(
        actor,
        policy_id,
        "account_metadata",
        "privacy_intake",
        "policy_approved",
        step,
        now,
    )
    row = apps.get_model("governance", "RetentionPolicy").objects.get(pk=result)
    assert (
        row.status == "draft"
        and row.duration_seconds is None
        and row.backup_reference == ""
    )
    with pytest.raises((ValueError, PermissionDenied)):
        module.approve_policy(actor, result, 1, None, "", "policy_approved", step, now)
    module.approve_policy(
        actor, result, 1, 3600, "test-backup-v1", "policy_approved", step, now
    )
    module.activate_policy(actor, result, 2, "policy_approved", step, now)
    row.refresh_from_db()
    assert (
        row.status == "effective" and row.version == 3 and row.duration_seconds == 3600
    )
    with pytest.raises(PermissionDenied):
        module.activate_policy(actor, result, 2, "policy_approved", step, now)


def test_record_hold_does_not_block_unrelated_delete_intake(settings):
    from config.use_cases.privacy import request_privacy

    module, record, case = subject()
    staff, step, now = authority(settings, case)
    module.apply_hold(
        staff,
        record,
        case,
        "security",
        "hold_applied",
        now + timedelta(minutes=5),
        now + timedelta(hours=1),
        step,
        now,
    )
    user = apps.get_model("accounts", "User").objects.get(public_id=record.owner_uuid)
    actor, _ = actor_for(user)
    result = request_privacy(actor, "delete", uuid4(), timezone.now(), confirmed=True)
    user.refresh_from_db()
    assert user.state == "pending_deletion" and result != case
    assert module.is_record_held(record, timezone.now())
