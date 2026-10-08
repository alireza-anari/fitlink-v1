import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class ProfileCommandReceipt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="athlete_profile_receipts",
    )
    operation_id = models.UUIDField()
    command = models.CharField(max_length=64)
    request_hash = models.CharField(max_length=64)
    object_uuid = models.UUIDField(null=True, blank=True)
    result_uuid = models.UUIDField(null=True, blank=True)
    resulting_version = models.PositiveBigIntegerField(default=1)
    created_at = models.DateTimeField(default=timezone.now)

    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    command__in=[
                        "profile.create",
                        "baseline.begin",
                        "baseline.save_step",
                        "baseline.submit",
                        "baseline.correct",
                        "baseline.clear",
                        "baseline.grant_storage",
                        "baseline.revoke_storage",
                    ]
                ),
                name="athletes_receipt_command",
            ),
            models.CheckConstraint(
                condition=models.Q(request_hash__regex=r"^[0-9a-f]{64}$"),
                name="athletes_receipt_hash",
            ),
            models.UniqueConstraint(
                fields=["owner", "operation_id"], name="athlete_receipt_operation"
            ),
            models.CheckConstraint(
                condition=models.Q(resulting_version__gte=1),
                name="athlete_receipt_version",
            ),
        ]
