from django.db import migrations


FORWARD = r"""
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
CREATE TRIGGER fitlink_baseline_answers_immutable
    BEFORE UPDATE ON athletes_baselineassessment
    FOR EACH ROW EXECUTE FUNCTION fitlink_guard_baseline_answers();

CREATE OR REPLACE FUNCTION fitlink_guard_current_baseline() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.current_baseline_id IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM athletes_baselineassessment b
        WHERE b.id = NEW.current_baseline_id AND b.athlete_id = NEW.id
    ) THEN
        RAISE EXCEPTION 'Current baseline must belong to athlete'
            USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER fitlink_current_baseline_owned
    BEFORE INSERT OR UPDATE OF current_baseline_id ON athletes_athleteprofile
    FOR EACH ROW EXECUTE FUNCTION fitlink_guard_current_baseline();
"""

REVERSE = r"""
DROP TRIGGER IF EXISTS fitlink_current_baseline_owned ON athletes_athleteprofile;
DROP FUNCTION IF EXISTS fitlink_guard_current_baseline();
DROP TRIGGER IF EXISTS fitlink_baseline_answers_immutable ON athletes_baselineassessment;
DROP FUNCTION IF EXISTS fitlink_guard_baseline_answers();
"""


class Migration(migrations.Migration):
    dependencies = [("athletes", "0001_initial")]
    operations = [migrations.RunSQL(FORWARD, REVERSE)]
