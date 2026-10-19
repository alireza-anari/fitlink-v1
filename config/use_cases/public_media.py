"""Professional confirmation composes assets' separate private copy inventory."""

import hashlib
import json
from datetime import datetime
from uuid import UUID

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.assets.contracts import AssetNotFound
from apps.assets.models import Asset, AssetDerivative, PublicAssetCopy
from apps.assets.publication_contracts import AuthorizedPublicMediaRelease
from apps.governance.flags import feature_enabled
from apps.professionals.publication_models import (
    ProfessionalPublication,
    PublicationMediaBinding,
)
from apps.professionals.publication_selectors import confirmed_media_publication


def _binding(user, publication_uuid, revision_uuid, purpose, at):
    if (
        not all(isinstance(v, UUID) for v in (publication_uuid, revision_uuid))
        or not isinstance(purpose, str)
        or purpose not in {"avatar", "cover", "logo"}
        or not isinstance(at, datetime)
        or not timezone.is_aware(at)
        or feature_enabled("marketplace") is not True
    ):
        raise AssetNotFound("Publication media unavailable")
    at = max(at, timezone.now())
    publication = ProfessionalPublication.objects.filter(
        pk=publication_uuid,
        profile__user=user,
    ).first()
    if publication is None:
        raise AssetNotFound("Publication media unavailable")
    facts = confirmed_media_publication(publication.profile_id, revision_uuid, at)
    if facts is None or facts.publication_id != publication.id:
        raise AssetNotFound("Publication media unavailable")
    binding = PublicationMediaBinding.objects.filter(
        revision_id=revision_uuid,
        purpose=purpose,
    ).first()
    if binding is None:
        raise AssetNotFound("Publication media unavailable")
    source = (
        Asset.objects.select_for_update()
        .filter(
            pk=binding.asset_id,
            owner=user,
            state="ready",
            revoked_at__isnull=True,
            purpose=purpose,
            classification="private_source",
            subject_kind="professional_profile",
            subject_uuid=publication.profile_id,
            version=binding.asset_version,
            processing_version=binding.processing_version,
        )
        .first()
    )
    if source is None:
        raise AssetNotFound("Publication media unavailable")
    derivative = (
        AssetDerivative.objects.select_for_update()
        .filter(
            asset=source,
            processing_version=source.processing_version,
            purpose="owner_preview",
            state="ready",
        )
        .first()
    )
    if derivative is None:
        raise AssetNotFound("Publication media unavailable")
    old = PublicAssetCopy.objects.filter(
        release_revision_uuid=revision_uuid,
        purpose=purpose,
        source_asset=source,
        processing_version=source.processing_version,
    ).first()
    release = AuthorizedPublicMediaRelease(
        user.public_id,
        publication.profile_id,
        publication.id,
        revision_uuid,
        source.id,
        purpose,
        source.version,
        source.processing_version,
        old.publication_version if old else facts.version,
        old.generation if old else 1,
    )
    vector = {
        "release": [str(getattr(release, key)) for key in release.__dataclass_fields__],
        "owner_auth_version": user.auth_version,
        "publication_version": facts.version,
        "source_profile_version": facts.source_profile_version,
        "public_snapshot": facts.snapshot,
        "derivative": [
            str(derivative.id),
            derivative.version,
            derivative.sha256,
            derivative.mime_type,
            derivative.width,
            derivative.height,
        ],
    }
    digest = hashlib.sha256(json.dumps(vector, sort_keys=True).encode()).hexdigest()
    return release, digest


def authorize_public_media(publication_uuid, revision_uuid, purpose, at):
    """Internal server constructor; never exposed as browser-supplied authority."""
    owner_id = (
        ProfessionalPublication.objects.filter(pk=publication_uuid)
        .values_list("profile__user_id", flat=True)
        .first()
    )
    if owner_id is None:
        raise AssetNotFound("Publication media unavailable")
    with transaction.atomic():
        user = User.objects.select_for_update().get(pk=owner_id)
        return _binding(user, publication_uuid, revision_uuid, purpose, at)[0]


def validate_release(user, release, at):
    if not isinstance(release, AuthorizedPublicMediaRelease):
        raise AssetNotFound("Publication media unavailable")
    release.__post_init__()
    if user.public_id != release.owner_uuid:
        raise AssetNotFound("Publication media unavailable")
    expected, digest = _binding(
        user, release.publication_uuid, release.revision_uuid, release.purpose, at
    )
    if release != expected:
        raise AssetNotFound("Publication media unavailable")
    return digest


def scan_due_public_copies(at, batch_size=100):
    from apps.assets.public_copies import scan_due_public_copies as scan

    if feature_enabled("marketplace") is not True:
        return 0
    return scan(at, batch_size, authorize=validate_release)
