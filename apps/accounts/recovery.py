"""Receipt capabilities reveal no old-account identity or staff decision reason."""

import hmac
import re
import secrets
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import datetime, timedelta
from uuid import UUID

from django.conf import settings
from django.db import models, transaction

from .contracts import (
    IdentityChangeResult,
    OutcomeRecorder,
    RecoveryReceipt,
    SecurityOutcome,
)
from .limiter import canonical_ip, reserve_admission
from .models import User
from .otp import OtpBinding, OtpThrottled
from .phone import normalize_iranian_mobile
from .recovery_models import (
    EVIDENCE_OUTCOMES,
    EVIDENCE_TYPES,
    PhoneChangeHistory,
    RecoveryEvidenceMetadata,
    RecoveryRequest,
)
from .security_keys import security_digest
from .security_models import OTPChallenge, OTPPhoneState
from .sessions import AccountActor
from .state import invalidate_auth_locked


class RecoveryUnavailable(RuntimeError):
    pass


class RecoveryNotFound(LookupError):
    pass


class RecoveryConflict(PermissionError):
    pass


def ensure_recovery_enabled(at: datetime) -> None:
    if at.tzinfo is None or at.utcoffset() is None:
        raise ValueError("Required recovery time")
    if (
        not settings.ACCOUNT_SECURITY.staff_recovery_enabled
        or settings.SETTINGS_ENV not in {"test", "development"}
    ):
        # No approved operational evidence/MFA production adapter exists in C02.
        raise RecoveryUnavailable("Recovery unavailable")


def normalize_recovery_phones(old: str, new: str) -> tuple[str, str]:
    old, new = normalize_iranian_mobile(old), normalize_iranian_mobile(new)
    if old == new:
        raise ValueError("Distinct recovery phones required")
    return old, new


def validate_evidence_metadata(
    classification: str, outcome: str, checksum: str, reference: UUID
) -> None:
    if (
        classification not in EVIDENCE_TYPES
        or outcome not in EVIDENCE_OUTCOMES
        or not isinstance(checksum, str)
        or not re.fullmatch(r"[0-9a-f]{64}", checksum)
        or not isinstance(reference, UUID)
    ):
        raise ValueError("Invalid evidence metadata")


def open_recovery(
    old_phone: str, new_phone: str, ip: str, at: datetime, record: OutcomeRecorder
) -> RecoveryReceipt:
    ensure_recovery_enabled(at)
    if not callable(record):
        raise ValueError("Required recovery recorder")
    if transaction.get_connection().in_atomic_block:
        raise RecoveryUnavailable("Recovery unavailable")
    old, new = normalize_recovery_phones(old_phone, new_phone)
    admitted = reserve_admission(old, canonical_ip(ip), "recovery_intake", at)
    if not admitted.allowed:
        raise OtpThrottled(admitted.retry_after)
    raw = secrets.token_urlsafe(32)
    key_id = settings.ACCOUNT_SECURITY.keys.active_id
    with transaction.atomic():
        case = RecoveryRequest.objects.create(
            claimed_old_phone=old,
            proposed_new_phone=new,
            receipt_key_id=key_id,
            receipt_digest=security_digest("receipt", raw, key_id),
            created_at=at,
            receipt_expires_at=at
            + timedelta(
                seconds=settings.ACCOUNT_SECURITY.policy.recovery_receipt_seconds
            ),
        )
        record(SecurityOutcome("recovery.requested", "accepted", None, case.id))
    return RecoveryReceipt(case.id, raw)


def receipt_case(
    request_uuid: UUID, receipt: str, at: datetime, *, lock: bool = False
) -> RecoveryRequest:
    ensure_recovery_enabled(at)
    query = (
        RecoveryRequest.objects.select_for_update()
        if lock
        else RecoveryRequest.objects.all()
    )
    case = query.filter(pk=request_uuid).first()
    ring = settings.ACCOUNT_SECURITY.keys
    retained = bool(case and case.receipt_key_id in ring.key_ids)
    key = case.receipt_key_id if case and retained else ring.active_id
    bounded = isinstance(receipt, str) and bool(
        re.fullmatch(r"[A-Za-z0-9_-]{43}", receipt)
    )
    digest = security_digest("receipt", receipt if bounded else "invalid", key)
    matched = hmac.compare_digest(digest, case.receipt_digest if case else "0" * 64)
    if not (
        case
        and retained
        and bounded
        and matched
        and case.created_at <= at < case.receipt_expires_at
    ):
        raise RecoveryNotFound("Recovery unavailable")
    return case


def recovery_status(request_uuid: UUID, receipt: str, at: datetime) -> str:
    case = receipt_case(request_uuid, receipt, at)
    return "closed" if case.state in {"rejected", "applied"} else "received"


