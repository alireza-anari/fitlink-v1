"""Current owner setup boundary; registration switch never grants authority."""

from collections.abc import Callable
from datetime import datetime
from hashlib import sha256
from uuid import UUID

from django.db import transaction

from apps.accounts.contracts import OutcomeRecorder, SecurityOutcome
from apps.accounts.sessions import AccountActor, locked_actor

from .contracts import ProfessionalProfileDTO, ProfileConflict, ProfileNotFound
from .models import ProfessionalProfile
from .policies import owned_profile, validate_context
from .receipt_models import ProfileCommandReceipt
from .selectors import own_professional_profile


def save_professional_step(*args, **kwargs):
    from .setup import save_professional_step as save

    return save(*args, **kwargs)


CREATE_HASH = sha256(b'{"command":"profile.create"}').hexdigest()


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
        row = ProfessionalProfile.objects.select_for_update().filter(user=user).first()
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
            return own_professional_profile(actor, at)
        created = row is None
        if row is None:
            if registration_enabled() is not True:
                raise PermissionError("Professional registration unavailable")
            row = ProfessionalProfile.objects.create(user=user, created_at=at)
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
                    "professional.profile_created",
                    "succeeded",
                    row.id,
                    operation_id,
                    ("version", "setup_step"),
                    "user_requested",
                )
            )
        dto = own_professional_profile(actor, at)
        if created:
            emit(dto)
        return dto
