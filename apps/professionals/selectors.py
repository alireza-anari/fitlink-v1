"""Coherent current-session own projection; no publication authority."""

from datetime import datetime

from django.db import transaction

from apps.accounts.sessions import AccountActor, locked_actor

from .contracts import ProfessionalProfileDTO, ProfileNotFound
from .models import ProfessionalProfile
from .policies import owned_profile, validate_context


def own_professional_profile(
    actor: AccountActor, at: datetime
) -> ProfessionalProfileDTO:
    validate_context(actor, at)
    with transaction.atomic():
        user = locked_actor(actor, "professional.profile_read", at)
        identifier = (
            ProfessionalProfile.objects.filter(user=user)
            .values_list("id", flat=True)
            .first()
        )
        if identifier is None:
            raise ProfileNotFound("Profile unavailable")
        row = owned_profile(user, identifier, lock=True)
        return ProfessionalProfileDTO(
            row.id,
            row.version,
            row.state,
            row.setup_step,
            row.created_at,
            row.updated_at,
        )
