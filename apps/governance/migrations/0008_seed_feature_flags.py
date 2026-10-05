import uuid

from django.db import migrations

KEYS = ("marketplace", "professional_registration", "ai_insights", "ai_mirror")


def seed_flags(apps, schema_editor):
    flag = apps.get_model("governance", "FeatureFlag")
    for key in KEYS:
        flag.objects.using(schema_editor.connection.alias).get_or_create(
            key=key,
            defaults={
                "id": uuid.uuid5(uuid.NAMESPACE_URL, "fitlink:c02:flag:" + key),
                "enabled": False,
                "version": 1,
            },
        )


class Migration(migrations.Migration):
    dependencies = [("governance", "0007_featureflag")]
    operations = [migrations.RunPython(seed_flags, migrations.RunPython.noop)]
