"""Current-session own projection; no directory, foreign list or count."""

from datetime import datetime

from django.db import transaction

from apps.accounts.sessions import AccountActor, locked_actor

from .contracts import AthleteProfileDTO, ProfileNotFound
from .models import AthleteProfile
from .policies import owned_profile, validate_context


def own_athlete_profile(actor: AccountActor, at: datetime) -> AthleteProfileDTO:
    validate_context(actor, at)
    with transaction.atomic():
        user = locked_actor(actor, "athlete.profile_read", at)
        identifier = (
            AthleteProfile.objects.filter(user=user)
            .values_list("id", flat=True)
            .first()
        )
        if identifier is None:
            raise ProfileNotFound("Profile unavailable")
        row = owned_profile(user, identifier, lock=True)
        return AthleteProfileDTO(
            row.id,
            row.version,
            row.status,
            row.timezone,
            row.onboarding_step,
            row.current_baseline_id,
            row.created_at,
            row.updated_at,
        )
