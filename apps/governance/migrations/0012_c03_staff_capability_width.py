from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("governance", "0011_c03_profile_contracts")]
    operations = [
        migrations.AlterField(
            model_name="staffcapabilitygrant",
            name="capability",
            field=models.CharField(max_length=32),
        ),
        migrations.AlterField(
            model_name="staffstepupgrant",
            name="capability",
            field=models.CharField(max_length=32),
        ),
    ]
