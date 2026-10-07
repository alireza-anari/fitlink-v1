import uuid

from django.db import models
from django.utils import timezone


class ProfessionalRole(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(
        "professionals.ProfessionalProfile",
        on_delete=models.PROTECT,
        related_name="roles",
    )
    role = models.CharField(max_length=16)
    declared_active = models.BooleanField(default=True)
    version = models.PositiveBigIntegerField(default=1)
    declaration_version = models.PositiveBigIntegerField(default=1)
    evidence_revision = models.PositiveBigIntegerField(default=1)
    decision_version = models.PositiveBigIntegerField(default=1)
    created_at = models.DateTimeField(default=timezone.now)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "role"], name="profile_role_unique"
            ),
            models.CheckConstraint(
                condition=models.Q(role__in=["coach", "nutritionist"]),
                name="professional_role_kind",
            ),
            models.CheckConstraint(
                condition=models.Q(version__gte=1), name="professional_role_version"
            ),
            models.CheckConstraint(
                condition=models.Q(declaration_version__gte=1),
                name="role_declaration_version",
            ),
            models.CheckConstraint(
                condition=models.Q(evidence_revision__gte=1),
                name="role_evidence_revision",
            ),
            models.CheckConstraint(
                condition=models.Q(decision_version__gte=1),
                name="role_decision_version",
            ),
        ]


class ProfessionalLocation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(
        "professionals.ProfessionalProfile",
        on_delete=models.PROTECT,
        related_name="locations",
    )
    country_code = models.CharField(max_length=2, default="IR")
    region = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    modes = models.JSONField(default=list)
    archived_at = models.DateTimeField(null=True, blank=True)
    version = models.PositiveBigIntegerField(default=1)
    created_at = models.DateTimeField(default=timezone.now)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "country_code", "region", "city"],
                condition=models.Q(archived_at__isnull=True),
                name="professional_location_fact",
            ),
            models.CheckConstraint(
                condition=models.Q(version__gte=1), name="professional_location_version"
            ),
        ]
