import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

CAPABILITIES = (
    "account_recovery",
    "account_restriction",
    "security_audit",
    "privacy_operations",
    "feature_flags",
    "professional_verification",
)


class StaffCapabilityGrant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="staff_capabilities",
    )
    capability = models.CharField(max_length=24)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True)
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="issued_staff_capabilities",
    )
    reason_code = models.CharField(max_length=32)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "capability"],
                condition=models.Q(revoked_at__isnull=True),
                name="staff_live_capability",
            ),
            models.CheckConstraint(
                condition=models.Q(capability__in=CAPABILITIES),
                name="staff_capability_kind",
            ),
            models.CheckConstraint(
                condition=models.Q(valid_until__gt=models.F("valid_from")),
                name="staff_capability_expiry",
            ),
        ]


class StaffStepUpGrant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="staff_step_ups",
    )
    auth_version = models.PositiveBigIntegerField()
    capability = models.CharField(max_length=24)
    case_uuid = models.UUIDField(null=True)
    method = models.CharField(max_length=16)
    provider_reference = models.UUIDField(unique=True)
    verified_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True)
    trusted_issuer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="issued_staff_step_ups",
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(capability__in=CAPABILITIES),
                name="step_up_capability_kind",
            ),
            models.CheckConstraint(
                condition=models.Q(auth_version__gte=1), name="step_up_auth_version"
            ),
            models.CheckConstraint(
                condition=models.Q(expires_at__gt=models.F("verified_at")),
                name="step_up_expiry",
            ),
            models.CheckConstraint(
                condition=models.Q(method__in=["mock", "verified_mfa"]),
                name="step_up_method",
            ),
        ]
