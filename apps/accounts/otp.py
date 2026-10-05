"""Digest-only OTP issuance; possession never creates identity at send time."""

import hmac
import math
import re
import secrets
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from uuid import UUID, uuid4

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .contracts import (
    OtpProofResult,
    OtpRequestResult,
    OutcomeRecorder,
    SecurityOutcome,
)
from .limiter import (
    canonical_ip,
    finalize_verification,
    locked_rate_anchors,
    reserve_admission,
)
from .models import User
from .phone import normalize_iranian_mobile
from .policies import ADULT_ATTESTATION_VERSION, adult_entry_date, entry_allowed
from .security_keys import SecurityKeyRing, security_digest
from .security_models import LOGIN_CONTEXT, OTP_PURPOSES, OTPChallenge, OTPPhoneState
from .sms import SmsProvider, bounded_send


@dataclass(frozen=True)
class OtpDigestContext:
    challenge_uuid: UUID
    generation: int
    purpose: str
    context_uuid: UUID
    target_user_uuid: UUID | None
    target_auth_version: int | None


@dataclass(frozen=True)
class OtpBinding:
    purpose: str
    context_uuid: UUID
    user_uuid: UUID
    auth_version: int
    phone: str = field(repr=False)


@dataclass(frozen=True)
class _IssuedOtp:
    context: OtpDigestContext
    code: str = field(repr=False)


class OtpThrottled(RuntimeError):
    def __init__(self, retry_after: int):
        super().__init__("OTP request throttled")
        self.retry_after = retry_after


class OtpUnavailable(RuntimeError):
    pass


def generate_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def code_digest(
    code: str,
    context: OtpDigestContext,
    key_id: str,
    *,
    ring: SecurityKeyRing | None = None,
) -> str:
    if not re.fullmatch(r"[0-9]{6}", code):
        raise ValueError("Invalid OTP syntax")
    value = ":".join(
        str(value)
        for value in (
            context.challenge_uuid,
            context.generation,
            context.purpose,
            context.context_uuid,
            context.target_user_uuid,
            context.target_auth_version,
            code,
        )
    )
    return security_digest("otp", value, key_id, ring=ring)


def matches_code(
    code: str,
    stored_digest: str,
    context: OtpDigestContext,
    key_id: str,
    *,
    ring: SecurityKeyRing | None = None,
) -> bool:
    ring = ring or settings.ACCOUNT_SECURITY.keys
    retained = key_id in ring.key_ids
    digest = code_digest(
        code, context, key_id if retained else ring.active_id, ring=ring
    )
    return hmac.compare_digest(digest, stored_digest) and retained


def _bound_user(binding: OtpBinding | None) -> User | None:
    if binding is None:
        return None
    user = User.objects.select_for_update().filter(public_id=binding.user_uuid).first()
    if (
        not user
        or user.auth_version != binding.auth_version
        or not user.is_active
        or user.state
        not in {"active", "restricted", "deletion_requested", "pending_deletion"}
    ):
        raise OtpUnavailable("OTP context unavailable")
    return user


