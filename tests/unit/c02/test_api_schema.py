import importlib
from uuid import uuid4

import pytest
from rest_framework import serializers

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "name,data",
    [
        ("OtpRequestSerializer", {"phone": "09123456789"}),
        (
            "OtpVerifySerializer",
            {"phone": "09123456789", "challenge_id": str(uuid4()), "code": "123456"},
        ),
        ("AccountPreferencesSerializer", {"locale": "fa", "timezone": "Asia/Tehran"}),
        ("PhoneChangeSerializer", {"new_phone": "09123456789"}),
        (
            "RecoveryRequestSerializer",
            {"old_phone": "09123456789", "new_phone": "09123456780"},
        ),
        (
            "PrivacyRequestSerializer",
            {"kind": "export", "request_id": str(uuid4()), "confirmed": True},
        ),
    ],
)
def test_explicit_schema_rejects_unknown_authority_fields(name, data):
    module = importlib.import_module("apps.accounts.serializers")
    cls = getattr(module, name)
    assert not issubclass(cls, serializers.ModelSerializer)
    assert cls(data=data).is_valid()
    for forbidden in (
        "is_staff",
        "auth_version",
        "user_uuid",
        "receipt",
        "provider",
        "scope",
    ):
        assert not cls(data={**data, forbidden: "injected"}).is_valid()


@pytest.mark.parametrize("extra", [{}, {"confirmed": False}])
def test_privacy_confirmation_defaults_denied(extra):
    module = importlib.import_module("apps.accounts.serializers")
    schema = module.PrivacyRequestSerializer(
        data={"kind": "delete", "request_id": str(uuid4()), **extra}
    )
    assert schema.is_valid()
    assert schema.validated_data["confirmed"] is False


@pytest.mark.parametrize("data", [{"locale": "xx"}, {"timezone": "private/invalid"}])
def test_preferences_are_bounded(data):
    module = importlib.import_module("apps.accounts.serializers")
    assert not module.AccountPreferencesSerializer(data=data).is_valid()
