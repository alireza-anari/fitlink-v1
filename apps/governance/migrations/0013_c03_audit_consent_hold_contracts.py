from django.db import migrations, models

C03_ACTIONS = (
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
C03_REASONS = (
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
)
C03_SUBJECT_TYPES = (
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
C03_CONSENT_PURPOSES = (
    "account_metadata",
    "active_sharing",
    "archive_sharing",
    "nutrition_adherence_read",
    "ai_feature",
    "mirror_summary",
    "case_study",
    "baseline_storage",
)
C03_HOLD_SUBJECTS = (
    "privacy_request",
    "athlete_baseline",
    "professional_credential",
    "professional_verification",
    "profile_asset",
)

FORWARD_AUDIT_FIELDS = r"""
CREATE OR REPLACE FUNCTION fitlink_valid_audit_fields(value jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE STRICT AS $$
    SELECT CASE WHEN jsonb_typeof(value) = 'array' THEN
        jsonb_array_length(value) <= 33 AND value <@
        '["phone","state","state_version","auth_version","birth_date",
          "adult_attested_at","adult_attestation_version","locale","timezone",
          "delivery_state","attempts","consumed_at","proof_applied_at",
          "revoked_at","status","version","enabled","assigned_staff","decision",
          "onboarding_step","current_baseline","setup_step","declared_active",
          "declaration_version","evidence_revision","decision_version",
          "current_revision","processing_version","archived_at","withdrawn_at",
          "released_at","finalized_at","rejection_code"]'::jsonb
        ELSE false END;
$$;
"""

REVERSE_AUDIT_FIELDS = r"""
CREATE OR REPLACE FUNCTION fitlink_valid_audit_fields(value jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE STRICT AS $$
    SELECT CASE WHEN jsonb_typeof(value) = 'array' THEN
        jsonb_array_length(value) <= 19 AND value <@
        '["phone","state","state_version","auth_version","birth_date",
          "adult_attested_at","adult_attestation_version","locale","timezone",
          "delivery_state","attempts","consumed_at","proof_applied_at",
          "revoked_at","status","version","enabled","assigned_staff","decision"]'
          ::jsonb
        ELSE false END;
$$;
"""


class Migration(migrations.Migration):
    dependencies = [("governance", "0012_c03_staff_capability_width")]
    operations = [
        migrations.RunSQL(FORWARD_AUDIT_FIELDS, REVERSE_AUDIT_FIELDS),
        migrations.RemoveConstraint(model_name="auditevent", name="audit_action"),
        migrations.AddConstraint(
            model_name="auditevent",
            constraint=models.CheckConstraint(
                condition=models.Q(action__in=C03_ACTIONS), name="audit_action"
            ),
        ),
        migrations.RemoveConstraint(model_name="auditevent", name="audit_subject_type"),
        migrations.AddConstraint(
            model_name="auditevent",
            constraint=models.CheckConstraint(
                condition=models.Q(subject_type__in=C03_SUBJECT_TYPES),
                name="audit_subject_type",
            ),
        ),
        migrations.RemoveConstraint(model_name="auditevent", name="audit_reason_code"),
        migrations.AddConstraint(
            model_name="auditevent",
            constraint=models.CheckConstraint(
                condition=models.Q(reason_code__in=tuple(sorted(C03_REASONS))),
                name="audit_reason_code",
            ),
        ),
        migrations.RemoveConstraint(model_name="consent", name="consent_purpose"),
        migrations.AddConstraint(
            model_name="consent",
            constraint=models.CheckConstraint(
                condition=models.Q(purpose__in=C03_CONSENT_PURPOSES),
                name="consent_purpose",
            ),
        ),
        migrations.RemoveConstraint(model_name="recordhold", name="hold_subject_kind"),
        migrations.AddConstraint(
            model_name="recordhold",
            constraint=models.CheckConstraint(
                condition=models.Q(subject_kind__in=C03_HOLD_SUBJECTS),
                name="hold_subject_kind",
            ),
        ),
    ]
