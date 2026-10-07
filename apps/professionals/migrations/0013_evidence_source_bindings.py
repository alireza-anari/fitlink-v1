from django.db import migrations

FORWARD = """
CREATE FUNCTION fitlink_guard_credential_identity() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.profile_id IS DISTINCT FROM OLD.profile_id OR
       NEW.role_id IS DISTINCT FROM OLD.role_id OR
       NEW.category IS DISTINCT FROM OLD.category THEN
        RAISE EXCEPTION 'Credential identity is immutable'
            USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER fitlink_credential_identity_immutable
    BEFORE UPDATE ON professionals_credential
    FOR EACH ROW EXECUTE FUNCTION fitlink_guard_credential_identity();

CREATE FUNCTION fitlink_guard_revision_source_binding() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
    credential_profile uuid;
    credential_owner bigint;
    credential_category text;
    source_owner bigint;
    source_purpose text;
    source_hash text;
    source_subject_kind text;
    source_subject uuid;
BEGIN
    SELECT c.profile_id, c.category INTO credential_profile, credential_category
      FROM professionals_credential c WHERE c.id = NEW.credential_id;
    SELECT p.user_id INTO credential_owner
      FROM professionals_professionalprofile p
     WHERE p.id = credential_profile FOR UPDATE;
    PERFORM 1 FROM professionals_credential
     WHERE id = NEW.credential_id FOR UPDATE;
    SELECT a.owner_id, a.purpose, a.sha256, a.subject_kind, a.subject_uuid
      INTO source_owner, source_purpose, source_hash,
           source_subject_kind, source_subject
      FROM assets_asset a WHERE a.id = NEW.source_asset_id FOR UPDATE;
    IF credential_owner IS NULL OR source_owner IS NULL OR
       source_owner IS DISTINCT FROM credential_owner OR
       source_hash IS DISTINCT FROM NEW.source_sha256 OR
       credential_category IS DISTINCT FROM NEW.category OR
       (NEW.category = 'identity' AND source_purpose <> 'identity_evidence') OR
       (NEW.category = 'qualification' AND source_purpose <> 'credential_evidence') OR
       NOT ((source_subject_kind = 'professional_profile' AND
                source_subject = credential_profile) OR
            (source_subject_kind = 'professional_credential' AND
                source_subject = NEW.credential_id)) THEN
        RAISE EXCEPTION 'Credential source binding mismatch'
            USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER fitlink_revision_source_bound
    BEFORE INSERT ON professionals_credentialrevision
    FOR EACH ROW EXECUTE FUNCTION fitlink_guard_revision_source_binding();

CREATE FUNCTION fitlink_guard_history_case_binding() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
    target_case uuid;
BEGIN
    IF NEW.target_id IS NOT NULL THEN
        SELECT verification_id INTO target_case
          FROM professionals_verificationtarget
         WHERE id = NEW.target_id FOR UPDATE;
        IF target_case IS DISTINCT FROM NEW.verification_id THEN
            RAISE EXCEPTION 'History target case mismatch'
                USING ERRCODE = '23514';
        END IF;
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER fitlink_history_case_bound
    BEFORE INSERT ON professionals_verificationhistory
    FOR EACH ROW EXECUTE FUNCTION fitlink_guard_history_case_binding();
"""

REVERSE = """
DROP TRIGGER fitlink_history_case_bound ON professionals_verificationhistory;
DROP FUNCTION fitlink_guard_history_case_binding();
DROP TRIGGER fitlink_revision_source_bound ON professionals_credentialrevision;
DROP FUNCTION fitlink_guard_revision_source_binding();
DROP TRIGGER fitlink_credential_identity_immutable ON professionals_credential;
DROP FUNCTION fitlink_guard_credential_identity();
"""


class Migration(migrations.Migration):
    dependencies = [
        ("professionals", "0012_profile_json_contract"),
        ("assets", "0004_immutable_accepted_source"),
    ]
    operations = [migrations.RunSQL(FORWARD, REVERSE)]
