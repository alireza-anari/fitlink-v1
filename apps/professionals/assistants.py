"""Trusted inert metadata primitives; a membership is never authorization."""

from datetime import datetime
from uuid import UUID

from django.db import transaction

from apps.accounts.contracts import OutcomeRecorder, SecurityOutcome
from apps.accounts.models import User
from apps.accounts.policies import require_account_action
from apps.accounts.sessions import AccountActor, locked_actor

from .contracts import AssistantMembershipDTO, ProfileConflict, ProfileNotFound
from .models import AssistantMembership
from .policies import validate_context
from .setup import (
    ProfileEmitter,
    context,
    locked_profile,
    receipt,
    remember,
    request_hash,
)


def _dto(row: AssistantMembership) -> AssistantMembershipDTO:
    return AssistantMembershipDTO(
        row.id,
        row.profile_id,
        row.assistant.public_id,
        row.role,
        row.state,
        row.version,
        row.defined_at,
        row.revoked_at,
    )


def _membership(profile, identifier):
    row = (
        AssistantMembership.objects.select_for_update()
        .filter(pk=identifier, profile=profile)
        .first()
    )
    if row is None:
        raise ProfileNotFound("Membership unavailable")
    return row


def _effect(profile, row, actor, operation_id, action, record, emit):
    profile.version += 1
    profile.save(update_fields=["version", "updated_at"])
    record(
        SecurityOutcome(
            action,
            "succeeded",
            row.id,
            operation_id,
            ("state", "version")
            if action == "assistant.defined"
            else ("state", "version", "revoked_at"),
            "user_requested",
        )
    )
    emit(profile)


def define_assistant_role(
    actor: AccountActor,
    assistant_uuid: UUID,
    operation_id: UUID,
    at: datetime,
    *,
    record: OutcomeRecorder,
    emit: ProfileEmitter,
) -> AssistantMembershipDTO:
    validate_context(actor, at)
    if not isinstance(assistant_uuid, UUID) or not isinstance(operation_id, UUID):
        raise ValueError("Invalid assistant command")
    if not callable(record) or not callable(emit):
        raise ValueError("Invalid assistant command")
    with transaction.atomic():
        # Both participants precede all profile anchors, in stable User PK order.
        users = list(
            User.objects.select_for_update()
            .filter(public_id__in=[actor.user_uuid, assistant_uuid])
            .order_by("pk")
        )
        user = locked_actor(actor, "professional.profile_write", at)
        profile = locked_profile(user)
        assistant = next((u for u in users if u.public_id == assistant_uuid), None)
        if assistant is None or assistant.pk == user.pk:
            raise ProfileNotFound("Assistant unavailable")
        require_account_action(assistant, "professional.profile_read", "normal")
        digest = request_hash("assistant.define", {"assistant_uuid": assistant_uuid})
        old = receipt(user, operation_id, "assistant.define", digest, profile.id)
        if old:
            return _dto(_membership(profile, old.result_uuid))
        row = (
            AssistantMembership.objects.select_for_update()
            .filter(profile=profile, assistant=assistant, state="defined")
            .first()
        )
        created = row is None
        if row is None:
            row = AssistantMembership.objects.create(
                profile=profile,
                assistant=assistant,
                role="client_support",
                state="defined",
                defined_at=at,
                created_at=at,
            )
        remember(
            user,
            operation_id,
            "assistant.define",
            digest,
            profile.id,
            row.id,
            row.version,
            at,
        )
        if created:
            _effect(
                profile, row, actor, operation_id, "assistant.defined", record, emit
            )
        return _dto(row)


def revoke_assistant_role(
    actor: AccountActor,
    membership_uuid: UUID,
    expected_version: int,
    operation_id: UUID,
    at: datetime,
    *,
    record: OutcomeRecorder,
    emit: ProfileEmitter,
) -> AssistantMembershipDTO:
    context(actor, expected_version, operation_id, at)
    if (
        not isinstance(membership_uuid, UUID)
        or not callable(record)
        or not callable(emit)
    ):
        raise ValueError("Invalid assistant command")
    with transaction.atomic():
        user = locked_actor(actor, "professional.profile_write", at)
        profile = locked_profile(user)
        row = _membership(profile, membership_uuid)
        digest = request_hash(
            "assistant.revoke",
            {
                "membership_uuid": membership_uuid,
                "expected_version": expected_version,
            },
        )
        if receipt(user, operation_id, "assistant.revoke", digest, row.id):
            return _dto(row)
        if row.version != expected_version or row.state != "defined":
            raise ProfileConflict("Membership version conflict")
        row.state, row.revoked_at = "revoked", at
        row.version += 1
        row.save(update_fields=["state", "revoked_at", "version", "updated_at"])
        remember(
            user,
            operation_id,
            "assistant.revoke",
            digest,
            row.id,
            row.id,
            row.version,
            at,
        )
        _effect(profile, row, actor, operation_id, "assistant.revoked", record, emit)
        return _dto(row)
