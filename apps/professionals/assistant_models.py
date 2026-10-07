import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class AssistantMembership(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(
        "professionals.ProfessionalProfile",
        on_delete=models.PROTECT,
        related_name="assistant_definitions",
    )
    assistant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="assistant_definitions",
    )
    role = models.CharField(max_length=20, default="client_support")
    state = models.CharField(max_length=12, default="defined")
    version = models.PositiveBigIntegerField(default=1)
    defined_at = models.DateTimeField(default=timezone.now)
    revoked_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(state="defined", revoked_at__isnull=True)
                | models.Q(state="revoked", revoked_at__isnull=False),
                name="assistant_revocation_time",
            ),
            models.UniqueConstraint(
                fields=["profile", "assistant"],
                condition=models.Q(state="defined"),
                name="assistant_membership_live",
            ),
            models.CheckConstraint(
                condition=models.Q(role="client_support"), name="assistant_fixed_role"
            ),
            models.CheckConstraint(
                condition=models.Q(state__in=["defined", "revoked"]),
                name="assistant_membership_state",
            ),
            models.CheckConstraint(
                condition=models.Q(version__gte=1), name="assistant_membership_version"
            ),
        ]
