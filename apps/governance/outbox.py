import re
from uuid import UUID

from django.db import transaction

from .outbox_models import EVENT_TYPES, OutboxEvent

PAYLOAD_FIELDS = {
    "account.security_changed": frozenset({"user_uuid"}),
    "consent.granted": frozenset({"consent_uuid", "user_uuid"}),
    "consent.revoked": frozenset({"consent_uuid", "user_uuid"}),
    "privacy.intake_recorded": frozenset({"privacy_uuid", "user_uuid"}),
    "feature_flag.changed": frozenset({"flag_uuid"}),
    "athlete.baseline_changed": frozenset({"baseline_uuid", "user_uuid"}),
    "professional.profile_changed": frozenset({"profile_uuid", "user_uuid"}),
    "verification.changed": frozenset({"verification_uuid", "user_uuid"}),
    "asset.processing_requested": frozenset({"asset_uuid", "user_uuid"}),
    "asset.cleanup_requested": frozenset({"asset_uuid", "user_uuid"}),
    "assistant.membership_changed": frozenset({"membership_uuid", "user_uuid"}),
}


def validate_event(
    event_type: str, aggregate_uuid: UUID, version: int, payload: dict, dedup_key: str
) -> None:
    try:
        valid = (
            event_type in EVENT_TYPES
            and isinstance(aggregate_uuid, UUID)
            and type(version) is int
            and version >= 1
            and isinstance(payload, dict)
            and set(payload) <= PAYLOAD_FIELDS[event_type]
            and isinstance(dedup_key, str)
            and len(dedup_key) <= 160
            and re.fullmatch(r"[a-zA-Z0-9_:.-]+", dedup_key)
        )
        if not valid:
            raise ValueError
        for value in payload.values():
            if not isinstance(value, str) or str(UUID(value)) != value:
                raise ValueError
    except (ValueError, TypeError, KeyError, AttributeError):
        raise ValueError("Invalid outbox metadata") from None


def append_outbox(
    event_type: str, aggregate_uuid: UUID, version: int, payload: dict, dedup_key: str
) -> UUID:
    validate_event(event_type, aggregate_uuid, version, payload, dedup_key)
    if not transaction.get_connection().in_atomic_block:
        raise RuntimeError("Outbox requires the domain transaction")
    event, _ = OutboxEvent.objects.get_or_create(
        dedup_key=dedup_key,
        defaults={
            "event_type": event_type,
            "aggregate_uuid": aggregate_uuid,
            "aggregate_version": version,
            "payload": payload,
        },
    )
    if (
        event.event_type,
        event.aggregate_uuid,
        event.aggregate_version,
        event.payload,
    ) != (event_type, aggregate_uuid, version, payload):
        raise ValueError("Outbox dedup conflict")
    return event.id


def retry_seconds(attempt: int) -> int:
    if type(attempt) is not int or not 1 <= attempt <= 8:
        raise ValueError("Invalid retry attempt")
    return min(5 * 2 ** (attempt - 1), 300)


def validate_dispatch(
    event_type: str, schema: int, aggregate_uuid: UUID, version: int, payload: dict
) -> None:
    validate_event(event_type, aggregate_uuid, version, payload, "dispatch")
    if (
        type(schema) is not int
        or schema != 1
        or set(payload) != PAYLOAD_FIELDS[event_type]
    ):
        raise ValueError("Invalid dispatch envelope")
    aggregate_field = {
        "account.security_changed": "user_uuid",
        "consent.granted": "consent_uuid",
        "consent.revoked": "consent_uuid",
        "privacy.intake_recorded": "privacy_uuid",
        "feature_flag.changed": "flag_uuid",
        "athlete.baseline_changed": "baseline_uuid",
        "professional.profile_changed": "profile_uuid",
        "verification.changed": "verification_uuid",
        "asset.processing_requested": "asset_uuid",
        "asset.cleanup_requested": "asset_uuid",
        "assistant.membership_changed": "membership_uuid",
    }[event_type]
    if payload[aggregate_field] != str(aggregate_uuid):
        raise ValueError("Invalid dispatch aggregate")


def enqueue_event(event_uuid: UUID, lease_uuid: UUID) -> None:
    from .tasks import deliver_event

    deliver_event.apply_async(args=[str(event_uuid), str(lease_uuid)], retry=False)


def _fail(event_uuid, lease_uuid, at, code, *, fatal=False):
    from datetime import timedelta

    with transaction.atomic():
        row = (
            OutboxEvent.objects.select_for_update()
            .filter(pk=event_uuid, state="leased", lease_uuid=lease_uuid)
            .first()
        )
        if not row:
            return
        row.lease_uuid = row.lease_until = None
        row.last_error_code = code
        if fatal or row.attempts >= 8:
            row.state, row.exhausted_at = "exhausted", at
        else:
            row.state = "pending"
            row.available_at = at + timedelta(seconds=retry_seconds(row.attempts))
        row.save(
            update_fields=[
                "lease_uuid",
                "lease_until",
                "last_error_code",
                "state",
                "exhausted_at",
                "available_at",
            ]
        )


