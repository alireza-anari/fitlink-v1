"""Trusted Task 7 intake, assignment and metadata-only governance wiring."""

from apps.accounts.contracts import SecurityOutcome
from apps.accounts.sessions import AccountActor
from apps.governance import audit
from apps.governance.outbox import append_outbox
from apps.professionals.verification_models import Verification


def binding_hooks(actor: AccountActor):
    def record(outcome: SecurityOutcome) -> None:
        audit.append_event(
            outcome, actor_uuid=actor.user_uuid, subject_type="verification"
        )

    def emit(case: Verification) -> None:
        append_outbox(
            "verification.changed",
            case.id,
            case.version,
            {
                "verification_uuid": str(case.id),
                "user_uuid": str(case.profile.user.public_id),
            },
            f"verification.changed:{case.id}:{case.version}",
        )

    return record, emit


def prepare_verification(
    actor, requested_targets, expected_profile_version, operation_id, at
):
    from apps.professionals import verification

    from .professional_profile import _safe_asset

    record, emit = binding_hooks(actor)
    return verification.prepare_verification(
        actor,
        requested_targets,
        expected_profile_version,
        operation_id,
        at,
        record=record,
        emit=emit,
        asset_validator=_safe_asset,
    )


def submit_verification(actor, verification_uuid, expected_version, operation_id, at):
    from apps.professionals import verification

    from .professional_profile import _safe_asset

    record, emit = binding_hooks(actor)
    return verification.submit_verification(
        actor,
        verification_uuid,
        expected_version,
        operation_id,
        at,
        record=record,
        emit=emit,
        asset_validator=_safe_asset,
    )


def withdraw_verification_target(
    actor, verification_uuid, target_uuid, expected_version, operation_id, at
):
    from apps.professionals import verification

    record, emit = binding_hooks(actor)
    return verification.withdraw_verification_target(
        actor,
        verification_uuid,
        target_uuid,
        expected_version,
        operation_id,
        at,
        record=record,
        emit=emit,
    )


def assign_verification(
    actor,
    verification_uuid,
    assignee_uuid,
    expected_version,
    step_up_id,
    reason_code,
    at,
):
    from apps.professionals import verification

    record, emit = binding_hooks(actor)
    return verification.assign_verification(
        actor,
        verification_uuid,
        assignee_uuid,
        expected_version,
        step_up_id,
        reason_code,
        at,
        record=record,
        emit=emit,
    )


def start_verification_review(
    actor, verification_uuid, expected_version, step_up_id, reason_code, at
):
    from apps.professionals import verification

    record, emit = binding_hooks(actor)
    return verification.start_verification_review(
        actor,
        verification_uuid,
        expected_version,
        step_up_id,
        reason_code,
        at,
        record=record,
        emit=emit,
    )
