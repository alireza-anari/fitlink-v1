"""Coherent current-session own projection; no publication authority."""

from copy import deepcopy
from datetime import datetime
from uuid import UUID

from django.db import transaction

from apps.accounts.sessions import AccountActor, locked_actor

from .contracts import (
    CredentialDTO,
    ProfessionalLocationDTO,
    ProfessionalProfileDTO,
    ProfessionalRoleDTO,
    ProfileNotFound,
)
from .models import Credential, ProfessionalProfile
from .policies import owned_profile, validate_context
from .validation import PROFILE_FIELDS


def project_credential(row: Credential) -> CredentialDTO:
    return CredentialDTO(
        row.id,
        row.version,
        row.category,
        row.role.role if row.role is not None else None,
        row.type_code,
        row.issuer,
        row.title,
        row.issued_on,
        row.expires_on,
        row.current_revision_id,
        row.withdrawn_at,
    )


def own_credential(
    actor: AccountActor, credential_uuid: UUID, at: datetime
) -> CredentialDTO:
    validate_context(actor, at)
    with transaction.atomic():
        user = locked_actor(actor, "professional.profile_read", at)
        profile = (
            ProfessionalProfile.objects.select_for_update()
            .filter(user=user)
            .exclude(state="archived")
            .first()
        )
        if profile is None or not isinstance(credential_uuid, UUID):
            raise ProfileNotFound("Credential unavailable")
        row = (
            Credential.objects.filter(pk=credential_uuid, profile=profile)
            .select_related("role")
            .first()
        )
        if row is None:
            raise ProfileNotFound("Credential unavailable")
        return project_credential(row)


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
            deepcopy(
                {
                    name: getattr(
                        row,
                        name + "_id" if name in {"avatar", "cover", "logo"} else name,
                    )
                    for name in PROFILE_FIELDS
                }
            ),
            tuple(
                ProfessionalRoleDTO(
                    role.id,
                    role.role,
                    role.declared_active,
                    role.version,
                    role.declaration_version,
                    role.evidence_revision,
                    role.decision_version,
                )
                for role in row.roles.order_by("role")
            ),
            tuple(
                ProfessionalLocationDTO(
                    location.id,
                    location.country_code,
                    location.region,
                    location.city,
                    tuple(location.modes),
                    location.version,
                )
                for location in row.locations.filter(archived_at__isnull=True).order_by(
                    "country_code", "region", "city", "id"
                )
            ),
        )


def own_verification(actor: AccountActor, verification_uuid: UUID, at: datetime):
    """Coarse immutable target/history view with no staff-private explanation."""
    from uuid import uuid4

    from apps.accounts.contracts import SecurityOutcome
    from apps.governance import audit

    from .setup import locked_profile
    from .verification import _case, _owner_dto

    validate_context(actor, at)
    with transaction.atomic():
        user = locked_actor(actor, "professional.profile_read", at)
        profile = locked_profile(user)
        case = _case(profile, verification_uuid)
        audit.append_event(
            SecurityOutcome(
                "verification.read", "succeeded", case.id, uuid4(), (), "user_requested"
            ),
            actor_uuid=actor.user_uuid,
            subject_type="verification",
        )
        return _owner_dto(case)
