"""Private metadata and append-only evidence revisions under owner anchors."""

from datetime import datetime
from uuid import UUID

from django.db import transaction
from django.db.models import Max

from apps.accounts.contracts import OutcomeRecorder, SecurityOutcome
from apps.accounts.sessions import AccountActor, locked_actor

from .contracts import CredentialDTO, CredentialInput, ProfileConflict, ProfileNotFound
from .models import (
    Credential,
    CredentialRevision,
    ProfessionalProfile,
    ProfessionalRole,
)
from .selectors import project_credential
from .setup import (
    AssetValidator,
    ProfileEmitter,
    context,
    locked_profile,
    locked_roles,
    receipt,
    remember,
    request_hash,
)
from .validation import normalize_credential
from .verification import VerificationEmitter, target_evidence_changed


def _role(
    profile: ProfessionalProfile, roles: list[ProfessionalRole], kind: object
) -> ProfessionalRole | None:
    if kind is None:
        return None
    row = next((r for r in roles if r.role == kind and r.declared_active), None)
    if row is None:
        raise ProfileNotFound("Credential unavailable")
    return row


def _owned(profile: ProfessionalProfile, identifier: UUID) -> Credential:
    if not isinstance(identifier, UUID):
        raise ProfileNotFound("Credential unavailable")
    row = (
        Credential.objects.select_for_update()
        .filter(pk=identifier, profile=profile)
        .first()
    )
    if row is None:
        raise ProfileNotFound("Credential unavailable")
    return row


def _revision(user, profile, row, values, at, asset_validator: AssetValidator) -> None:
    source = values["source_asset"]
    if source is None:
        if row.current_revision_id:
            source = CredentialRevision.objects.get(
                pk=row.current_revision_id
            ).source_asset_id
        else:
            return
    purpose = (
        "identity_evidence" if row.category == "identity" else "credential_evidence"
    )
    asset = asset_validator(user, profile, source, purpose, row.id)
    sequence = (row.revisions.aggregate(value=Max("sequence"))["value"] or 0) + 1
    metadata = {
        name: values[name]
        for name in (
            "category",
            "type_code",
            "issuer",
            "title",
            "issued_on",
            "expires_on",
        )
    }
    digest = request_hash(
        "credential.revision",
        {
            **metadata,
            "credential": row.id,
            "sequence": sequence,
            "source_asset": asset.id,
            "source_sha256": asset.sha256,
        },
    )
    revision = CredentialRevision.objects.create(
        credential=row,
        sequence=sequence,
        source_asset=asset,
        source_sha256=asset.sha256,
        revision_hash=digest,
        created_at=at,
        updated_at=at,
        **metadata,
    )
    row.current_revision = revision


def _changed(profile, row, operation_id, record, emit, action):
    profile.version += 1
    profile.save(update_fields=["version", "updated_at"])
    record(
        SecurityOutcome(
            action,
            "succeeded",
            row.id,
            operation_id,
            ("version", "current_revision", "withdrawn_at"),
            "user_requested",
        )
    )
    emit(profile)


def create_credential(
    actor: AccountActor,
    payload: CredentialInput,
    expected_profile_version: int,
    operation_id: UUID,
    at: datetime,
    *,
    record: OutcomeRecorder,
    emit: ProfileEmitter,
    binding_record: OutcomeRecorder,
    binding_emit: VerificationEmitter,
    asset_validator: AssetValidator,
) -> CredentialDTO:
    context(actor, expected_profile_version, operation_id, at)
    with transaction.atomic():
        user = locked_actor(actor, "professional.profile_write", at)
        profile = locked_profile(user)
        values = normalize_credential(payload)
        digest = request_hash(
            "credential.create",
            {"input": values, "expected_version": expected_profile_version},
        )
        old = receipt(user, operation_id, "credential.create", digest, profile.id)
        if old:
            if old.result_uuid is None:
                raise ProfileConflict("Credential command conflict")
            return project_credential(_owned(profile, old.result_uuid))
        if profile.version != expected_profile_version:
            raise ProfileConflict("Profile version conflict")
        roles = locked_roles(profile)
        role = _role(profile, roles, values["role"])
        metadata = {
            name: values[name]
            for name in (
                "category",
                "type_code",
                "issuer",
                "title",
                "issued_on",
                "expires_on",
            )
        }
        row = Credential.objects.create(
            profile=profile, role=role, created_at=at, **metadata
        )
        # Binding effects lock cases/targets before private Asset anchors; failure
        # of source validation rolls back these effects and the new credential.
        target_evidence_changed(
            profile,
            role,
            user,
            operation_id,
            at,
            record=binding_record,
            emit=binding_emit,
        )
        _revision(user, profile, row, values, at, asset_validator)
        row.save()
        _changed(profile, row, operation_id, record, emit, "credential.created")
        remember(
            user,
            operation_id,
            "credential.create",
            digest,
            profile.id,
            row.id,
            row.version,
            at,
        )
        return project_credential(row)


