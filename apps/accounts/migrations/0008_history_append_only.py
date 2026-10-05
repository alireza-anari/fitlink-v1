from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("accounts", "0007_recoveryrequest_recovery_live_target")]
    operations = [
        migrations.RunSQL(
            """
        CREATE FUNCTION fitlink_reject_history_mutation() RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            RAISE EXCEPTION 'Phone history is append-only' USING ERRCODE = '42501';
        END;
        $$;
        CREATE TRIGGER fitlink_history_immutable BEFORE UPDATE OR DELETE
            ON accounts_phonechangehistory FOR EACH ROW
            EXECUTE FUNCTION fitlink_reject_history_mutation();
        REVOKE UPDATE, DELETE, TRUNCATE ON accounts_phonechangehistory FROM PUBLIC;
        """,
            """
        DROP TRIGGER fitlink_history_immutable ON accounts_phonechangehistory;
        DROP FUNCTION fitlink_reject_history_mutation();
        """,
        )
    ]
