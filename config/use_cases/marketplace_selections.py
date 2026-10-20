"""Selection composition: current accounts, owned athletes and server DB sessions."""

import hashlib
import hmac
import re
import secrets

from django.conf import settings
from django.contrib.sessions.models import Session
from django.utils import timezone

from apps.accounts.models import User
from apps.accounts.sessions import (
    AccountActor,
    actor_user,
    locked_actor,
    resolve_session,
)
from apps.athletes.selectors import own_athlete_profile
from apps.marketplace import selections
from apps.marketplace.contracts import context
from apps.marketplace.selection_contracts import ComparisonScope
from apps.professionals.models import ProfessionalProfile
from config.use_cases.marketplace import public_professionals


def _digest(key, secret, key_id):
    ring = settings.ACCOUNT_SECURITY.keys
    if key_id not in ring.material:
        raise PermissionError("Comparison unavailable")
    return hmac.new(
        ring.material[key_id],
        b"fitlink:c04:comparison\x00" + key.encode() + b"\x00" + secret.encode(),
        hashlib.sha256,
    ).hexdigest()


def comparison_scope(request, at):
    """No client collection ID/owner ID accepted. Login/logout flush this secret."""
    actor = resolve_session(request, at)
    if actor is not None:
        return ComparisonScope(actor=actor)
    if request.session.get("_auth_user_id") is not None or getattr(
        getattr(request, "user", None), "is_authenticated", False
    ):
        raise PermissionError("Comparison unavailable")
    secret = request.session.get("c04_comparison_secret")
    key_id = request.session.get("c04_comparison_key_id")
    if (
        not isinstance(secret, str)
        or not re.fullmatch(r"[0-9a-f]{64}", secret)
        or key_id not in settings.ACCOUNT_SECURITY.keys.material
    ):
        secret = secrets.token_hex(32)
        key_id = settings.ACCOUNT_SECURITY.keys.active_id
        request.session["c04_comparison_secret"] = secret
        request.session["c04_comparison_key_id"] = key_id
        request.session.save()
    key = request.session.session_key
    if key is None:
        raise PermissionError("Comparison unavailable")
    return ComparisonScope(
        session_key=key, session_digest=_digest(key, secret, key_id), key_id=key_id
    )


def _anchors(actor, identifiers):
    owners = set(
        ProfessionalProfile.objects.filter(pk__in=identifiers).values_list(
            "user_id", flat=True
        )
    )
    if actor is not None:
        owners.update(
            User.objects.filter(public_id=actor.user_uuid).values_list("pk", flat=True)
        )
    tuple(User.objects.select_for_update().filter(pk__in=owners).order_by("pk"))


def authorize_athlete(actor, identifiers, at):
    if not isinstance(actor, AccountActor):
        raise PermissionError("Selection unavailable")
    _anchors(actor, identifiers)
    user = locked_actor(actor, "marketplace.selection", max(at, timezone.now()))
    try:
        own_athlete_profile(actor, max(at, timezone.now()))
    except LookupError:
        raise PermissionError("Selection unavailable") from None
    return user


def authorize_scope(scope, identifiers, at):
    if not isinstance(scope, ComparisonScope):
        raise PermissionError("Comparison unavailable")
    scope.__post_init__()
    if scope.actor is not None:
        return authorize_athlete(scope.actor, identifiers, at)
    _anchors(None, identifiers)
    session = (
        Session.objects.select_for_update()
        .filter(session_key=scope.session_key, expire_date__gt=max(at, timezone.now()))
        .first()
    )
    if session is None:
        raise PermissionError("Comparison unavailable")
    value = session.get_decoded()
    secret = value.get("c04_comparison_secret")
    if (
        "_auth_user_id" in value
        or value.get("c04_comparison_key_id") != scope.key_id
        or not isinstance(secret, str)
        or not re.fullmatch(r"[0-9a-f]{64}", secret)
        or not hmac.compare_digest(
            _digest(scope.session_key, secret, scope.key_id), scope.session_digest
        )
    ):
        raise PermissionError("Comparison unavailable")
    return None


def set_favorite(actor, identifier, selected, operation, at):
    return selections.set_favorite(
        actor,
        identifier,
        selected,
        operation,
        at,
        authorize=authorize_athlete,
        current=public_professionals,
    )


def list_favorites(actor, at, *, release=None):
    if not isinstance(actor, AccountActor):
        raise PermissionError("Selection unavailable")
    context(actor.user_uuid, at)
    # Reject forged/revoked actors before even inspecting private hint counts.
    # This preflight grants nothing: the domain still locks all owners in sorted
    # order and repeats current actor/athlete authorization inside its transaction.
    actor_user(actor, "marketplace.selection", max(at, timezone.now()))
    return selections.list_favorites(
        actor,
        at,
        authorize=authorize_athlete,
        current=public_professionals,
        release=release,
    )


def read_comparison(scope, at, *, release=None):
    return selections.read_comparison(
        scope,
        at,
        authorize=authorize_scope,
        current=public_professionals,
        release=release,
    )


def change_comparison(scope, command, identifier, version, operation, at):
    from apps.governance.flags import feature_enabled

    return selections.change_comparison(
        scope,
        command,
        identifier,
        version,
        operation,
        at,
        authorize=authorize_scope,
        current=public_professionals,
        enabled=lambda: feature_enabled("marketplace", raise_unavailable=True),
    )
