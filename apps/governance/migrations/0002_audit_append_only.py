from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("governance", "0001_initial")]
    operations = [
        migrations.RunSQL(
            """
            CREATE FUNCTION fitlink_reject_audit_mutation() RETURNS trigger
            LANGUAGE plpgsql AS $$
            BEGIN
                RAISE EXCEPTION 'Audit evidence is append-only'
                    USING ERRCODE = '42501';
            END;
            $$;
            CREATE TRIGGER fitlink_audit_immutable
                BEFORE UPDATE OR DELETE ON governance_auditevent
                FOR EACH ROW EXECUTE FUNCTION fitlink_reject_audit_mutation();
            REVOKE UPDATE, DELETE, TRUNCATE ON governance_auditevent FROM PUBLIC;
            """,
            """
            DROP TRIGGER fitlink_audit_immutable ON governance_auditevent;
            DROP FUNCTION fitlink_reject_audit_mutation();
            """,
        )
    ]
