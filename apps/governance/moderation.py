"""Serialized, bounded reporting and case-bound capability decisions."""

import hashlib
import json
from datetime import UTC, datetime, timedelta

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils import timezone

from apps.accounts.contracts import SecurityOutcome
from apps.accounts.sessions import AccountActor, locked_actor

from .audit import append_event
from .moderation_contracts import (
    ModerationDTO,
    ReportReceipt,
    validate_decision_command,
    validate_report_command,
)
from .moderation_models import (
    ModerationCase,
    ModerationHistory,
    PublicContentOperation,
    PublicContentReport,
)
from .outbox import append_outbox
from .staff import require_staff


def _staff(*args):
    try:
        return require_staff(*args)
    except PermissionDenied:
        raise PermissionError("Public moderation unavailable") from None


def context(actor, at):
    if not isinstance(at, datetime) or not timezone.is_aware(at):
        raise ValueError("Invalid moderation time")
    if not isinstance(actor, AccountActor):
        raise PermissionError("Account action denied")


def digest(command, values):
    return hashlib.sha256(
        json.dumps([command, values], sort_keys=True, default=str).encode()
    ).hexdigest()


def replay(user, operation, command, hash_value):
    old = PublicContentOperation.objects.filter(
        actor=user, operation_id=operation
    ).first()
    if old and (old.command != command or old.request_hash != hash_value):
        raise ValueError("Public content command conflict")
    return old


def remember(user, operation, command, hash_value, identifier, version, state, at):
    PublicContentOperation.objects.create(
        actor=user,
        operation_id=operation,
        command=command,
        request_hash=hash_value,
        result_uuid=identifier,
        resulting_version=version,
        resulting_state=state,
        created_at=at,
        updated_at=at,
    )


def audit(user, action, identifier, operation, at, reason="user_requested"):
    append_event(
        SecurityOutcome(
            "moderation." + action,
            "succeeded",
            identifier,
            operation,
            ("version", "state"),
            reason,
        ),
        actor_uuid=user.public_id,
        subject_type="moderation",
    )


def report_public_content(
    actor, target, reason, operation_id, at, *, target_source, lock_target
):
    validate_report_command(target, reason, operation_id)
    context(actor, at)
    now = max(at, timezone.now())
    hashed = digest("report", [target.kind, target.object_uuid, reason])
    with transaction.atomic():
        lock_target(actor, target)
        user = locked_actor(actor, "marketplace.report", now)
        old = replay(user, operation_id, "report", hashed)
        if old:
            return ReportReceipt(old.result_uuid)
        source = target_source(target, now)
        if source is None:
            raise LookupError("Content unavailable")
        owner_id, revision_uuid = source
        case, _ = ModerationCase.objects.get_or_create(
            target_kind=target.kind,
            target_uuid=target.object_uuid,
            revision_uuid=revision_uuid,
            defaults={"owner_id": owner_id, "created_at": now, "updated_at": now},
        )
        case = ModerationCase.objects.select_for_update().get(pk=case.id)
        # A moderator who reports their own case loses decision authority. Never
        # create an implicit reassignment; a separate current claim is required.
        if case.assigned_staff_id == user.pk:
            raise PermissionError("Public moderation conflict")
        row = PublicContentReport.objects.filter(case=case, reporter=user).first()
        if row is None:
            midnight = now.astimezone(UTC).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            if (
                PublicContentReport.objects.filter(
                    reporter=user,
                    created_at__gte=midnight,
                    created_at__lt=midnight + timedelta(days=1),
                ).count()
                >= 5
            ):
                raise PermissionError("Report quota exceeded")
            row = PublicContentReport.objects.create(
                case=case, reporter=user, reason=reason, created_at=now, updated_at=now
            )
            audit(user, "reported", row.id, operation_id, now)
        remember(user, operation_id, "report", hashed, row.id, 1, "received", now)
        return ReportReceipt(row.id)


def _authority(actor, case_uuid, version, step, reason, operation, at, lock_case):
    context(actor, at)
    lock_case(actor, case_uuid)
    user = locked_actor(actor, "staff.command", at)
    _staff(
        user, "marketplace_moderation", case_uuid, step, reason, max(at, timezone.now())
    )
    case = ModerationCase.objects.select_for_update().filter(pk=case_uuid).first()
    if case is None:
        raise LookupError("Moderation unavailable")
    if case.owner_id == user.pk or case.reports.filter(reporter=user).exists():
        raise PermissionError("Public moderation conflict")
    return user, case


