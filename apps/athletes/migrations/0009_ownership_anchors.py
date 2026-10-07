from django.db import migrations

FORWARD = """
CREATE FUNCTION fitlink_guard_athlete_owner() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.user_id IS DISTINCT FROM OLD.user_id THEN
        RAISE EXCEPTION 'Athlete profile owner is permanent'
            USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER fitlink_athlete_owner_permanent
    BEFORE UPDATE OF user_id ON athletes_athleteprofile
    FOR EACH ROW EXECUTE FUNCTION fitlink_guard_athlete_owner();

CREATE FUNCTION fitlink_guard_baseline_identity() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
    parent_athlete uuid;
BEGIN
    IF TG_OP = 'UPDATE' AND NEW.athlete_id IS DISTINCT FROM OLD.athlete_id THEN
        RAISE EXCEPTION 'Baseline athlete is permanent'
            USING ERRCODE = '23514';
    END IF;
    IF NEW.parent_id IS NOT NULL THEN
        SELECT athlete_id INTO parent_athlete
          FROM athletes_baselineassessment
         WHERE id = NEW.parent_id FOR UPDATE;
        IF parent_athlete IS DISTINCT FROM NEW.athlete_id THEN
            RAISE EXCEPTION 'Correction parent belongs to another athlete'
                USING ERRCODE = '23514';
        END IF;
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER fitlink_baseline_identity_bound
    BEFORE INSERT OR UPDATE OF athlete_id, parent_id ON athletes_baselineassessment
    FOR EACH ROW EXECUTE FUNCTION fitlink_guard_baseline_identity();
"""

REVERSE = """
DROP TRIGGER fitlink_baseline_identity_bound ON athletes_baselineassessment;
DROP FUNCTION fitlink_guard_baseline_identity();
DROP TRIGGER fitlink_athlete_owner_permanent ON athletes_athleteprofile;
DROP FUNCTION fitlink_guard_athlete_owner();
"""


class Migration(migrations.Migration):
    dependencies = [("athletes", "0008_lifecycle_timestamp_guard")]
    operations = [migrations.RunSQL(FORWARD, REVERSE)]
