"""Checked recovery composition; providers and governance stay outside accounts."""

from datetime import datetime
from uuid import UUID

from django.core.exceptions import PermissionDenied
from django.db import IntegrityError

from apps.accounts import otp, recovery
from apps.accounts.contracts import (
    IdentityChangeResult,
    OtpProofResult,
    OtpRequestResult,
)
from apps.accounts.sessions import AccountActor, locked_actor
from apps.accounts.sms import SmsProvider, configured_provider
from apps.governance.outbox import append_outbox
from apps.governance.staff import require_staff

from .identity import record_security_outcome


def authorize(
    actor: AccountActor, case: UUID, step: UUID, reason: str, at: datetime
) -> None:
    try:
        user = locked_actor(actor, "staff.command", at)
        require_staff(user, "account_recovery", case, step, reason, at)
    except PermissionDenied:
        raise PermissionError("Staff authority denied") from None


def open_recovery(
    old_phone: str,
    new_phone: str,
    ip: str,
    at: datetime,
    *,
    contact_preference: str = "new_phone",
):
    if contact_preference != "new_phone":
        raise ValueError("Invalid contact preference")
    return recovery.open_recovery(old_phone, new_phone, ip, at, record_security_outcome)


def receipt_status(request_uuid: UUID, receipt: str, at: datetime) -> str:
    return recovery.recovery_status(request_uuid, receipt, at)


def _recorder(actor: AccountActor):
    return lambda outcome: record_security_outcome(outcome, actor_uuid=actor.user_uuid)


def assign_recovery(
    actor: AccountActor,
    request_uuid: UUID,
    expected_version: int,
    staff_uuid: UUID,
    step_up_id: UUID,
    reason_code: str,
    at: datetime,
) -> None:
    recovery.assign_recovery(
        actor,
        request_uuid,
        expected_version,
        staff_uuid,
        step_up_id,
        reason_code,
        at,
        _recorder(actor),
        authorize=authorize,
    )


def resolve_recovery(
    actor: AccountActor,
    request_uuid: UUID,
    expected_version: int,
    step_up_id: UUID,
    reason_code: str,
    at: datetime,
) -> None:
    recovery.resolve_recovery(
        actor,
        request_uuid,
        expected_version,
        step_up_id,
        reason_code,
        at,
        _recorder(actor),
        authorize=authorize,
    )


def add_recovery_evidence(
    actor: AccountActor,
    request_uuid: UUID,
    expected_version: int,
    classification: str,
    outcome: str,
    checksum: str,
    reference: UUID,
    step_up_id: UUID,
    reason_code: str,
    at: datetime,
) -> UUID:
    return recovery.add_recovery_evidence(
        actor,
        request_uuid,
        expected_version,
        classification,
        outcome,
        checksum,
        reference,
        step_up_id,
        reason_code,
        at,
        _recorder(actor),
        authorize=authorize,
    )


def decide_recovery(
    actor: AccountActor,
    request_uuid: UUID,
    expected_version: int,
    decision: str,
    reason_code: str,
    step_up_id: UUID,
    at: datetime,
) -> None:
    recovery.decide_recovery(
        actor,
        request_uuid,
        expected_version,
        decision,
        reason_code,
        step_up_id,
        at,
        _recorder(actor),
        authorize=authorize,
    )


def recovery_detail(
    actor: AccountActor,
    request_uuid: UUID,
    step_up_id: UUID,
    reason_code: str,
    at: datetime,
):
    return recovery.recovery_detail(
        actor,
        request_uuid,
        step_up_id,
        reason_code,
        at,
        _recorder(actor),
        authorize=authorize,
    )


def evidence_detail(
    actor: AccountActor,
    request_uuid: UUID,
    evidence_uuid: UUID,
    step_up_id: UUID,
    reason_code: str,
    at: datetime,
):
    return recovery.evidence_detail(
        actor,
        request_uuid,
        evidence_uuid,
        step_up_id,
        reason_code,
        at,
        _recorder(actor),
        authorize=authorize,
    )


def _emit(result: IdentityChangeResult) -> None:
    append_outbox(
        "account.security_changed",
        result.user_uuid,
        result.auth_version,
        {"user_uuid": str(result.user_uuid)},
        f"recovery:{result.context_uuid}",
    )


def apply_recovery(
    actor: AccountActor,
    request_uuid: UUID,
    expected_version: int,
    step_up_id: UUID,
    reason_code: str,
    at: datetime,
) -> IdentityChangeResult:
    try:
        return recovery.apply_recovery(
            actor,
            request_uuid,
            expected_version,
            step_up_id,
            reason_code,
            at,
            _recorder(actor),
            authorize=authorize,
            emit=_emit,
        )
    except IntegrityError:
        # The owned transaction has already rolled back history/proof/auth state.
        raise recovery.RecoveryConflict("Recovery conflict") from None


def request_recovery_otp(
    request_uuid: UUID,
    receipt: str,
    ip: str,
    at: datetime,
    *,
    provider: SmsProvider | None = None,
) -> OtpRequestResult:
    binding = recovery.recovery_binding(request_uuid, receipt, at)
    return otp.request_otp(
        binding.phone,
        ip,
        binding.purpose,
        binding.context_uuid,
        at,
        record_security_outcome,
        provider=provider or configured_provider(),
        binding=binding,
        validate_context=lambda value: recovery.validate_recovery_binding(
            value, receipt, at
        ),
    )


def verify_recovery_otp(
    request_uuid: UUID,
    receipt: str,
    challenge_id: UUID,
    code: str,
    ip: str,
    at: datetime,
) -> OtpProofResult:
    binding = recovery.recovery_binding(request_uuid, receipt, at)
    return otp.verify_otp(
        binding.phone,
        challenge_id,
        code,
        binding.purpose,
        binding.context_uuid,
        ip,
        at,
        record_security_outcome,
        binding=binding,
        validate_context=lambda value: recovery.validate_recovery_binding(
            value, receipt, at
        ),
        on_proof=lambda proof: recovery.record_recovery_proof(
            binding, receipt, proof.challenge_id, at
        ),
    )
