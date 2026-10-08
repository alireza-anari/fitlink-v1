"""Current owner setup boundary; registration switch never grants authority."""

from collections.abc import Callable
from datetime import datetime
from uuid import UUID

from django.db import transaction

from apps.accounts.contracts import OutcomeRecorder, SecurityOutcome
from apps.accounts.sessions import AccountActor, locked_actor

from .contracts import ProfessionalProfileDTO
from .models import ProfessionalProfile
from .policies import validate_context
from .selectors import own_professional_profile


def create_professional_profile(
    actor: AccountActor,
    operation_id: UUID,
    at: datetime,
    *,
    record: OutcomeRecorder,
    emit: Callable[[ProfessionalProfileDTO], None],
    registration_enabled: Callable[[], bool],
) -> ProfessionalProfileDTO:
    validate_context(actor, at)
    if not isinstance(operation_id, UUID) or not all(
        map(callable, (record, emit, registration_enabled))
    ):
        raise ValueError("Invalid profile command")
    with transaction.atomic():
        user = locked_actor(actor, "professional.profile_write", at)
        if not registration_enabled():
            raise PermissionError("Professional registration unavailable")
        row = ProfessionalProfile.objects.create(user=user, created_at=at)
        record(
            SecurityOutcome(
                "professional.profile_created",
                "succeeded",
                row.id,
                operation_id,
                ("version", "setup_step"),
                "user_requested",
            )
        )
        dto = own_professional_profile(actor, at)
        emit(dto)
        return dto