def request_otp(
    phone: str,
    ip: str,
    purpose: str,
    context_uuid: UUID,
    at: datetime,
    record: OutcomeRecorder,
    *,
    provider: SmsProvider,
    binding: OtpBinding | None = None,
    validate_context: Callable[[OtpBinding], None] | None = None,
) -> OtpRequestResult:
    # Two committed phases surround external I/O. An outer atomic block would
    # retain locks and permit delivery before challenge/audit durability.
    if transaction.get_connection().in_atomic_block:
        raise OtpUnavailable("OTP issuance unavailable")
    phone, ip = normalize_iranian_mobile(phone), canonical_ip(ip)
    if not callable(record) or at.tzinfo is None:
        raise ValueError("Required OTP security contract")
    if purpose not in OTP_PURPOSES or not isinstance(context_uuid, UUID):
        raise ValueError("Invalid OTP context")
    if purpose == "login":
        if context_uuid != LOGIN_CONTEXT or binding is not None:
            raise ValueError("Invalid OTP context")
    elif (
        context_uuid == LOGIN_CONTEXT
        or binding is None
        or validate_context is None
        or (binding.purpose, binding.context_uuid, binding.phone)
        != (purpose, context_uuid, phone)
    ):
        raise ValueError("Invalid OTP context")
    admitted = reserve_admission(phone, ip, "send", at)
    if not admitted.allowed:
        with transaction.atomic():
            record(
                SecurityOutcome(
                    "otp.requested",
                    "throttled",
                    None,
                    uuid4(),
                    reason_code="quota_exceeded",
                )
            )
        raise OtpThrottled(admitted.retry_after)
    policy = settings.ACCOUNT_SECURITY.policy
    issued, retry = None, 0
    with transaction.atomic():
        locked_rate_anchors(phone, ip)
        phone_row, _ = OTPPhoneState.objects.get_or_create(phone=phone)
        phone_row = OTPPhoneState.objects.select_for_update().get(pk=phone_row.pk)
        user = _bound_user(binding)
        if binding is not None:
            assert validate_context is not None
            validate_context(binding)
        if at < phone_row.next_send_at:
            retry = max(1, math.ceil((phone_row.next_send_at - at).total_seconds()))
            record(
                SecurityOutcome(
                    "otp.requested", "throttled", None, uuid4(), reason_code="cooldown"
                )
            )
        else:
            OTPChallenge.objects.filter(
                phone_state=phone_row,
                purpose=purpose,
                context_uuid=context_uuid,
                retired_at__isnull=True,
            ).update(retired_at=at)
            phone_row.generation += 1
            phone_row.next_send_at = at + timedelta(seconds=policy.resend_seconds)
            phone_row.save(update_fields=["generation", "next_send_at"])
            context = OtpDigestContext(
                uuid4(),
                phone_row.generation,
                purpose,
                context_uuid,
                user.public_id if user else None,
                user.auth_version if user else None,
            )
            code = generate_code()
            key_id = settings.ACCOUNT_SECURITY.keys.active_id
            OTPChallenge.objects.create(
                id=context.challenge_uuid,
                phone_state=phone_row,
                generation=context.generation,
                purpose=purpose,
                context_uuid=context_uuid,
                target_user=user,
                target_auth_version=context.target_auth_version,
                key_id=key_id,
                code_digest=code_digest(code, context, key_id),
                issued_at=at,
                expires_at=at + timedelta(seconds=policy.expiry_seconds),
            )
            record(
                SecurityOutcome(
                    "otp.requested", "accepted", None, context.challenge_uuid
                )
            )
            issued = _IssuedOtp(context, code)
    if issued is None:
        raise OtpThrottled(retry)
    # Provider I/O occurs after the digest/pending/audit transaction commits.
    delivery = bounded_send(
        provider,
        phone,
        issued.code,
        issued.context.challenge_uuid,
        policy.sms_timeout_seconds,
    )
    ack_at = timezone.now()
    with transaction.atomic():
        phone_row = OTPPhoneState.objects.select_for_update().get(phone=phone)
        user = _bound_user(binding)
        if binding is not None:
            assert validate_context is not None
            validate_context(binding)
        challenge = OTPChallenge.objects.select_for_update().get(
            pk=issued.context.challenge_uuid
        )
        sent = (
            delivery.state == "accepted"
            and phone_row.generation == challenge.generation
            and challenge.retired_at is None
            and challenge.delivery_state == "pending"
            and challenge.issued_at <= ack_at < challenge.expires_at
            and challenge.consumed_at is None
            and challenge.locked_at is None
        )
        challenge.delivery_state = "sent" if sent else "failed"
        challenge.save(update_fields=["delivery_state"])
        record(
            SecurityOutcome(
                "otp.delivery",
                "succeeded" if sent else "failed",
                None,
                challenge.id,
                ("delivery_state",),
                "delivery_accepted" if sent else "delivery_failed",
            )
        )
    return OtpRequestResult(
        "accepted", issued.context.challenge_uuid, policy.resend_seconds
    )


_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


