"""Owner-locked resumable drafts with optimistic receipts and frozen snapshots."""

import json
from collections.abc import Callable
from copy import deepcopy
from datetime import datetime
from hashlib import sha256
from uuid import UUID
from zoneinfo import ZoneInfo

from django.db import transaction
from django.db.models import Max

from apps.accounts.contracts import OutcomeRecorder, SecurityOutcome
from apps.accounts.models import User
from apps.accounts.sessions import AccountActor, locked_actor

from .baseline_models import BaselineAssessment
from .contracts import BaselineDTO, BaselineStepInput, ProfileConflict, ProfileNotFound
from .models import AthleteProfile
from .policies import validate_context
from .receipt_models import ProfileCommandReceipt
from .validation import (
    NON_SENSITIVE_FIELDS,
    OPTIONAL_DEFAULTS,
    completed_steps,
    normalize_step,
    optional_present,
)

StoragePredicate = Callable[[User, BaselineAssessment, datetime], bool]
BaselineEmitter = Callable[[BaselineAssessment], None]


def context(
    actor: AccountActor, expected_version: int, operation_id: UUID, at: datetime
) -> None:
    validate_context(actor, at)
    if (
        type(expected_version) is not int
        or expected_version < 1
        or not isinstance(operation_id, UUID)
    ):
        raise ValueError("Invalid baseline command")


def locked_profile(user: User) -> AthleteProfile:
    profile = (
        AthleteProfile.objects.select_for_update()
        .filter(user=user)
        .exclude(status="archived")
        .first()
    )
    if profile is None:
        raise ProfileNotFound("Profile unavailable")
    return profile


def locked_baseline(profile: AthleteProfile, identifier: UUID) -> BaselineAssessment:
    if not isinstance(identifier, UUID):
        raise ProfileNotFound("Baseline unavailable")
    row = (
        BaselineAssessment.objects.select_for_update()
        .filter(pk=identifier, athlete=profile)
        .first()
    )
    if row is None:
        raise ProfileNotFound("Baseline unavailable")
    return row


