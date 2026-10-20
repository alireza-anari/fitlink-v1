"""Private owned selections; no public names, snapshots or media are retained."""

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class Favorite(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+"
    )
    professional_uuid = models.UUIDField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "professional_uuid"], name="c04_favorite_owned_unique"
            )
        ]


class ComparisonCollection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT, related_name="+"
    )
    session_digest = models.CharField(max_length=64, null=True, unique=True)
    version = models.PositiveBigIntegerField(default=1)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(owner__isnull=False, session_digest__isnull=True)
                    | models.Q(
                        owner__isnull=True,
                        session_digest__isnull=False,
                        session_digest__regex=r"^[0-9a-f]{64}$",
                    )
                ),
                name="c04_comparison_owner_xor",
            ),
            models.CheckConstraint(
                condition=models.Q(version__gte=1), name="c04_comparison_version"
            ),
        ]


class ComparisonEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    collection = models.ForeignKey(
        ComparisonCollection, on_delete=models.PROTECT, related_name="entries"
    )
    professional_uuid = models.UUIDField()
    slot = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(slot__gte=1, slot__lte=3),
                name="c04_comparison_slot_bound",
            ),
            models.UniqueConstraint(
                fields=["collection", "slot"], name="c04_comparison_unique_slot"
            ),
            models.UniqueConstraint(
                fields=["collection", "professional_uuid"],
                name="c04_comparison_unique_target",
            ),
        ]


class FavoriteReceipt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+"
    )
    operation_uuid = models.UUIDField()
    request_hash = models.CharField(max_length=64)
    selected = models.BooleanField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "operation_uuid"], name="c04_favorite_receipt_unique"
            ),
            models.CheckConstraint(
                condition=models.Q(request_hash__regex=r"^[0-9a-f]{64}$"),
                name="c04_favorite_receipt_hash",
            ),
        ]


class ComparisonReceipt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    collection = models.ForeignKey(
        ComparisonCollection, on_delete=models.PROTECT, related_name="receipts"
    )
    operation_uuid = models.UUIDField()
    request_hash = models.CharField(max_length=64)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["collection", "operation_uuid"],
                name="c04_comparison_receipt_unique",
            ),
            models.CheckConstraint(
                condition=models.Q(request_hash__regex=r"^[0-9a-f]{64}$"),
                name="c04_comparison_receipt_hash",
            ),
        ]
