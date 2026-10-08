"""Explicit owner profile creation; baseline creation is a separate command."""

from datetime import datetime
from uuid import UUID

from django.db import transaction

from apps.accounts.contracts import OutcomeRecorder, SecurityOutcome
from apps.accounts.sessions import AccountActor, locked_actor

from .contracts import AthleteProfileDTO
from .models import AthleteProfile
from .policies import validate_context
from .selectors import own_athlete_profile


def create_athlete_profile(
    actor: AccountActor, operation_id: UUID, at: datetime, *, record: OutcomeRecorder
) -> AthleteProfileDTO:
    validate_context(actor, at)
    if not isinstance(operation_id, UUID) or not callable(record):
        raise ValueError("Invalid profile command")
    with transaction.atomic():
        user = locked_actor(actor, "athlete.profile_write", at)
        row = AthleteProfile.objects.create(
            user=user, timezone=user.timezone, created_at=at
        )
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
