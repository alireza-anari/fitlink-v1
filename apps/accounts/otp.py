"""Digest-only OTP issuance; possession never creates identity at send time."""

import hmac
import math
import re
import secrets
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .contracts import OtpRequestResult, OutcomeRecorder, SecurityOutcome
from .limiter import canonical_ip, locked_rate_anchors, reserve_admission
from .models import User
from .phone import normalize_iranian_mobile
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
