"""Disposable public index and separate restricted reconciliation metadata."""

import uuid

from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.utils import timezone


class PublicProfessionalProjection(models.Model):
    profile_uuid = models.UUIDField(primary_key=True)
    normalized_name = models.TextField(default="")
    normalized_specialties = models.TextField(default="")
    normalized_summary = models.TextField(default="")
    normalized_biography = models.TextField(default="")
    normalized_lookup = models.TextField(default="")
    normalized_filters = models.JSONField(default=dict)
    experience_years = models.PositiveSmallIntegerField(null=True)
    normalization_version = models.CharField(max_length=32, default="fa-search-v1")
    search_vector = SearchVectorField(null=True)
    publication_uuid = models.UUIDField(null=True)
    revision_uuid = models.UUIDField(null=True)
    publication_version = models.PositiveBigIntegerField(default=1)
    source_version = models.PositiveBigIntegerField(default=1)
    slug = models.CharField(max_length=80, blank=True)
    snapshot = models.JSONField(default=dict)
    generation = models.PositiveBigIntegerField(default=1)
    state = models.CharField(max_length=16, default="tombstone")
    refreshed_at = models.DateTimeField(default=timezone.now)
    next_expiry = models.DateTimeField(null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            GinIndex(fields=["search_vector"], name="c04_public_fts_gin"),
            GinIndex(
                fields=["normalized_lookup"],
                opclasses=["gin_trgm_ops"],
                name="c04_public_trgm_gin",
            ),
            GinIndex(fields=["normalized_filters"], name="c04_public_filters_gin"),
            models.Index(fields=["state", "profile_uuid"], name="c04_public_browse"),
            models.Index(fields=["experience_years"], name="c04_public_experience"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(normalization_version="fa-search-v1"),
                name="c04_projection_normalization_version",
            ),
            models.CheckConstraint(
                condition=models.Q(experience_years__isnull=True)
                | models.Q(experience_years__lte=80),
                name="c04_projection_experience_bound",
            ),
            models.CheckConstraint(
                condition=models.Func(
                    models.F("normalized_filters"),
                    function="fitlink_valid_c04_search_filters",
                    output_field=models.BooleanField(),
                ),
                name="c04_projection_filter_shape",
            ),
            models.CheckConstraint(
                condition=models.Q(state__in=["active", "tombstone"]),
                name="projection_finite_state",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    generation__gte=1, publication_version__gte=1, source_version__gte=1
                ),
                name="projection_positive_versions",
            ),
            models.CheckConstraint(
                condition=models.Q(state="tombstone", snapshot={})
                | models.Q(
                    state="active",
                    publication_uuid__isnull=False,
                    revision_uuid__isnull=False,
                ),
                name="projection_current_or_empty",
            ),
        ]


class PublicLocation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    projection = models.ForeignKey(
        PublicProfessionalProjection, on_delete=models.CASCADE, related_name="locations"
    )
    normalized_region = models.TextField(default="")
    normalized_city = models.TextField(default="")
    country_code = models.CharField(max_length=2)
    region = models.CharField(max_length=160)
    city = models.CharField(max_length=160)
    modes = models.JSONField(default=list)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(
                fields=["country_code", "normalized_region", "normalized_city"],
                name="c04_public_location",
            )
        ]


class ProjectionRefreshState(models.Model):
    profile_uuid = models.UUIDField(primary_key=True)
    authority_hash = models.CharField(max_length=64, blank=True)
    generation = models.PositiveBigIntegerField(default=1)
    due_at = models.DateTimeField(default=timezone.now, db_index=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(generation__gte=1),
                name="projection_refresh_positive_generation",
            ),
            models.CheckConstraint(
                condition=models.Q(authority_hash="")
                | models.Q(authority_hash__regex=r"^[0-9a-f]{64}$"),
                name="projection_private_hash",
            ),
        ]


class PublicationScanCursor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=32, unique=True)
    after_uuid = models.UUIDField(null=True)
    lease_uuid = models.UUIDField(null=True)
    lease_until = models.DateTimeField(null=True)
    version = models.PositiveBigIntegerField(default=1)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(version__gte=1),
                name="projection_cursor_positive_version",
            ),
            models.CheckConstraint(
                condition=models.Q(lease_uuid__isnull=True, lease_until__isnull=True)
                | models.Q(lease_uuid__isnull=False, lease_until__isnull=False),
                name="projection_cursor_lease_pair",
            ),
        ]