# Domain owns case transitions. The root supplies current named staff authority.
StaffAuthorizer = Callable[[AccountActor, UUID, UUID, str, datetime], None]
EffectRecorder = Callable[[IdentityChangeResult], None]


@contextmanager
def locked_case(
    actor: AccountActor,
    request_uuid: UUID,
    step_up_id: UUID,
    reason_code: str,
    at: datetime,
    authorize: StaffAuthorizer,
    *,
    assigned: bool = True,
    extra_user: UUID | None = None,
) -> Iterator[RecoveryRequest]:
    ensure_recovery_enabled(at)
    if not callable(authorize):
        raise ValueError("Required staff authority")
    snapshot = RecoveryRequest.objects.filter(pk=request_uuid).first()
    if not snapshot:
        raise PermissionError("Staff authority denied")
    users = list(
        User.objects.filter(
            models.Q(
                phone__in=[snapshot.claimed_old_phone, snapshot.proposed_new_phone]
            )
            | models.Q(public_id__in=[actor.user_uuid, extra_user])
            | models.Q(pk=snapshot.target_user_id)
        ).order_by("pk")
    )
    phones = sorted(
        {
            snapshot.claimed_old_phone,
            snapshot.proposed_new_phone,
            *(u.phone for u in users),
        }
    )
    with transaction.atomic():
        for phone in phones:
            anchor, _ = OTPPhoneState.objects.get_or_create(phone=phone)
            OTPPhoneState.objects.select_for_update().get(pk=anchor.pk)
        current_users = list(
            User.objects.select_for_update()
            .filter(pk__in=[u.pk for u in users])
            .order_by("pk")
        )
        if [(u.pk, u.phone) for u in users] != [(u.pk, u.phone) for u in current_users]:
            raise PermissionError("Staff authority denied")
        case = RecoveryRequest.objects.select_for_update().get(pk=request_uuid)
        if (case.claimed_old_phone, case.proposed_new_phone, case.target_user_id) != (
            snapshot.claimed_old_phone,
            snapshot.proposed_new_phone,
            snapshot.target_user_id,
        ):
            raise RecoveryConflict("Recovery conflict")
        if case.new_phone_challenge_id is not None:
            OTPChallenge.objects.select_for_update().get(pk=case.new_phone_challenge_id)
        authorize(actor, case.id, step_up_id, reason_code, at)
        staff = next((u for u in current_users if u.public_id == actor.user_uuid), None)
        if (
            not staff
            or staff.phone in {case.claimed_old_phone, case.proposed_new_phone}
            or staff.pk == case.target_user_id
            or (assigned and case.assigned_staff_id != staff.pk)
        ):
            raise PermissionError("Staff authority denied")
        yield case


def _version(case: RecoveryRequest, expected: int, *, state: str = "received") -> None:
    if type(expected) is not int or case.version != expected or case.state != state:
        raise RecoveryConflict("Recovery conflict")


def _record_case(
    case: RecoveryRequest, action: str, record: OutcomeRecorder, reason: str
) -> None:
    if not callable(record):
        raise ValueError("Required recovery recorder")
    record(
        SecurityOutcome(
            action,
            "succeeded",
            case.target_user.public_id if case.target_user else None,
            case.id,
            ("version",),
            reason,
        )
    )


def assign_recovery(
    actor: AccountActor,
    request_uuid: UUID,
    expected_version: int,
    staff_uuid: UUID,
    step_up_id: UUID,
    reason_code: str,
    at: datetime,
    record: OutcomeRecorder,
    *,
    authorize: StaffAuthorizer,
) -> None:
    with locked_case(
        actor,
        request_uuid,
        step_up_id,
        reason_code,
        at,
        authorize,
        assigned=False,
        extra_user=staff_uuid,
    ) as case:
        _version(case, expected_version)
        staff = User.objects.get(public_id=staff_uuid)
        if (
            not staff.is_active
            or staff.state != "active"
            or staff.phone in {case.claimed_old_phone, case.proposed_new_phone}
            or staff.pk == case.target_user_id
        ):
            raise PermissionError("Staff authority denied")
        # Assignment does not grant a capability. Every subsequent read/write
        # independently checks the assignee's live grant and verified step-up.
        case.assigned_staff, case.version = staff, case.version + 1
        case.save(update_fields=["assigned_staff", "version"])
        _record_case(case, "recovery.assigned", record, reason_code)


