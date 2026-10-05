import uuid

from django.conf import settings
from django.db import models


class PrivacyRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+"
    )
    kind = models.CharField(max_length=6)
    status = models.CharField(max_length=20)
    version = models.PositiveBigIntegerField(default=1)
    created_at = models.DateTimeField()
    verified_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(kind__in=["export", "delete"]), name="privacy_kind"
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(kind="export", status="pending_execution")
                    | models.Q(kind="delete", status="pending_deletion")
                ),
                name="privacy_intake_status",
            ),
            models.CheckConstraint(
                condition=models.Q(version__gte=1), name="privacy_version"
            ),
            models.CheckConstraint(
                condition=models.Q(verified_at__gte=models.F("created_at")),
                name="privacy_verified_time",
            ),
            models.UniqueConstraint(fields=["user", "kind"], name="privacy_open_kind"),
        ]


class RetentionPolicy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    data_class = models.CharField(max_length=32)
    purpose = models.CharField(max_length=32)
    status = models.CharField(max_length=12, default="draft")
    version = models.PositiveBigIntegerField(default=1)
    duration_seconds = models.PositiveBigIntegerField(null=True)
    backup_reference = models.CharField(max_length=64, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+", null=True
    )
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    approved_at = models.DateTimeField(null=True)
    effective_at = models.DateTimeField(null=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    status__in=["draft", "approved", "effective", "superseded"]
                ),
                name="retention_status",
            ),
            models.CheckConstraint(
                condition=models.Q(version__gte=1), name="retention_version"
            ),
            models.CheckConstraint(
                condition=models.Q(duration_seconds__isnull=True)
                | models.Q(duration_seconds__gt=0),
                name="retention_duration",
            ),
            models.CheckConstraint(
                condition=models.Q(status="draft")
                | (
                    models.Q(
                        duration_seconds__isnull=False,
                        approved_at__isnull=False,
                        approved_by__isnull=False,
                    )
                    & ~models.Q(backup_reference="")
                ),
                name="retention_approval",
            ),
            models.CheckConstraint(
                condition=~models.Q(status="effective")
                | models.Q(effective_at__isnull=False),
                name="retention_effective",
            ),
            models.UniqueConstraint(
                fields=["data_class", "purpose"],
                condition=models.Q(status="effective"),
                name="retention_one_effective",
            ),
        ]


class RecordHold(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject_kind = models.CharField(max_length=32)
    subject_uuid = models.UUIDField()
    subject_version = models.PositiveBigIntegerField()
    owner_uuid = models.UUIDField()
    case_uuid = models.UUIDField()
    purpose = models.CharField(max_length=16)
    reason_code = models.CharField(max_length=32)
    authorized_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+"
    )
    version = models.PositiveBigIntegerField(default=1)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    review_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    released_at = models.DateTimeField(null=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(subject_kind="privacy_request"),
                name="hold_subject_kind",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    purpose__in=["dispute", "fraud", "security", "required_audit"]
                ),
                name="hold_purpose",
            ),
            models.CheckConstraint(
                condition=models.Q(version__gte=1, subject_version__gte=1),
                name="hold_versions",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    review_at__gt=models.F("created_at"),
                    expires_at__gte=models.F("review_at"),
                ),
                name="hold_review_expiry",
            ),
            models.CheckConstraint(
                condition=models.Q(released_at__isnull=True)
                | models.Q(released_at__gte=models.F("created_at")),
                name="hold_release_time",
            ),
        ]
