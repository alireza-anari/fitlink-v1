from django.db import migrations

FORWARD = r"""
CREATE OR REPLACE FUNCTION fitlink_guard_submitted_verification() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    IF OLD.state IN ('submitted', 'under_review', 'decided', 'withdrawn') AND
       (to_jsonb(NEW) - ARRAY['state','version','updated_at','decided_at']::text[])
       IS DISTINCT FROM
       (to_jsonb(OLD) - ARRAY['state','version','updated_at','decided_at']::text[])
    THEN
        RAISE EXCEPTION 'Submitted verification snapshot is immutable'
            USING ERRCODE = '42501';
    END IF;
    RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION fitlink_guard_submitted_target() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    IF OLD.state IN (
        'submitted','under_review','approved','rejected','stale','withdrawn'
    ) AND
       (to_jsonb(NEW) - ARRAY['state','version','updated_at']::text[])
       IS DISTINCT FROM
       (to_jsonb(OLD) - ARRAY['state','version','updated_at']::text[])
    THEN
        RAISE EXCEPTION 'Submitted verification target is immutable'
            USING ERRCODE = '42501';
    END IF;
    RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION fitlink_guard_target_membership() RETURNS trigger
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
                (to_jsonb(NEW) - ARRAY['state','version','updated_at']::text[])
                IS DISTINCT FROM
                (to_jsonb(OLD) - ARRAY['state','version','updated_at']::text[]) THEN
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
"""

REVERSE = r"""
CREATE OR REPLACE FUNCTION fitlink_guard_submitted_verification() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    IF OLD.state IN ('submitted', 'under_review', 'decided', 'withdrawn') AND
       (to_jsonb(NEW) - ARRAY['state','version','decided_at']::text[])
       IS DISTINCT FROM
       (to_jsonb(OLD) - ARRAY['state','version','decided_at']::text[])
    THEN
        RAISE EXCEPTION 'Submitted verification snapshot is immutable'
            USING ERRCODE = '42501';
    END IF;
    RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION fitlink_guard_submitted_target() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    IF OLD.state IN (
        'submitted','under_review','approved','rejected','stale','withdrawn'
    ) AND
       (to_jsonb(NEW) - ARRAY['state','version']::text[])
       IS DISTINCT FROM
       (to_jsonb(OLD) - ARRAY['state','version']::text[])
    THEN
        RAISE EXCEPTION 'Submitted verification target is immutable'
            USING ERRCODE = '42501';
    END IF;
    RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION fitlink_guard_target_membership() RETURNS trigger
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
"""


class Migration(migrations.Migration):
    dependencies = [("professionals", "0014_record_timestamps")]
    operations = [migrations.RunSQL(FORWARD, REVERSE)]