def revise_credential(
    actor: AccountActor,
    credential_uuid: UUID,
    payload: CredentialInput,
    expected_version: int,
    operation_id: UUID,
    at: datetime,
    *,
    record: OutcomeRecorder,
    emit: ProfileEmitter,
    binding_record: OutcomeRecorder,
    binding_emit: VerificationEmitter,
    asset_validator: AssetValidator,
) -> CredentialDTO:
    context(actor, expected_version, operation_id, at)
    with transaction.atomic():
        user = locked_actor(actor, "professional.profile_write", at)
        profile = locked_profile(user)
        roles = locked_roles(profile)
        row = _owned(profile, credential_uuid)
        values = normalize_credential(payload)
        digest = request_hash(
            "credential.revise", {"input": values, "expected_version": expected_version}
        )
        if receipt(user, operation_id, "credential.revise", digest, row.id):
            return project_credential(row)
        if row.version != expected_version or row.withdrawn_at:
            raise ProfileConflict("Credential version conflict")
        existing_role = next((r for r in roles if r.id == row.role_id), None)
        if row.category != values["category"] or values["role"] != (
            existing_role.role if existing_role else None
        ):
            raise ValueError("Credential target is immutable")
        role = _role(profile, roles, values["role"])
        target_evidence_changed(
            profile,
            role,
            user,
            operation_id,
            at,
            record=binding_record,
            emit=binding_emit,
        )
        _revision(user, profile, row, values, at, asset_validator)
        for name in ("type_code", "issuer", "title", "issued_on", "expires_on"):
            setattr(row, name, values[name])
        row.version += 1
        row.save()
        _changed(profile, row, operation_id, record, emit, "credential.revised")
        remember(
            user,
            operation_id,
            "credential.revise",
            digest,
            row.id,
            row.id,
            row.version,
            at,
        )
        return project_credential(row)


def withdraw_credential(
    actor: AccountActor,
    credential_uuid: UUID,
    expected_version: int,
    operation_id: UUID,
    at: datetime,
    *,
    record: OutcomeRecorder,
    emit: ProfileEmitter,
    binding_record: OutcomeRecorder,
    binding_emit: VerificationEmitter,
) -> CredentialDTO:
    context(actor, expected_version, operation_id, at)
    with transaction.atomic():
        user = locked_actor(actor, "professional.profile_write", at)
        profile = locked_profile(user)
        roles = locked_roles(profile)
        row = _owned(profile, credential_uuid)
        digest = request_hash(
            "credential.withdraw", {"expected_version": expected_version}
        )
        if receipt(user, operation_id, "credential.withdraw", digest, row.id):
            return project_credential(row)
        if row.version != expected_version or row.withdrawn_at:
            raise ProfileConflict("Credential version conflict")
        role = next((r for r in roles if r.id == row.role_id), None)
        target_evidence_changed(
            profile,
            role,
            user,
            operation_id,
            at,
            record=binding_record,
            emit=binding_emit,
        )
        row.withdrawn_at = at
        row.version += 1
        row.save(update_fields=["withdrawn_at", "version", "updated_at"])
        _changed(profile, row, operation_id, record, emit, "credential.withdrawn")
        remember(
            user,
            operation_id,
            "credential.withdraw",
            digest,
            row.id,
            row.id,
            row.version,
            at,
        )
        return project_credential(row)
