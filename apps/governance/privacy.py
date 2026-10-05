"""Verified owner intake only. Export and erasure execution belong to C18."""

from collections.abc import Callable
from datetime import datetime
from uuid import UUID, uuid4

from django.utils import timezone

from apps.accounts.contracts import OutcomeRecorder, SecurityOutcome
from apps.accounts.models import User
from apps.accounts.sessions import AccountActor, actor_user, locked_actor
from apps.accounts.state import locked_identity

from .consent_models import Consent
from .privacy_models import PrivacyRequest


def require_recent_privacy_auth(actor: AccountActor, at: datetime) -> None:
    if (
        not isinstance(actor, AccountActor)
        or not isinstance(at, datetime)
        or not timezone.is_aware(at)
        or not isinstance(actor.authenticated_at, datetime)
        or not timezone.is_aware(actor.authenticated_at)
        or not 0 <= (at - actor.authenticated_at).total_seconds() <= 600
    ):
        raise PermissionError("Recent authentication required")


def request_privacy(
    actor: AccountActor,
    kind: str,
    request_id: UUID,
    at: datetime,
    record: OutcomeRecorder,
    *,
    confirmed: bool = False,
    restrict: Callable[[User, datetime], None],
) -> UUID:
    if (
        kind not in {"export", "delete"}
        or not isinstance(request_id, UUID)
        or not callable(record)
        or not callable(restrict)
    ):
        raise ValueError("Invalid privacy intake")
    if confirmed is not True:
        raise PermissionError("Explicit confirmation required")
    require_recent_privacy_auth(actor, at)
    # Phone anchor precedes User, preventing inversion with recovery/change/logout.
    with locked_identity(actor.user_uuid, actor.auth_version) as user:
        locked_actor(actor, "privacy.intake", at)
        collision = PrivacyRequest.objects.filter(pk=request_id).first()
        if collision and (collision.user_id != user.pk or collision.kind != kind):
            raise PermissionError("Privacy action denied")
        existing = PrivacyRequest.objects.filter(user=user, kind=kind).first()
        if existing:
            return existing.id
        row = PrivacyRequest.objects.create(
            id=request_id,
            user=user,
            kind=kind,
            status="pending_deletion" if kind == "delete" else "pending_execution",
            created_at=at,
            verified_at=at,
            updated_at=at,
        )
        if kind == "delete":
            restrict(user, at)
            # Serializes with grant/revoke through the already-held subject User.
            for consent in (
                Consent.objects.select_for_update()
                .filter(subject=user, revoked_at__isnull=True)
                .order_by("id")
            ):
                consent.revoked_at = at
                consent.version += 1
                consent.save(update_fields=["revoked_at", "version"])
                record(
                    SecurityOutcome(
                        "consent.revoked",
                        "succeeded",
                        consent.id,
                        uuid4(),
                        ("revoked_at", "version"),
                        "user_requested",
                    )
                )
        record(
            SecurityOutcome(
                "privacy.intake",
                "accepted",
                row.id,
                uuid4(),
                ("status",),
                "user_requested",
            )
        )
        return row.id


def visible_requests(actor: AccountActor, at: datetime):
    user = actor_user(actor, "privacy.status", at)
    return PrivacyRequest.objects.filter(user=user)


def privacy_status(actor: AccountActor, request_uuid: UUID, at: datetime) -> dict:
    row = visible_requests(actor, at).filter(pk=request_uuid).first()
    if not row:
        raise PermissionError("Privacy action denied")
    return {"request_id": row.id, "kind": row.kind, "status": row.status}
