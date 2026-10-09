"""Profile declaration and staff flags grant no workspace ownership."""

from datetime import datetime
from uuid import UUID

from django.utils import timezone

from apps.accounts.models import User
from apps.accounts.sessions import AccountActor

from .contracts import ProfileNotFound
from .models import ProfessionalProfile


def validate_context(actor: AccountActor, at: datetime) -> None:
    if not isinstance(at, datetime) or not timezone.is_aware(at):
        raise ValueError("Invalid profile command time")
    if (
        not isinstance(actor, AccountActor)
        or not isinstance(actor.user_uuid, UUID)
        or not isinstance(actor.control_id, UUID)
        or type(actor.auth_version) is not int
        or actor.auth_version < 1
        or not isinstance(actor.authenticated_at, datetime)
        or not timezone.is_aware(actor.authenticated_at)
        or actor.authenticated_at > at
    ):
        raise PermissionError("Account action denied")


def owned_profile(
    user: User, profile_uuid: UUID, *, lock: bool = False
) -> ProfessionalProfile:
    if not isinstance(profile_uuid, UUID):
        raise ProfileNotFound("Profile unavailable")
    query = ProfessionalProfile.objects.all()
    if lock:
        query = query.select_for_update()
    row = query.filter(pk=profile_uuid, user=user).exclude(state="archived").first()
    if row is None:
        raise ProfileNotFound("Profile unavailable")
    return row


def owned_asset_subject(user: User, purpose: str, identifier: UUID):
    """Exact current professional purpose; profile/role existence grants no access."""
    from apps.assets.contracts import AssetNotFound, AssetSubject
    from apps.assets.validation import PURPOSES

    from .credential_models import Credential
    from .profile_models import ProfessionalRole

    if not isinstance(purpose, str) or purpose not in PURPOSES:
        raise ValueError("Invalid upload purpose")
    if not isinstance(identifier, UUID):
        raise AssetNotFound("Asset unavailable")
    profile = (
        ProfessionalProfile.objects.select_for_update()
        .filter(user=user)
        .exclude(state="archived")
        .first()
    )
    if profile is None:
        raise AssetNotFound("Asset unavailable")
    if purpose in {"avatar", "cover", "logo"}:
        if profile.id != identifier:
            raise AssetNotFound("Asset unavailable")
        return AssetSubject("professional_profile", profile.id)
    credential = (
        Credential.objects.select_for_update()
        .filter(
            pk=identifier,
            profile=profile,
            withdrawn_at__isnull=True,
            category="identity" if purpose == "identity_evidence" else "qualification",
        )
        .first()
    )
    if credential is None:
        raise AssetNotFound("Asset unavailable")
    if purpose == "credential_evidence" and (
        credential.role_id is None
        or not ProfessionalRole.objects.filter(
            pk=credential.role_id,
            profile=profile,
            declared_active=True,
        ).exists()
    ):
        raise AssetNotFound("Asset unavailable")
    return AssetSubject("professional_credential", credential.id)


def ready_asset(user, profile, identifier, purpose, credential_uuid):
    from apps.assets.models import Asset
    from apps.professionals.contracts import ProfileNotFound

    row = (
        Asset.objects.select_for_update()
        .filter(
            pk=identifier,
            owner=user,
            purpose=purpose,
            classification="private_source",
            state="ready",
            revoked_at__isnull=True,
        )
        .first()
    )
    if row is None:
        raise ProfileNotFound("Asset unavailable")
    subject_matches = (
        row.subject_kind == "professional_profile" and row.subject_uuid == profile.id
    )
    if credential_uuid is not None:
        subject_matches = subject_matches or (
            row.subject_kind == "professional_credential"
            and row.subject_uuid == credential_uuid
        )
    if not subject_matches:
        raise ProfileNotFound("Asset unavailable")
    preview = "evidence_preview" if purpose.endswith("evidence") else "owner_preview"
    attempt = (
        row.processing_attempts.filter(processing_version=row.processing_version)
        .order_by("-attempt")
        .first()
    )
    if (
        attempt is None
        or attempt.state != "ready"
        or attempt.algorithm_version != "jpeg-png-pixels-v1"
        or attempt.scanner_engine != "ClamAV 1.5.4"
        or not attempt.scanner_signature.isdecimal()
        or not row.derivatives.filter(
            processing_version=row.processing_version, purpose=preview, state="ready"
        ).exists()
    ):
        raise ProfileNotFound("Asset unavailable")
    return row
