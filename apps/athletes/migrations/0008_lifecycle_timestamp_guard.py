from django.db import migrations

FORWARD = r"""
CREATE OR REPLACE FUNCTION fitlink_guard_baseline_answers() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    IF OLD.state IN ('submitted', 'superseded') AND
       (
         to_jsonb(NEW) - ARRAY['state','version','updated_at']::text[]
       ) IS DISTINCT FROM (
         to_jsonb(OLD) - ARRAY['state','version','updated_at']::text[]
       )
    THEN
        RAISE EXCEPTION 'Submitted baseline answers are immutable'
            USING ERRCODE = '42501';
    END IF;
    RETURN NEW;
END;
$$;
"""

REVERSE = r"""
CREATE OR REPLACE FUNCTION fitlink_guard_baseline_answers() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    IF OLD.state IN ('submitted', 'superseded') AND
       (
         to_jsonb(NEW) - ARRAY['state','version']::text[]
       ) IS DISTINCT FROM (
         to_jsonb(OLD) - ARRAY['state','version']::text[]
       )
    THEN
        RAISE EXCEPTION 'Submitted baseline answers are immutable'
            USING ERRCODE = '42501';
    END IF;
    RETURN NEW;
END;
$$;
"""


class Migration(migrations.Migration):
    dependencies = [("athletes", "0007_record_timestamps")]
    operations = [migrations.RunSQL(FORWARD, REVERSE)]
