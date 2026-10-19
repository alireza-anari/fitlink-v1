"""Publication-copy metadata; every command requires current server authority."""

import re
from datetime import datetime

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.accounts.policies import require_account_action

from .contracts import AssetNotFound
from .models import Asset, AssetDerivative, PublicAssetCopy, PublicCopyAttempt
from .public_storage import publication_key
from .publication_contracts import AuthorizedPublicMediaRelease, PublicCopyDTO


def context(release, at, authorize):
    if (
        not isinstance(release, AuthorizedPublicMediaRelease)
        or not isinstance(at, datetime)
        or not timezone.is_aware(at)
        or not callable(authorize)
    ):
        raise AssetNotFound("Publication media unavailable")
    release.__post_init__()


def locked_source(release, authorize, at):
    """Reuse the account anchor before composition's domain and source locks."""
    user = User.objects.select_for_update().filter(public_id=release.owner_uuid).first()
    if user is None:
        raise AssetNotFound("Publication media unavailable")
    require_account_action(user, "asset.owner_write", "normal")
    digest = authorize(user, release, max(at, timezone.now()))
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise AssetNotFound("Publication media unavailable")
    asset = (
        Asset.objects.select_for_update()
        .filter(
            pk=release.source_asset_uuid,
            owner=user,
            subject_kind="professional_profile",
            subject_uuid=release.profile_uuid,
            purpose=release.purpose,
            classification="private_source",
            state="ready",
            revoked_at__isnull=True,
            version=release.source_version,
            processing_version=release.processing_version,
        )
        .first()
    )
    if asset is None:
        raise AssetNotFound("Publication media unavailable")
    derivative = (
        AssetDerivative.objects.select_for_update()
        .filter(
            asset=asset,
            processing_version=release.processing_version,
            purpose="owner_preview",
            state="ready",
        )
        .first()
    )
    if derivative is None:
        raise AssetNotFound("Publication media unavailable")
    return user, asset, derivative, digest


def project_copy(row):
    return PublicCopyDTO(row.id, row.generation, row.state)


def prepare_public_copy(release: AuthorizedPublicMediaRelease, at, *, authorize=None):
    """Commit inventory only; no store, scanner, decoder or broker under locks."""
    context(release, at, authorize)
    at = max(at, timezone.now())
    with transaction.atomic():
        user, asset, derivative, digest = locked_source(release, authorize, at)
        row = (
            PublicAssetCopy.objects.select_for_update()
            .filter(
                release_revision_uuid=release.revision_uuid,
                purpose=release.purpose,
                source_asset=asset,
                processing_version=release.processing_version,
            )
            .first()
        )
        if row is None:
            if release.generation != 1:
                raise AssetNotFound("Publication media unavailable")
            row = PublicAssetCopy.objects.create(
                owner=user,
                source_asset=asset,
                source_derivative=derivative,
                source_derivative_version=derivative.version,
                profile_uuid=release.profile_uuid,
                publication_uuid=release.publication_uuid,
                release_revision_uuid=release.revision_uuid,
                purpose=release.purpose,
                source_version=release.source_version,
                processing_version=release.processing_version,
                publication_version=release.publication_version,
                owner_auth_version=user.auth_version,
                created_at=at,
                updated_at=at,
            )
            PublicCopyAttempt.objects.create(
                copy=row,
                generation=1,
                key=publication_key(row.id, 1),
                next_attempt_at=at,
                created_at=at,
                updated_at=at,
            )
        if (
            row.owner_id != user.pk
            or row.profile_uuid != release.profile_uuid
            or row.publication_uuid != release.publication_uuid
            or row.source_version != release.source_version
            or row.source_derivative_id != derivative.id
            or row.source_derivative_version != derivative.version
            or row.publication_version != release.publication_version
            or row.generation != release.generation
            or row.state not in {"pending", "running", "ready"}
        ):
            raise AssetNotFound("Publication media unavailable")
        return project_copy(row)
