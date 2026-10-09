"""Internal Task 8 contract; declarations never authorize publication."""

import importlib
from dataclasses import fields, is_dataclass

import pytest

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "name",
    [
        "decide_verification_target",
        "revoke_verification_target",
        "restrict_professional_role",
        "release_professional_role_restriction",
    ],
)
def test_explicit_task8_command_contract(name):
    module = importlib.import_module("config.use_cases.professional_verification")
    assert callable(getattr(module, name, None)), f"Missing Task 8 command: {name}"


def test_typed_internal_eligibility_contract():
    module = importlib.import_module("apps.professionals.selectors")
    assert callable(getattr(module, "publication_eligibility", None)), (
        "Missing internal eligibility"
    )
    assert is_dataclass(getattr(module, "PublicationEligibility", None))
    assert {
        "identity_verified",
        "verified_roles",
        "eligible",
        "reason_codes",
        "blocked_roles",
        "evaluated_at",
        "evidence_binding",
    } <= {f.name for f in fields(module.PublicationEligibility)}


def test_typed_assigned_review_binding():
    module = importlib.import_module("apps.professionals.verification_selectors")
    assert callable(getattr(module, "assigned_target_review_binding", None)), (
        "Missing assigned binding reader"
    )
    assert is_dataclass(getattr(module, "TargetReviewBinding", None))
    assert {
        "evidence_revision",
        "decision_version",
        "declaration_version",
        "snapshot_hash",
        "restriction_token",
    } <= {f.name for f in fields(module.TargetReviewBinding)}
