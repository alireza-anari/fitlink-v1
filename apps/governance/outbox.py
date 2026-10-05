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
