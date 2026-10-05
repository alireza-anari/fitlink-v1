from django.db import migrations, models

import apps.governance.audit_models
import apps.governance.outbox_models


class Migration(migrations.Migration):
    dependencies = [("governance", "0002_audit_append_only")]
    operations = [
        migrations.RunSQL(
            """
            CREATE FUNCTION fitlink_valid_audit_fields(value jsonb) RETURNS boolean
            LANGUAGE sql IMMUTABLE STRICT AS $$
                SELECT CASE WHEN jsonb_typeof(value) = 'array' THEN
                    jsonb_array_length(value) <= 19 AND value <@
                    '["phone","state","state_version","auth_version","birth_date",
                      "adult_attested_at","adult_attestation_version","locale",
                      "timezone","delivery_state","attempts","consumed_at",
                      "proof_applied_at","revoked_at","status","version",
                      "enabled","assigned_staff","decision"]'::jsonb
                    ELSE false END;
            $$;
            CREATE FUNCTION fitlink_valid_outbox_payload(kind text, value jsonb)
            RETURNS boolean LANGUAGE plpgsql IMMUTABLE STRICT AS $$
            DECLARE
                allowed text[];
                item record;
            BEGIN
                IF jsonb_typeof(value) <> 'object' THEN RETURN false; END IF;
                allowed := CASE kind
                    WHEN 'account.security_changed' THEN ARRAY['user_uuid']
                    WHEN 'consent.revoked' THEN ARRAY['consent_uuid','user_uuid']
                    WHEN 'privacy.intake_recorded'
                        THEN ARRAY['privacy_uuid','user_uuid']
                    WHEN 'feature_flag.changed' THEN ARRAY['flag_uuid']
                    ELSE NULL END;
                IF allowed IS NULL THEN RETURN false; END IF;
                FOR item IN SELECT * FROM jsonb_each(value) LOOP
                    IF NOT (item.key = ANY(allowed)) OR
                       jsonb_typeof(item.value) <> 'string' OR
                       (item.value #>> '{}') !~
                       '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
                    THEN RETURN false; END IF;
                END LOOP;
                RETURN true;
            END;
            $$;
            """,
            """
            DROP FUNCTION fitlink_valid_outbox_payload(text, jsonb);
            DROP FUNCTION fitlink_valid_audit_fields(jsonb);
            """,
        ),
        migrations.AddConstraint(
            model_name="auditevent",
            constraint=models.CheckConstraint(
                condition=apps.governance.audit_models.AuditFieldsAllowed(
                    "changed_fields"
                ),
                name="audit_fields_allowlist",
            ),
        ),
        migrations.AddConstraint(
            model_name="outboxevent",
            constraint=models.CheckConstraint(
                condition=apps.governance.outbox_models.OutboxPayloadAllowed(
                    "event_type", "payload"
                ),
                name="outbox_payload_id_only",
            ),
        ),
    ]
