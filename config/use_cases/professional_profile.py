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


def _safe_asset(user, profile, identifier, purpose, credential_uuid):
    from apps.professionals.policies import ready_asset

    return ready_asset(user, profile, identifier, purpose, credential_uuid)


def _hooks(actor, *, credential=False):
    def record(outcome):
        append_event(
            outcome,
            actor_uuid=actor.user_uuid,
            subject_type="credential" if credential else "professional",
        )

    def emit(profile):
        append_outbox(
            "professional.profile_changed",
            profile.id,
            profile.version,
            {"profile_uuid": str(profile.id), "user_uuid": str(actor.user_uuid)},
            f"professional.profile_changed:{profile.id}:{profile.version}",
        )

    from .professional_verification import binding_hooks

    binding_record, binding_emit = binding_hooks(actor)
    return {
        "record": record,
        "emit": emit,
        "binding_record": binding_record,
        "binding_emit": binding_emit,
    }


def save_professional_step(actor, step, payload, expected_version, operation_id, at):
    return services.save_professional_step(
        actor,
        step,
        payload,
        expected_version,
        operation_id,
        at,
        **_hooks(actor),
        asset_validator=_safe_asset,
    )


def create_credential(actor, payload, expected_profile_version, operation_id, at):
    from apps.professionals.credentials import create_credential as create

    return create(
        actor,
        payload,
        expected_profile_version,
        operation_id,
        at,
        **_hooks(actor, credential=True),
        asset_validator=_safe_asset,
    )


def revise_credential(
    actor, credential_uuid, payload, expected_version, operation_id, at
):
    from apps.professionals.credentials import revise_credential as revise

    return revise(
        actor,
        credential_uuid,
        payload,
        expected_version,
        operation_id,
        at,
        **_hooks(actor, credential=True),
        asset_validator=_safe_asset,
    )


def withdraw_credential(actor, credential_uuid, expected_version, operation_id, at):
    from apps.professionals.credentials import withdraw_credential as withdraw

    return withdraw(
        actor,
        credential_uuid,
        expected_version,
        operation_id,
        at,
        **_hooks(actor, credential=True),
    )


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
