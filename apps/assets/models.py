import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from .derivative_models import AssetDerivative as AssetDerivative
from .derivative_models import AssetProcessingAttempt as AssetProcessingAttempt


class Asset(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="private_assets",
    )
    subject_kind = models.CharField(max_length=32)
    subject_uuid = models.UUIDField()
    purpose = models.CharField(max_length=32)
    source_key = models.CharField(max_length=255, blank=True)
    classification = models.CharField(max_length=24, default="private_source")
    state = models.CharField(max_length=20, default="pending_upload")
    version = models.PositiveBigIntegerField(default=1)
    declared_size = models.PositiveBigIntegerField(default=0)
    declared_type = models.CharField(max_length=64, blank=True)
    actual_size = models.PositiveBigIntegerField(null=True, blank=True)
    detected_type = models.CharField(max_length=64, blank=True)
    sha256 = models.CharField(max_length=64, blank=True)
    processing_version = models.PositiveBigIntegerField(default=1)
    created_at = models.DateTimeField(default=timezone.now)
    upload_expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)
    finalized_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    rejection_code = models.CharField(max_length=32, blank=True)

    class Meta:
        indexes = [
            models.Index(
                fields=["owner", "state", "created_at"], name="asset_owner_state"
            ),
            models.Index(
                fields=["state", "upload_expires_at"], name="asset_state_expiry"
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(version__gte=1), name="asset_version"
            ),
            models.CheckConstraint(
                condition=models.Q(processing_version__gte=1),
                name="asset_processing_version",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    purpose__in=[
                        "identity_evidence",
                        "credential_evidence",
                        "avatar",
                        "cover",
                        "logo",
                    ]
                ),
                name="asset_c03_purpose",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    classification__in=["private_source", "private_derivative"]
                ),
                name="asset_private_class",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    state__in=[
                        "pending_upload",
                        "receiving",
                        "quarantined",
                        "processing",
                        "ready",
                        "rejected",
                        "abandoned",
                        "revoked",
                        "deletion_pending",
                        "deleted",
                    ]
                ),
                name="asset_state",
            ),
        ]
