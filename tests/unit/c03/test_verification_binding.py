import importlib
import importlib.util

import pytest

pytestmark = pytest.mark.unit


def test_binding_fields_are_exact_and_cosmetics_are_unbound():
    assert importlib.util.find_spec("apps.professionals.validation"), (
        "Binding rules absent"
    )
    rules = importlib.import_module("apps.professionals.validation")
    assert rules.IDENTITY_FIELDS == {"identity_name"}
    assert rules.CREDENTIAL_FIELDS == {
        "category",
        "role",
        "type_code",
        "issuer",
        "title",
        "issued_on",
        "expires_on",
        "source_asset",
    }
    assert not rules.IDENTITY_FIELDS & {
        "display_name",
        "biography",
        "specialties",
        "experience_years",
        "service_modes",
        "languages",
        "locations",
        "avatar",
        "cover",
        "logo",
        "accent_color",
        "welcome_message",
    }


def test_binding_helpers_preserved_without_task8_authority():
    assert importlib.util.find_spec("apps.professionals.verification"), (
        "Binding helpers absent"
    )
    module = importlib.import_module("apps.professionals.verification")
    assert callable(module.target_evidence_changed)
    assert callable(module.target_declaration_changed)
    for name in (
        "decide_verification_target",
        "approve",
        "publication_eligibility",
    ):
        assert not hasattr(module, name)
