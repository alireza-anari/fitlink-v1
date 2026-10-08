"""Explicit owner profile creation; baseline creation is a separate command."""

from datetime import datetime
from hashlib import sha256
from uuid import UUID

from django.db import transaction

from apps.accounts.contracts import OutcomeRecorder, SecurityOutcome
from apps.accounts.sessions import AccountActor, locked_actor

from .contracts import AthleteProfileDTO, ProfileConflict, ProfileNotFound
from .models import AthleteProfile
from .policies import owned_profile, validate_context
from .receipt_models import ProfileCommandReceipt
from .selectors import own_athlete_profile

CREATE_HASH = sha256(b'{"command":"profile.create"}').hexdigest()


def create_athlete_profile(
    actor: AccountActor, operation_id: UUID, at: datetime, *, record: OutcomeRecorder
) -> AthleteProfileDTO:
    validate_context(actor, at)
    if not isinstance(operation_id, UUID) or not callable(record):
        raise ValueError("Invalid profile command")
    with transaction.atomic():
        user = locked_actor(actor, "athlete.profile_write", at)
        row = AthleteProfile.objects.select_for_update().filter(user=user).first()
        if row is not None:
            owned_profile(user, row.id, lock=True)
        receipt = (
            ProfileCommandReceipt.objects.select_for_update()
            .filter(owner=user, operation_id=operation_id)
            .first()
        )
        if receipt is not None:
            if row is None:
                raise ProfileNotFound("Profile unavailable")
            if (
                receipt.command != "profile.create"
                or receipt.request_hash != CREATE_HASH
            ):
                raise ProfileConflict("Profile command conflict")
            if receipt.object_uuid != row.id:
                raise ProfileNotFound("Profile unavailable")
            return own_athlete_profile(actor, at)
        created = row is None
        if row is None:
            row = AthleteProfile.objects.create(
                user=user, timezone=user.timezone, created_at=at
            )
        ProfileCommandReceipt.objects.create(
            owner=user,
            operation_id=operation_id,
            command="profile.create",
            request_hash=CREATE_HASH,
            object_uuid=row.id,
            resulting_version=row.version,
            created_at=at,
            updated_at=at,
        )
        if created:
            record(
                SecurityOutcome(
                    "athlete.profile_created",
                    "succeeded",
                    row.id,
                    operation_id,
                    ("version", "onboarding_step"),
                    "user_requested",
                )
            )
        return own_athlete_profile(actor, at)
