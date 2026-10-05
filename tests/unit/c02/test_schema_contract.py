import pytest
from django.apps import apps
from django.conf import settings
from django.db import models

pytestmark = pytest.mark.unit

USER_FIELDS = {
    "birth_date",
    "adult_attested_at",
    "adult_attestation_version",
    "locale",
    "timezone",
    "state",
    "state_version",
    "auth_version",
}
SECURITY_MODELS = {
    "OTPPhoneState",
    "SecurityRateAnchor",
    "SecurityRateEvent",
    "OTPChallenge",
    "AccountSessionControl",
}


def test_additive_identity_contract():
    assert settings.AUTH_USER_MODEL == "accounts.User"
    user = apps.get_model("accounts", "User")
    assert USER_FIELDS <= {field.name for field in user._meta.fields}
    assert user._meta.get_field("birth_date").null
    assert user._meta.get_field("adult_attested_at").null
    assert user._meta.get_field("auth_version").default == 1
    assert user._meta.get_field("state_version").default == 1
    assert user._meta.get_field("state").default == "active"
    assert user._meta.get_field("password").default == "!"


def test_registered_security_contracts():
    registered = {
        model.__name__ for model in apps.get_app_config("accounts").get_models()
    }
    assert SECURITY_MODELS <= registered
    assert registered == SECURITY_MODELS | {
        "User",
        "RecoveryRequest",
        "RecoveryEvidenceMetadata",
        "PhoneChangeHistory",
    }
    for name in SECURITY_MODELS:
        model = apps.get_model("accounts", name)
        assert model._meta.constraints, f"{name} has no database constraints"
        assert not {"code", "raw_code", "raw_ip", "session_key"} & {
            field.name for field in model._meta.fields
        }
    for name in ("SecurityRateEvent", "OTPChallenge", "AccountSessionControl"):
        for field in apps.get_model("accounts", name)._meta.fields:
            if isinstance(field, models.ForeignKey):
                assert field.remote_field.on_delete is models.PROTECT
