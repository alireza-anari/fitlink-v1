"""Owned educational sources and immutable revisions, separate from evidence."""

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class EducationalPost(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(
        "professionals.ProfessionalProfile",
        on_delete=models.PROTECT,
        related_name="educational_posts",
    )
    version = models.PositiveBigIntegerField(default=1)
    state = models.CharField(max_length=16, default="draft")
    current_revision = models.ForeignKey(
        "professionals.PostRevision",
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
        blank=True,
    )
    requested_revision = models.ForeignKey(
        "professionals.PostRevision",
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
        blank=True,
    )
    withdrawn_at = models.DateTimeField(null=True, blank=True)
    hidden_at = models.DateTimeField(null=True, blank=True)
    hidden_case_uuid = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(version__gte=1), name="post_positive_version"
            ),
            models.CheckConstraint(
                condition=models.Q(
                    state__in=["draft", "published", "hidden", "archived", "deleted"]
                ),
                name="post_state",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    hidden_at__isnull=True, hidden_case_uuid__isnull=True
                )
                | models.Q(hidden_at__isnull=False, hidden_case_uuid__isnull=False),
                name="post_hidden_pair",
            ),
            models.CheckConstraint(
                condition=~models.Q(state="published")
                | models.Q(
                    current_revision__isnull=False,
                    requested_revision__isnull=True,
                    withdrawn_at__isnull=True,
                    hidden_at__isnull=True,
                ),
                name="post_published_pointer",
            ),
            models.CheckConstraint(
                condition=~models.Q(state="hidden") | models.Q(hidden_at__isnull=False),
                name="post_hidden_state",
            ),
        ]


class PostRevision(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(
        EducationalPost, on_delete=models.PROTECT, related_name="revisions"
    )
    sequence = models.PositiveIntegerField()
    schema_version = models.PositiveSmallIntegerField(default=1)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="educational_revisions",
    )
    parent_revision = models.ForeignKey(
        "professionals.PublicationRevision",
        on_delete=models.PROTECT,
        related_name="post_revisions",
        null=True,
        blank=True,
    )
    text = models.CharField(max_length=2000)
    disclosure_version = models.CharField(max_length=64)
    disclosure_hash = models.CharField(max_length=64)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="confirmed_post_revisions",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["post", "sequence"], name="post_revision_sequence"
            ),
            models.CheckConstraint(
                condition=models.Q(sequence__gte=1, schema_version=1),
                name="post_revision_schema",
            ),
            models.CheckConstraint(
                condition=models.Q(confirmed_at__isnull=True, confirmed_by__isnull=True)
                | models.Q(
                    confirmed_at__isnull=False,
                    confirmed_by__isnull=False,
                    parent_revision__isnull=False,
                ),
                name="post_confirmation_pair",
            ),
            models.CheckConstraint(
                condition=models.Q(disclosure_hash__regex=r"^[0-9a-f]{64}$"),
                name="post_disclosure_hash",
            ),
        ]


class PostImageBinding(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    revision = models.ForeignKey(
        PostRevision, on_delete=models.PROTECT, related_name="images"
    )
    asset = models.ForeignKey(
        "assets.Asset", on_delete=models.PROTECT, related_name="post_bindings"
    )
    position = models.PositiveSmallIntegerField()
    alt = models.CharField(max_length=200)
    asset_version = models.PositiveBigIntegerField()
    processing_version = models.PositiveBigIntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["revision", "position"], name="post_image_slot"
            ),
            models.UniqueConstraint(
                fields=["revision", "asset"], name="post_image_unique"
            ),
            models.CheckConstraint(
                condition=models.Q(position__gte=1, position__lte=4),
                name="post_image_bound",
            ),
            models.CheckConstraint(
                condition=models.Q(asset_version__gte=1, processing_version__gte=1),
                name="post_image_versions",
            ),
        ]


class PostHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(
        EducationalPost, on_delete=models.PROTECT, related_name="history"
    )
    revision = models.ForeignKey(PostRevision, on_delete=models.PROTECT, null=True)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    operation_id = models.UUIDField()
    action = models.CharField(max_length=16)
    resulting_version = models.PositiveBigIntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["actor", "operation_id"], name="post_history_operation"
            ),
            models.CheckConstraint(
                condition=models.Q(action__in=["saved", "confirmed", "withdrawn"]),
                name="post_history_action",
            ),
            models.CheckConstraint(
                condition=models.Q(resulting_version__gte=1),
                name="post_history_version",
            ),
        ]