def project(
    user: User, row: BaselineAssessment, at: datetime, storage: StoragePredicate
) -> BaselineDTO:
    accessible = storage(user, row, at)
    answers = {name: getattr(row, name) for name in NON_SENSITIVE_FIELDS}
    answers.update(
        {
            name: getattr(row, name) if accessible else default
            for name, default in OPTIONAL_DEFAULTS.items()
        }
    )
    return BaselineDTO(
        row.id,
        row.athlete_id,
        row.version,
        row.state,
        row.schema_version,
        row.sequence,
        row.parent_id,
        row.observed_at,
        row.age_at_assessment,
        "self_reported",
        row.submitted_at,
        row.updated_at,
        deepcopy(answers),
        accessible,
        completed_steps(row),
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
    row = ProfileCommandReceipt.objects.filter(
        owner=user, operation_id=operation_id
    ).first()
    if row is not None and (
        row.command != command
        or row.request_hash != digest
        or row.object_uuid != object_uuid
    ):
        raise ProfileConflict("Baseline command conflict")
    return row


def remember(
    user: User,
    operation_id: UUID,
    command: str,
    digest: str,
    object_uuid: UUID,
    row: BaselineAssessment,
    at: datetime,
    result_uuid: UUID | None = None,
) -> None:
    ProfileCommandReceipt.objects.create(
        owner=user,
        operation_id=operation_id,
        command=command,
        request_hash=digest,
        object_uuid=object_uuid,
        result_uuid=result_uuid or row.id,
        resulting_version=row.version,
        created_at=at,
        updated_at=at,
    )


def changed(
    profile: AthleteProfile,
    row: BaselineAssessment,
    action: str,
    operation_id: UUID,
    record: OutcomeRecorder,
    emit: BaselineEmitter,
) -> None:
    profile.version += 1
    profile.onboarding_step = next(
        (
            step
            for step in ("goals", "experience", "availability", "facilities")
            if step not in completed_steps(row)
        ),
        "review",
    )
    profile.save(
        update_fields=[
            "version",
            "onboarding_step",
            "status",
            "current_baseline",
            "updated_at",
        ]
    )
    record(
        SecurityOutcome(
            action, "succeeded", row.id, operation_id, ("version",), "user_requested"
        )
    )
    emit(row)


def new_draft(
    user: User,
    profile: AthleteProfile,
    at: datetime,
    parent: BaselineAssessment | None = None,
) -> BaselineAssessment:
    sequence = (
        BaselineAssessment.objects.filter(athlete=profile).aggregate(
            value=Max("sequence")
        )["value"]
        or 0
    ) + 1
    assert user.birth_date is not None
    today = at.astimezone(ZoneInfo("Asia/Tehran")).date()
    age = (
        today.year
        - user.birth_date.year
        - ((today.month, today.day) < (user.birth_date.month, user.birth_date.day))
    )
    values = (
        {name: getattr(parent, name) for name in NON_SENSITIVE_FIELDS} if parent else {}
    )
    return BaselineAssessment.objects.create(
        athlete=profile,
        parent=parent,
        sequence=sequence,
        observed_at=at,
        age_at_assessment=age,
        created_at=at,
        **values,
    )


def begin_baseline(
    actor: AccountActor,
    expected_profile_version: int,
    operation_id: UUID,
    at: datetime,
    *,
    storage: StoragePredicate,
    record: OutcomeRecorder,
    emit: BaselineEmitter,
) -> BaselineDTO:
    context(actor, expected_profile_version, operation_id, at)
    with transaction.atomic():
        user = locked_actor(actor, "athlete.baseline_write", at)
        profile = locked_profile(user)
        digest = request_hash(
            "baseline.begin", {"expected_version": expected_profile_version}
        )
        old = receipt(user, operation_id, "baseline.begin", digest, profile.id)
        if old:
            assert old.result_uuid is not None
            return project(user, locked_baseline(profile, old.result_uuid), at, storage)
        if profile.version != expected_profile_version:
            raise ProfileConflict("Baseline version conflict")
        row = (
            BaselineAssessment.objects.select_for_update()
            .filter(athlete=profile, state="draft")
            .first()
        )
        if row is None:
            if profile.current_baseline_id is not None:
                raise ProfileConflict("Create a correction for the submitted baseline")
            row = new_draft(user, profile, at)
            changed(profile, row, "baseline.saved", operation_id, record, emit)
        remember(user, operation_id, "baseline.begin", digest, profile.id, row, at)
        return project(user, row, at, storage)


def mutate_baseline(
    actor: AccountActor,
    baseline_uuid: UUID,
    expected_version: int,
    operation_id: UUID,
    at: datetime,
    command: str,
    *,
    storage: StoragePredicate,
    record: OutcomeRecorder,
    emit: BaselineEmitter,
    step: str | None = None,
    payload: BaselineStepInput | None = None,
) -> BaselineDTO:
    context(actor, expected_version, operation_id, at)
    values = (
        normalize_step(step, payload)
        if command == "baseline.save_step" and step is not None and payload is not None
        else {}
    )
    with transaction.atomic():
        user = locked_actor(actor, "athlete.baseline_write", at)
        profile = locked_profile(user)
        row = locked_baseline(profile, baseline_uuid)
        storage(user, row, at)  # Consent anchors precede receipt/effect writes.
        digest = request_hash(
            command,
            {
                "baseline_uuid": baseline_uuid,
                "expected_version": expected_version,
                "step": step,
                "values": values,
            },
        )
        old = receipt(user, operation_id, command, digest, row.id)
        if old:
            assert old.result_uuid is not None
            return project(user, locked_baseline(profile, old.result_uuid), at, storage)
        if row.version != expected_version:
            raise ProfileConflict("Baseline version conflict")
        if command == "baseline.correct":
            if row.state != "submitted" or profile.current_baseline_id != row.id:
                raise ProfileConflict(
                    "Correction requires the current submitted snapshot"
                )
            draft = (
                BaselineAssessment.objects.select_for_update()
                .filter(athlete=profile, state="draft")
                .first()
            )
            if draft is not None and draft.parent_id != row.id:
                raise ProfileConflict("Another correction is pending")
            if draft is None:
                draft = new_draft(user, profile, at, row)
                changed(
                    profile, draft, "baseline.corrected", operation_id, record, emit
                )
            remember(user, operation_id, command, digest, row.id, draft, at)
            return project(user, draft, at, storage)
        if row.state != "draft":
            raise ProfileConflict(
                "Submitted baseline is immutable; create a correction"
            )
        if command == "baseline.save_step":
            if any(
                name in OPTIONAL_DEFAULTS and value != OPTIONAL_DEFAULTS[name]
                for name, value in values.items()
            ) and not storage(user, row, at):
                raise PermissionError("Current baseline self-storage consent required")
            for name, value in values.items():
                setattr(row, name, value)
            action = "baseline.saved"
        elif command == "baseline.clear":
            for name, default in OPTIONAL_DEFAULTS.items():
                setattr(
                    row, name, default.copy() if isinstance(default, list) else default
                )
            action = "baseline.cleared"
        elif command == "baseline.submit":
            if len(completed_steps(row)) != 4:
                raise ValueError("Required baseline setup is incomplete")
            if optional_present(row) and not storage(user, row, at):
                raise PermissionError("Current baseline self-storage consent required")
            if row.parent_id is not None:
                predecessor = locked_baseline(profile, row.parent_id)
                if (
                    predecessor.state != "submitted"
                    or profile.current_baseline_id != predecessor.id
                ):
                    raise ProfileConflict("Correction predecessor is no longer current")
                predecessor.state = "superseded"
                predecessor.version += 1
                predecessor.save(update_fields=["state", "version", "updated_at"])
            row.state = "submitted"
            row.submitted_at = at
            profile.status = "active"
            profile.current_baseline = row
            action = "baseline.submitted"
        else:
            raise ValueError("Unknown baseline command")
        row.version += 1
        row.save()
        changed(profile, row, action, operation_id, record, emit)
        remember(user, operation_id, command, digest, row.id, row, at)
        return project(user, row, at, storage)
