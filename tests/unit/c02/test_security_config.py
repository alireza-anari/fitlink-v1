import base64
import json
from importlib import import_module

import pytest
from django.core.exceptions import ImproperlyConfigured
from test_environment import boot
from test_settings import production_env

pytestmark = pytest.mark.unit


def config():
    try:
        return import_module("apps.accounts.security_config")
    except ModuleNotFoundError:
        pytest.fail("missing C02 contract: security_config")


def values():
    return {
        "ACCOUNT_SECURITY_KEYS_JSON": json.dumps(
            {"v1": base64.b64encode(bytes(range(32))).decode()}
        ),
        "ACCOUNT_SECURITY_ACTIVE_KEY_ID": "v1",
    }


def test_exact_defaults_and_redacted_key_contract():
    loaded = config().load_security_config(values(), production=False)
    policy = loaded.policy
    assert (
        policy.otp_digits,
        policy.expiry_seconds,
        policy.resend_seconds,
        policy.attempts,
        policy.send_phone,
        policy.send_ip,
        policy.failure_phone,
        policy.failure_ip,
        policy.window_seconds,
    ) == (6, 300, 60, 5, 5, 20, 10, 60, 3600)
    assert loaded.entry_enabled is True
    assert loaded.sms_provider == "mock"
    assert loaded.policy.sms_timeout_seconds == 3
    assert base64.b64encode(bytes(range(32))).decode() not in repr(loaded)
    assert repr(bytes(range(32))) not in repr(loaded)


@pytest.mark.parametrize(
    "key,value",
    [
        ("OTP_EXPIRY_SECONDS", "0"),
        ("OTP_SEND_PHONE_LIMIT", "-1"),
        ("SMS_TIMEOUT_SECONDS", "4"),
        ("OTP_DIGITS", "8"),
        ("ACCOUNT_SECURITY_ACTIVE_KEY_ID", "missing"),
        ("ACCOUNT_SECURITY_KEYS_JSON", "{secret-bad-json"),
        ("ACCOUNT_SECURITY_KEYS_JSON", '{"v1":"short"}'),
        ("ACCOUNT_SECURITY_KEYS_JSON", '{"v1":"AAAA", "v1":"AAAA"}'),
        ("TRUSTED_PROXY_CIDRS", "0.0.0.0/0"),
    ],
)
def test_invalid_config_is_value_safe(key, value):
    supplied = {**values(), key: value}
    with pytest.raises(ImproperlyConfigured) as caught:
        config().load_security_config(supplied, production=False)
    assert key in str(caught.value)
    assert value not in str(caught.value)


def test_domain_and_key_separation():
    loaded = config().load_security_config(values(), production=False)
    keys = import_module("apps.accounts.security_keys")
    a = keys.security_digest("otp", "sample", "v1", ring=loaded.keys)
    assert a == keys.security_digest("otp", "sample", "v1", ring=loaded.keys)
    assert a != keys.security_digest("phone", "sample", "v1", ring=loaded.keys)
    assert a != keys.security_digest("otp", "different", "v1", ring=loaded.keys)
    with pytest.raises(ValueError):
        keys.security_digest("otp", "sample", "missing", ring=loaded.keys)


def test_production_disabled_by_default_and_no_vendor():
    loaded = config().load_security_config(values(), production=True)
    assert not loaded.entry_enabled and not loaded.staff_recovery_enabled
    assert loaded.sms_provider == "disabled"
    for key, value in [
        ("SMS_PROVIDER", "mock"),
        ("SMS_PROVIDER", "unknown"),
        ("AUTH_ENTRY_ENABLED", "true"),
        ("STAFF_RECOVERY_ENABLED", "true"),
        ("OTP_CODE_GENERATOR", "fake"),
        ("STAFF_STEP_UP_PROVIDER", "fake"),
    ]:
        with pytest.raises(ImproperlyConfigured):
            config().load_security_config({**values(), key: value}, production=True)


def test_production_settings_reject_missing_security_keys():
    supplied = production_env()
    supplied.pop("ACCOUNT_SECURITY_KEYS_JSON")
    supplied.pop("ACCOUNT_SECURITY_ACTIVE_KEY_ID")
    result = boot("config.settings.production", supplied)
    assert result.returncode != 0
    assert "ACCOUNT_SECURITY_KEYS_JSON" in result.stderr


def test_production_boot_with_disabled_auth_and_keys():
    result = boot("config.settings.production", {**production_env(), **values()})
    assert result.returncode == 0, result.stderr
