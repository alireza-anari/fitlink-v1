from django.db import migrations


FORWARD = """
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
        SELECT d.target_id, d.profile_id, d.target_kind, d.decision
          INTO approval_target, approval_profile, approval_kind, approval_decision
          FROM professionals_verificationdecision AS d
         WHERE d.id = NEW.revoked_approval_id;
        IF approval_decision <> 'approve'
           OR approval_target <> NEW.target_id
           OR approval_profile <> NEW.profile_id
           OR approval_kind <> NEW.target_kind THEN
            RAISE EXCEPTION 'Revocation must reference same target approval'
                USING ERRCODE = '23514';
        END IF;
    END IF;

    IF NEW.supersedes_decision_id IS NOT NULL THEN
        SELECT d.profile_id, d.target_kind
          INTO supersedes_profile, supersedes_kind
          FROM professionals_verificationdecision AS d
         WHERE d.id = NEW.supersedes_decision_id;
        IF supersedes_profile <> NEW.profile_id OR supersedes_kind <> NEW.target_kind THEN
            RAISE EXCEPTION 'Superseded decision target mismatch'
                USING ERRCODE = '23514';
        END IF;
    END IF;
    RETURN NEW;
END;
$$;
"""

REVERSE = """
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
"""


class Migration(migrations.Migration):
    dependencies = [("professionals", "0003_immutable_evidence_guards")]
    operations = [migrations.RunSQL(FORWARD, REVERSE)]
