import uuid

from django.db import models


class AssetDerivative(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset = models.ForeignKey(
        "assets.Asset", on_delete=models.PROTECT, related_name="derivatives"
    )
    processing_version = models.PositiveBigIntegerField()
    purpose = models.CharField(max_length=24)
    key = models.CharField(max_length=255)
    sha256 = models.CharField(max_length=64)
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    mime_type = models.CharField(max_length=16)
    state = models.CharField(max_length=12, default="pending")
    version = models.PositiveBigIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["asset", "processing_version", "purpose"],
                name="asset_derivative_effect",
            ),
            models.CheckConstraint(
                condition=models.Q(processing_version__gte=1),
                name="derivative_processing_version",
            ),
            models.CheckConstraint(
                condition=models.Q(version__gte=1), name="derivative_version"
            ),
            models.CheckConstraint(
                condition=models.Q(purpose__in=["owner_preview", "evidence_preview"]),
                name="derivative_purpose",
            ),
            models.CheckConstraint(
                condition=models.Q(mime_type__in=["image/jpeg", "image/png"]),
                name="derivative_mime",
            ),
            models.CheckConstraint(
                condition=models.Q(state__in=["pending", "ready", "revoked", "deleted"]),
                name="derivative_state",
            ),
        ]


class AssetProcessingAttempt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset = models.ForeignKey(
        "assets.Asset", on_delete=models.PROTECT, related_name="processing_attempts"
    )
    processing_version = models.PositiveBigIntegerField()
    lease_uuid = models.UUIDField(null=True, blank=True)
    lease_until = models.DateTimeField(null=True, blank=True)
    attempt = models.PositiveSmallIntegerField(default=1)
    state = models.CharField(max_length=12, default="pending")
    scanner_engine = models.CharField(max_length=64, blank=True)
    scanner_signature = models.CharField(max_length=128, blank=True)
    failure_code = models.CharField(max_length=32, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["state", "lease_until"], name="asset_attempt_lease")
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["asset", "processing_version", "attempt"],
                name="asset_processing_attempt_unique",
            ),
            models.CheckConstraint(
                condition=models.Q(processing_version__gte=1),
                name="attempt_processing_version",
            ),
            models.CheckConstraint(
                condition=models.Q(attempt__gte=1), name="attempt_positive"
            ),
            models.CheckConstraint(
                condition=models.Q(state__in=["pending", "running", "ready", "failed"]),
                name="attempt_state",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(lease_uuid__isnull=True, lease_until__isnull=True)
                    | models.Q(lease_uuid__isnull=False, lease_until__isnull=False)
                ),
                name="attempt_lease_pair",
            ),
        ]