def normalize_code(raw: str) -> str:
    if not isinstance(raw, str) or len(raw) != 6:
        raise ValueError("Invalid OTP syntax")
    code = raw.translate(_DIGITS)
    if not re.fullmatch(r"[0-9]{6}", code):
        raise ValueError("Invalid OTP syntax")
    return code


def _challenge_context(row: OTPChallenge, user: User | None) -> OtpDigestContext:
    return OtpDigestContext(
        row.id,
        row.generation,
        row.purpose,
        row.context_uuid,
        user.public_id if user and row.target_user_id == user.pk else None,
        row.target_auth_version,
    )


def _binding_matches(
    binding: OtpBinding | None, user: User | None, row: OTPChallenge, phone: str
) -> bool:
    return bool(
        binding
        and user
        and entry_allowed(user)
        and binding.phone == phone
        and binding.user_uuid == user.public_id
        and binding.auth_version == user.auth_version == row.target_auth_version
        and row.target_user_id == user.pk
        and binding.purpose == row.purpose
        and binding.context_uuid == row.context_uuid
    )


def verify_otp(
    phone: str,
    challenge_id: UUID,
    code: str,
    purpose: str,
    context_uuid: UUID,
    ip: str,
    at: datetime,
    record: OutcomeRecorder,
    *,
    birth_date: date | None = None,
    adult_attested: bool = False,
    binding: OtpBinding | None = None,
    validate_context: Callable[[OtpBinding], None] | None = None,
    on_login: Callable[[User], None] | None = None,
) -> OtpProofResult:
    """Commit failure evidence or proof/identity and synchronous session effects."""
    if transaction.get_connection().in_atomic_block:
        raise OtpUnavailable("OTP verification unavailable")
    phone, ip, code = (
        normalize_iranian_mobile(phone),
        canonical_ip(ip),
        normalize_code(code),
    )
    if (
        not callable(record)
        or at.tzinfo is None
        or at.utcoffset() is None
        or purpose not in OTP_PURPOSES
        or not isinstance(challenge_id, UUID)
        or not isinstance(context_uuid, UUID)
    ):
        raise ValueError("Required OTP security contract")
    admitted = reserve_admission(phone, ip, "verify_failure", at)
    if not admitted.allowed:
        with transaction.atomic():
            record(
                SecurityOutcome(
                    "otp.verification",
                    "throttled",
                    None,
                    uuid4(),
                    reason_code="quota_exceeded",
                )
            )
        raise OtpThrottled(admitted.retry_after)
    assert admitted.reservation_id is not None
    result = OtpProofResult(False, purpose, challenge_id, None, None)
    with transaction.atomic():
        locked_rate_anchors(phone, ip)
        phone_row, _ = OTPPhoneState.objects.get_or_create(phone=phone)
        phone_row = OTPPhoneState.objects.select_for_update().get(pk=phone_row.pk)
        # Discover and lock identity before challenge; mapping is re-read under
        # the phone lock. Every verification uses the same lookup path.
        user = (
            User.objects.select_for_update().filter(public_id=binding.user_uuid).first()
            if binding
            else User.objects.select_for_update().filter(phone=phone).first()
        )
        row = OTPChallenge.objects.select_for_update().filter(pk=challenge_id).first()
        if row:
            context = _challenge_context(row, user)
            matched = matches_code(code, row.code_digest, context, row.key_id)
        else:
            context = OtpDigestContext(
                challenge_id, 1, purpose, context_uuid, None, None
            )
            matched = matches_code(
                code, "0" * 64, context, settings.ACCOUNT_SECURITY.keys.active_id
            )
        eligible = bool(
            row
            and row.phone_state_id == phone_row.pk
            and row.purpose == purpose
            and row.context_uuid == context_uuid
            and row.generation == phone_row.generation
            and row.delivery_state == "sent"
            and row.issued_at <= at < row.expires_at
            and row.retired_at is None
            and row.consumed_at is None
            and row.locked_at is None
            and row.attempts < settings.ACCOUNT_SECURITY.policy.attempts
        )
        if purpose == "login":
            eligible = eligible and context_uuid == LOGIN_CONTEXT and binding is None
            eligible = eligible and entry_allowed(user)
        else:
            eligible = eligible and bool(
                row and _binding_matches(binding, user, row, phone)
            )
            eligible = eligible and callable(validate_context)
            if eligible:
                assert binding is not None and validate_context is not None
                validate_context(binding)
        valid = eligible and matched
        declared = None
        if valid and purpose == "login":
            try:
                declared = adult_entry_date(user, birth_date, adult_attested, at)
            except ValueError:
                valid = False
        changed: tuple[str, ...] = ()
        if eligible and not matched:
            assert row is not None
            row.attempts += 1
            if row.attempts == settings.ACCOUNT_SECURITY.policy.attempts:
                row.locked_at = at
            row.save(update_fields=["attempts", "locked_at"])
            changed = ("attempts",)
        if valid:
            assert row is not None
            if purpose == "login":
                assert declared is not None
                if user is None:
                    user = User.objects.create_user(
                        phone,
                        birth_date=declared,
                        adult_attested_at=at,
                        adult_attestation_version=ADULT_ATTESTATION_VERSION,
                    )
                elif (
                    user.adult_attested_at is None or not user.adult_attestation_version
                ):
                    user.birth_date, user.adult_attested_at = declared, at
                    user.adult_attestation_version = ADULT_ATTESTATION_VERSION
                    user.save(
                        update_fields=[
                            "birth_date",
                            "adult_attested_at",
                            "adult_attestation_version",
                        ]
                    )
            assert user is not None
            row.consumed_at = at
            row.save(update_fields=["consumed_at"])
            changed = ("consumed_at",)
            result = OtpProofResult(
                True, purpose, challenge_id, user.public_id, context_uuid
            )
        # A cleanup error rolls back identity/proof and cannot issue a session.
        # A later audit failure leaves a durable pending reservation even when
        # Redis cleanup already happened: PostgreSQL remains authoritative.
        finalize_verification(admitted.reservation_id, valid, at)
        record(
            SecurityOutcome(
                "otp.verification",
                "succeeded" if valid else "failed",
                result.user_uuid if valid else None,
                challenge_id,
                changed,
                "valid_proof" if valid else "invalid_proof",
            )
        )
        if valid and purpose == "login" and on_login is not None:
            assert user is not None
            on_login(user)
    return result


