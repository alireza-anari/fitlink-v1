import uuid

from django.conf import settings
from django.db import models

PURPOSES = (
    "account_metadata",
    "active_sharing",
    "archive_sharing",
    "nutrition_adherence_read",
    "ai_feature",
    "mirror_summary",
    "case_study",
    "baseline_storage",
)


class Consent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+"
    )
    grantee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+"
    )
    purpose = models.CharField(max_length=32)
    text_version = models.CharField(max_length=64)
    content_hash = models.CharField(max_length=64)
    granted_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True)
    version = models.PositiveBigIntegerField(default=1)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(purpose__in=PURPOSES), name="consent_purpose"
            ),
            models.CheckConstraint(
                condition=models.Q(version__gte=1), name="consent_version"
            ),
            models.CheckConstraint(
                condition=models.Q(expires_at__gt=models.F("granted_at")),
                name="consent_expiry",
            ),
            models.CheckConstraint(
                condition=models.Q(revoked_at__isnull=True)
                | models.Q(revoked_at__gte=models.F("granted_at")),
                name="consent_revocation_time",
            ),
            models.CheckConstraint(
                condition=models.Q(content_hash__regex=r"^[0-9a-f]{64}$"),
                name="consent_content_hash",
            ),
            models.CheckConstraint(
                condition=models.Q(text_version__regex=r"^[a-zA-Z0-9_.:-]{1,64}$"),
                name="consent_text_version",
            ),
        ]
        indexes = [
            models.Index(
                fields=["subject", "grantee", "purpose"],
                name="consent_exact_participants",
            )
        ]


class ConsentScope(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consent = models.ForeignKey(
        Consent, on_delete=models.PROTECT, related_name="scopes"
    )
    kind = models.CharField(max_length=32)
    object_uuid = models.UUIDField()
    object_version = models.PositiveBigIntegerField()

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(object_version__gte=1), name="consent_scope_version"
            ),
            models.CheckConstraint(
                condition=models.Q(kind__regex=r"^[a-z_]{1,32}$"),
                name="consent_scope_kind",
            ),
            models.UniqueConstraint(
                fields=["consent", "kind", "object_uuid", "object_version"],
                name="consent_scope_unique",
            ),
        ]
