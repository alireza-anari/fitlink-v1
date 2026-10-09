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
