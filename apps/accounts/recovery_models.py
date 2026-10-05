"""Confidential recovery metadata and append-only identity effects."""

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from .security_models import CANONICAL_PHONE, DIGEST, KEY_ID

EVIDENCE_TYPES = ("identity_match", "phone_loss", "ownership_review")
EVIDENCE_OUTCOMES = ("verified", "unresolved", "rejected")


class RecoveryRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    claimed_old_phone = models.CharField(max_length=13)
    proposed_new_phone = models.CharField(max_length=13)
    contact_preference = models.CharField(max_length=9, default="new_phone")
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.PROTECT,
        related_name="recovery_targets",
    )
    target_auth_version = models.PositiveBigIntegerField(null=True)
    assigned_staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.PROTECT,
        related_name="assigned_recoveries",
    )
    state = models.CharField(max_length=8, default="received")
    version = models.PositiveBigIntegerField(default=1)
    receipt_key_id = models.CharField(max_length=32)
    receipt_digest = models.CharField(max_length=64, unique=True)
    receipt_expires_at = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)
    decision_authorizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.PROTECT,
        related_name="recovery_decisions",
    )
    decision_reason = models.CharField(max_length=32, default="")
    decided_at = models.DateTimeField(null=True)
    evidence_decision = models.CharField(max_length=10, default="unresolved")
    new_phone_challenge = models.ForeignKey(
        "accounts.OTPChallenge",
        null=True,
        on_delete=models.PROTECT,
        related_name="recovery_proofs",
    )
    new_phone_verified_at = models.DateTimeField(null=True)
    applied_at = models.DateTimeField(null=True)
    effect_auth_version = models.PositiveBigIntegerField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["target_user"],
                condition=models.Q(
                    state__in=["received", "approved"], target_user__isnull=False
                ),
                name="recovery_live_target",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    claimed_old_phone__regex=CANONICAL_PHONE,
                    proposed_new_phone__regex=CANONICAL_PHONE,
                )
                & ~models.Q(claimed_old_phone=models.F("proposed_new_phone")),
                name="recovery_distinct_phones",
            ),
            models.CheckConstraint(
                condition=models.Q(contact_preference="new_phone"),
                name="recovery_contact_preference",
            ),
            models.CheckConstraint(
                condition=models.Q(version__gte=1), name="recovery_positive_version"
            ),
            models.CheckConstraint(
                condition=models.Q(
                    state__in=["received", "approved", "rejected", "applied"]
                ),
                name="recovery_state",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    receipt_key_id__regex=KEY_ID,
                    receipt_digest__regex=DIGEST,
                    receipt_expires_at__gt=models.F("created_at"),
                ),
                name="recovery_receipt",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    target_user__isnull=True, target_auth_version__isnull=True
                )
                | models.Q(
                    target_user__isnull=False,
                    target_auth_version__isnull=False,
                    target_auth_version__gte=1,
                ),
                name="recovery_target_version",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    new_phone_challenge__isnull=True, new_phone_verified_at__isnull=True
                )
                | models.Q(
                    new_phone_challenge__isnull=False,
                    new_phone_verified_at__isnull=False,
                ),
                name="recovery_proof_pair",
            ),
            models.CheckConstraint(
                condition=models.Q(evidence_decision__in=EVIDENCE_OUTCOMES),
                name="recovery_evidence_outcome",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    state="received",
                    decision_authorizer__isnull=True,
                    decision_reason="",
                )
                | models.Q(
                    state__in=["approved", "rejected", "applied"],
                    decision_authorizer__isnull=False,
                    decision_reason__in=["identity_verified", "permission_denied"],
                ),
                name="recovery_decision_binding",
            ),
            models.CheckConstraint(
                condition=models.Q(state="received", decided_at__isnull=True)
                | models.Q(
                    state__in=["approved", "rejected", "applied"],
                    decided_at__isnull=False,
                ),
                name="recovery_decision_time",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    state="applied",
                    applied_at__isnull=False,
                    effect_auth_version__isnull=False,
                    effect_auth_version__gte=2,
                    target_user__isnull=False,
                    new_phone_challenge__isnull=False,
                )
                | (
                    ~models.Q(state="applied")
                    & models.Q(
                        applied_at__isnull=True, effect_auth_version__isnull=True
                    )
                ),
                name="recovery_effect_binding",
            ),
        ]


