import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from .assistant_models import AssistantMembership as AssistantMembership
from .credential_models import Credential as Credential
from .credential_models import CredentialRevision as CredentialRevision
from .profile_models import ProfessionalLocation as ProfessionalLocation
from .profile_models import ProfessionalRole as ProfessionalRole
from .receipt_models import ProfileCommandReceipt as ProfileCommandReceipt
from .restriction_models import (
    ProfessionalRoleRestriction as ProfessionalRoleRestriction,
)
from .restriction_models import RoleRestrictionHistory as RoleRestrictionHistory
from .verification_models import Verification as Verification
from .verification_models import VerificationAssignment as VerificationAssignment
from .verification_models import VerificationDecision as VerificationDecision
from .verification_models import VerificationEvidence as VerificationEvidence
from .verification_models import VerificationHistory as VerificationHistory
from .verification_models import VerificationTarget as VerificationTarget


class ProfessionalProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="professional_profile",
    )
    state = models.CharField(max_length=16, default="setup")
    version = models.PositiveBigIntegerField(default=1)
    identity_evidence_revision = models.PositiveBigIntegerField(default=1)
    identity_decision_version = models.PositiveBigIntegerField(default=1)
    display_name = models.CharField(max_length=120, blank=True)
    identity_name = models.CharField(max_length=120, blank=True)
    biography = models.CharField(max_length=2000, blank=True)
    specialties = models.JSONField(default=list, blank=True)
    experience_years = models.PositiveSmallIntegerField(null=True, blank=True)
    service_modes = models.JSONField(default=list, blank=True)
    languages = models.JSONField(default=list, blank=True)
    setup_step = models.CharField(max_length=32, default="identity")
    avatar = models.ForeignKey(
        "assets.Asset",
        on_delete=models.PROTECT,
        related_name="professional_avatar_profiles",
        null=True,
        blank=True,
    )
    cover = models.ForeignKey(
        "assets.Asset",
        on_delete=models.PROTECT,
        related_name="professional_cover_profiles",
        null=True,
        blank=True,
    )
    logo = models.ForeignKey(
        "assets.Asset",
        on_delete=models.PROTECT,
        related_name="professional_logo_profiles",
        null=True,
        blank=True,
    )
    accent_color = models.CharField(max_length=7, blank=True)
    welcome_message = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(experience_years__isnull=True)
                | models.Q(experience_years__lte=80),
                name="professional_experience_bound",
            ),
            models.CheckConstraint(
                condition=models.Q(accent_color="")
                | models.Q(accent_color__regex=r"^#[0-9A-Fa-f]{6}$"),
                name="professional_accent_color",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    setup_step__in=[
                        "identity",
                        "description",
                        "locations",
                        "branding",
                        "credentials",
                        "preview",
                    ]
                ),
                name="professional_setup_step",
            ),
            models.CheckConstraint(
                condition=models.Q(state__in=["setup", "private_ready", "archived"]),
                name="professional_profile_state",
            ),
            models.CheckConstraint(
                condition=models.Q(version__gte=1), name="professional_profile_version"
            ),
            models.CheckConstraint(
                condition=models.Q(identity_evidence_revision__gte=1),
                name="profile_identity_evidence_version",
            ),
            models.CheckConstraint(
                condition=models.Q(identity_decision_version__gte=1),
                name="profile_identity_decision_version",
            ),
        ]