def scan_outbox(at, batch_size: int = 100) -> int:
    from datetime import timedelta
    from uuid import uuid4

    from django.db.models import Q
    from django.utils import timezone

    if (
        type(batch_size) is not int
        or not 1 <= batch_size <= 100
        or not timezone.is_aware(at)
    ):
        raise ValueError("Invalid bounded scan")
    if transaction.get_connection().in_atomic_block:
        raise RuntimeError("Scanner requires its own commit boundary")
    claimed = []
    with transaction.atomic():
        eligible = (
            OutboxEvent.objects.select_for_update(skip_locked=True)
            .filter(
                Q(state="pending", available_at__lte=at)
                | Q(state="leased", lease_until__lte=at)
            )
            .order_by("available_at", "id")[:batch_size]
        )
        for row in eligible:
            if row.attempts >= 8:
                row.state, row.exhausted_at = "exhausted", at
                row.lease_uuid = row.lease_until = None
                row.last_error_code = "attempts_exhausted"
                row.save(
                    update_fields=[
                        "state",
                        "exhausted_at",
                        "lease_uuid",
                        "lease_until",
                        "last_error_code",
                    ]
                )
                continue
            row.state, row.lease_uuid = "leased", uuid4()
            row.lease_until = at + timedelta(seconds=60)
            row.attempts += 1
            row.save(update_fields=["state", "lease_uuid", "lease_until", "attempts"])
            claimed.append((row.id, row.lease_uuid))
    for event_id, lease_id in claimed:
        try:
            enqueue_event(event_id, lease_id)
        except Exception:
            # Persist a bounded code, never arbitrary exception/provider details.
            _fail(event_id, lease_id, at, "broker_unavailable")
    return len(claimed)


def dispatch_event(event_uuid: UUID, at, *, lease_uuid: UUID) -> bool:
    from django.utils import timezone

    from apps.accounts.models import User
    from config.event_handlers import HANDLERS

    from .outbox_models import OutboxDeliveryReceipt

    if (
        not isinstance(event_uuid, UUID)
        or not isinstance(lease_uuid, UUID)
        or not timezone.is_aware(at)
    ):
        raise ValueError("Invalid dispatch IDs")
    if transaction.get_connection().in_atomic_block:
        raise RuntimeError("Dispatch requires its own commit boundary")
    try:
        with transaction.atomic():
            candidate = OutboxEvent.objects.filter(pk=event_uuid).first()
            if not candidate:
                return False
            if candidate.state == "sent":
                return True
            # User precedes outbox/receipt locks, matching domain and staff retries.
            owner_id = candidate.payload.get("user_uuid")
            if owner_id:
                list(
                    User.objects.select_for_update()
                    .filter(public_id=owner_id)
                    .order_by("id")
                )
            row = OutboxEvent.objects.select_for_update().get(pk=event_uuid)
            if row.state == "sent":
                return True
            if (
                row.state != "leased"
                or row.lease_uuid != lease_uuid
                or row.lease_until is None
                or at >= row.lease_until
            ):
                return False
            try:
                validate_dispatch(
                    row.event_type,
                    row.schema_version,
                    row.aggregate_uuid,
                    row.aggregate_version,
                    row.payload,
                )
                handler = HANDLERS[row.event_type]
            except (ValueError, KeyError):
                raise InvalidDispatch from None
            effect_key = f"{row.aggregate_uuid}:{row.aggregate_version}"
            receipt = OutboxDeliveryReceipt.objects.filter(
                handler=row.event_type, effect_key=effect_key
            ).first()
            if receipt is None:
                result = handler(row, at)
                OutboxDeliveryReceipt.objects.create(
                    event=row,
                    handler=row.event_type,
                    effect_key=effect_key,
                    result=result,
                    completed_at=at,
                )
            row.state, row.dispatched_at = "sent", at
            row.lease_uuid = row.lease_until = None
            row.last_error_code = ""
            row.save(
                update_fields=[
                    "state",
                    "dispatched_at",
                    "lease_uuid",
                    "lease_until",
                    "last_error_code",
                ]
            )
            return True
    except InvalidDispatch:
        _fail(event_uuid, lease_uuid, at, "invalid_event", fatal=True)
    except Exception:
        _fail(event_uuid, lease_uuid, at, "handler_unavailable")
    return False


class InvalidDispatch(ValueError):
    pass


def retry_exhausted(
    actor,
    event_uuid: UUID,
    expected_attempts: int,
    step_up_id: UUID,
    reason_code: str,
    at,
) -> None:
    from uuid import uuid4

    from django.core.exceptions import PermissionDenied

    from apps.accounts.contracts import SecurityOutcome
    from apps.accounts.sessions import locked_actor

    from .audit import append_event
    from .staff import require_staff

    with transaction.atomic():
        user = locked_actor(actor, "staff.command", at)
        require_staff(user, "security_audit", event_uuid, step_up_id, reason_code, at)
        row = OutboxEvent.objects.select_for_update().get(pk=event_uuid)
        if (
            reason_code != "operator_retry"
            or type(expected_attempts) is not int
            or row.state != "exhausted"
            or row.attempts != expected_attempts
        ):
            raise PermissionDenied("Retry denied")
        validate_dispatch(
            row.event_type,
            row.schema_version,
            row.aggregate_uuid,
            row.aggregate_version,
            row.payload,
        )
        row.state, row.attempts, row.available_at = "pending", 0, at
        row.exhausted_at = None
        row.last_error_code = ""
        row.save(
            update_fields=[
                "state",
                "attempts",
                "available_at",
                "exhausted_at",
                "last_error_code",
            ]
        )
        append_event(
            SecurityOutcome(
                "outbox.retry", "succeeded", row.id, uuid4(), ("status",), reason_code
            ),
            actor_uuid=user.public_id,
            subject_type="outbox",
        )
