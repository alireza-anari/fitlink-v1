"""Record-specific holds and approved policy metadata; never erasure or access."""

import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils import timezone

from apps.accounts.contracts import SecurityOutcome
from apps.accounts.models import User
from apps.accounts.sessions import AccountActor, locked_actor

from .audit import append_event
from .privacy_models import PrivacyRequest, RecordHold, RetentionPolicy
from .staff import require_staff


@dataclass(frozen=True)
class ValidatedRecordSubject:
    kind: str
    record_uuid: UUID
    owner_uuid: UUID
    version: int


def _validate_subject(
    subject: ValidatedRecordSubject,
    subject_validator: Callable[[ValidatedRecordSubject], bool] | None = None,
) -> PrivacyRequest | None:
    if subject_validator is not None:
        if subject_validator(subject) is not True:
            raise PermissionError("Record subject denied")
        return None
    if (
        not isinstance(subject, ValidatedRecordSubject)
        or subject.kind != "privacy_request"
        or not isinstance(subject.record_uuid, UUID)
        or not isinstance(subject.owner_uuid, UUID)
        or type(subject.version) is not int
        or subject.version < 1
    ):
        raise PermissionError("Record subject denied")
    row = PrivacyRequest.objects.filter(
        pk=subject.record_uuid,
        user__public_id=subject.owner_uuid,
        version=subject.version,
    ).first()
    if not row:
        raise PermissionError("Record subject denied")
    return row


def _time(at: datetime) -> None:
    if not isinstance(at, datetime) or not timezone.is_aware(at):
        raise ValueError("Invalid metadata time")


def is_record_held(
    subject: ValidatedRecordSubject,
    at: datetime,
    *,
    subject_validator: Callable[[ValidatedRecordSubject], bool] | None = None,
) -> bool:
    _time(at)
    _validate_subject(subject, subject_validator)
    return RecordHold.objects.filter(
        subject_kind=subject.kind,
        subject_uuid=subject.record_uuid,
        subject_version=subject.version,
        owner_uuid=subject.owner_uuid,
        released_at__isnull=True,
        created_at__lte=at,
        expires_at__gt=at,
    ).exists()


def _audit(actor: AccountActor, action: str, subject: UUID, reason: str) -> None:
    append_event(
        SecurityOutcome(action, "succeeded", subject, uuid4(), ("version",), reason),
        actor_uuid=actor.user_uuid,
        subject_type="privacy",
    )


def apply_hold(
    actor: AccountActor,
    subject: ValidatedRecordSubject,
    case_uuid: UUID,
    purpose: str,
    reason_code: str,
    review_at: datetime,
    expires_at: datetime,
    step_up_id: UUID,
    at: datetime,
    *,
    subject_validator: Callable[[ValidatedRecordSubject], bool] | None = None,
    case_validator: Callable[[ValidatedRecordSubject, UUID, User], bool] | None = None,
) -> UUID:
    for value in (at, review_at, expires_at):
        _time(value)
    if (
        purpose not in {"dispute", "fraud", "security", "required_audit"}
        or reason_code != "hold_applied"
        or not at < review_at <= expires_at
    ):
        raise ValueError("Invalid bounded hold")
    with transaction.atomic():
        user = locked_actor(actor, "staff.command", at)
        require_staff(
            user, "privacy_operations", case_uuid, step_up_id, reason_code, at
        )
        row = _validate_subject(subject, subject_validator)
        # Default C02 behavior remains an exact privacy intake.
        valid_case = (
            case_validator(subject, case_uuid, user) is True
            if case_validator is not None
            else row is not None and case_uuid == row.id
        )
        if not valid_case:
            raise PermissionDenied("Hold case denied")
        hold = RecordHold.objects.create(
            subject_kind=subject.kind,
            subject_uuid=subject.record_uuid,
            subject_version=subject.version,
            owner_uuid=subject.owner_uuid,
            case_uuid=case_uuid,
            purpose=purpose,
            reason_code=reason_code,
            authorized_by=user,
            created_at=at,
            updated_at=at,
            review_at=review_at,
            expires_at=expires_at,
        )
        _audit(actor, "privacy.hold", hold.id, reason_code)
        return hold.id


