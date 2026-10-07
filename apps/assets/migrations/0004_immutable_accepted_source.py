from django.db import migrations

FORWARD = """
CREATE FUNCTION fitlink_guard_accepted_asset_source() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    IF OLD.accepted_at IS NOT NULL AND
       (to_jsonb(NEW) - ARRAY['state','version','processing_version',
          'finalized_at','revoked_at','rejection_code','upload_expires_at']::text[])
       IS DISTINCT FROM
       (to_jsonb(OLD) - ARRAY['state','version','processing_version',
          'finalized_at','revoked_at','rejection_code','upload_expires_at']::text[])
    THEN
        RAISE EXCEPTION 'Accepted source binding is immutable'
            USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER fitlink_accepted_asset_source_immutable
    BEFORE UPDATE ON assets_asset
    FOR EACH ROW EXECUTE FUNCTION fitlink_guard_accepted_asset_source();
"""

REVERSE = """
DROP TRIGGER fitlink_accepted_asset_source_immutable ON assets_asset;
DROP FUNCTION fitlink_guard_accepted_asset_source();
"""


class Migration(migrations.Migration):
    dependencies = [("assets", "0003_bounded_metadata")]
    operations = [migrations.RunSQL(FORWARD, REVERSE)]
