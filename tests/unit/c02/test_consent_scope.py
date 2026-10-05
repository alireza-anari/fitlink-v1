import importlib
import importlib.util
from dataclasses import fields

import pytest

pytestmark = pytest.mark.unit


def test_grant_outbox_is_id_only_and_explicitly_typed():
    from uuid import uuid4

    from apps.governance.outbox import validate_event

    consent_id, user_id = uuid4(), uuid4()
    validate_event(
        "consent.granted",
        consent_id,
        1,
        {"consent_uuid": str(consent_id), "user_uuid": str(user_id)},
        f"consent_granted:{consent_id}:1",
    )


def contract():
    assert importlib.util.find_spec("apps.governance.consents"), (
        "missing purpose-limited validated consent core"
    )
    return importlib.import_module("apps.governance.consents")


def test_scopes_are_typed_server_contracts_without_object_authority():
    module = contract()
    names = {field.name for field in fields(module.ValidatedConsentScope)}
    assert {
        "subject_uuid",
        "grantee_uuid",
        "purpose",
        "kind",
        "object_uuid",
        "object_version",
        "expires_at",
    } <= names
    assert "account_terms" not in module.PURPOSES
    assert not hasattr(module, "can_access_object")


@pytest.mark.parametrize(
    "kind",
    ["health", "photo", "case_study", "archive", "ai_file", "mirror_video", "unknown"],
)
def test_uninstalled_or_excluded_scope_validator_fails_closed(kind):
    module = contract()
    assert kind not in module.SCOPE_VALIDATORS


def test_required_command_and_owner_scoped_selector_contracts():
    module = contract()
    assert all(
        callable(getattr(module, name, None))
        for name in (
            "validate_scope",
            "grant_consent",
            "revoke_consent",
            "has_current_grant",
            "visible_consents",
        )
    )
    from django.apps import apps

    for name in ("Consent", "ConsentScope"):
        assert apps.get_model("governance", name)._meta.constraints
