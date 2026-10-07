import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone as django_timezone


class AthleteProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="athlete_profile",
    )
    status = models.CharField(max_length=12, default="onboarding")
    version = models.PositiveBigIntegerField(default=1)
    timezone = models.CharField(max_length=64, default="Asia/Tehran")
    onboarding_step = models.CharField(max_length=32, default="basics")
    current_baseline = models.ForeignKey(
        "athletes.BaselineAssessment",
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(status__in=["onboarding", "active", "archived"]),
                name="athlete_profile_status",
            ),
            models.CheckConstraint(
                condition=models.Q(version__gte=1), name="athlete_profile_version"
            ),
        ]


from .baseline_models import BaselineAssessment as BaselineAssessment
from .receipt_models import ProfileCommandReceipt as ProfileCommandReceipt
