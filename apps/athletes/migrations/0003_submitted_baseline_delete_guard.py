from django.db import migrations

FORWARD = """
CREATE FUNCTION fitlink_guard_baseline_delete() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    IF OLD.state <> 'draft' THEN
        RAISE EXCEPTION 'Submitted baseline cannot be deleted'
            USING ERRCODE = '42501';
    END IF;
    RETURN OLD;
END;
$$;
CREATE TRIGGER fitlink_submitted_baseline_delete
    BEFORE DELETE ON athletes_baselineassessment
    FOR EACH ROW EXECUTE FUNCTION fitlink_guard_baseline_delete();
"""

REVERSE = """
DROP TRIGGER fitlink_submitted_baseline_delete ON athletes_baselineassessment;
DROP FUNCTION fitlink_guard_baseline_delete();
"""


class Migration(migrations.Migration):
    dependencies = [("athletes", "0002_baseline_guards")]
    operations = [migrations.RunSQL(FORWARD, REVERSE)]
