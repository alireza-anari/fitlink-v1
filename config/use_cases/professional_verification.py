"""Trusted Task 7 intake, assignment and metadata-only governance wiring."""

from apps.accounts.contracts import SecurityOutcome
from apps.accounts.sessions import AccountActor
from apps.governance import audit
from apps.governance.outbox import append_outbox
from apps.professionals.verification_models import Verification


def append_event(*args, **kwargs):
    """Preserve the trusted binding audit seam and current audit implementation."""
    return audit.append_event(*args, **kwargs)


def binding_hooks(actor: AccountActor):
    def record(outcome: SecurityOutcome) -> None:
        append_event(outcome, actor_uuid=actor.user_uuid, subject_type="verification")

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


def decide_verification_target(
    actor,
    verification_uuid,
    target_uuid,
    decision,
    expected_case_version,
    expected_target_version,
    expected_binding,
    step_up_id,
    reason_code,
    explanation,
    operation_id,
    at,
):
    from apps.professionals import verification

    from .professional_profile import _safe_asset

    record, emit = binding_hooks(actor)
    return verification.decide_verification_target(
        actor,
        verification_uuid,
        target_uuid,
        decision,
        expected_case_version,
        expected_target_version,
        expected_binding,
        step_up_id,
        reason_code,
        explanation,
        operation_id,
        at,
        record=record,
        emit=emit,
        asset_validator=_safe_asset,
    )


def revoke_verification_target(
    actor,
    verification_uuid,
    target_uuid,
    effective_approval_uuid,
    expected_case_version,
    expected_target_version,
    expected_binding,
    step_up_id,
    reason_code,
    explanation,
    operation_id,
    at,
):
    from apps.professionals import verification

    from .professional_profile import _safe_asset

    record, emit = binding_hooks(actor)
    return verification.revoke_verification_target(
        actor,
        verification_uuid,
        target_uuid,
        effective_approval_uuid,
        expected_case_version,
        expected_target_version,
        expected_binding,
        step_up_id,
        reason_code,
        explanation,
        operation_id,
        at,
        record=record,
        emit=emit,
        asset_validator=_safe_asset,
    )


def restrict_professional_role(
    actor,
    verification_uuid,
    role_uuid,
    expected_case_version,
    expected_role_version,
    expected_restriction_token,
    step_up_id,
    reason_code,
    operation_id,
    at,
):
    from apps.professionals import restrictions

    record, emit = binding_hooks(actor)
    return restrictions.restrict_professional_role(
        actor,
        verification_uuid,
        role_uuid,
        expected_case_version,
        expected_role_version,
        expected_restriction_token,
        step_up_id,
        reason_code,
        operation_id,
        at,
        record=record,
        emit=emit,
    )


def release_professional_role_restriction(
    actor,
    verification_uuid,
    role_uuid,
    expected_case_version,
    expected_role_version,
    expected_restriction_token,
    step_up_id,
    reason_code,
    operation_id,
    at,
):
    from apps.professionals import restrictions

    record, emit = binding_hooks(actor)
    return restrictions.release_professional_role_restriction(
        actor,
        verification_uuid,
        role_uuid,
        expected_case_version,
        expected_role_version,
        expected_restriction_token,
        step_up_id,
        reason_code,
        operation_id,
        at,
        record=record,
        emit=emit,
    )
