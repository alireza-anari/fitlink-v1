from django.db import migrations

FORWARD = """
CREATE FUNCTION fitlink_guard_professional_owner() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.user_id IS DISTINCT FROM OLD.user_id THEN
        RAISE EXCEPTION 'Professional profile owner is permanent'
            USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER fitlink_professional_owner_permanent
    BEFORE UPDATE OF user_id ON professionals_professionalprofile
    FOR EACH ROW EXECUTE FUNCTION fitlink_guard_professional_owner();

CREATE FUNCTION fitlink_guard_role_identity() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.profile_id IS DISTINCT FROM OLD.profile_id OR
       NEW.role IS DISTINCT FROM OLD.role THEN
        RAISE EXCEPTION 'Professional role identity is permanent'
            USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER fitlink_role_identity_permanent
    BEFORE UPDATE OF profile_id, role ON professionals_professionalrole
    FOR EACH ROW EXECUTE FUNCTION fitlink_guard_role_identity();
"""

REVERSE = """
DROP TRIGGER fitlink_role_identity_permanent ON professionals_professionalrole;
DROP FUNCTION fitlink_guard_role_identity();
DROP TRIGGER fitlink_professional_owner_permanent ON professionals_professionalprofile;
DROP FUNCTION fitlink_guard_professional_owner();
"""


class Migration(migrations.Migration):
    dependencies = [("professionals", "0016_lifecycle_metadata")]
    operations = [migrations.RunSQL(FORWARD, REVERSE)]
