"""Synchronous audit wiring; owner is always derived from AccountActor."""

from datetime import datetime
from uuid import UUID

from apps.accounts.contracts import SecurityOutcome
from apps.accounts.sessions import AccountActor
from apps.athletes import services
from apps.athletes.contracts import AthleteProfileDTO
from apps.governance.audit import append_event


def create_athlete_profile(
    actor: AccountActor, operation_id: UUID, at: datetime
) -> AthleteProfileDTO:
    def record(outcome: SecurityOutcome) -> None:
        append_event(outcome, actor_uuid=actor.user_uuid, subject_type="athlete")

    return services.create_athlete_profile(
        actor,
        operation_id,
        at,
        record=record,
    )
