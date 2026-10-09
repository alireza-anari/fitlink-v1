import inspect

import pytest

from apps.professionals import contracts, verification
from config.use_cases import professional_verification

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "name",
    [
        "prepare_verification",
        "submit_verification",
        "withdraw_verification_target",
        "assign_verification",
        "start_verification_review",
    ],
)
def test_commands_have_required_governance_callbacks(name):
    assert callable(getattr(verification, name, None)), (
        f"Missing domain contract: {name}"
    )
    parameters = inspect.signature(getattr(verification, name)).parameters
    assert parameters["record"].default is inspect.Parameter.empty
    assert parameters["emit"].default is inspect.Parameter.empty
    assert callable(getattr(professional_verification, name, None))


@pytest.mark.parametrize(
    "name", ["VerificationOwnerDTO", "VerificationStaffDTO", "VerificationQueueDTO"]
)
def test_private_dtos_are_explicit(name):
    assert hasattr(contracts, name), f"Missing private DTO: {name}"
    assert not {"source_key", "signed_url", "phone", "verified_roles"} & set(
        getattr(contracts, name).__dataclass_fields__
    )


def test_verification_submission_uses_finite_account_action():
    from datetime import date

    from django.utils import timezone

    from apps.accounts.models import User
    from apps.accounts.policies import require_account_action

    user = User(
        birth_date=date(1990, 1, 1),
        adult_attested_at=timezone.now(),
        adult_attestation_version="adult-v1",
    )
    require_account_action(user, "professional.verify_submit", "normal")
    with pytest.raises(PermissionError):
        require_account_action(user, "professional.verify_submit", "account_control")
    with pytest.raises(PermissionError):
        require_account_action(user, "professional.verify_override", "normal")
