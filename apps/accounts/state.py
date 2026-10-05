"""Owned state transitions and synchronous authentication invalidation."""

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
from uuid import UUID, uuid4

from django.db import transaction
from django.db.models import F, Q

from .contracts import OutcomeRecorder, SecurityOutcome
from .models import User
from .security_models import AccountSessionControl, OTPChallenge, OTPPhoneState


class _MappingChanged(RuntimeError):
    pass


@contextmanager
def locked_identity(
    user_uuid: UUID, expected_version: int | None = None
) -> Iterator[User]:
    """Savepoint rollback releases a changed mapping before bounded retry."""
    for _ in range(3):
        candidate = (
            User.objects.filter(public_id=user_uuid).values("pk", "phone").first()
        )
        if not candidate:
            raise PermissionError("Account unavailable")
        try:
            with transaction.atomic():
                anchor, _ = OTPPhoneState.objects.get_or_create(
                    phone=candidate["phone"]
                )
                OTPPhoneState.objects.select_for_update().get(pk=anchor.pk)
                user = User.objects.select_for_update().get(pk=candidate["pk"])
                if user.phone != candidate["phone"]:
                    raise _MappingChanged()
                if (
                    expected_version is not None
                    and user.auth_version != expected_version
                ):
                    raise PermissionError("Account unavailable")
                yield user
                return
        except _MappingChanged:
            continue
    raise PermissionError("Account unavailable")


def invalidate_auth_locked(user: User, at: datetime) -> None:
    """Caller holds canonical phone then User; all effects remain synchronous."""
    if not transaction.get_connection().in_atomic_block:
        raise RuntimeError("Authentication invalidation requires transaction")
    user.auth_version += 1
    user.save(update_fields=["auth_version"])
    OTPChallenge.objects.filter(
        Q(target_user=user) | Q(phone_state__phone=user.phone), retired_at__isnull=True
    ).update(retired_at=at)
    OTPPhoneState.objects.filter(phone=user.phone).update(
        generation=F("generation") + 1
    )
    list(
        AccountSessionControl.objects.select_for_update()
        .filter(user=user)
        .order_by("id")
    )
    AccountSessionControl.objects.filter(user=user, revoked_at__isnull=True).update(
        revoked_at=at
    )


def transition_account_state(
    user_uuid: UUID,
    expected_auth_version: int,
    state: str,
    at: datetime,
    record: OutcomeRecorder,
) -> None:
    # Internal server-owned command; no generic state-edit route or staff bypass.
    if state not in {
        "restricted",
        "suspended",
        "deletion_requested",
        "pending_deletion",
    }:
        raise ValueError("Unsupported account transition")
    if not callable(record) or at.tzinfo is None or at.utcoffset() is None:
        raise ValueError("Required state transition contract")
    with locked_identity(user_uuid, expected_auth_version) as user:
        if user.state in {"deleted", "anonymized", "deletion_completed"}:
            raise PermissionError("Account unavailable")
        # No transition can reactivate a suspended account.
        if not user.is_active and state != "suspended":
            raise PermissionError("Account unavailable")
        user.state, user.is_active = state, state != "suspended"
        user.state_version += 1
        user.save(update_fields=["state", "is_active", "state_version"])
        invalidate_auth_locked(user, at)
        record(
            SecurityOutcome(
                "account.state_changed",
                "succeeded",
                user.public_id,
                uuid4(),
                ("state", "state_version", "auth_version", "revoked_at"),
                "security_restriction",
            )
        )
