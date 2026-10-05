import uuid

from django.db import models

FEATURE_KEYS = ("marketplace", "professional_registration", "ai_insights", "ai_mirror")


class FeatureFlag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=32, unique=True)
    enabled = models.BooleanField(default=False)
    version = models.PositiveBigIntegerField(default=1)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(key__in=FEATURE_KEYS), name="feature_key"
            ),
            models.CheckConstraint(
                condition=models.Q(version__gte=1), name="feature_version"
            ),
        ]
