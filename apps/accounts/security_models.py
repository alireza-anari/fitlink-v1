"""Durable security primitives; none of these records grants access by itself."""

import uuid
from datetime import UTC, datetime

from django.conf import settings
from django.db import models
from django.utils import timezone

CANONICAL_PHONE = r"^\+989[0-9]{9}$"
DIGEST = r"^[0-9a-f]{64}$"
KEY_ID = r"^[A-Za-z0-9_-]{1,32}$"
LOGIN_CONTEXT = uuid.UUID(int=0)
OTP_PURPOSES = ("login", "recovery_new_phone", "phone_change_old", "phone_change_new")


def never_sent() -> datetime:
    return datetime(1970, 1, 1, tzinfo=UTC)


class OTPPhoneState(models.Model):
    phone = models.CharField(max_length=13, unique=True)
    generation = models.PositiveBigIntegerField(default=0)
    next_send_at = models.DateTimeField(default=never_sent)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(phone__regex=CANONICAL_PHONE),
                name="otp_phone_canonical",
            ),
            models.CheckConstraint(
                condition=models.Q(generation__gte=0), name="otp_generation_nonnegative"
            ),
        ]


class SecurityRateAnchor(models.Model):
    kind = models.CharField(max_length=5, choices=[("phone", "phone"), ("ip", "ip")])
    key_id = models.CharField(max_length=32)
    key_digest = models.CharField(max_length=64)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["kind", "key_id", "key_digest"], name="rate_anchor_identity"
            ),
            models.CheckConstraint(
                condition=models.Q(kind__in=["phone", "ip"]), name="rate_anchor_kind"
            ),
            models.CheckConstraint(
                condition=models.Q(key_id__regex=KEY_ID), name="rate_anchor_key_id"
            ),
            models.CheckConstraint(
                condition=models.Q(key_digest__regex=DIGEST), name="rate_anchor_digest"
            ),
        ]


class SecurityRateEvent(models.Model):
    reservation_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    phone_anchor = models.ForeignKey(
        SecurityRateAnchor, on_delete=models.PROTECT, related_name="phone_events"
    )
    ip_anchor = models.ForeignKey(
        SecurityRateAnchor, on_delete=models.PROTECT, related_name="ip_events"
    )
    kind = models.CharField(max_length=16)
    outcome = models.CharField(max_length=9, default="pending")
    at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(
                fields=["phone_anchor", "kind", "at"], name="rate_phone_window"
            ),
            models.Index(fields=["ip_anchor", "kind", "at"], name="rate_ip_window"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    kind__in=["send", "verify_failure", "recovery_intake"]
                ),
                name="rate_event_kind",
            ),
            models.CheckConstraint(
                condition=models.Q(outcome__in=["pending", "failed", "succeeded"]),
                name="rate_event_outcome",
            ),
            models.CheckConstraint(
                condition=~models.Q(phone_anchor=models.F("ip_anchor")),
                name="rate_event_distinct_anchors",
            ),
        ]


class OTPChallenge(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_state = models.ForeignKey(OTPPhoneState, on_delete=models.PROTECT)
    generation = models.PositiveBigIntegerField()
    purpose = models.CharField(max_length=18, choices=[(p, p) for p in OTP_PURPOSES])
    context_uuid = models.UUIDField(default=LOGIN_CONTEXT)
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT
    )
    target_auth_version = models.PositiveBigIntegerField(null=True)
    key_id = models.CharField(max_length=32)
    code_digest = models.CharField(max_length=64)
    issued_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    delivery_state = models.CharField(max_length=7, default="pending")
    attempts = models.PositiveSmallIntegerField(default=0)
    consumed_at = models.DateTimeField(null=True)
    proof_applied_at = models.DateTimeField(null=True)
    locked_at = models.DateTimeField(null=True)
    retired_at = models.DateTimeField(null=True)

    class Meta:
        indexes = [
            models.Index(
                fields=["phone_state", "purpose", "issued_at"], name="otp_phone_purpose"
            ),
            models.Index(fields=["expires_at"], name="otp_expiry"),
            models.Index(
                fields=["target_user", "target_auth_version"], name="otp_bound_identity"
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["phone_state", "generation", "purpose", "context_uuid"],
                name="otp_generation_context",
            ),
            models.CheckConstraint(
                condition=models.Q(purpose__in=OTP_PURPOSES), name="otp_purpose"
            ),
            models.CheckConstraint(
                condition=models.Q(delivery_state__in=["pending", "sent", "failed"]),
                name="otp_delivery_state",
            ),
            models.CheckConstraint(
                condition=models.Q(generation__gte=1), name="otp_generation_positive"
            ),
            models.CheckConstraint(
                condition=models.Q(attempts__lte=5), name="otp_attempts_bound"
            ),
            models.CheckConstraint(
                condition=models.Q(expires_at__gt=models.F("issued_at")),
                name="otp_expiry_after_issue",
            ),
            models.CheckConstraint(
                condition=models.Q(key_id__regex=KEY_ID), name="otp_key_id"
            ),
            models.CheckConstraint(
                condition=models.Q(code_digest__regex=DIGEST), name="otp_code_digest"
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(purpose="login", context_uuid=LOGIN_CONTEXT)
                    | (
                        ~models.Q(purpose="login")
                        & ~models.Q(context_uuid=LOGIN_CONTEXT)
                    )
                ),
                name="otp_purpose_context",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(target_user__isnull=True, target_auth_version__isnull=True)
                    | models.Q(
                        target_user__isnull=False,
                        target_auth_version__isnull=False,
                        target_auth_version__gte=1,
                    )
                ),
                name="otp_target_version",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(consumed_at__isnull=True)
                    | models.Q(
                        delivery_state="sent",
                        locked_at__isnull=True,
                        consumed_at__gte=models.F("issued_at"),
                        consumed_at__lt=models.F("expires_at"),
                    )
                ),
                name="otp_consumed_consistency",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(proof_applied_at__isnull=True)
                    | (
                        models.Q(consumed_at__isnull=False)
                        & ~models.Q(purpose="login")
                        & models.Q(proof_applied_at__gte=models.F("consumed_at"))
                    )
                ),
                name="otp_applied_proof",
            ),
        ]


class AccountSessionControl(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    key_id = models.CharField(max_length=32)
    session_digest = models.CharField(max_length=64)
    auth_version = models.PositiveBigIntegerField()
    scope = models.CharField(max_length=15)
    authenticated_at = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True)

    class Meta:
        indexes = [
            models.Index(
                fields=["user", "revoked_at", "expires_at"], name="session_live"
            )
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["key_id", "session_digest"], name="session_control_digest"
            ),
            models.CheckConstraint(
                condition=models.Q(key_id__regex=KEY_ID), name="session_control_key_id"
            ),
            models.CheckConstraint(
                condition=models.Q(session_digest__regex=DIGEST),
                name="session_control_hmac",
            ),
            models.CheckConstraint(
                condition=models.Q(auth_version__gte=1), name="session_auth_version"
            ),
            models.CheckConstraint(
                condition=models.Q(scope__in=["normal", "account_control"]),
                name="session_scope",
            ),
            models.CheckConstraint(
                condition=models.Q(expires_at__gt=models.F("created_at")),
                name="session_expiry",
            ),
        ]
