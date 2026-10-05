from uuid import UUID

from django.db import transaction

from apps.accounts.contracts import SecurityOutcome

from .audit_models import ACTIONS, CHANGED_FIELDS, REASONS, RESULTS, AuditEvent


def validate_outcome(outcome: SecurityOutcome) -> SecurityOutcome:
    if (
        not isinstance(outcome, SecurityOutcome)
        or outcome.action not in ACTIONS
        or outcome.result not in RESULTS
        or outcome.reason_code not in REASONS
        or not isinstance(outcome.correlation_id, UUID)
        or (
            outcome.subject_uuid is not None
            and not isinstance(outcome.subject_uuid, UUID)
        )
        or not isinstance(outcome.changed_fields, tuple)
        or len(outcome.changed_fields) > len(CHANGED_FIELDS)
        or any(field not in CHANGED_FIELDS for field in outcome.changed_fields)
    ):
        raise ValueError("Invalid audit metadata")
    return outcome


def append_event(
    outcome: SecurityOutcome,
    *,
    actor_uuid: UUID | None = None,
    subject_type: str = "account",
) -> UUID:
    validate_outcome(outcome)
    if not transaction.get_connection().in_atomic_block:
        raise RuntimeError("Audit requires the domain transaction")
    event = AuditEvent.objects.create(
        actor_uuid=actor_uuid,
        actor_kind="user" if actor_uuid else "system",
        action=outcome.action,
        result=outcome.result,
        subject_type=subject_type,
        subject_uuid=outcome.subject_uuid,
        correlation_id=outcome.correlation_id,
        reason_code=outcome.reason_code,
        changed_fields=list(outcome.changed_fields),
    )
    return event.id