def release_hold(
    actor: AccountActor,
    hold_uuid: UUID,
    expected_version: int,
    reason_code: str,
    step_up_id: UUID,
    at: datetime,
    *,
    subject_validator: Callable[[ValidatedRecordSubject], bool] | None = None,
) -> None:
    _time(at)
    with transaction.atomic():
        user = locked_actor(actor, "staff.command", at)
        candidate = RecordHold.objects.filter(pk=hold_uuid).first()
        if candidate is None or reason_code != "hold_released":
            raise PermissionDenied("Hold action denied")
        require_staff(
            user, "privacy_operations", candidate.case_uuid, step_up_id, reason_code, at
        )
        if subject_validator is not None:
            _validate_subject(
                ValidatedRecordSubject(
                    candidate.subject_kind,
                    candidate.subject_uuid,
                    candidate.owner_uuid,
                    candidate.subject_version,
                ),
                subject_validator,
            )
        hold = RecordHold.objects.select_for_update().get(pk=hold_uuid)
        if (
            type(expected_version) is not int
            or hold.version != expected_version
            or hold.released_at is not None
            or at < hold.created_at
        ):
            raise PermissionDenied("Hold action denied")
        hold.released_at = at
        hold.updated_at = at
        hold.version += 1
        hold.save(update_fields=["released_at", "updated_at", "version"])
        _audit(actor, "privacy.hold", hold.id, reason_code)


def create_policy(
    actor: AccountActor,
    policy_uuid: UUID,
    data_class: str,
    purpose: str,
    reason_code: str,
    step_up_id: UUID,
    at: datetime,
) -> UUID:
    _time(at)
    if (
        not isinstance(policy_uuid, UUID)
        or any(
            not isinstance(value, str)
            or re.fullmatch(r"[a-z][a-z0-9_]{0,31}", value) is None
            for value in (data_class, purpose)
        )
        or reason_code != "policy_approved"
    ):
        raise ValueError("Invalid policy metadata")
    with transaction.atomic():
        user = locked_actor(actor, "staff.command", at)
        require_staff(
            user, "privacy_operations", policy_uuid, step_up_id, reason_code, at
        )
        row = RetentionPolicy.objects.create(
            id=policy_uuid,
            data_class=data_class,
            purpose=purpose,
            created_at=at,
            updated_at=at,
        )
        _audit(actor, "privacy.policy", row.id, reason_code)
        return row.id


def approve_policy(
    actor: AccountActor,
    policy_uuid: UUID,
    expected_version: int,
    duration_seconds: int,
    backup_reference: str,
    reason_code: str,
    step_up_id: UUID,
    at: datetime,
) -> None:
    _time(at)
    if (
        type(duration_seconds) is not int
        or not 0 < duration_seconds <= 2**63 - 1
        or not isinstance(backup_reference, str)
        or re.fullmatch(r"[A-Za-z0-9_.:-]{1,64}", backup_reference) is None
        or reason_code != "policy_approved"
    ):
        raise ValueError("Approved duration and backup reference required")
    with transaction.atomic():
        user = locked_actor(actor, "staff.command", at)
        require_staff(
            user, "privacy_operations", policy_uuid, step_up_id, reason_code, at
        )
        row = RetentionPolicy.objects.select_for_update().filter(pk=policy_uuid).first()
        if (
            not row
            or type(expected_version) is not int
            or row.version != expected_version
            or row.status != "draft"
            or at < row.created_at
        ):
            raise PermissionDenied("Policy action denied")
        row.duration_seconds, row.backup_reference = duration_seconds, backup_reference
        row.status, row.approved_by, row.approved_at = "approved", user, at
        row.updated_at = at
        row.version += 1
        row.save(
            update_fields=[
                "duration_seconds",
                "backup_reference",
                "status",
                "approved_by",
                "approved_at",
                "updated_at",
                "version",
            ]
        )
        _audit(actor, "privacy.policy", row.id, reason_code)


def activate_policy(
    actor: AccountActor,
    policy_uuid: UUID,
    expected_version: int,
    reason_code: str,
    step_up_id: UUID,
    at: datetime,
) -> None:
    _time(at)
    if reason_code != "policy_approved":
        raise PermissionDenied("Policy action denied")
    with transaction.atomic():
        user = locked_actor(actor, "staff.command", at)
        require_staff(
            user, "privacy_operations", policy_uuid, step_up_id, reason_code, at
        )
        row = RetentionPolicy.objects.select_for_update().filter(pk=policy_uuid).first()
        if (
            not row
            or type(expected_version) is not int
            or row.version != expected_version
            or row.status != "approved"
            or row.approved_at is None
            or at < row.approved_at
        ):
            raise PermissionDenied("Policy action denied")
        # Preserve effective policies; supersession requires a reviewed command.
        if RetentionPolicy.objects.filter(
            data_class=row.data_class, purpose=row.purpose, status="effective"
        ).exists():
            raise PermissionDenied("Policy action denied")
        row.status, row.effective_at, row.updated_at = "effective", at, at
        row.version += 1
        row.save(update_fields=["status", "effective_at", "updated_at", "version"])
        _audit(actor, "privacy.policy", row.id, reason_code)
