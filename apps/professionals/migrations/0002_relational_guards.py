from django.db import migrations


FORWARD = """
CREATE OR REPLACE FUNCTION fitlink_guard_professional_role_reference() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
    role_profile uuid;
BEGIN
    IF NEW.role_id IS NOT NULL THEN
        SELECT profile_id INTO role_profile
        FROM professionals_professionalrole
        WHERE id = NEW.role_id;
        IF role_profile IS NULL OR role_profile <> NEW.profile_id THEN
            RAISE EXCEPTION 'Credential role must belong to profile'
                USING ERRCODE = '23514';
        END IF;
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER fitlink_credential_role_owned
    BEFORE INSERT OR UPDATE OF profile_id, role_id, category
    ON professionals_credential
    FOR EACH ROW EXECUTE FUNCTION fitlink_guard_professional_role_reference();

CREATE OR REPLACE FUNCTION fitlink_guard_credential_current_revision() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.current_revision_id IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM professionals_credentialrevision r
        WHERE r.id = NEW.current_revision_id AND r.credential_id = NEW.id
    ) THEN
        RAISE EXCEPTION 'Current credential revision must belong to credential'
            USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER fitlink_credential_revision_owned
    BEFORE INSERT OR UPDATE OF current_revision_id
    ON professionals_credential
    FOR EACH ROW EXECUTE FUNCTION fitlink_guard_credential_current_revision();

CREATE OR REPLACE FUNCTION fitlink_guard_verification_target() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
    verification_profile uuid;
    role_profile uuid;
    role_kind text;
BEGIN
    SELECT profile_id INTO verification_profile
    FROM professionals_verification
    WHERE id = NEW.verification_id;
    IF verification_profile IS NULL THEN
        RAISE EXCEPTION 'Verification target requires case'
            USING ERRCODE = '23514';
    END IF;
    IF NEW.target = 'identity' THEN
        IF NEW.role_id IS NOT NULL OR NEW.bound_declaration_version IS NOT NULL THEN
            RAISE EXCEPTION 'Identity target cannot bind role'
                USING ERRCODE = '23514';
        END IF;
    ELSE
        SELECT profile_id, role INTO role_profile, role_kind
        FROM professionals_professionalrole
        WHERE id = NEW.role_id;
        IF role_profile IS NULL
           OR role_profile <> verification_profile
           OR role_kind <> NEW.target THEN
            RAISE EXCEPTION 'Verification role target mismatch'
                USING ERRCODE = '23514';
        END IF;
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER fitlink_verification_target_owned
    BEFORE INSERT OR UPDATE OF verification_id, target, role_id, bound_declaration_version
    ON professionals_verificationtarget
    FOR EACH ROW EXECUTE FUNCTION fitlink_guard_verification_target();

CREATE OR REPLACE FUNCTION fitlink_guard_verification_evidence() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
    target_kind text;
    target_role uuid;
    target_profile uuid;
    credential_role uuid;
    credential_profile uuid;
    credential_category text;
    revision_category text;
BEGIN
    SELECT t.target, t.role_id, v.profile_id
      INTO target_kind, target_role, target_profile
      FROM professionals_verificationtarget t
      JOIN professionals_verification v ON v.id = t.verification_id
     WHERE t.id = NEW.target_id;

    SELECT c.role_id, c.profile_id, c.category, r.category
      INTO credential_role, credential_profile, credential_category, revision_category
      FROM professionals_credentialrevision r
      JOIN professionals_credential c ON c.id = r.credential_id
     WHERE r.id = NEW.credential_revision_id;

    IF target_kind IS NULL OR credential_profile IS NULL
       OR credential_profile <> target_profile
       OR credential_category <> NEW.category
       OR revision_category <> NEW.category THEN
        RAISE EXCEPTION 'Verification evidence profile/category mismatch'
            USING ERRCODE = '23514';
    END IF;

    IF target_kind = 'identity' THEN
        IF credential_role IS NOT NULL OR NEW.category <> 'identity' THEN
            RAISE EXCEPTION 'Identity evidence mismatch'
                USING ERRCODE = '23514';
        END IF;
    ELSE
        IF credential_role IS NULL
           OR credential_role <> target_role
           OR NEW.category <> 'qualification' THEN
            RAISE EXCEPTION 'Capability evidence mismatch'
                USING ERRCODE = '23514';
        END IF;
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER fitlink_verification_evidence_owned
    BEFORE INSERT OR UPDATE OF target_id, credential_revision_id, category
    ON professionals_verificationevidence
    FOR EACH ROW EXECUTE FUNCTION fitlink_guard_verification_evidence();

CREATE OR REPLACE FUNCTION fitlink_guard_verification_assignment() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
    owner_id bigint;
BEGIN
    SELECT p.user_id INTO owner_id
      FROM professionals_verification v
      JOIN professionals_professionalprofile p ON p.id = v.profile_id
     WHERE v.id = NEW.verification_id;
    IF owner_id IS NULL OR NEW.assignee_id = owner_id THEN
        RAISE EXCEPTION 'Verification cannot be assigned to profile owner'
            USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER fitlink_verification_assignment_nonself
    BEFORE INSERT OR UPDATE OF verification_id, assignee_id
    ON professionals_verificationassignment
    FOR EACH ROW EXECUTE FUNCTION fitlink_guard_verification_assignment();

CREATE OR REPLACE FUNCTION fitlink_guard_verification_decision() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
    target_kind text;
    target_profile uuid;
    approval_target uuid;
    approval_profile uuid;
    approval_kind text;
    approval_decision text;
    supersedes_profile uuid;
    supersedes_kind text;
BEGIN
    SELECT t.target, v.profile_id
      INTO target_kind, target_profile
      FROM professionals_verificationtarget t
      JOIN professionals_verification v ON v.id = t.verification_id
     WHERE t.id = NEW.target_id;
    IF target_kind IS NULL
       OR target_kind <> NEW.target_kind
       OR target_profile <> NEW.profile_id THEN
        RAISE EXCEPTION 'Verification decision target mismatch'
            USING ERRCODE = '23514';
    END IF;

    IF NEW.revoked_approval_id IS NOT NULL THEN
        SELECT target_id, profile_id, target_kind, decision
          INTO approval_target, approval_profile, approval_kind, approval_decision
          FROM professionals_verificationdecision
         WHERE id = NEW.revoked_approval_id;
        IF approval_decision <> 'approve'
           OR approval_target <> NEW.target_id
           OR approval_profile <> NEW.profile_id
           OR approval_kind <> NEW.target_kind THEN
            RAISE EXCEPTION 'Revocation must reference same target approval'
                USING ERRCODE = '23514';
        END IF;
    END IF;

    IF NEW.supersedes_decision_id IS NOT NULL THEN
        SELECT profile_id, target_kind
          INTO supersedes_profile, supersedes_kind
          FROM professionals_verificationdecision
         WHERE id = NEW.supersedes_decision_id;
        IF supersedes_profile <> NEW.profile_id OR supersedes_kind <> NEW.target_kind THEN
            RAISE EXCEPTION 'Superseded decision target mismatch'
                USING ERRCODE = '23514';
        END IF;
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER fitlink_verification_decision_owned
    BEFORE INSERT ON professionals_verificationdecision
    FOR EACH ROW EXECUTE FUNCTION fitlink_guard_verification_decision();

CREATE OR REPLACE FUNCTION fitlink_guard_role_restriction() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
    role_profile uuid;
    verification_profile uuid;
BEGIN
    SELECT profile_id INTO role_profile
      FROM professionals_professionalrole WHERE id = NEW.role_id;
    SELECT profile_id INTO verification_profile
      FROM professionals_verification WHERE id = NEW.verification_id;
    IF role_profile IS NULL OR verification_profile IS NULL
       OR role_profile <> verification_profile THEN
        RAISE EXCEPTION 'Restriction case/profile mismatch'
            USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER fitlink_role_restriction_owned
    BEFORE INSERT OR UPDATE OF role_id, verification_id
    ON professionals_professionalrolerestriction
    FOR EACH ROW EXECUTE FUNCTION fitlink_guard_role_restriction();
"""

