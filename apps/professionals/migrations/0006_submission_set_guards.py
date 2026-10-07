from django.db import migrations

FORWARD = """
CREATE FUNCTION fitlink_guard_target_membership() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
    case_state text;
BEGIN
    IF TG_OP <> 'INSERT' THEN
        SELECT state INTO case_state FROM professionals_verification
        WHERE id = OLD.verification_id FOR UPDATE;
        IF OLD.state <> 'draft' OR case_state <> 'draft' THEN
            IF TG_OP = 'DELETE' THEN
                RAISE EXCEPTION 'Submitted target cannot be deleted'
                    USING ERRCODE = '42501';
            END IF;
            IF NEW.state = 'draft' OR
                (to_jsonb(NEW) - ARRAY['state','version']::text[])
                IS DISTINCT FROM
                (to_jsonb(OLD) - ARRAY['state','version']::text[]) THEN
                RAISE EXCEPTION 'Submitted target binding is immutable'
                    USING ERRCODE = '42501';
            END IF;
        END IF;
    END IF;
    IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
    IF TG_OP = 'INSERT' OR NEW.verification_id <> OLD.verification_id THEN
        SELECT state INTO case_state FROM professionals_verification
        WHERE id = NEW.verification_id FOR UPDATE;
        IF case_state IS DISTINCT FROM 'draft' THEN
            RAISE EXCEPTION 'Submitted target set is immutable'
                USING ERRCODE = '42501';
        END IF;
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER fitlink_target_membership_immutable
    BEFORE INSERT OR UPDATE OR DELETE ON professionals_verificationtarget
    FOR EACH ROW EXECUTE FUNCTION fitlink_guard_target_membership();

CREATE FUNCTION fitlink_guard_evidence_membership() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
    target_state text;
    case_state text;
BEGIN
    IF TG_OP <> 'INSERT' THEN
        SELECT t.state, v.state INTO target_state, case_state
        FROM professionals_verification v
        JOIN professionals_verificationtarget t ON t.verification_id = v.id
        WHERE t.id = OLD.target_id FOR UPDATE OF v, t;
        IF target_state IS DISTINCT FROM 'draft'
            OR case_state IS DISTINCT FROM 'draft' THEN
            RAISE EXCEPTION 'Submitted evidence set is immutable'
                USING ERRCODE = '42501';
        END IF;
    END IF;
    IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
    SELECT t.state, v.state INTO target_state, case_state
    FROM professionals_verification v
    JOIN professionals_verificationtarget t ON t.verification_id = v.id
    WHERE t.id = NEW.target_id FOR UPDATE OF v, t;
    IF target_state IS DISTINCT FROM 'draft'
        OR case_state IS DISTINCT FROM 'draft' THEN
        RAISE EXCEPTION 'Submitted evidence set is immutable'
            USING ERRCODE = '42501';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER fitlink_evidence_membership_immutable
    BEFORE INSERT OR UPDATE OR DELETE ON professionals_verificationevidence
    FOR EACH ROW EXECUTE FUNCTION fitlink_guard_evidence_membership();
"""

REVERSE = """
DROP TRIGGER fitlink_evidence_membership_immutable
    ON professionals_verificationevidence;
DROP FUNCTION fitlink_guard_evidence_membership();
DROP TRIGGER fitlink_target_membership_immutable
    ON professionals_verificationtarget;
DROP FUNCTION fitlink_guard_target_membership();
"""


class Migration(migrations.Migration):
    dependencies = [
        (
            "professionals",
            "0005_remove_verificationtarget_target_role_declaration_pair_and_more",
        )
    ]
    operations = [migrations.RunSQL(FORWARD, REVERSE)]
