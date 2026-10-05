from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("accounts", "0009_recoveryrequest_decided_at")]
    operations = [
        migrations.AddConstraint(
            model_name="recoveryrequest",
            constraint=models.CheckConstraint(
                condition=models.Q(state="received", decided_at__isnull=True)
                | models.Q(
                    state__in=["approved", "rejected", "applied"],
                    decided_at__isnull=False,
                ),
                name="recovery_decision_time",
            ),
        )
    ]
