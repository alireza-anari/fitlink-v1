from django.db import migrations


def map_inactive(apps, schema_editor):
    user = apps.get_model("accounts", "User")
    user.objects.using(schema_editor.connection.alias).filter(is_active=False).update(
        state="suspended"
    )


class Migration(migrations.Migration):
    dependencies = [("accounts", "0002_account_security")]
    operations = [migrations.RunPython(map_inactive, migrations.RunPython.noop)]