REVERSE = """
DROP TRIGGER IF EXISTS fitlink_role_restriction_owned ON professionals_professionalrolerestriction;
DROP FUNCTION IF EXISTS fitlink_guard_role_restriction();
DROP TRIGGER IF EXISTS fitlink_verification_decision_owned ON professionals_verificationdecision;
DROP FUNCTION IF EXISTS fitlink_guard_verification_decision();
DROP TRIGGER IF EXISTS fitlink_verification_assignment_nonself ON professionals_verificationassignment;
DROP FUNCTION IF EXISTS fitlink_guard_verification_assignment();
DROP TRIGGER IF EXISTS fitlink_verification_evidence_owned ON professionals_verificationevidence;
DROP FUNCTION IF EXISTS fitlink_guard_verification_evidence();
DROP TRIGGER IF EXISTS fitlink_verification_target_owned ON professionals_verificationtarget;
DROP FUNCTION IF EXISTS fitlink_guard_verification_target();
DROP TRIGGER IF EXISTS fitlink_credential_revision_owned ON professionals_credential;
DROP FUNCTION IF EXISTS fitlink_guard_credential_current_revision();
DROP TRIGGER IF EXISTS fitlink_credential_role_owned ON professionals_credential;
DROP FUNCTION IF EXISTS fitlink_guard_professional_role_reference();
"""


class Migration(migrations.Migration):
    dependencies = [("professionals", "0001_profile_verification_metadata")]
    operations = [migrations.RunSQL(FORWARD, REVERSE)]