class RecoveryEvidenceMetadata(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case = models.ForeignKey(
        RecoveryRequest, on_delete=models.PROTECT, related_name="evidence"
    )
    classification = models.CharField(max_length=16)
    outcome = models.CharField(max_length=10)
    checksum = models.CharField(max_length=64)
    secured_reference = models.UUIDField()
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="recovery_evidence_reviews",
    )
    reviewed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    classification__in=EVIDENCE_TYPES,
                    outcome__in=EVIDENCE_OUTCOMES,
                    checksum__regex=DIGEST,
                ),
                name="recovery_evidence_metadata",
            ),
        ]


class HistoryQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValueError("History is append-only")

    def delete(self):
        raise ValueError("History is append-only")

    def bulk_update(self, objs, fields, batch_size=None):
        raise ValueError("History is append-only")


class PhoneChangeHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="phone_history"
    )
    old_phone = models.CharField(max_length=13)
    new_phone = models.CharField(max_length=13)
    recovery_context = models.UUIDField(null=True, unique=True)
    change_context = models.UUIDField(null=True, unique=True)
    actor_uuid = models.UUIDField()
    at = models.DateTimeField(default=timezone.now)
    old_auth_version = models.PositiveBigIntegerField()
    new_auth_version = models.PositiveBigIntegerField()
    objects = HistoryQuerySet.as_manager()

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValueError("History is append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("History is append-only")

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    old_phone__regex=CANONICAL_PHONE, new_phone__regex=CANONICAL_PHONE
                )
                & ~models.Q(old_phone=models.F("new_phone")),
                name="history_distinct_phones",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    recovery_context__isnull=False, change_context__isnull=True
                )
                | models.Q(recovery_context__isnull=True, change_context__isnull=False),
                name="history_exact_context",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    old_auth_version__gte=1,
                    new_auth_version=models.F("old_auth_version") + 1,
                ),
                name="history_auth_versions",
            ),
        ]


class PhoneChangeIntent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="phone_change_intents",
    )
    old_phone = models.CharField(max_length=13)
    new_phone = models.CharField(max_length=13)
    issued_auth_version = models.PositiveBigIntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    version = models.PositiveBigIntegerField(default=1)
    old_phone_challenge = models.ForeignKey(
        "accounts.OTPChallenge",
        null=True,
        on_delete=models.PROTECT,
        related_name="old_phone_intents",
    )
    new_phone_challenge = models.ForeignKey(
        "accounts.OTPChallenge",
        null=True,
        on_delete=models.PROTECT,
        related_name="new_phone_intents",
    )
    old_phone_verified_at = models.DateTimeField(null=True)
    new_phone_verified_at = models.DateTimeField(null=True)
    applied_at = models.DateTimeField(null=True)
    retired_at = models.DateTimeField(null=True)
    effect_auth_version = models.PositiveBigIntegerField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=models.Q(applied_at__isnull=True, retired_at__isnull=True),
                name="phone_change_live_user",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    old_phone__regex=CANONICAL_PHONE, new_phone__regex=CANONICAL_PHONE
                )
                & ~models.Q(old_phone=models.F("new_phone")),
                name="phone_change_distinct_phones",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    issued_auth_version__gte=1,
                    version__gte=1,
                    expires_at__gt=models.F("created_at"),
                ),
                name="phone_change_version_expiry",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    old_phone_challenge__isnull=True, old_phone_verified_at__isnull=True
                )
                | models.Q(
                    old_phone_challenge__isnull=False,
                    old_phone_verified_at__isnull=False,
                ),
                name="phone_change_old_proof_pair",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    new_phone_challenge__isnull=True, new_phone_verified_at__isnull=True
                )
                | models.Q(
                    new_phone_challenge__isnull=False,
                    new_phone_verified_at__isnull=False,
                ),
                name="phone_change_new_proof_pair",
            ),
            models.CheckConstraint(
                condition=models.Q(old_phone_challenge__isnull=True)
                | models.Q(new_phone_challenge__isnull=True)
                | ~models.Q(old_phone_challenge=models.F("new_phone_challenge")),
                name="phone_change_distinct_proofs",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    applied_at__isnull=True, effect_auth_version__isnull=True
                )
                | models.Q(
                    applied_at__isnull=False,
                    retired_at__isnull=True,
                    effect_auth_version__isnull=False,
                    effect_auth_version=models.F("issued_auth_version") + 1,
                    old_phone_challenge__isnull=False,
                    new_phone_challenge__isnull=False,
                ),
                name="phone_change_effect_binding",
            ),
        ]
