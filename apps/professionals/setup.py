"""Owner-serialized private setup, declarations and broad location facts."""

import json
from collections.abc import Callable
from datetime import datetime
from hashlib import sha256
from uuid import UUID

from django.db import transaction

from apps.accounts.contracts import OutcomeRecorder, SecurityOutcome
from apps.accounts.models import User
from apps.accounts.sessions import AccountActor, locked_actor
from apps.assets.models import Asset

from .contracts import (
    ProfessionalProfileDTO,
    ProfessionalStepInput,
    ProfileConflict,
    ProfileNotFound,
)
from .models import ProfessionalLocation, ProfessionalProfile, ProfessionalRole
from .policies import validate_context
from .receipt_models import ProfileCommandReceipt
from .selectors import own_professional_profile
from .validation import normalize_step
from .verification import (
    VerificationEmitter,
    target_declaration_changed,
    target_evidence_changed,
)

ProfileEmitter = Callable[[ProfessionalProfile], None]
AssetValidator = Callable[[User, ProfessionalProfile, UUID, str, UUID | None], Asset]


def context(
    actor: AccountActor, expected_version: int, operation_id: UUID, at: datetime
) -> None:
    validate_context(actor, at)
    if (
        type(expected_version) is not int
        or expected_version < 1
        or not isinstance(operation_id, UUID)
    ):
        raise ValueError("Invalid professional command")


def locked_profile(user: User) -> ProfessionalProfile:
    row = (
        ProfessionalProfile.objects.select_for_update()
        .filter(user=user)
        .exclude(state="archived")
        .first()
    )
    if row is None:
        raise ProfileNotFound("Profile unavailable")
    return row


def locked_roles(profile: ProfessionalProfile) -> list[ProfessionalRole]:
    return list(
        ProfessionalRole.objects.select_for_update()
        .filter(profile=profile)
        .order_by("id")
    )


def request_hash(command: str, values: dict[str, object]) -> str:
    return sha256(
        json.dumps(
            {"command": command, **values},
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        ).encode()
    ).hexdigest()


def receipt(
    user: User, operation_id: UUID, command: str, digest: str, object_uuid: UUID
) -> ProfileCommandReceipt | None:
    old = ProfileCommandReceipt.objects.filter(
        owner=user, operation_id=operation_id
    ).first()
    if old and (
        old.command != command
        or old.request_hash != digest
        or old.object_uuid != object_uuid
    ):
        raise ProfileConflict("Professional command conflict")
    return old


def remember(
    user: User,
    operation_id: UUID,
    command: str,
    digest: str,
    object_uuid: UUID,
    result_uuid: UUID,
    version: int,
    at: datetime,
) -> None:
    ProfileCommandReceipt.objects.create(
        owner=user,
        operation_id=operation_id,
        command=command,
        request_hash=digest,
        object_uuid=object_uuid,
        result_uuid=result_uuid,
        resulting_version=version,
        created_at=at,
        updated_at=at,
    )


def _locations(
    profile: ProfessionalProfile, values: list[dict[str, object]], at: datetime
) -> None:
    existing = list(
        ProfessionalLocation.objects.select_for_update()
        .filter(profile=profile, archived_at__isnull=True)
        .order_by("id")
    )
    for old in existing:
        match = next(
            (
                entry
                for entry in values
                if all(
                    getattr(old, name) == entry[name]
                    for name in ("country_code", "region", "city")
                )
            ),
            None,
        )
        if match is None:
            old.archived_at = at
            old.version += 1
            old.save(update_fields=["archived_at", "version", "updated_at"])
        elif old.modes != match["modes"]:
            old.modes = match["modes"]
            old.version += 1
            old.save(update_fields=["modes", "version", "updated_at"])
    for entry in values:
        if not any(
            all(
                getattr(old, name) == entry[name]
                for name in ("country_code", "region", "city")
            )
            for old in existing
        ):
            ProfessionalLocation.objects.create(profile=profile, created_at=at, **entry)


def complete(profile: ProfessionalProfile) -> bool:
    return bool(
        profile.display_name
        and profile.identity_name
        and profile.roles.filter(declared_active=True).exists()
        and profile.service_modes
        and profile.languages
        and (
            "in_person" not in profile.service_modes
            or profile.locations.filter(
                archived_at__isnull=True, modes__contains=["in_person"]
            ).exists()
        )
    )


def save_professional_step(
    actor: AccountActor,
    step: str,
    payload: ProfessionalStepInput,
    expected_version: int,
    operation_id: UUID,
    at: datetime,
    *,
    record: OutcomeRecorder,
    emit: ProfileEmitter,
    binding_record: OutcomeRecorder,
    binding_emit: VerificationEmitter,
    asset_validator: AssetValidator,
) -> ProfessionalProfileDTO:
    context(actor, expected_version, operation_id, at)
    with transaction.atomic():
        user = locked_actor(actor, "professional.profile_write", at)
        profile = locked_profile(user)
        values = normalize_step(step, payload)
        digest = request_hash(
            "profile.save_step",
            {"step": step, "input": values, "expected_version": expected_version},
        )
        if receipt(user, operation_id, "profile.save_step", digest, profile.id):
            return own_professional_profile(actor, at)
        if profile.version != expected_version:
            raise ProfileConflict("Profile version conflict")
        roles = locked_roles(profile)
        if "roles" in values:
            selected = values.pop("roles")
            assert isinstance(selected, list)
            for role in roles:
                target_declaration_changed(
                    profile,
                    role,
                    role.role in selected,
                    user,
                    operation_id,
                    at,
                    record=binding_record,
                    emit=binding_emit,
                )
            for kind in selected:
                if not any(role.role == kind for role in roles):
                    ProfessionalRole.objects.create(
                        profile=profile, role=kind, created_at=at
                    )
            record(
                SecurityOutcome(
                    "professional.roles_changed",
                    "succeeded",
                    profile.id,
                    operation_id,
                    ("declared_active", "declaration_version"),
                    "user_requested",
                )
            )
        if (
            "identity_name" in values
            and profile.identity_name != values["identity_name"]
        ):
            target_evidence_changed(
                profile,
                None,
                user,
                operation_id,
                at,
                record=binding_record,
                emit=binding_emit,
            )
        if "locations" in values:
            broad = values.pop("locations")
            assert isinstance(broad, list)
            _locations(profile, broad, at)
        for name, value in values.items():
            if name in {"avatar", "cover", "logo"}:
                setattr(
                    profile,
                    name,
                    asset_validator(user, profile, value, name, None)
                    if isinstance(value, UUID)
                    else None,
                )
            else:
                setattr(profile, name, value)
        if not profile.languages:
            profile.languages = ["fa"]
        if (
            "in_person" in profile.service_modes
            and not profile.locations.filter(
                archived_at__isnull=True, modes__contains=["in_person"]
            ).exists()
        ):
            raise ValueError("In-person setup requires an active broad location")
        ready = complete(profile)
        if step == "preview" and not ready:
            raise ValueError("Professional setup incomplete")
        # Editing a ready profile can make setup incomplete, never public.
        profile.state = (
            "private_ready"
            if ready and (step == "preview" or profile.state == "private_ready")
            else "setup"
        )
        profile.setup_step = step
        profile.version += 1
        profile.save()
        remember(
            user,
            operation_id,
            "profile.save_step",
            digest,
            profile.id,
            profile.id,
            profile.version,
            at,
        )
        record(
            SecurityOutcome(
                "professional.profile_saved",
                "succeeded",
                profile.id,
                operation_id,
                ("version", "setup_step"),
                "user_requested",
            )
        )
        emit(profile)
        return own_professional_profile(actor, at)
