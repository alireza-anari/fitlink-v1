from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("governance", "0005_consent_granted_outbox")]
    operations = [
        migrations.RunSQL(
            """
            CREATE FUNCTION fitlink_consent_terminal() RETURNS trigger
            LANGUAGE plpgsql AS $$
            BEGIN
                IF TG_OP = 'DELETE' OR OLD.revoked_at IS NOT NULL THEN
                    RAISE EXCEPTION 'Consent transition denied';
                END IF;
                IF NEW.revoked_at IS NULL OR NEW.version <> OLD.version + 1
                   OR ROW(NEW.id, NEW.subject_id, NEW.grantee_id, NEW.purpose,
                          NEW.text_version, NEW.content_hash, NEW.granted_at,
                          NEW.expires_at)
                      IS DISTINCT FROM
                      ROW(OLD.id, OLD.subject_id, OLD.grantee_id, OLD.purpose,
                          OLD.text_version, OLD.content_hash, OLD.granted_at,
                          OLD.expires_at) THEN
                    RAISE EXCEPTION 'Consent transition denied';
                END IF;
                RETURN NEW;
            END; $$;
            CREATE TRIGGER consent_terminal_guard BEFORE UPDATE OR DELETE
                ON governance_consent FOR EACH ROW
                EXECUTE FUNCTION fitlink_consent_terminal();
            CREATE FUNCTION fitlink_consent_scope_immutable() RETURNS trigger
            LANGUAGE plpgsql AS $$
            BEGIN
                RAISE EXCEPTION 'Consent scope is immutable';
            END; $$;
            CREATE TRIGGER consent_scope_immutable BEFORE UPDATE OR DELETE
                ON governance_consentscope FOR EACH ROW
                EXECUTE FUNCTION fitlink_consent_scope_immutable();
            """,
            """
            DROP TRIGGER consent_scope_immutable ON governance_consentscope;
            DROP FUNCTION fitlink_consent_scope_immutable();
            DROP TRIGGER consent_terminal_guard ON governance_consent;
            DROP FUNCTION fitlink_consent_terminal();
            """,
        ),
    ]
