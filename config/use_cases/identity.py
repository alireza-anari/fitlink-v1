"""Explicit provider and synchronous audit wiring for public identity commands."""

from uuid import UUID

from django.conf import settings
from django.utils import timezone

from apps.accounts import otp
from apps.accounts.contracts import OtpRequestResult, SecurityOutcome
from apps.accounts.security_models import LOGIN_CONTEXT
from apps.accounts.sms import configured_provider
from apps.governance.audit import append_event


def record_security_outcome(
    outcome: SecurityOutcome, *, actor_uuid: UUID | None = None
) -> None:
    append_event(outcome, actor_uuid=actor_uuid)


def request_login_otp(phone: str, ip: str) -> OtpRequestResult:
    if not settings.ACCOUNT_SECURITY.entry_enabled:
        raise otp.OtpUnavailable("Authentication entry unavailable")
    return otp.request_otp(
        phone,
        ip,
        "login",
        LOGIN_CONTEXT,
        timezone.now(),
        record_security_outcome,
        provider=configured_provider(),
    )
