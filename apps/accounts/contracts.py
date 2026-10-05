"""Immutable values shared by account services and explicit composition wiring."""

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from uuid import UUID


@dataclass(frozen=True)
class SecurityOutcome:
    action: str
    result: str
    subject_uuid: UUID | None
    correlation_id: UUID
    changed_fields: tuple[str, ...] = ()
    reason_code: str = ""


OutcomeRecorder = Callable[[SecurityOutcome], None]


@dataclass(frozen=True)
class AccountSecurityPolicy:
    otp_digits: int = 6
    expiry_seconds: int = 300
    resend_seconds: int = 60
    attempts: int = 5
    window_seconds: int = 3600
    send_phone: int = 5
    send_ip: int = 20
    failure_phone: int = 10
    failure_ip: int = 60
    recovery_phone: int = 3
    recovery_ip: int = 10
    recovery_window_seconds: int = 86400
    sms_timeout_seconds: int = 3
    recent_auth_seconds: int = 600
    recovery_receipt_seconds: int = 604800
    outbox_scan_seconds: int = 30
    outbox_batch: int = 100
    outbox_lease_seconds: int = 60
    outbox_max_attempts: int = 8
    outbox_backoff_seconds: int = 300


@dataclass(frozen=True)
class AdmissionResult:
    allowed: bool
    retry_after: int
    reservation_id: UUID | None


@dataclass(frozen=True)
class OtpRequestResult:
    status: str
    challenge_id: UUID
    resend_after_seconds: int


@dataclass(frozen=True)
class OtpProofResult:
    valid: bool
    purpose: str
    challenge_id: UUID
    user_uuid: UUID | None
    context_uuid: UUID | None


class SessionScope(StrEnum):
    NORMAL = "normal"
    ACCOUNT_CONTROL = "account_control"


@dataclass(frozen=True)
class RecoveryReceipt:
    request_uuid: UUID
    raw_receipt: str = field(repr=False)


@dataclass(frozen=True)
class IdentityChangeResult:
    user_uuid: UUID
    auth_version: int
    context_uuid: UUID
