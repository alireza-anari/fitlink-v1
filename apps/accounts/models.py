import uuid

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

from .managers import UserManager, canonical_phone


class User(AbstractBaseUser, PermissionsMixin):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    phone = models.CharField(
        max_length=13, unique=True, validators=[RegexValidator(r"\A\+989[0-9]{9}\Z")]
    )
    password = models.CharField(max_length=128, default="!")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    birth_date = models.DateField(null=True)
    adult_attested_at = models.DateTimeField(null=True)
    adult_attestation_version = models.CharField(max_length=40, default="", blank=True)
    locale = models.CharField(max_length=5, default="fa")
    timezone = models.CharField(max_length=64, default="Asia/Tehran")
    state = models.CharField(max_length=20, default="active")
    state_version = models.PositiveBigIntegerField(default=1)
    auth_version = models.PositiveBigIntegerField(default=1)
    objects = UserManager()
    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(phone__regex=r"^\+989[0-9]{9}$"),
                name="accounts_user_canonical_phone",
            ),
            models.CheckConstraint(
                condition=models.Q(auth_version__gte=1), name="account_auth_version"
            ),
            models.CheckConstraint(
                condition=models.Q(state_version__gte=1), name="account_state_version"
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        state__in=[
                            "active",
                            "restricted",
                            "deletion_requested",
                            "pending_deletion",
                        ],
                        is_active=True,
                    )
                    | models.Q(
                        state__in=[
                            "suspended",
                            "deleted",
                            "anonymized",
                            "deletion_completed",
                        ],
                        is_active=False,
                    )
                ),
                name="account_state_active_consistency",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        adult_attested_at__isnull=True, adult_attestation_version=""
                    )
                    | (
                        models.Q(
                            birth_date__isnull=False, adult_attested_at__isnull=False
                        )
                        & ~models.Q(adult_attestation_version="")
                    )
                ),
                name="account_attestation_consistency",
            ),
        ]

    def save(self, *args, **kwargs):
        canonical_phone(self.phone)
        return super().save(*args, **kwargs)


# Register focused models without replacing the permanent User module.
from .recovery_models import (  # noqa: E402, F401
    PhoneChangeHistory,
    RecoveryEvidenceMetadata,
    RecoveryRequest,
)
from .security_models import (  # noqa: E402, F401
    AccountSessionControl,
    OTPChallenge,
    OTPPhoneState,
    SecurityRateAnchor,
    SecurityRateEvent,
)
