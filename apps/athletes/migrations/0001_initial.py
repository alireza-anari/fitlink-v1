import uuid

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="AthleteProfile",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("status", models.CharField(default="onboarding", max_length=12)),
                ("version", models.PositiveBigIntegerField(default=1)),
                ("timezone", models.CharField(default="Asia/Tehran", max_length=64)),
                ("onboarding_step", models.CharField(default="basics", max_length=32)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="athlete_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.CheckConstraint(
                        condition=models.Q(
                            ("status__in", ["onboarding", "active", "archived"])
                        ),
                        name="athlete_profile_status",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(("version__gte", 1)),
                        name="athlete_profile_version",
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="BaselineAssessment",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("sequence", models.PositiveIntegerField()),
                ("state", models.CharField(default="draft", max_length=12)),
                ("schema_version", models.PositiveSmallIntegerField(default=1)),
                ("version", models.PositiveBigIntegerField(default=1)),
                ("observed_at", models.DateTimeField()),
                ("submitted_at", models.DateTimeField(blank=True, null=True)),
                (
                    "age_at_assessment",
                    models.PositiveSmallIntegerField(blank=True, null=True),
                ),
                (
                    "height_cm",
                    models.DecimalField(
                        blank=True, decimal_places=1, max_digits=5, null=True
                    ),
                ),
                (
                    "weight_kg",
                    models.DecimalField(
                        blank=True, decimal_places=1, max_digits=5, null=True
                    ),
                ),
                ("goals", models.JSONField(blank=True, default=list)),
                ("experience", models.CharField(blank=True, max_length=16)),
                (
                    "training_experience_months",
                    models.PositiveSmallIntegerField(blank=True, null=True),
                ),
                ("available_days", models.JSONField(blank=True, default=list)),
                ("equipment", models.JSONField(blank=True, default=list)),
                ("equipment_other", models.CharField(blank=True, max_length=200)),
                ("facilities", models.JSONField(blank=True, default=list)),
                ("lifestyle", models.CharField(blank=True, max_length=16)),
                (
                    "sleep_hours",
                    models.DecimalField(
                        blank=True, decimal_places=1, max_digits=3, null=True
                    ),
                ),
                ("energy", models.PositiveSmallIntegerField(blank=True, null=True)),
                (
                    "meals_per_day",
                    models.PositiveSmallIntegerField(blank=True, null=True),
                ),
                ("hydration_habit", models.CharField(blank=True, max_length=12)),
                ("nutrition_habits", models.CharField(blank=True, max_length=500)),
                (
                    "waist_cm",
                    models.DecimalField(
                        blank=True, decimal_places=1, max_digits=5, null=True
                    ),
                ),
                ("approximate_records", models.JSONField(blank=True, default=list)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "athlete",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="baselines",
                        to="athletes.athleteprofile",
                    ),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="corrections",
                        to="athletes.baselineassessment",
                    ),
                ),
            ],
            options={
                "indexes": [
                    models.Index(
                        fields=["athlete", "sequence"], name="baseline_athlete_seq"
                    )
                ],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("athlete", "sequence"), name="baseline_sequence_unique"
                    ),
                    models.UniqueConstraint(
                        condition=models.Q(("state", "draft")),
                        fields=("athlete",),
                        name="baseline_one_live_draft",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(("sequence__gte", 1)),
                        name="baseline_sequence_positive",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(("schema_version", 1)),
                        name="baseline_schema_version",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(("version__gte", 1)),
                        name="baseline_version_positive",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(
                            ("state__in", ["draft", "submitted", "superseded"])
                        ),
                        name="baseline_state",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(
                            models.Q(
                                ("state", "draft"), ("submitted_at__isnull", True)
                            ),
                            models.Q(
                                ("state", "submitted"), ("submitted_at__isnull", False)
                            ),
                            models.Q(
                                ("state", "superseded"), ("submitted_at__isnull", False)
                            ),
                            _connector="OR",
                        ),
                        name="baseline_submit_timestamp",
                    ),
                ],
            },
        ),
        migrations.AddField(
            model_name="athleteprofile",
            name="current_baseline",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="athletes.baselineassessment",
            ),
        ),
        migrations.CreateModel(
            name="ProfileCommandReceipt",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("operation_id", models.UUIDField()),
                ("command", models.CharField(max_length=64)),
                ("request_hash", models.CharField(max_length=64)),
                ("object_uuid", models.UUIDField(blank=True, null=True)),
                ("result_uuid", models.UUIDField(blank=True, null=True)),
                ("resulting_version", models.PositiveBigIntegerField(default=1)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="athlete_profile_receipts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=("owner", "operation_id"),
                        name="athlete_receipt_operation",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(("resulting_version__gte", 1)),
                        name="athlete_receipt_version",
                    ),
                ],
            },
        ),
    ]
