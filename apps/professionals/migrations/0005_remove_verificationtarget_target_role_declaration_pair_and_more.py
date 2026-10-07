from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("professionals", "0004_fix_verification_decision_guard"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="verificationtarget",
            name="target_role_declaration_pair",
        ),
        migrations.AddConstraint(
            model_name="verificationtarget",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(
                        ("bound_declaration_version__isnull", True),
                        ("role__isnull", True),
                        ("target", "identity"),
                    ),
                    models.Q(
                        ("bound_declaration_version__isnull", False),
                        ("role__isnull", False),
                        ("target__in", ["coach", "nutritionist"]),
                        ("bound_declaration_version__gte", 1),
                    ),
                    _connector="OR",
                ),
                name="target_role_declaration_pair",
            ),
        ),
    ]
