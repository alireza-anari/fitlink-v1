import uuid

from django.conf import settings
from django.db import models


class InviteReferralLink(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    issuer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+"
    )
    token_digest = models.CharField(max_length=64, unique=True)
    key_id = models.CharField(max_length=32)
    created_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(token_digest__regex=r"^[0-9a-f]{64}$"),
                name="referral_digest",
            ),
            models.CheckConstraint(
                condition=models.Q(key_id__regex=r"^[A-Za-z0-9_-]{1,32}$"),
                name="referral_key_id",
            ),
            models.CheckConstraint(
                condition=models.Q(expires_at__gt=models.F("created_at")),
                name="referral_expiry",
            ),
            models.CheckConstraint(
                condition=models.Q(revoked_at__isnull=True)
                | models.Q(revoked_at__gte=models.F("created_at")),
                name="referral_revocation",
            ),
        ]


class ReferralAttribution(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+"
    )
    link = models.ForeignKey(
        InviteReferralLink, on_delete=models.PROTECT, related_name="+"
    )
    attributed_at = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["recipient"], name="referral_first_attribution"
            )
        ]
