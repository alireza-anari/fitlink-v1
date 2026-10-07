from django.db import migrations

FORWARD = r"""
CREATE FUNCTION fitlink_valid_baseline_json(field text, value jsonb) RETURNS boolean
LANGUAGE plpgsql IMMUTABLE AS $$
DECLARE
    allowed text[];
    cap integer;
    item jsonb;
    measured numeric;
    observed timestamptz;
BEGIN
    IF value IS NULL OR jsonb_typeof(value) <> 'array' THEN RETURN false; END IF;
    CASE field
      WHEN 'goals' THEN
        allowed := ARRAY['general_fitness','strength','endurance',
                         'muscle_gain','weight_management']; cap := 5;
      WHEN 'equipment' THEN
        allowed := ARRAY['bodyweight','dumbbells','barbell','machines',
                         'bands','other']; cap := 6;
      WHEN 'facilities' THEN
        allowed := ARRAY['home','gym','outdoors','other']; cap := 4;
      WHEN 'available_days' THEN cap := 7;
      WHEN 'approximate_records' THEN cap := 5;
      ELSE RETURN false;
    END CASE;
    IF jsonb_array_length(value) > cap THEN RETURN false; END IF;
    IF field <> 'approximate_records' AND
       (SELECT count(*) <> count(DISTINCT element)
          FROM jsonb_array_elements(value) AS entries(element)) THEN
        RETURN false;
    END IF;
    FOR item IN SELECT element FROM jsonb_array_elements(value) AS entries(element)
    LOOP
        IF field = 'available_days' THEN
            IF jsonb_typeof(item) <> 'number' OR item::text !~ '^[1-7]$' THEN
                RETURN false;
            END IF;
        ELSIF field = 'approximate_records' THEN
            IF jsonb_typeof(item) <> 'object' OR
               NOT (item ?& ARRAY['label','value','unit','observed_at','provenance']) OR
               (item - ARRAY['label','value','unit','observed_at','provenance'])
                   <> '{}'::jsonb OR
               jsonb_typeof(item->'label') <> 'string' OR
               length(item->>'label') NOT BETWEEN 1 AND 80 OR
               jsonb_typeof(item->'unit') <> 'string' OR
               item->>'unit' NOT IN ('kg','reps','seconds','metres') OR
               item->>'provenance' IS DISTINCT FROM 'self_reported' OR
               jsonb_typeof(item->'observed_at') <> 'string' OR
               item->>'observed_at' !~
                   '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,6})?(Z|[+]00:00)$' OR
               jsonb_typeof(item->'value') NOT IN ('string','number') OR
               item->>'value' !~ '^\d{1,6}(\.\d{1,2})?$' THEN
                RETURN false;
            END IF;
            measured := (item->>'value')::numeric;
            observed := (item->>'observed_at')::timestamptz;
            IF measured <= 0 OR measured > 999999.99 THEN RETURN false; END IF;
        ELSE
            IF jsonb_typeof(item) <> 'string' OR
               NOT ((item #>> '{}') = ANY(allowed)) THEN RETURN false; END IF;
        END IF;
    END LOOP;
    RETURN true;
EXCEPTION WHEN OTHERS THEN RETURN false;
END;
$$;
ALTER TABLE athletes_baselineassessment ADD CONSTRAINT baseline_json_contract
    CHECK (fitlink_valid_baseline_json('goals', goals) AND
           fitlink_valid_baseline_json('available_days', available_days) AND
           fitlink_valid_baseline_json('equipment', equipment) AND
           fitlink_valid_baseline_json('facilities', facilities) AND
           fitlink_valid_baseline_json('approximate_records', approximate_records));
"""

REVERSE = """
ALTER TABLE athletes_baselineassessment DROP CONSTRAINT baseline_json_contract;
DROP FUNCTION fitlink_valid_baseline_json(text, jsonb);
"""


class Migration(migrations.Migration):
    dependencies = [("athletes", "0005_receipt_restriction_contracts")]
    operations = [migrations.RunSQL(FORWARD, REVERSE)]
