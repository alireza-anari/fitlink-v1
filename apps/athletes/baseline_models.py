import uuid

from django.db import models
from django.utils import timezone


class BaselineAssessment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    athlete = models.ForeignKey(
        "athletes.AthleteProfile",
        on_delete=models.PROTECT,
        related_name="baselines",
    )
    sequence = models.PositiveIntegerField()
    parent = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        related_name="corrections",
        null=True,
        blank=True,
    )
    state = models.CharField(max_length=12, default="draft")
    schema_version = models.PositiveSmallIntegerField(default=1)
    version = models.PositiveBigIntegerField(default=1)
    observed_at = models.DateTimeField()
    submitted_at = models.DateTimeField(null=True, blank=True)
    age_at_assessment = models.PositiveSmallIntegerField(null=True, blank=True)
    height_cm = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True
    )
    weight_kg = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True
    )
    goals = models.JSONField(default=list, blank=True)
    experience = models.CharField(max_length=16, blank=True)
    training_experience_months = models.PositiveSmallIntegerField(null=True, blank=True)
    available_days = models.JSONField(default=list, blank=True)
    equipment = models.JSONField(default=list, blank=True)
    equipment_other = models.CharField(max_length=200, blank=True)
    facilities = models.JSONField(default=list, blank=True)
    lifestyle = models.CharField(max_length=16, blank=True)
    sleep_hours = models.DecimalField(
        max_digits=3, decimal_places=1, null=True, blank=True
    )
    energy = models.PositiveSmallIntegerField(null=True, blank=True)
    meals_per_day = models.PositiveSmallIntegerField(null=True, blank=True)
    hydration_habit = models.CharField(max_length=12, blank=True)
    nutrition_habits = models.CharField(max_length=500, blank=True)
    waist_cm = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True
    )
    approximate_records = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["athlete", "sequence"], name="baseline_athlete_seq")
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(height_cm__isnull=True)
                | models.Q(height_cm__gte=50, height_cm__lte=250),
                name="baseline_height_bound",
            ),
            models.CheckConstraint(
                condition=models.Q(weight_kg__isnull=True)
                | models.Q(weight_kg__gte=20, weight_kg__lte=400),
                name="baseline_weight_bound",
            ),
            models.CheckConstraint(
                condition=models.Q(waist_cm__isnull=True)
                | models.Q(waist_cm__gte=20, waist_cm__lte=250),
                name="baseline_waist_bound",
            ),
            models.CheckConstraint(
                condition=models.Q(sleep_hours__isnull=True)
                | models.Q(sleep_hours__gte=0, sleep_hours__lte=24),
                name="baseline_sleep_bound",
            ),
            models.CheckConstraint(
                condition=models.Q(energy__isnull=True)
                | models.Q(energy__gte=1, energy__lte=10),
                name="baseline_energy_bound",
            ),
            models.CheckConstraint(
                condition=models.Q(meals_per_day__isnull=True)
                | models.Q(meals_per_day__lte=12),
                name="baseline_meals_bound",
            ),
            models.CheckConstraint(
                condition=models.Q(training_experience_months__isnull=True)
                | models.Q(training_experience_months__lte=1200),
                name="baseline_experience_month_bound",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    experience__in=["", "beginner", "intermediate", "advanced"]
                ),
                name="baseline_experience_kind",
            ),
            models.CheckConstraint(
                condition=models.Q(lifestyle__in=["", "sedentary", "mixed", "active"]),
                name="baseline_lifestyle_kind",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    hydration_habit__in=["", "low", "regular", "unknown"]
                ),
                name="baseline_hydration_kind",
            ),
            models.UniqueConstraint(
                fields=["athlete", "sequence"], name="baseline_sequence_unique"
            ),
            models.UniqueConstraint(
                fields=["athlete"],
                condition=models.Q(state="draft"),
                name="baseline_one_live_draft",
            ),
            models.CheckConstraint(
                condition=models.Q(sequence__gte=1), name="baseline_sequence_positive"
            ),
            models.CheckConstraint(
                condition=models.Q(schema_version=1), name="baseline_schema_version"
            ),
            models.CheckConstraint(
                condition=models.Q(version__gte=1), name="baseline_version_positive"
            ),
            models.CheckConstraint(
                condition=models.Q(state__in=["draft", "submitted", "superseded"]),
                name="baseline_state",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(state="draft", submitted_at__isnull=True)
                    | models.Q(state="submitted", submitted_at__isnull=False)
                    | models.Q(state="superseded", submitted_at__isnull=False)
                ),
                name="baseline_submit_timestamp",
            ),
        ]