def moderation_queue(actor, step_up_id, reason_code, at, *, limit=25, cursor=None):
    from uuid import UUID

    from django.core import signing
    from django.db.models import Q

    from .moderation_contracts import ModerationPage

    if (
        type(limit) is not int
        or not 1 <= limit <= 25
        or (cursor is not None and (not isinstance(cursor, str) or len(cursor) > 2048))
    ):
        raise ValueError("Invalid moderation page")
    context(actor, at)
    boundary = None
    if cursor is not None:
        try:
            data = signing.loads(cursor, salt="c04-public-moderation", max_age=900)
            if set(data) != {"actor", "at", "id"} or data["actor"] != str(
                actor.user_uuid
            ):
                raise ValueError
            stamp = datetime.fromisoformat(data["at"])
            if not timezone.is_aware(stamp):
                raise ValueError
            boundary = (stamp, UUID(data["id"]))
        except (ValueError, TypeError, KeyError, signing.BadSignature):
            raise ValueError("Invalid moderation cursor") from None
    with transaction.atomic():
        now = max(at, timezone.now())
        user = locked_actor(actor, "staff.command", now)
        _staff(
            user,
            "marketplace_moderation",
            None,
            step_up_id,
            reason_code,
            max(now, timezone.now()),
        )
        query = ModerationCase.objects.exclude(owner=user).exclude(
            reports__reporter=user
        )
        if boundary:
            stamp, identifier = boundary
            query = query.filter(
                Q(created_at__gt=stamp) | Q(created_at=stamp, id__gt=identifier)
            )
        rows = list(query.order_by("created_at", "id")[: limit + 1])
        following = None
        if len(rows) > limit:
            last = rows[limit - 1]
            following = signing.dumps(
                {
                    "actor": str(user.public_id),
                    "at": last.created_at.isoformat(),
                    "id": str(last.id),
                },
                salt="c04-public-moderation",
            )
        return ModerationPage(
            tuple(ModerationDTO(r.id, r.version, r.state) for r in rows[:limit]),
            following,
        )


def read_public_moderation(actor, case_uuid, step_up_id, reason_code, at, *, lock_case):
    context(actor, at)
    with transaction.atomic():
        user, case = _authority(
            actor,
            case_uuid,
            None,
            step_up_id,
            reason_code,
            None,
            max(at, timezone.now()),
            lock_case,
        )
        if case.assigned_staff_id != user.pk:
            raise PermissionError("Assigned moderator required")
        return ModerationDTO(case.id, case.version, case.state)


def _complete(user, case, action, operation, hashed, reason, at):
    case.version += 1
    case.updated_at = at
    case.save()
    ModerationHistory.objects.create(
        case=case,
        actor=user,
        operation_id=operation,
        action=action,
        resulting_version=case.version,
        reason_code=reason,
        created_at=at,
        updated_at=at,
    )
    remember(user, operation, action, hashed, case.id, case.version, case.state, at)
    audit(
        user, "claimed" if action == "claim" else action, case.id, operation, at, reason
    )
    append_outbox(
        "marketplace.moderation_changed",
        case.id,
        case.version,
        {"moderation_uuid": str(case.id), "user_uuid": str(case.owner.public_id)},
        f"marketplace.moderation_changed:{case.id}:{case.version}",
    )
    return ModerationDTO(case.id, case.version, case.state)


def claim_public_moderation(
    actor,
    case_uuid,
    expected_version,
    step_up_id,
    reason_code,
    operation_id,
    at,
    *,
    lock_case,
):
    validate_decision_command(
        case_uuid, expected_version, "hide", step_up_id, operation_id
    )
    context(actor, at)
    now = max(at, timezone.now())
    hashed = digest("claim", [case_uuid, expected_version, step_up_id, reason_code])
    with transaction.atomic():
        user, case = _authority(
            actor,
            case_uuid,
            expected_version,
            step_up_id,
            reason_code,
            operation_id,
            now,
            lock_case,
        )
        old = replay(user, operation_id, "claim", hashed)
        if old:
            return ModerationDTO(
                old.result_uuid, old.resulting_version, old.resulting_state
            )
        if case.version != expected_version or case.assigned_staff_id not in {
            None,
            user.pk,
        }:
            raise ValueError("Moderation version conflict")
        case.assigned_staff = user
        return _complete(user, case, "claim", operation_id, hashed, reason_code, now)


def decide_public_moderation(
    actor,
    case_uuid,
    expected_version,
    action,
    step_up_id,
    reason_code,
    operation_id,
    at,
    *,
    lock_case,
    apply_decision,
):
    validate_decision_command(
        case_uuid, expected_version, action, step_up_id, operation_id
    )
    context(actor, at)
    now = max(at, timezone.now())
    hashed = digest(action, [case_uuid, expected_version, step_up_id, reason_code])
    with transaction.atomic():
        user, case = _authority(
            actor,
            case_uuid,
            expected_version,
            step_up_id,
            reason_code,
            operation_id,
            now,
            lock_case,
        )
        if case.assigned_staff_id != user.pk:
            raise PermissionError("Assigned moderator required")
        old = replay(user, operation_id, action, hashed)
        if old:
            return ModerationDTO(
                old.result_uuid, old.resulting_version, old.resulting_state
            )
        if (
            case.version != expected_version
            or (action == "restore" and case.state != "hidden")
            or (action != "restore" and case.state == "hidden")
        ):
            raise ValueError("Moderation version conflict")
        apply_decision(case, action, now)
        case.state = {"hide": "hidden", "dismiss": "dismissed", "restore": "restored"}[
            action
        ]
        return _complete(user, case, action, operation_id, hashed, reason_code, now)
