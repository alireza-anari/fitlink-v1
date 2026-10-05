import uuid

from django.db import models
from django.utils import timezone

ACTIONS = (
    "otp.requested",
    "otp.delivery",
    "otp.verification",
    "account.login",
    "account.logout",
    "account.logout_all",
    "account.state_changed",
    "account.phone_changed",
    "recovery.requested",
    "recovery.assigned",
    "recovery.evidence",
    "recovery.approved",
    "recovery.rejected",
    "recovery.applied",
    "phone_change.requested",
    "consent.granted",
    "consent.revoked",
    "feature_flag.changed",
    "referral.created",
    "referral.attributed",
    "privacy.intake",
    "privacy.hold",
    "privacy.policy",
    "outbox.retry",
    "staff.step_up",
    "staff.capability",
)
RESULTS = ("accepted", "denied", "failed", "succeeded", "throttled", "unavailable")
CHANGED_FIELDS = frozenset(
    {
        "phone",
        "state",
        "state_version",
        "auth_version",
        "birth_date",
        "adult_attested_at",
        "adult_attestation_version",
        "locale",
        "timezone",
        "delivery_state",
        "attempts",
        "consumed_at",
        "proof_applied_at",
        "revoked_at",
        "status",
        "version",
        "enabled",
        "assigned_staff",
        "decision",
    }
)
REASONS = frozenset(
    {
        "",
        "identity_verified",
        "staff_assigned",
        "user_requested",
        "security_restriction",
        "invalid_proof",
        "valid_proof",
        "delivery_accepted",
        "delivery_failed",
        "quota_exceeded",
        "cooldown",
        "account_ineligible",
        "adult_required",
        "receipt_expired",
        "case_conflict",
        "phone_conflict",
        "permission_denied",
        "policy_approved",
        "hold_applied",
        "hold_released",
        "operator_retry",
    }
)


class AppendOnlyQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValueError("Evidence is append-only")

    def delete(self):
        raise ValueError("Evidence is append-only")

    def bulk_update(self, objs, fields, batch_size=None):
        raise ValueError("Evidence is append-only")


class AuditEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor_uuid = models.UUIDField(null=True, blank=True)
    actor_kind = models.CharField(max_length=6, default="system")
    action = models.CharField(max_length=32)
    result = models.CharField(max_length=12)
    subject_type = models.CharField(max_length=16, default="account")
    subject_uuid = models.UUIDField(null=True, blank=True)
    correlation_id = models.UUIDField()
    reason_code = models.CharField(max_length=32, blank=True)
    changed_fields = models.JSONField(default=list, blank=True)
    at = models.DateTimeField(default=timezone.now)
    objects = AppendOnlyQuerySet.as_manager()

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValueError("Evidence is append-only")
        from apps.accounts.contracts import SecurityOutcome

        from .audit import validate_outcome

        validate_outcome(
            SecurityOutcome(
                self.action,
                self.result,
                self.subject_uuid,
                self.correlation_id,
                tuple(self.changed_fields),
                self.reason_code,
            )
        )
        self.full_clean()
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Evidence is append-only")

    class Meta:
        indexes = [
            models.Index(fields=["subject_uuid", "at"], name="audit_subject_time")
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(action__in=ACTIONS), name="audit_action"
            ),
            models.CheckConstraint(
                condition=models.Q(result__in=RESULTS), name="audit_result"
            ),
            models.CheckConstraint(
                condition=models.Q(actor_kind__in=["system", "user", "job"]),
                name="audit_actor_kind",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    subject_type__in=[
                        "account",
                        "recovery",
                        "consent",
                        "privacy",
                        "flag",
                        "outbox",
                        "referral",
                        "staff",
                    ]
                ),
                name="audit_subject_type",
            ),
            models.CheckConstraint(
                condition=models.Q(reason_code__in=tuple(sorted(REASONS))),
                name="audit_reason_code",
            ),
        ]
