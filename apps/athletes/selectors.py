"""Current-session own projection; no directory, foreign list or count."""

from datetime import datetime
from uuid import UUID, uuid4

from django.db import transaction

from apps.accounts.contracts import OutcomeRecorder, SecurityOutcome
from apps.accounts.sessions import AccountActor, locked_actor

from .baseline import StoragePredicate, locked_baseline, locked_profile, project
from .contracts import AthleteProfileDTO, BaselineDTO, ProfileNotFound
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


def own_baseline(
    actor: AccountActor,
    baseline_uuid: UUID,
    at: datetime,
    *,
    storage: StoragePredicate,
    record: OutcomeRecorder,
) -> BaselineDTO:
    validate_context(actor, at)
    with transaction.atomic():
        user = locked_actor(actor, "athlete.baseline_read", at)
        profile = locked_profile(user)
        row = locked_baseline(profile, baseline_uuid)
        result = project(user, row, at, storage)
        record(
            SecurityOutcome(
                "baseline.read",
                "accepted",
                row.id,
                uuid4(),
                reason_code="user_requested",
            )
        )
        return result