def resolve_recovery(
    actor: AccountActor,
    request_uuid: UUID,
    expected_version: int,
    step_up_id: UUID,
    reason_code: str,
    at: datetime,
    record: OutcomeRecorder,
    *,
    authorize: StaffAuthorizer,
) -> None:
    with locked_case(
        actor, request_uuid, step_up_id, reason_code, at, authorize
    ) as case:
        _version(case, expected_version)
        target = User.objects.filter(phone=case.claimed_old_phone).first()
        if target and target.public_id == actor.user_uuid:
            raise PermissionError("Staff authority denied")
        if case.target_user_id and (
            not target
            or case.target_user_id != target.pk
            or case.target_auth_version != target.auth_version
        ):
            raise RecoveryConflict("Recovery conflict")
        case.target_user = target
        case.target_auth_version = target.auth_version if target else None
        case.new_phone_challenge = case.new_phone_verified_at = None
        case.version += 1
        case.save(
            update_fields=[
                "target_user",
                "target_auth_version",
                "new_phone_challenge",
                "new_phone_verified_at",
                "version",
            ]
        )
        _record_case(case, "recovery.evidence", record, reason_code)


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
    record: OutcomeRecorder,
    *,
    authorize: StaffAuthorizer,
) -> UUID:
    validate_evidence_metadata(classification, outcome, checksum, reference)
    with locked_case(
        actor, request_uuid, step_up_id, reason_code, at, authorize
    ) as case:
        _version(case, expected_version)
        evidence = RecoveryEvidenceMetadata.objects.create(
            case=case,
            classification=classification,
            outcome=outcome,
            checksum=checksum,
            secured_reference=reference,
            reviewer=User.objects.get(public_id=actor.user_uuid),
            reviewed_at=at,
        )
        case.evidence_decision = outcome
        case.version += 1
        case.save(update_fields=["evidence_decision", "version"])
        _record_case(case, "recovery.evidence", record, reason_code)
        return evidence.id


def decide_recovery(
    actor: AccountActor,
    request_uuid: UUID,
    expected_version: int,
    decision: str,
    reason_code: str,
    step_up_id: UUID,
    at: datetime,
    record: OutcomeRecorder,
    *,
    authorize: StaffAuthorizer,
) -> None:
    if decision not in {"approved", "rejected"} or reason_code not in {
        "identity_verified",
        "permission_denied",
    }:
        raise ValueError("Invalid recovery decision")
    with locked_case(
        actor, request_uuid, step_up_id, reason_code, at, authorize
    ) as case:
        _version(case, expected_version)
        if not case.evidence.exists() or case.evidence_decision == "unresolved":
            raise PermissionError("Evidence review required")
        if decision == "approved":
            if (
                not case.target_user
                or case.evidence_decision != "verified"
                or case.target_user.phone != case.claimed_old_phone
                or case.target_user.auth_version != case.target_auth_version
                or case.target_user.state
                in {"deleted", "anonymized", "deletion_completed"}
            ):
                raise PermissionError("Recovery unavailable")
        case.state, case.decision_reason, case.decided_at = decision, reason_code, at
        case.decision_authorizer = User.objects.get(public_id=actor.user_uuid)
        case.version += 1
        case.save(
            update_fields=[
                "state",
                "decision_authorizer",
                "decision_reason",
                "decided_at",
                "version",
            ]
        )
        _record_case(case, "recovery." + decision, record, reason_code)


def _record_access(case: RecoveryRequest, record: OutcomeRecorder, reason: str) -> None:
    if not callable(record):
        raise ValueError("Required evidence-access recorder")
    record(
        SecurityOutcome(
            "recovery.evidence",
            "succeeded",
            case.target_user.public_id if case.target_user else None,
            case.id,
            (),
            reason,
        )
    )


def recovery_detail(
    actor: AccountActor,
    request_uuid: UUID,
    step_up_id: UUID,
    reason_code: str,
    at: datetime,
    record: OutcomeRecorder,
    *,
    authorize: StaffAuthorizer,
) -> RecoveryRequest:
    with locked_case(
        actor, request_uuid, step_up_id, reason_code, at, authorize
    ) as case:
        _record_access(case, record, reason_code)
        return case


def evidence_detail(
    actor: AccountActor,
    request_uuid: UUID,
    evidence_uuid: UUID,
    step_up_id: UUID,
    reason_code: str,
    at: datetime,
    record: OutcomeRecorder,
    *,
    authorize: StaffAuthorizer,
) -> RecoveryEvidenceMetadata | None:
    with locked_case(
        actor, request_uuid, step_up_id, reason_code, at, authorize
    ) as case:
        evidence = case.evidence.filter(pk=evidence_uuid).first()
        _record_access(case, record, reason_code)
        return evidence


