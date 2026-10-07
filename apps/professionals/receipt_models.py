import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class ProfileCommandReceipt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="professional_profile_receipts",
    )
    operation_id = models.UUIDField()
    command = models.CharField(max_length=64)
    request_hash = models.CharField(max_length=64)
    object_uuid = models.UUIDField(null=True, blank=True)
    result_uuid = models.UUIDField(null=True, blank=True)
    resulting_version = models.PositiveBigIntegerField(default=1)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "operation_id"], name="professional_receipt_operation"
            ),
            models.CheckConstraint(
                condition=models.Q(resulting_version__gte=1),
                name="professional_receipt_version",
            ),
        ]
