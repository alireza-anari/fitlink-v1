from django.db import migrations

FORWARD = r"""
CREATE FUNCTION fitlink_valid_professional_json(field text, value jsonb)
RETURNS boolean LANGUAGE plpgsql IMMUTABLE AS $$
DECLARE
    cap integer;
    item jsonb;
    token text;
BEGIN
    IF value IS NULL OR jsonb_typeof(value) <> 'array' THEN RETURN false; END IF;
    CASE field
      WHEN 'specialties' THEN cap := 10;
      WHEN 'languages' THEN cap := 5;
      WHEN 'service_modes' THEN cap := 2;
      ELSE RETURN false;
    END CASE;
    IF jsonb_array_length(value) > cap OR
       (SELECT count(*) <> count(DISTINCT element)
          FROM jsonb_array_elements(value) AS entries(element)) THEN
        RETURN false;
    END IF;
    FOR item IN SELECT element FROM jsonb_array_elements(value) AS entries(element)
    LOOP
        IF jsonb_typeof(item) <> 'string' THEN RETURN false; END IF;
        token := item #>> '{}';
        IF field = 'specialties' THEN
            IF length(token) NOT BETWEEN 1 AND 64 OR token ~ '[<>]' OR
               token <> btrim(token) THEN RETURN false; END IF;
        ELSIF field = 'languages' THEN
            IF length(token) > 35 OR
               token !~ '^[A-Za-z]{2,8}(-[A-Za-z0-9]{1,8})*$' THEN
                RETURN false;
            END IF;
        ELSE
            IF token NOT IN ('online','in_person') THEN RETURN false; END IF;
        END IF;
    END LOOP;
    RETURN true;
END;
$$;
ALTER TABLE professionals_professionalprofile ADD CONSTRAINT professional_json_contract
    CHECK (fitlink_valid_professional_json('specialties', specialties) AND
           fitlink_valid_professional_json('languages', languages) AND
           fitlink_valid_professional_json('service_modes', service_modes));
ALTER TABLE professionals_professionallocation ADD CONSTRAINT location_modes_contract
    CHECK (fitlink_valid_professional_json('service_modes', modes));
"""

REVERSE = """
ALTER TABLE professionals_professionallocation DROP CONSTRAINT location_modes_contract;
ALTER TABLE professionals_professionalprofile
    DROP CONSTRAINT professional_json_contract;
DROP FUNCTION fitlink_valid_professional_json(text, jsonb);
"""


class Migration(migrations.Migration):
    dependencies = [("professionals", "0011_receipt_restriction_contracts")]
    operations = [migrations.RunSQL(FORWARD, REVERSE)]
