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
    "athlete.profile_created",
    "baseline.saved",
    "baseline.submitted",
    "baseline.corrected",
    "baseline.cleared",
    "professional.profile_created",
    "professional.profile_saved",
    "professional.roles_changed",
    "credential.created",
    "credential.revised",
    "credential.withdrawn",
    "asset.begun",
    "asset.uploaded",
    "asset.finalized",
    "asset.read",
    "asset.rejected",
    "asset.revoked",
    "asset.deleted",
    "verification.submitted",
    "verification.assigned",
    "verification.review_started",
    "verification.read",
    "verification.approved",
    "verification.rejected",
    "verification.stale",
    "verification.withdrawn",
    "verification.revoked",
    "professional.role_restricted",
    "professional.role_released",
    "assistant.defined",
    "assistant.revoked",
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
        "onboarding_step",
        "current_baseline",
        "setup_step",
        "declared_active",
        "declaration_version",
        "evidence_revision",
        "decision_version",
        "current_revision",
        "processing_version",
        "archived_at",
        "withdrawn_at",
        "released_at",
        "finalized_at",
        "rejection_code",
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
        "verification_submitted",
        "verification_review",
        "credentials_approved",
        "evidence_incomplete",
        "credentials_invalid",
        "evidence_expired",
        "evidence_revoked",
        "role_restricted",
        "restriction_removed",
        "material_changed",
        "owner_withdrawn",
        "upload_invalid",
        "scan_failed",
        "retention_due",
    }
)
SUBJECT_TYPES = (
    "account",
    "recovery",
    "consent",
    "privacy",
    "flag",
    "outbox",
    "referral",
    "staff",
    "athlete",
    "baseline",
    "professional",
    "credential",
    "asset",
    "verification",
    "assistant",
)


class AppendOnlyQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValueError("Evidence is append-only")

    def delete(self):
        raise ValueError("Evidence is append-only")

    def bulk_update(self, objs, fields, batch_size=None):
        raise ValueError("Evidence is append-only")


class AuditFieldsAllowed(models.Func):
    function = "fitlink_valid_audit_fields"
    output_field = models.BooleanField()


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
        if not isinstance(self.changed_fields, list) or any(
            not isinstance(value, str) for value in self.changed_fields
        ):
            raise ValueError("Invalid audit metadata")
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
                condition=AuditFieldsAllowed("changed_fields"),
                name="audit_fields_allowlist",
            ),
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
                condition=models.Q(subject_type__in=SUBJECT_TYPES),
                name="audit_subject_type",
            ),
            models.CheckConstraint(
                condition=models.Q(reason_code__in=tuple(sorted(REASONS))),
                name="audit_reason_code",
            ),
        ]
