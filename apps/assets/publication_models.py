"""Private publication-copy inventory; source and private derivative stay intact."""

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class PublicAssetCopy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="public_asset_copies",
    )
    source_asset = models.ForeignKey(
        "assets.Asset", on_delete=models.PROTECT, related_name="publication_copies"
    )
    source_derivative = models.ForeignKey(
        "assets.AssetDerivative",
        on_delete=models.PROTECT,
        related_name="publication_copies",
    )
    profile_uuid = models.UUIDField()
    publication_uuid = models.UUIDField()
    release_revision_uuid = models.UUIDField()
    purpose = models.CharField(max_length=16)
    source_version = models.PositiveBigIntegerField()
    source_derivative_version = models.PositiveBigIntegerField()
    source_derivative_sha256 = models.CharField(max_length=64)
    processing_version = models.PositiveBigIntegerField()
    publication_version = models.PositiveBigIntegerField()
    owner_auth_version = models.PositiveBigIntegerField()
    generation = models.PositiveSmallIntegerField(default=1)
    version = models.PositiveBigIntegerField(default=1)
    state = models.CharField(max_length=20, default="pending")
    revoked_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=["state", "updated_at", "id"], name="public_copy_due")
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(source_derivative_sha256__regex=r"^[0-9a-f]{64}$"),
                name="public_copy_source_checksum",
            ),
            models.UniqueConstraint(
                fields=[
                    "release_revision_uuid",
                    "purpose",
                    "source_asset",
                    "processing_version",
                ],
                name="public_copy_effect",
            ),
            models.CheckConstraint(
                condition=models.Q(purpose__in=["avatar", "cover", "logo"]),
                name="public_copy_branding_purpose",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    source_version__gte=1,
                    source_derivative_version__gte=1,
                    processing_version__gte=1,
                    publication_version__gte=1,
                    owner_auth_version__gte=1,
                    version__gte=1,
                ),
                name="public_copy_positive_versions",
            ),
            models.CheckConstraint(
                condition=models.Q(generation__gte=1, generation__lte=8),
                name="public_copy_generation_bound",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    state__in=[
                        "pending",
                        "running",
                        "ready",
                        "failed",
                        "revoked",
                        "deletion_pending",
                        "deleted",
                    ]
                ),
                name="public_copy_state",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        state__in=["pending", "running", "ready"],
                        revoked_at__isnull=True,
                    )
                    | models.Q(
                        state__in=["failed", "revoked", "deletion_pending", "deleted"],
                        revoked_at__isnull=False,
                    )
                ),
                name="public_copy_revocation_pair",
            ),
        ]


class PublicCopyAttempt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    copy = models.ForeignKey(
        PublicAssetCopy, on_delete=models.PROTECT, related_name="attempts"
    )
    generation = models.PositiveSmallIntegerField()
    key = models.CharField(max_length=255)
    state = models.CharField(max_length=20, default="pending")
    lease_uuid = models.UUIDField(null=True)
    lease_until = models.DateTimeField(null=True)
    next_attempt_at = models.DateTimeField(default=timezone.now)
    authority_hash = models.CharField(max_length=64, blank=True)
    sha256 = models.CharField(max_length=64, blank=True)
    mime_type = models.CharField(max_length=16, blank=True)
    width = models.PositiveIntegerField(default=0)
    height = models.PositiveIntegerField(default=0)
    size = models.PositiveIntegerField(default=0)
    scanner_engine = models.CharField(max_length=64, blank=True)
    scanner_signature = models.CharField(max_length=10, blank=True)
    signature_expires_at = models.DateTimeField(null=True)
    failure_code = models.CharField(max_length=32, blank=True)
    retired_at = models.DateTimeField(null=True)
    deleted_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(
                fields=["state", "lease_until", "next_attempt_at"],
                name="public_attempt_due",
            )
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["copy", "generation"], name="public_copy_generation_effect"
            ),
            models.UniqueConstraint(fields=["key"], name="public_copy_unique_object"),
            models.CheckConstraint(
                condition=models.Q(generation__gte=1, generation__lte=8),
                name="public_attempt_generation",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    state__in=[
                        "pending",
                        "running",
                        "ready",
                        "failed",
                        "stale",
                        "deletion_pending",
                        "deleted",
                    ]
                ),
                name="public_attempt_state",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(lease_uuid__isnull=True, lease_until__isnull=True)
                    | models.Q(lease_uuid__isnull=False, lease_until__isnull=False)
                ),
                name="public_attempt_lease_pair",
            ),
            models.CheckConstraint(
                condition=~models.Q(state="running")
                | models.Q(
                    lease_uuid__isnull=False,
                    lease_until__isnull=False,
                    authority_hash__regex=r"^[0-9a-f]{64}$",
                ),
                name="public_running_authority",
            ),
            models.CheckConstraint(
                condition=models.Q(authority_hash="")
                | models.Q(authority_hash__regex=r"^[0-9a-f]{64}$"),
                name="public_attempt_hash",
            ),
            models.CheckConstraint(
                condition=models.Q(sha256="")
                | models.Q(sha256__regex=r"^[0-9a-f]{64}$"),
                name="public_output_hash",
            ),
            models.CheckConstraint(
                condition=models.Q(mime_type__in=["", "image/png", "image/jpeg"]),
                name="public_output_mime",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    size__lte=10_000_000, width__lte=1600, height__lte=1600
                ),
                name="public_output_bounds",
            ),
            models.CheckConstraint(
                condition=~models.Q(state="ready")
                | models.Q(
                    sha256__regex=r"^[0-9a-f]{64}$",
                    mime_type__in=["image/png", "image/jpeg"],
                    size__gte=1,
                    width__gte=1,
                    height__gte=1,
                    scanner_engine="ClamAV 1.5.4",
                    scanner_signature__regex=r"^[0-9]{1,10}$",
                    signature_expires_at__isnull=False,
                ),
                name="public_ready_metadata",
            ),
        ]
