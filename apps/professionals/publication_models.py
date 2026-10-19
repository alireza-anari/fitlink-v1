"""Owner-confirmed publication records, separate from C03 readiness/evidence."""

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from .publication_contracts import RESERVED_SLUGS


class PublicSnapshotAllowed(models.Func):
    function = "fitlink_valid_public_snapshot"
    output_field = models.BooleanField()


class PublicationSelectionAllowed(models.Func):
    function = "fitlink_valid_public_selection"
    output_field = models.BooleanField()


class ProfessionalPublication(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.OneToOneField(
        "professionals.ProfessionalProfile",
        on_delete=models.PROTECT,
        related_name="publication",
    )
    slug = models.CharField(max_length=80, unique=True)
    state = models.CharField(max_length=24, default="draft")
    version = models.PositiveBigIntegerField(default=1)
    current_revision = models.ForeignKey(
        "professionals.PublicationRevision",
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
        blank=True,
    )
    requested_revision = models.ForeignKey(
        "professionals.PublicationRevision",
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
                condition=models.Q(version__gte=1), name="publication_positive_version"
            ),
            models.CheckConstraint(
                condition=models.Q(slug__regex=r"^[a-z0-9-]{1,80}$")
                & ~models.Q(slug__in=tuple(sorted(RESERVED_SLUGS))),
                name="publication_safe_slug",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        state="draft",
                        current_revision__isnull=True,
                        requested_revision__isnull=True,
                        withdrawn_at__isnull=True,
                    )
                    | models.Q(
                        state="publication_requested",
                        requested_revision__isnull=False,
                        withdrawn_at__isnull=True,
                    )
                    | models.Q(
                        state="published",
                        current_revision__isnull=False,
                        requested_revision__isnull=True,
                        withdrawn_at__isnull=True,
                    )
                    | models.Q(
                        state="unpublished",
                        current_revision__isnull=True,
                        requested_revision__isnull=True,
                        withdrawn_at__isnull=False,
                    )
                ),
                name="publication_state_pointers",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(hidden_at__isnull=True, hidden_case_uuid__isnull=True)
                    | models.Q(hidden_at__isnull=False, hidden_case_uuid__isnull=False)
                ),
                name="publication_hidden_pair",
            ),
        ]


class PublicationRevision(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    publication = models.ForeignKey(
        ProfessionalPublication, on_delete=models.PROTECT, related_name="revisions"
    )
    sequence = models.PositiveIntegerField()
    schema_version = models.PositiveSmallIntegerField(default=1)
    source_profile_version = models.PositiveBigIntegerField()
    snapshot = models.JSONField()
    selection = models.JSONField()
    disclosure_version = models.CharField(max_length=64)
    disclosure_hash = models.CharField(max_length=64)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="confirmed_publication_revisions",
        null=True,
        blank=True,
    )
    valid_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["publication", "sequence"], name="publication_revision_sequence"
            ),
            models.CheckConstraint(
                condition=models.Q(sequence__gte=1),
                name="publication_revision_positive",
            ),
            models.CheckConstraint(
                condition=models.Q(schema_version=1), name="publication_revision_schema"
            ),
            models.CheckConstraint(
                condition=models.Q(source_profile_version__gte=1),
                name="publication_source_positive",
            ),
            models.CheckConstraint(
                condition=PublicSnapshotAllowed("snapshot"),
                name="publication_snapshot_allowlist",
            ),
            models.CheckConstraint(
                condition=PublicationSelectionAllowed("selection"),
                name="publication_selection_allowlist",
            ),
            models.CheckConstraint(
                condition=models.Q(disclosure_hash__regex=r"^[0-9a-f]{64}$"),
                name="publication_disclosure_hash",
            ),
            models.CheckConstraint(
                condition=models.Q(disclosure_version__regex=r"^[a-zA-Z0-9._-]{1,64}$"),
                name="publication_disclosure_version",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(confirmed_at__isnull=True, confirmed_by__isnull=True)
                    | models.Q(confirmed_at__isnull=False, confirmed_by__isnull=False)
                ),
                name="publication_confirmation_pair",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(valid_until__isnull=True)
                    | models.Q(confirmed_at__isnull=True)
                    | models.Q(valid_until__gt=models.F("confirmed_at"))
                ),
                name="publication_expiry_order",
            ),
        ]


class PublicationQualification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    revision = models.ForeignKey(
        PublicationRevision,
        on_delete=models.PROTECT,
        related_name="selected_qualifications",
    )
    credential_revision = models.ForeignKey(
        "professionals.CredentialRevision",
        on_delete=models.PROTECT,
        related_name="publication_selections",
    )
    position = models.PositiveSmallIntegerField()
    role = models.CharField(max_length=12)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["revision", "position"], name="publication_qualification_order"
            ),
            models.UniqueConstraint(
                fields=["revision", "credential_revision"],
                name="publication_qualification_once",
            ),
            models.CheckConstraint(
                condition=models.Q(role__in=["coach", "nutritionist"]),
                name="publication_qualification_role",
            ),
        ]


class PublicationMediaBinding(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    revision = models.ForeignKey(
        PublicationRevision, on_delete=models.PROTECT, related_name="selected_media"
    )
    asset = models.ForeignKey(
        "assets.Asset", on_delete=models.PROTECT, related_name="publication_bindings"
    )
    purpose = models.CharField(max_length=6)
    asset_version = models.PositiveBigIntegerField()
    processing_version = models.PositiveBigIntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["revision", "purpose"], name="publication_media_purpose_once"
            ),
            models.UniqueConstraint(
                fields=["revision", "asset"], name="publication_media_asset_once"
            ),
            models.CheckConstraint(
                condition=models.Q(purpose__in=["avatar", "cover", "logo"]),
                name="publication_media_purpose",
            ),
            models.CheckConstraint(
                condition=models.Q(asset_version__gte=1),
                name="publication_media_asset_version",
            ),
            models.CheckConstraint(
                condition=models.Q(processing_version__gte=1),
                name="publication_media_processing",
            ),
        ]
