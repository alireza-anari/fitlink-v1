from django.db import migrations

FORWARD = """
CREATE FUNCTION fitlink_guard_decision_snapshot() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
    target_hash text;
    target_revision bigint;
BEGIN
    SELECT target_snapshot_hash, bound_evidence_revision
      INTO target_hash, target_revision
      FROM professionals_verificationtarget
     WHERE id = NEW.target_id FOR UPDATE;
    IF target_hash IS NULL
       OR target_hash IS DISTINCT FROM NEW.target_snapshot_hash
       OR target_revision IS DISTINCT FROM NEW.bound_evidence_revision THEN
        RAISE EXCEPTION 'Decision snapshot binding mismatch'
            USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER fitlink_decision_snapshot_bound
    BEFORE INSERT ON professionals_verificationdecision
    FOR EACH ROW EXECUTE FUNCTION fitlink_guard_decision_snapshot();
"""

REVERSE = """
DROP TRIGGER fitlink_decision_snapshot_bound ON professionals_verificationdecision;
DROP FUNCTION fitlink_guard_decision_snapshot();
"""


class Migration(migrations.Migration):
    dependencies = [("professionals", "0009_evidence_metadata_contracts")]
    operations = [migrations.RunSQL(FORWARD, REVERSE)]
