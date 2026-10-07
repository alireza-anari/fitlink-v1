from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("assets", "0001_private_asset_metadata"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="assetprocessingattempt",
            name="attempt_lease_pair",
        ),
        migrations.AddConstraint(
            model_name="assetprocessingattempt",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(
                        ("lease_until__isnull", True),
                        ("lease_uuid__isnull", True),
                    ),
                    models.Q(
                        ("lease_until__isnull", False),
                        ("lease_uuid__isnull", False),
                    ),
                    _connector="OR",
                ),
                name="attempt_lease_pair",
            ),
        ),
    ]
