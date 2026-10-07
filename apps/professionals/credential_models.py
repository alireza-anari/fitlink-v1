import uuid

from django.db import models
from django.utils import timezone


class Credential(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(
        "professionals.ProfessionalProfile",
        on_delete=models.PROTECT,
        related_name="credentials",
    )
    role = models.ForeignKey(
        "professionals.ProfessionalRole",
        on_delete=models.PROTECT,
        related_name="credentials",
        null=True,
        blank=True,
    )
    category = models.CharField(max_length=16)
    type_code = models.CharField(max_length=64)
    issuer = models.CharField(max_length=160)
    title = models.CharField(max_length=160)
    issued_on = models.DateField(null=True, blank=True)
    expires_on = models.DateField(null=True, blank=True)
    current_revision = models.ForeignKey(
        "professionals.CredentialRevision",
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
        blank=True,
    )
    version = models.PositiveBigIntegerField(default=1)
    withdrawn_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=["profile", "role"], name="credential_profile_role")
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(version__gte=1), name="credential_version"
            ),
            models.CheckConstraint(
                condition=models.Q(category__in=["identity", "qualification"]),
                name="credential_category",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(category="identity", role__isnull=True)
                    | models.Q(category="qualification", role__isnull=False)
                ),
                name="credential_role_pair",
            ),
        ]


class CredentialRevision(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    credential = models.ForeignKey(
        "professionals.Credential",
        on_delete=models.PROTECT,
        related_name="revisions",
    )
    sequence = models.PositiveIntegerField()
    category = models.CharField(max_length=16)
    type_code = models.CharField(max_length=64)
    issuer = models.CharField(max_length=160)
    title = models.CharField(max_length=160)
    issued_on = models.DateField(null=True, blank=True)
    expires_on = models.DateField(null=True, blank=True)
    source_asset = models.ForeignKey(
        "assets.Asset",
        on_delete=models.PROTECT,
        related_name="credential_revisions",
    )
    source_sha256 = models.CharField(max_length=64)
    revision_hash = models.CharField(max_length=64)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(source_sha256__regex=r"^[0-9a-f]{64}$"),
                name="credential_revision_source_hash",
            ),
            models.CheckConstraint(
                condition=models.Q(revision_hash__regex=r"^[0-9a-f]{64}$"),
                name="credential_revision_hash",
            ),
            models.UniqueConstraint(
                fields=["credential", "sequence"], name="credential_revision_sequence"
            ),
            models.CheckConstraint(
                condition=models.Q(sequence__gte=1), name="credential_revision_positive"
            ),
            models.CheckConstraint(
                condition=models.Q(category__in=["identity", "qualification"]),
                name="credential_revision_category",
            ),
        ]
