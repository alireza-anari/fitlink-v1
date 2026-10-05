import pytest
from django.apps import apps
from django.conf import settings
from django.urls import get_resolver

pytestmark = pytest.mark.unit


def test_only_foundation_routes_and_identity_model():
    assert {str(route.pattern) for route in get_resolver().url_patterns} == {
        "",
        "health/live/",
        "health/ready/",
        "api/v1/status/",
    }
    assert settings.AUTH_USER_MODEL == "accounts.User"
    assert "django.contrib.admin" not in settings.INSTALLED_APPS
    own_models = {
        model.__name__
        for model in apps.get_models()
        if model.__module__.startswith("apps.")
    }
    # Precisely the authorized additive C02 security tables, no future profiles.
    assert own_models == {
        "User",
        "OTPPhoneState",
        "SecurityRateAnchor",
        "SecurityRateEvent",
        "OTPChallenge",
        "AccountSessionControl",
    }
    user = apps.get_model("accounts", "User")
    assert {field.name for field in user._meta.get_fields()} == {
        "id",
        "password",
        "last_login",
        "is_superuser",
        "groups",
        "user_permissions",
        "public_id",
        "phone",
        "is_active",
        "is_staff",
        "date_joined",
        "birth_date",
        "adult_attested_at",
        "adult_attestation_version",
        "locale",
        "timezone",
        "state",
        "state_version",
        "auth_version",
        "otpchallenge",
        "accountsessioncontrol",
    }
