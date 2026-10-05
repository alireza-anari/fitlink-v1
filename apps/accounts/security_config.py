"""Fail-closed account configuration; no production adapter is installed."""

from collections.abc import Mapping
from dataclasses import dataclass, field, fields

from django.core.exceptions import ImproperlyConfigured

from .client_ip import trusted_networks
from .contracts import AccountSecurityPolicy
from .security_keys import SecurityKeyRing, parse_key_ring


@dataclass(frozen=True)
class AccountSecurityConfig:
    policy: AccountSecurityPolicy
    keys: SecurityKeyRing = field(repr=False)
    entry_enabled: bool
    staff_recovery_enabled: bool
    sms_provider: str
    trusted_proxy_cidrs: tuple[str, ...]
    step_up_provider: str


def _invalid(name: str):
    raise ImproperlyConfigured("Invalid " + name)


def _boolean(values: Mapping[str, str], name: str, default: bool) -> bool:
    raw = values.get(name)
    if raw is None:
        return default
    if raw.lower() not in {"true", "false", "1", "0"}:
        _invalid(name)
    return raw.lower() in {"true", "1"}


_POLICY_KEYS = {
    "otp_digits": ("OTP_DIGITS", 6, 6),
    "expiry_seconds": ("OTP_EXPIRY_SECONDS", 1, 300),
    "resend_seconds": ("OTP_RESEND_SECONDS", 1, 3600),
    "attempts": ("OTP_MAX_ATTEMPTS", 1, 5),
    "window_seconds": ("OTP_WINDOW_SECONDS", 3600, 3600),
    "send_phone": ("OTP_SEND_PHONE_LIMIT", 1, 100),
    "send_ip": ("OTP_SEND_IP_LIMIT", 1, 1000),
    "failure_phone": ("OTP_FAILURE_PHONE_LIMIT", 1, 100),
    "failure_ip": ("OTP_FAILURE_IP_LIMIT", 1, 1000),
    "recovery_phone": ("RECOVERY_INTAKE_PHONE_LIMIT", 1, 100),
    "recovery_ip": ("RECOVERY_INTAKE_IP_LIMIT", 1, 1000),
    "sms_timeout_seconds": ("SMS_TIMEOUT_SECONDS", 1, 3),
    "recent_auth_seconds": ("ACCOUNT_RECENT_AUTH_SECONDS", 1, 600),
    "recovery_receipt_seconds": ("RECOVERY_RECEIPT_SECONDS", 1, 604800),
    "outbox_scan_seconds": ("OUTBOX_SCAN_SECONDS", 1, 300),
    "outbox_batch": ("OUTBOX_BATCH", 1, 100),
    "outbox_lease_seconds": ("OUTBOX_LEASE_SECONDS", 1, 600),
    "outbox_max_attempts": ("OUTBOX_MAX_ATTEMPTS", 1, 8),
    "outbox_backoff_seconds": ("OUTBOX_BACKOFF_SECONDS", 1, 300),
}


def load_security_config(
    values: Mapping[str, str], *, production: bool
) -> AccountSecurityConfig:
    defaults = AccountSecurityPolicy()
    policy = {}
    for item in fields(defaults):
        name, minimum, maximum = _POLICY_KEYS[item.name]
        raw = values.get(name)
        if raw is None:
            value = getattr(defaults, item.name)
        else:
            try:
                if not raw.isascii() or not raw.isdecimal():
                    raise ValueError
                value = int(raw)
            except (ValueError, TypeError):
                _invalid(name)
            if not minimum <= value <= maximum:
                _invalid(name)
        policy[item.name] = value
    raw_keys = values.get("ACCOUNT_SECURITY_KEYS_JSON")
    active = values.get("ACCOUNT_SECURITY_ACTIVE_KEY_ID", "")
    if raw_keys is None:
        if production:
            _invalid("ACCOUNT_SECURITY_KEYS_JSON")
        # Explicit public, non-production fixture. Never used by production.
        raw_keys = '{"development":"AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8="}'
        active = "development"
    keys = parse_key_ring(raw_keys, active)
    provider = values.get("SMS_PROVIDER", "disabled" if production else "mock")
    step_up = values.get("STAFF_STEP_UP_PROVIDER", "disabled")
    entry = _boolean(values, "AUTH_ENTRY_ENABLED", not production)
    recovery = _boolean(values, "STAFF_RECOVERY_ENABLED", False)
    if provider not in ({"disabled"} if production else {"mock", "disabled"}):
        _invalid("SMS_PROVIDER")
    if step_up not in ({"disabled"} if production else {"disabled", "mock"}):
        _invalid("STAFF_STEP_UP_PROVIDER")
    if values.get("OTP_CODE_GENERATOR", "secrets") != "secrets":
        _invalid("OTP_CODE_GENERATOR")
    if entry and provider == "disabled":
        _invalid("AUTH_ENTRY_ENABLED")
    if recovery and step_up == "disabled":
        _invalid("STAFF_RECOVERY_ENABLED")
    raw_cidrs = values.get("TRUSTED_PROXY_CIDRS", "")
    cidrs = tuple(raw_cidrs.split(",")) if raw_cidrs else ()
    try:
        if len(cidrs) > 10 or len(raw_cidrs) > 512:
            raise ValueError
        trusted_networks(cidrs)
    except ValueError:
        _invalid("TRUSTED_PROXY_CIDRS")
    return AccountSecurityConfig(
        AccountSecurityPolicy(**policy), keys, entry, recovery, provider, cidrs, step_up
    )
