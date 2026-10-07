from django.db import migrations


FORWARD = """
CREATE OR REPLACE FUNCTION fitlink_reject_professional_evidence_mutation() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'Professional evidence is append-only'
        USING ERRCODE = '42501';
END;
$$;

CREATE TRIGGER fitlink_credential_revision_immutable
    BEFORE UPDATE OR DELETE ON professionals_credentialrevision
    FOR EACH ROW EXECUTE FUNCTION fitlink_reject_professional_evidence_mutation();
CREATE TRIGGER fitlink_verification_decision_immutable
    BEFORE UPDATE OR DELETE ON professionals_verificationdecision
    FOR EACH ROW EXECUTE FUNCTION fitlink_reject_professional_evidence_mutation();
CREATE TRIGGER fitlink_verification_history_immutable
    BEFORE UPDATE OR DELETE ON professionals_verificationhistory
    FOR EACH ROW EXECUTE FUNCTION fitlink_reject_professional_evidence_mutation();
CREATE TRIGGER fitlink_role_restriction_history_immutable
    BEFORE UPDATE OR DELETE ON professionals_rolerestrictionhistory
    FOR EACH ROW EXECUTE FUNCTION fitlink_reject_professional_evidence_mutation();

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
CREATE TRIGGER fitlink_submitted_verification_immutable
    BEFORE UPDATE ON professionals_verification
    FOR EACH ROW EXECUTE FUNCTION fitlink_guard_submitted_verification();

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
CREATE TRIGGER fitlink_submitted_target_immutable
    BEFORE UPDATE ON professionals_verificationtarget
    FOR EACH ROW EXECUTE FUNCTION fitlink_guard_submitted_target();

CREATE OR REPLACE FUNCTION fitlink_guard_submitted_evidence() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
    target_state text;
BEGIN
    SELECT state INTO target_state
      FROM professionals_verificationtarget
     WHERE id = OLD.target_id;
    IF target_state IN (
        'submitted','under_review','approved','rejected','stale','withdrawn'
    ) THEN
        RAISE EXCEPTION 'Submitted verification evidence is immutable'
            USING ERRCODE = '42501';
    END IF;
    IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER fitlink_submitted_evidence_immutable
    BEFORE UPDATE OR DELETE ON professionals_verificationevidence
    FOR EACH ROW EXECUTE FUNCTION fitlink_guard_submitted_evidence();

REVOKE UPDATE, DELETE, TRUNCATE ON professionals_credentialrevision FROM PUBLIC;
REVOKE UPDATE, DELETE, TRUNCATE ON professionals_verificationdecision FROM PUBLIC;
REVOKE UPDATE, DELETE, TRUNCATE ON professionals_verificationhistory FROM PUBLIC;
REVOKE UPDATE, DELETE, TRUNCATE ON professionals_rolerestrictionhistory FROM PUBLIC;
"""

REVERSE = """
DROP TRIGGER IF EXISTS fitlink_submitted_evidence_immutable ON professionals_verificationevidence;
DROP FUNCTION IF EXISTS fitlink_guard_submitted_evidence();
DROP TRIGGER IF EXISTS fitlink_submitted_target_immutable ON professionals_verificationtarget;
DROP FUNCTION IF EXISTS fitlink_guard_submitted_target();
DROP TRIGGER IF EXISTS fitlink_submitted_verification_immutable ON professionals_verification;
DROP FUNCTION IF EXISTS fitlink_guard_submitted_verification();
DROP TRIGGER IF EXISTS fitlink_role_restriction_history_immutable ON professionals_rolerestrictionhistory;
DROP TRIGGER IF EXISTS fitlink_verification_history_immutable ON professionals_verificationhistory;
DROP TRIGGER IF EXISTS fitlink_verification_decision_immutable ON professionals_verificationdecision;
DROP TRIGGER IF EXISTS fitlink_credential_revision_immutable ON professionals_credentialrevision;
DROP FUNCTION IF EXISTS fitlink_reject_professional_evidence_mutation();
"""


class Migration(migrations.Migration):
    dependencies = [("professionals", "0002_relational_guards")]
    operations = [migrations.RunSQL(FORWARD, REVERSE)]
