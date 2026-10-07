from django.db import migrations

FORWARD = """
CREATE FUNCTION fitlink_guard_assistant_nonself() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
    owner_id bigint;
BEGIN
    SELECT user_id INTO owner_id FROM professionals_professionalprofile
    WHERE id = NEW.profile_id FOR KEY SHARE;
    IF owner_id IS NULL OR owner_id = NEW.assistant_id THEN
        RAISE EXCEPTION 'Assistant cannot be profile owner'
            USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER fitlink_assistant_nonself
    BEFORE INSERT OR UPDATE OF profile_id, assistant_id
    ON professionals_assistantmembership
    FOR EACH ROW EXECUTE FUNCTION fitlink_guard_assistant_nonself();
"""

REVERSE = """
DROP TRIGGER fitlink_assistant_nonself ON professionals_assistantmembership;
DROP FUNCTION fitlink_guard_assistant_nonself();
"""


class Migration(migrations.Migration):
    dependencies = [("professionals", "0006_submission_set_guards")]
    operations = [migrations.RunSQL(FORWARD, REVERSE)]