def apply_verified_proof(
    challenge_id: UUID,
    binding: OtpBinding,
    at: datetime,
    record: OutcomeRecorder,
    *,
    effect: Callable[[User], None],
    validate_context: Callable[[OtpBinding], None],
) -> None:
    """Internal owned command: consume durable non-login eligibility once.

    The context owner supplies locked authority checks and its transactional
    effect. This is never a client-selected callback or public proof endpoint.
    """
    if (
        not callable(record)
        or not callable(effect)
        or not callable(validate_context)
        or at.tzinfo is None
        or at.utcoffset() is None
        or binding.purpose == "login"
    ):
        raise ValueError("Required proof application contract")
    phone = normalize_iranian_mobile(binding.phone)
    with transaction.atomic():
        phone_row = (
            OTPPhoneState.objects.select_for_update().filter(phone=phone).first()
        )
        user = (
            User.objects.select_for_update().filter(public_id=binding.user_uuid).first()
        )
        row = OTPChallenge.objects.select_for_update().filter(pk=challenge_id).first()
        if (
            not phone_row
            or not row
            or not _binding_matches(binding, user, row, phone)
            or row.phone_state_id != phone_row.pk
            or row.generation != phone_row.generation
            or row.retired_at is not None
            or row.delivery_state != "sent"
            or row.consumed_at is None
            or row.proof_applied_at is not None
            or not row.consumed_at <= at < row.expires_at
            or row.locked_at is not None
        ):
            raise OtpUnavailable("OTP proof unavailable")
        validate_context(binding)
        assert user is not None
        effect(user)
        row.proof_applied_at = at
        row.save(update_fields=["proof_applied_at"])
        record(
            SecurityOutcome(
                "otp.verification",
                "succeeded",
                user.public_id,
                row.id,
                ("proof_applied_at",),
                "valid_proof",
            )
        )
