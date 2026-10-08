"""Trusted create-only flag and bounded metadata event wiring."""

from datetime import datetime
from uuid import UUID

from django.db import DatabaseError

from apps.accounts.contracts import SecurityOutcome
from apps.accounts.sessions import AccountActor
from apps.governance.audit import append_event
from apps.governance.flag_models import FeatureFlag
from apps.governance.flags import professional_entry_enabled
from apps.governance.outbox import append_outbox
from apps.professionals import services
from apps.professionals.contracts import ProfessionalProfileDTO


def _registration_enabled() -> bool:
    try:
        # Serialize the fresh switch check with trusted flag changes.
        list(
            FeatureFlag.objects.select_for_update().filter(
                key="professional_registration"
            )
        )
        return professional_entry_enabled()
    except DatabaseError:
        return False


def create_professional_profile(
    actor: AccountActor, operation_id: UUID, at: datetime
) -> ProfessionalProfileDTO:
    def record(outcome: SecurityOutcome) -> None:
        append_event(outcome, actor_uuid=actor.user_uuid, subject_type="professional")

    def emit(dto: ProfessionalProfileDTO) -> None:
        append_outbox(
            "professional.profile_changed",
            dto.id,
            dto.version,
            {"profile_uuid": str(dto.id), "user_uuid": str(actor.user_uuid)},
            f"professional.profile_changed:{dto.id}:{dto.version}",
        )

    return services.create_professional_profile(
        actor,
        operation_id,
        at,
        record=record,
        emit=emit,
        registration_enabled=_registration_enabled,
    )
