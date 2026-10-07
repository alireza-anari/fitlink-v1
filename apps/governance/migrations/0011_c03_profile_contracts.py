from django.db import migrations, models

C03_EVENT_TYPES = (
    "account.security_changed",
    "consent.granted",
    "consent.revoked",
    "privacy.intake_recorded",
    "feature_flag.changed",
    "athlete.baseline_changed",
    "professional.profile_changed",
    "verification.changed",
    "asset.processing_requested",
    "asset.cleanup_requested",
    "assistant.membership_changed",
)
C03_CAPABILITIES = (
    "account_recovery",
    "account_restriction",
    "security_audit",
    "privacy_operations",
    "feature_flags",
    "professional_verification",
)


FORWARD = r"""
CREATE OR REPLACE FUNCTION fitlink_valid_outbox_payload(
    kind text, value jsonb)
RETURNS boolean LANGUAGE plpgsql IMMUTABLE STRICT AS $$
DECLARE
    allowed text[];
    item record;
BEGIN
    IF jsonb_typeof(value) <> 'object' THEN RETURN false; END IF;
    allowed := CASE kind
        WHEN 'account.security_changed' THEN ARRAY['user_uuid']
        WHEN 'consent.granted' THEN ARRAY['consent_uuid','user_uuid']
        WHEN 'consent.revoked' THEN ARRAY['consent_uuid','user_uuid']
        WHEN 'privacy.intake_recorded' THEN ARRAY['privacy_uuid','user_uuid']
        WHEN 'feature_flag.changed' THEN ARRAY['flag_uuid']
        WHEN 'athlete.baseline_changed' THEN ARRAY['baseline_uuid','user_uuid']
        WHEN 'professional.profile_changed' THEN ARRAY['profile_uuid','user_uuid']
        WHEN 'verification.changed' THEN ARRAY['verification_uuid','user_uuid']
        WHEN 'asset.processing_requested' THEN ARRAY['asset_uuid','user_uuid']
        WHEN 'asset.cleanup_requested' THEN ARRAY['asset_uuid','user_uuid']
        WHEN 'assistant.membership_changed' THEN ARRAY['membership_uuid','user_uuid']
        ELSE NULL END;
    IF allowed IS NULL THEN RETURN false; END IF;
    FOR item IN SELECT * FROM jsonb_each(value) LOOP
        IF NOT (item.key = ANY(allowed))
           OR jsonb_typeof(item.value) <> 'string'
           OR (item.value #>> '{}') !~
              '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        THEN RETURN false; END IF;
    END LOOP;
    RETURN true;
END;
$$;
"""

REVERSE = r"""
CREATE OR REPLACE FUNCTION fitlink_valid_outbox_payload(
    kind text, value jsonb)
RETURNS boolean LANGUAGE plpgsql IMMUTABLE STRICT AS $$
DECLARE
    allowed text[];
    item record;
BEGIN
    IF jsonb_typeof(value) <> 'object' THEN RETURN false; END IF;
    allowed := CASE kind
        WHEN 'account.security_changed' THEN ARRAY['user_uuid']
        WHEN 'consent.granted' THEN ARRAY['consent_uuid','user_uuid']
        WHEN 'consent.revoked' THEN ARRAY['consent_uuid','user_uuid']
        WHEN 'privacy.intake_recorded' THEN ARRAY['privacy_uuid','user_uuid']
        WHEN 'feature_flag.changed' THEN ARRAY['flag_uuid']
        ELSE NULL END;
    IF allowed IS NULL THEN RETURN false; END IF;
    FOR item IN SELECT * FROM jsonb_each(value) LOOP
        IF NOT (item.key = ANY(allowed))
           OR jsonb_typeof(item.value) <> 'string'
           OR (item.value #>> '{}') !~
              '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        THEN RETURN false; END IF;
    END LOOP;
    RETURN true;
END;
$$;
"""


class Migration(migrations.Migration):
    dependencies = [("governance", "0010_outboxdeliveryreceipt")]
    operations = [
        migrations.RunSQL(FORWARD, REVERSE),
        migrations.RemoveConstraint(model_name="outboxevent", name="outbox_type"),
        migrations.AddConstraint(
            model_name="outboxevent",
            constraint=models.CheckConstraint(
                condition=models.Q(event_type__in=C03_EVENT_TYPES),
                name="outbox_type",
            ),
        ),
        migrations.RemoveConstraint(
            model_name="staffcapabilitygrant", name="staff_capability_kind"
        ),
        migrations.AddConstraint(
            model_name="staffcapabilitygrant",
            constraint=models.CheckConstraint(
                condition=models.Q(capability__in=C03_CAPABILITIES),
                name="staff_capability_kind",
            ),
        ),
        migrations.RemoveConstraint(
            model_name="staffstepupgrant", name="step_up_capability_kind"
        ),
        migrations.AddConstraint(
            model_name="staffstepupgrant",
            constraint=models.CheckConstraint(
                condition=models.Q(capability__in=C03_CAPABILITIES),
                name="step_up_capability_kind",
            ),
        ),
    ]
