from dataclasses import replace
from datetime import timedelta
from uuid import uuid4

from django.db import transaction
from django.utils import timezone

from apps.governance.staff import MockStepUpProvider, issue_mock_step_up
from apps.governance.staff_models import StaffCapabilityGrant
from config.use_cases import professional_verification as commands

from .profile_helpers import make_actor
from .test_credential_revisions import create, ready
from .test_professional_setup import owner, save


def command(name, *args, **kwargs):
    assert callable(getattr(commands, name, None)), (
        f"Missing verification command: {name}"
    )
    return getattr(commands, name)(*args, **kwargs)


def prepared(targets=("identity", "coach", "nutritionist")):
    s = owner()
    save(
        s,
        "identity",
        {
            "display_name": "Fixture",
            "identity_name": "Private Fixture",
            "roles": ["coach", "nutritionist"],
        },
    )
    save(s, "locations", {"service_modes": ["online"], "languages": ["fa"]})
    save(s, "preview", {})
    s.assets = {}
    for kind in ("identity", "coach", "nutritionist"):
        category = "identity" if kind == "identity" else "qualification"
        asset = ready(s, category)
        dto = create(
            s,
            category=category,
            role=None if kind == "identity" else kind,
            source_asset=asset.id,
        )
        s.assets[kind] = (asset, dto)
    s.profile.refresh_from_db()
    s.case = command(
        "prepare_verification",
        s.actor,
        targets,
        s.profile.version,
        uuid4(),
        timezone.now(),
    )
    s.profile.refresh_from_db()
    return s


def submitted(targets=("identity", "coach", "nutritionist")):
    s = prepared(targets)
    s.case = command(
        "submit_verification",
        s.actor,
        s.case.id,
        s.case.version,
        uuid4(),
        timezone.now(),
    )
    return s


def reviewer(settings, case_id, phone="+989123456781"):
    settings.ACCOUNT_SECURITY = replace(
        settings.ACCOUNT_SECURITY, step_up_provider="mock"
    )
    s = make_actor(phone)
    issuer = make_actor("+989123456782")
    s.grant = StaffCapabilityGrant.objects.create(
        user=s.user,
        capability="professional_verification",
        granted_by=issuer.user,
        reason_code="staff_assigned",
        valid_from=s.at - timedelta(seconds=1),
        valid_until=s.at + timedelta(hours=1),
    )
    provider = MockStepUpProvider()
    assertion = provider.prepare(
        s.user.public_id, "professional_verification", case_id, s.at
    )
    with transaction.atomic():
        s.step = issue_mock_step_up(
            s.user,
            "professional_verification",
            case_id,
            assertion.raw_assertion,
            issuer.user,
            s.at,
            provider,
        )
    return s


def assign(s, staff, version=None):
    return command(
        "assign_verification",
        staff.actor,
        s.case.id,
        staff.user.public_id,
        version or s.case.version,
        staff.step,
        "staff_assigned",
        timezone.now(),
    )


def selectors():
    import importlib.util

    assert importlib.util.find_spec("apps.professionals.verification_selectors"), (
        "Missing assigned selectors"
    )
    from apps.professionals import verification_selectors

    return verification_selectors