def recovery_binding(
    request_uuid: UUID, receipt: str, at: datetime, *, lock: bool = False
) -> OtpBinding:
    case = receipt_case(request_uuid, receipt, at, lock=lock)
    if case.state not in {"received", "approved"}:
        raise RecoveryNotFound("Recovery unavailable")
    return OtpBinding(
        "recovery_new_phone",
        case.id,
        case.target_user.public_id if case.target_user else None,
        case.target_auth_version,
        case.proposed_new_phone,
    )


def validate_recovery_binding(binding: OtpBinding, receipt: str, at: datetime) -> None:
    current = recovery_binding(binding.context_uuid, receipt, at, lock=True)
    if current != binding:
        raise RecoveryConflict("Recovery conflict")


def record_recovery_proof(
    binding: OtpBinding, receipt: str, challenge_id: UUID, at: datetime
) -> None:
    validate_recovery_binding(binding, receipt, at)
    case = RecoveryRequest.objects.select_for_update().get(pk=binding.context_uuid)
    case.new_phone_challenge_id, case.new_phone_verified_at = challenge_id, at
    case.version += 1
    case.save(update_fields=["new_phone_challenge", "new_phone_verified_at", "version"])


def apply_recovery(
    actor: AccountActor,
    request_uuid: UUID,
    expected_version: int,
    step_up_id: UUID,
    reason_code: str,
    at: datetime,
    record: OutcomeRecorder,
    *,
    authorize: StaffAuthorizer,
    emit: EffectRecorder,
) -> IdentityChangeResult:
    if not callable(record) or not callable(emit):
        raise ValueError("Required recovery effect recorders")
    with locked_case(
        actor, request_uuid, step_up_id, reason_code, at, authorize
    ) as case:
        if case.state == "applied":
            assert case.target_user and case.effect_auth_version
            return IdentityChangeResult(
                case.target_user.public_id, case.effect_auth_version, case.id
            )
        _version(case, expected_version, state="approved")
        target = case.target_user
        proof = (
            (
                OTPChallenge.objects.select_for_update()
                .filter(pk=case.new_phone_challenge_id)
                .first()
            )
            if case.new_phone_challenge_id is not None
            else None
        )
        anchor = OTPPhoneState.objects.get(phone=case.proposed_new_phone)
        if (
            not target
            or target.auth_version != case.target_auth_version
            or target.phone != case.claimed_old_phone
            or target.state in {"deleted", "anonymized", "deletion_completed"}
            or not proof
            or proof.target_user_id != target.pk
            or proof.target_auth_version != target.auth_version
            or proof.context_uuid != case.id
            or proof.purpose != "recovery_new_phone"
            or proof.phone_state_id != anchor.pk
            or proof.generation != anchor.generation
            or proof.delivery_state != "sent"
            or case.decided_at is None
            or proof.issued_at < case.decided_at
            or proof.consumed_at is None
            or proof.proof_applied_at is not None
            or proof.retired_at is not None
            or proof.locked_at is not None
            or not proof.consumed_at <= at < proof.expires_at
            or (at - proof.consumed_at).total_seconds() > 300
        ):
            raise RecoveryConflict("Recovery conflict")
        if (
            User.objects.filter(phone=case.proposed_new_phone)
            .exclude(pk=target.pk)
            .exists()
        ):
            raise RecoveryConflict("Phone unavailable")
        old, old_version = target.phone, target.auth_version
        invalidate_auth_locked(target, at)
        target.phone = case.proposed_new_phone
        target.save(update_fields=["phone"])
        OTPChallenge.objects.filter(phone_state=anchor, retired_at__isnull=True).update(
            retired_at=at
        )
        OTPPhoneState.objects.filter(pk=anchor.pk).update(
            generation=models.F("generation") + 1
        )
        PhoneChangeHistory.objects.create(
            user=target,
            old_phone=old,
            new_phone=target.phone,
            recovery_context=case.id,
            actor_uuid=actor.user_uuid,
            at=at,
            old_auth_version=old_version,
            new_auth_version=target.auth_version,
        )
        proof.proof_applied_at = at
        proof.save(update_fields=["proof_applied_at"])
        case.state, case.applied_at, case.effect_auth_version = (
            "applied",
            at,
            target.auth_version,
        )
        case.version += 1
        case.save(
            update_fields=["state", "applied_at", "effect_auth_version", "version"]
        )
        result = IdentityChangeResult(target.public_id, target.auth_version, case.id)
        record(
            SecurityOutcome(
                "recovery.applied",
                "succeeded",
                target.public_id,
                case.id,
                ("phone", "auth_version", "proof_applied_at", "revoked_at"),
                reason_code,
            )
        )
        emit(result)
        return result
