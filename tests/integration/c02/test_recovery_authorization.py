import importlib
import importlib.util
from dataclasses import replace
from datetime import date, timedelta
from uuid import uuid4

import pytest
from django.apps import apps
from django.db import transaction
from django.utils import timezone
from test_otp_issue import record
from test_sessions import request_with_session

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]
OLD, NEW = "+989123456789", "+989123456780"


def contract(settings):
    assert importlib.util.find_spec("apps.accounts.recovery"), (
        "missing audited manual recovery"
    )
    settings.ACCOUNT_SECURITY = replace(
        settings.ACCOUNT_SECURITY, staff_recovery_enabled=True, step_up_provider="mock"
    )
    return importlib.import_module("apps.accounts.recovery"), importlib.import_module(
        "config.use_cases.recovery"
    )


def owner(phone=OLD, state="active", active=True):
    return apps.get_model("accounts", "User").objects.create_user(
        phone,
        state=state,
        is_active=active,
        birth_date=date(1990, 1, 1),
        adult_attested_at=timezone.now(),
        adult_attestation_version="adult-v1",
    )


def staff_setup(case_id, phone="+989123456788"):
    from apps.accounts.sessions import issue_session, resolve_session
    from apps.governance.staff import MockStepUpProvider, issue_mock_step_up

    staff = apps.get_model("accounts", "User").objects.filter(
        phone=phone
    ).first() or owner(phone)
    issuer = apps.get_model("accounts", "User").objects.filter(
        phone="+989123456787"
    ).first() or owner("+989123456787")
    now = timezone.now()
    grant = apps.get_model("governance", "StaffCapabilityGrant").objects.filter(
        user=staff, capability="account_recovery"
    ).first() or apps.get_model("governance", "StaffCapabilityGrant").objects.create(
        user=staff,
        capability="account_recovery",
        valid_from=now - timedelta(seconds=1),
        valid_until=now + timedelta(hours=1),
        granted_by=issuer,
        reason_code="staff_assigned",
    )
    request = request_with_session()
    provider = MockStepUpProvider()
    assertion = provider.prepare(staff.public_id, "account_recovery", case_id, now)
    with transaction.atomic():
        issue_session(request, staff, "normal", now, record)
        step = issue_mock_step_up(
            staff,
            "account_recovery",
            case_id,
            assertion.raw_assertion,
            issuer,
            now,
            provider,
        )
    return resolve_session(request, now), staff, grant, step


def prepared(settings, old=OLD, new=NEW):
    recovery, commands = contract(settings)
    receipt = recovery.open_recovery(old, new, "127.0.0.1", timezone.now(), record)
    actor, staff, grant, step = staff_setup(receipt.request_uuid)
    case = apps.get_model("accounts", "RecoveryRequest").objects.get(
        pk=receipt.request_uuid
    )
    commands.assign_recovery(
        actor,
        case.id,
        case.version,
        staff.public_id,
        step,
        "staff_assigned",
        timezone.now(),
    )
    case.refresh_from_db()
    return recovery, commands, receipt, actor, staff, grant, step, case


def test_unknown_existing_receipt_has_same_shape_and_no_resolution(limiter, settings):
    recovery, _ = contract(settings)
    owner()
    receipts = [
        recovery.open_recovery(old, new, "127.0.0.1", timezone.now(), record)
        for old, new in [(OLD, NEW), ("+989123456786", "+989123456781")]
    ]
    assert all(
        recovery.recovery_status(value.request_uuid, value.raw_receipt, timezone.now())
        == "received"
        for value in receipts
    )
    assert (
        apps.get_model("accounts", "RecoveryRequest")
        .objects.filter(target_user__isnull=False)
        .count()
        == 0
    )
    for value in receipts:
        row = apps.get_model("accounts", "RecoveryRequest").objects.get(
            pk=value.request_uuid
        )
        assert value.raw_receipt not in repr(
            row.__dict__
        ) and value.raw_receipt not in repr(value)
    assert apps.get_model("accounts", "User").objects.count() == 1


@pytest.mark.parametrize("defect", ["missing", "foreign", "expired", "uuid_only"])
def test_receipt_capability_is_required(limiter, settings, defect):
    recovery, _ = contract(settings)
    value = recovery.open_recovery(OLD, NEW, "127.0.0.1", timezone.now(), record)
    row = apps.get_model("accounts", "RecoveryRequest").objects.get(
        pk=value.request_uuid
    )
    raw, case = value.raw_receipt, value.request_uuid
    if defect == "expired":
        at = row.receipt_expires_at
    else:
        at = timezone.now()
    if defect in {"missing", "uuid_only"}:
        raw = ""
    if defect == "foreign":
        case = uuid4()
    with pytest.raises(recovery.RecoveryNotFound):
        recovery.recovery_status(case, raw, at)


@pytest.mark.parametrize(
    "defect",
    [
        "bare_superuser",
        "missing_assignment",
        "forged_step",
        "expired_step",
        "wrong_user",
        "self_target",
        "unresolved_evidence",
    ],
)
def test_staff_decision_requires_every_authority(limiter, settings, defect):
    target = owner()
    recovery, commands, receipt, actor, staff, grant, step, case = prepared(settings)
    if defect == "bare_superuser":
        staff.is_staff = staff.is_superuser = True
        staff.save()
        grant.delete()
    elif defect == "missing_assignment":
        type(case).objects.filter(pk=case.pk).update(assigned_staff=None)
    elif defect == "forged_step":
        step = uuid4()
    elif defect == "expired_step":
        apps.get_model("governance", "StaffStepUpGrant").objects.filter(pk=step).update(
            verified_at=timezone.now() - timedelta(minutes=2),
            expires_at=timezone.now() - timedelta(seconds=1),
        )
    elif defect == "wrong_user":
        apps.get_model("governance", "StaffStepUpGrant").objects.filter(pk=step).update(
            user=target
        )
    elif defect == "self_target":
        type(case).objects.filter(pk=case.pk).update(claimed_old_phone=staff.phone)
    with pytest.raises(PermissionError):
        commands.decide_recovery(
            actor,
            case.id,
            case.version,
            "approved",
            "identity_verified",
            step,
            timezone.now(),
        )
    case.refresh_from_db()
    assert case.state == "received"


def test_production_recovery_remains_closed(limiter, settings):
    recovery, _ = contract(settings)
    settings.SETTINGS_ENV = "production"
    with pytest.raises(recovery.RecoveryUnavailable):
        recovery.open_recovery(OLD, NEW, "127.0.0.1", timezone.now(), record)


@pytest.mark.parametrize("existing", [True, False])
def test_rejected_case_exposes_only_closed_status(limiter, settings, existing):
    if existing:
        owner()
    recovery, commands, receipt, actor, staff, grant, step, case = prepared(settings)
    commands.add_recovery_evidence(
        actor,
        case.id,
        case.version,
        "ownership_review",
        "rejected",
        "a" * 64,
        uuid4(),
        step,
        "permission_denied",
        timezone.now(),
    )
    case.refresh_from_db()
    commands.decide_recovery(
        actor,
        case.id,
        case.version,
        "rejected",
        "permission_denied",
        step,
        timezone.now(),
    )
    assert (
        recovery.recovery_status(case.id, receipt.raw_receipt, timezone.now())
        == "closed"
    )
    with pytest.raises(recovery.RecoveryNotFound):
        commands.request_recovery_otp(
            case.id, receipt.raw_receipt, "127.0.0.1", timezone.now()
        )
