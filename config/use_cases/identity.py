"""Explicit provider and synchronous audit wiring for public identity commands."""

from datetime import date, datetime
from uuid import UUID

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.db import SessionStore
from django.db import IntegrityError, transaction
from django.http import HttpRequest
from django.utils import timezone

from apps.accounts import otp, phone_change
from apps.accounts.contracts import (
    IdentityChangeResult,
    OtpProofResult,
    OtpRequestResult,
    SecurityOutcome,
)
from apps.accounts.security_models import LOGIN_CONTEXT
from apps.accounts.sessions import AccountActor, issue_session, session_scope
from apps.accounts.sms import SmsProvider, configured_provider
from apps.governance.audit import append_event
from apps.governance.outbox import append_outbox


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


def verify_login_otp(
    request: HttpRequest,
    phone: str,
    challenge_id: UUID,
    code: str,
    ip: str,
    *,
    birth_date: date | None = None,
    adult_attested: bool = False,
) -> OtpProofResult:
    if not settings.ACCOUNT_SECURITY.entry_enabled:
        raise otp.OtpUnavailable("Authentication entry unavailable")
    try:
        return otp.verify_otp(
            phone,
            challenge_id,
            code,
            "login",
            LOGIN_CONTEXT,
            ip,
            timezone.now(),
            record_security_outcome,
            birth_date=birth_date,
            adult_attested=adult_attested,
            on_login=lambda user: issue_session(
                request,
                user,
                session_scope(user),
                timezone.now(),
                record_security_outcome,
            ),
        )
    except BaseException:
        # DB rollback does not undo the in-memory session/cookie state. Replace
        # it with a fresh empty store so no authenticated cookie can escape.
        request.session = SessionStore()
        request.user = AnonymousUser()
        raise


def begin_phone_change(actor: AccountActor, new_phone: str, at: datetime) -> UUID:
    return phone_change.begin_phone_change(
        actor,
        new_phone,
        at,
        lambda outcome: record_security_outcome(outcome, actor_uuid=actor.user_uuid),
    )


def _emit_phone_change(result: IdentityChangeResult) -> None:
    append_outbox(
        "account.security_changed",
        result.user_uuid,
        result.auth_version,
        {"user_uuid": str(result.user_uuid)},
        f"phone_change:{result.context_uuid}",
    )


def apply_phone_change(
    actor: AccountActor, change_uuid: UUID, at: datetime
) -> IdentityChangeResult:
    try:
        return phone_change.apply_phone_change(
            actor,
            change_uuid,
            at,
            lambda outcome: record_security_outcome(
                outcome, actor_uuid=actor.user_uuid
            ),
            emit=_emit_phone_change,
        )
    except IntegrityError:
        raise phone_change.PhoneChangeConflict("Phone change conflict") from None


def request_phone_change_otp(
    actor: AccountActor,
    change_uuid: UUID,
    kind: str,
    ip: str,
    at: datetime,
    *,
    provider: SmsProvider | None = None,
) -> OtpRequestResult:
    binding = phone_change.change_binding(actor, change_uuid, kind, at)
    return otp.request_otp(
        binding.phone,
        ip,
        binding.purpose,
        binding.context_uuid,
        at,
        record_security_outcome,
        provider=provider or configured_provider(),
        binding=binding,
        validate_context=lambda value: phone_change.validate_change_binding(
            actor, value, at
        ),
    )


def verify_phone_change_otp(
    actor: AccountActor,
    change_uuid: UUID,
    kind: str,
    challenge_id: UUID,
    code: str,
    ip: str,
    at: datetime,
) -> OtpProofResult:
    binding = phone_change.change_binding(actor, change_uuid, kind, at)
    return otp.verify_otp(
        binding.phone,
        challenge_id,
        code,
        binding.purpose,
        binding.context_uuid,
        ip,
        at,
        record_security_outcome,
        binding=binding,
        validate_context=lambda value: phone_change.validate_change_binding(
            actor, value, at
        ),
        on_proof=lambda proof: phone_change.record_change_proof(
            actor, binding, proof.challenge_id, at
        ),
    )


def own_account(actor: AccountActor, at: datetime) -> dict:
    from apps.accounts.sessions import actor_user

    user = actor_user(actor, "account.self", at)
    return {
        "account_uuid": user.public_id,
        "state": user.state,
        "scope": str(actor.scope),
        "locale": user.locale,
        "timezone": user.timezone,
    }


def update_preferences(actor: AccountActor, values: dict, at: datetime) -> dict:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

    from apps.accounts.sessions import locked_actor

    if set(values) - {"locale", "timezone"}:
        raise ValueError("Invalid preferences")
    if "locale" in values and values["locale"] not in {"fa", "en"}:
        raise ValueError("Invalid preferences")
    if "timezone" in values:
        value = values["timezone"]
        if not isinstance(value, str) or len(value) > 64:
            raise ValueError("Invalid preferences")
        try:
            ZoneInfo(value)
        except (ZoneInfoNotFoundError, ValueError):
            raise ValueError("Invalid preferences") from None
    with transaction.atomic():
        user = locked_actor(actor, "account.self", at)
        for name, value in values.items():
            setattr(user, name, value)
        if values:
            user.save(update_fields=list(values))
        return own_account(actor, at)


def logout_account(
    request: HttpRequest, actor: AccountActor, all_sessions: bool, at: datetime
) -> None:
    from apps.accounts.sessions import locked_actor, revoke_sessions
    from apps.accounts.state import locked_identity

    with locked_identity(actor.user_uuid, actor.auth_version):
        user = locked_actor(
            actor, "account.logout_all" if all_sessions else "account.logout", at
        )
        revoke_sessions(
            user,
            "all" if all_sessions else "current",
            at,
            lambda outcome: record_security_outcome(
                outcome, actor_uuid=actor.user_uuid
            ),
            control_id=actor.control_id,
        )
    request.session.flush()
    request.user = AnonymousUser()


def visible_phone_change(actor: AccountActor, change_uuid: UUID, at: datetime) -> bool:
    from apps.accounts.recovery_models import PhoneChangeIntent
    from apps.accounts.sessions import actor_user

    user = actor_user(actor, "phone_change.apply", at)
    return PhoneChangeIntent.objects.filter(pk=change_uuid, user=user).exists()
