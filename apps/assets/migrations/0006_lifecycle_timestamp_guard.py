from django.db import migrations

FORWARD = r"""
CREATE OR REPLACE FUNCTION fitlink_guard_accepted_asset_source() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    IF OLD.accepted_at IS NOT NULL AND
       (to_jsonb(NEW) - ARRAY['state','version','updated_at','processing_version',
          'finalized_at','revoked_at','rejection_code','upload_expires_at']::text[])
       IS DISTINCT FROM
       (to_jsonb(OLD) - ARRAY['state','version','updated_at','processing_version',
          'finalized_at','revoked_at','rejection_code','upload_expires_at']::text[])
    THEN
        RAISE EXCEPTION 'Accepted source binding is immutable'
            USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;
"""

REVERSE = r"""
CREATE OR REPLACE FUNCTION fitlink_guard_accepted_asset_source() RETURNS trigger
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
"""


class Migration(migrations.Migration):
    dependencies = [("assets", "0005_record_timestamps")]
    operations = [migrations.RunSQL(FORWARD, REVERSE)]
