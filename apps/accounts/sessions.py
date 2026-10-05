"""Database sessions backed by current identity and durable version controls."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Literal
from uuid import UUID, uuid4

from django.conf import settings
from django.contrib.auth import login
from django.db import transaction
from django.db.models import Q
from django.http import HttpRequest
from django.utils.crypto import constant_time_compare

from .contracts import OutcomeRecorder, SecurityOutcome, SessionScope
from .models import User
from .policies import require_account_action
from .security_keys import security_digest
from .security_models import AccountSessionControl
from .state import invalidate_auth_locked, locked_identity


@dataclass(frozen=True)
class AccountActor:
    user_uuid: UUID
    auth_version: int
    scope: SessionScope
    control_id: UUID
    authenticated_at: datetime


def session_scope(user: User) -> SessionScope:
    return (
        SessionScope.NORMAL if user.state == "active" else SessionScope.ACCOUNT_CONTROL
    )


def issue_session(
    request: HttpRequest, user: User, scope: str, at: datetime, record: OutcomeRecorder
) -> None:
    if not transaction.get_connection().in_atomic_block or not callable(record):
        raise RuntimeError("Session issue requires domain transaction and audit")
    # Re-read/lock even when caller already holds User; never trust stale object.
    current = User.objects.select_for_update().get(pk=user.pk)
    if current.auth_version != user.auth_version:
        raise PermissionError("Account action denied")
    require_account_action(current, "account.self", scope)
    seconds = int(settings.SESSION_COOKIE_AGE)
    if scope == SessionScope.ACCOUNT_CONTROL:
        seconds = min(seconds, settings.ACCOUNT_SECURITY.policy.recent_auth_seconds)
    old_key = request.session.session_key
    if old_key:
        old_identifiers = Q(pk__isnull=True)
        for old_id in settings.ACCOUNT_SECURITY.keys.key_ids:
            old_identifiers |= Q(
                key_id=old_id,
                session_digest=security_digest("session", old_key, old_id),
            )
        old_controls = (
            AccountSessionControl.objects.select_for_update()
            .filter(old_identifiers, revoked_at__isnull=True)
            .order_by("id")
        )
        for old_control in old_controls:
            old_control.revoked_at = at
            old_control.save(update_fields=["revoked_at"])
    # Django login intentionally retains a matching authenticated key. Flush
    # explicitly so every successful possession proof receives a fresh key.
    request.session.flush()
    request.session.set_expiry(seconds)
    login(request, current, backend="django.contrib.auth.backends.ModelBackend")
    request.session["fitlink_auth_version"] = current.auth_version
    request.session["fitlink_scope"] = str(scope)
    request.session.save()
    raw_key = request.session.session_key
    if not raw_key:
        raise RuntimeError("Session issue unavailable")
    key_id = settings.ACCOUNT_SECURITY.keys.active_id
    AccountSessionControl.objects.create(
        user=current,
        key_id=key_id,
        session_digest=security_digest("session", raw_key, key_id),
        auth_version=current.auth_version,
        scope=str(scope),
        authenticated_at=at,
        created_at=at,
        expires_at=at + timedelta(seconds=seconds),
    )
    record(
        SecurityOutcome(
            "account.login",
            "succeeded",
            current.public_id,
            uuid4(),
            reason_code="identity_verified",
        )
    )


def resolve_session(request: HttpRequest, at: datetime) -> AccountActor | None:
    raw_key = request.session.session_key
    user_id = request.session.get("_auth_user_id")
    version = request.session.get("fitlink_auth_version")
    scope = request.session.get("fitlink_scope")
    if (
        not raw_key
        or not isinstance(user_id, str)
        or not user_id.isascii()
        or not user_id.isdecimal()
        or len(user_id) > 20
        or type(version) is not int
        or version < 1
        or scope not in {"normal", "account_control"}
        or request.session.get("_auth_user_backend")
        != "django.contrib.auth.backends.ModelBackend"
    ):
        return None
    user = User.objects.filter(pk=int(user_id), auth_version=version).first()
    if not user:
        return None
    session_hash = request.session.get("_auth_user_hash", "")
    if not isinstance(session_hash, str) or not constant_time_compare(
        session_hash, user.get_session_auth_hash()
    ):
        return None
    try:
        require_account_action(user, "account.self", scope)
    except PermissionError:
        return None
    keys = Q(pk__isnull=True)
    for key_id in settings.ACCOUNT_SECURITY.keys.key_ids:
        keys |= Q(
            key_id=key_id, session_digest=security_digest("session", raw_key, key_id)
        )
    control = AccountSessionControl.objects.filter(
        keys,
        user=user,
        auth_version=version,
        scope=scope,
        revoked_at__isnull=True,
        expires_at__gt=at,
        authenticated_at__lte=at,
    ).first()
    if not control:
        return None
    return AccountActor(
        user.public_id,
        version,
        SessionScope(scope),
        control.id,
        control.authenticated_at,
    )


def actor_user(
    actor: AccountActor, action: str, at: datetime, *, lock: bool = False
) -> User:
    query = User.objects.select_for_update() if lock else User.objects.all()
    user = query.filter(
        public_id=actor.user_uuid, auth_version=actor.auth_version
    ).first()
    if not user:
        raise PermissionError("Account action denied")
    require_account_action(user, action, actor.scope)
    if not AccountSessionControl.objects.filter(
        pk=actor.control_id,
        user=user,
        auth_version=actor.auth_version,
        scope=actor.scope,
        revoked_at__isnull=True,
        expires_at__gt=at,
        authenticated_at=actor.authenticated_at,
    ).exists():
        raise PermissionError("Account action denied")
    return user


def locked_actor(actor: AccountActor, action: str, at: datetime) -> User:
    if not transaction.get_connection().in_atomic_block:
        raise RuntimeError("Mutation authority requires transaction")
    return actor_user(actor, action, at, lock=True)


def revoke_sessions(
    user: User,
    scope: Literal["current", "all"],
    at: datetime,
    record: OutcomeRecorder,
    *,
    control_id: UUID | None = None,
) -> None:
    if scope not in {"current", "all"} or not callable(record):
        raise ValueError("Invalid revocation contract")
    with locked_identity(user.public_id, user.auth_version) as current:
        if scope == "all":
            invalidate_auth_locked(current, at)
        else:
            if control_id is None:
                raise PermissionError("Account action denied")
            control = (
                AccountSessionControl.objects.select_for_update()
                .filter(
                    pk=control_id,
                    user=current,
                    auth_version=current.auth_version,
                    revoked_at__isnull=True,
                )
                .first()
            )
            if not control:
                raise PermissionError("Account action denied")
            control.revoked_at = at
            control.save(update_fields=["revoked_at"])
        record(
            SecurityOutcome(
                "account.logout_all" if scope == "all" else "account.logout",
                "succeeded",
                current.public_id,
                uuid4(),
                ("auth_version", "revoked_at") if scope == "all" else ("revoked_at",),
                "user_requested",
            )
        )
