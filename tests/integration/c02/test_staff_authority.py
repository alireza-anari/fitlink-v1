import importlib
from dataclasses import replace
from datetime import timedelta
from uuid import uuid4

import pytest
from django.apps import apps
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils import timezone

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def contract():
    assert apps.is_installed("apps.governance"), "missing named staff authority"
    return importlib.import_module("apps.governance.staff")


def test_bare_staff_superuser_and_submitted_id_never_authorize(user):
    staff = contract()
    user.is_staff = user.is_superuser = True
    user.save()
    with pytest.raises(PermissionDenied), transaction.atomic():
        staff.require_staff(
            user,
            "account_recovery",
            uuid4(),
            uuid4(),
            "identity_verified",
            timezone.now(),
        )


def test_step_up_is_issued_only_after_server_verification(user, settings):
    staff = contract()
    settings.ACCOUNT_SECURITY = replace(
        settings.ACCOUNT_SECURITY, step_up_provider="mock"
    )
    issuer = apps.get_model("accounts", "User").objects.create_user("+989123456788")
    case, now = uuid4(), timezone.now()
    provider = staff.MockStepUpProvider()
    assertion = provider.prepare(user.public_id, "account_recovery", case, now)
    with pytest.raises(PermissionDenied), transaction.atomic():
        staff.issue_mock_step_up(
            user, "account_recovery", case, str(uuid4()), issuer, now, provider
        )
    assert not apps.get_model("governance", "StaffStepUpGrant").objects.exists()
    with transaction.atomic():
        grant_id = staff.issue_mock_step_up(
            user,
            "account_recovery",
            case,
            assertion.raw_assertion,
            issuer,
            now,
            provider,
        )
    assert (
        apps.get_model("governance", "StaffStepUpGrant")
        .objects.get(pk=grant_id)
        .auth_version
        == user.auth_version
    )
    assert apps.get_model("governance", "AuditEvent").objects.count() == 1
    with pytest.raises(PermissionDenied), transaction.atomic():
        staff.issue_mock_step_up(
            user,
            "account_recovery",
            case,
            assertion.raw_assertion,
            issuer,
            now,
            provider,
        )


@pytest.mark.parametrize(
    "defect",
    [
        "none",
        "self_capability",
        "self_step_up",
        "expired",
        "wrong_user",
        "wrong_capability",
        "wrong_case",
        "old_version",
        "suspended",
        "revoked",
        "missing_reason",
    ],
)
def test_current_named_capability_and_trusted_step_up_required(user, defect):
    staff = contract()
    users = apps.get_model("accounts", "User")
    issuer = users.objects.create_user("+989123456788")
    now, case = timezone.now(), uuid4()
    grant = apps.get_model("governance", "StaffCapabilityGrant").objects.create(
        user=user,
        capability="account_recovery",
        valid_from=now - timedelta(seconds=1),
        valid_until=now + timedelta(hours=1),
        granted_by=issuer,
        reason_code="staff_assigned",
    )
    step = apps.get_model("governance", "StaffStepUpGrant").objects.create(
        user=user,
        auth_version=user.auth_version,
        capability="account_recovery",
        case_uuid=case,
        method="mock",
        provider_reference=uuid4(),
        verified_at=now - timedelta(seconds=1),
        expires_at=now + timedelta(seconds=300),
        trusted_issuer=issuer,
    )
    if defect == "self_capability":
        grant.granted_by = user
    elif defect == "self_step_up":
        step.trusted_issuer = user
    elif defect == "expired":
        step.verified_at, step.expires_at = (
            now - timedelta(hours=1),
            now - timedelta(seconds=1),
        )
    elif defect == "wrong_user":
        step.user = issuer
    elif defect == "wrong_capability":
        step.capability = "security_audit"
    elif defect == "wrong_case":
        step.case_uuid = uuid4()
    elif defect == "old_version":
        user.auth_version += 1
        user.save()
    elif defect == "suspended":
        user.state, user.is_active = "suspended", False
        user.save()
    elif defect == "revoked":
        grant.revoked_at = now
    grant.save()
    step.save()
    with transaction.atomic():
        if defect == "none":
            staff.require_staff(
                user, "account_recovery", case, step.pk, "identity_verified", now
            )
        else:
            with pytest.raises(PermissionDenied):
                staff.require_staff(
                    user,
                    "account_recovery",
                    case,
                    step.pk,
                    "" if defect == "missing_reason" else "identity_verified",
                    now,
                )
