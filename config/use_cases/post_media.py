"""Post-domain authorization for the existing isolated public-copy pipeline."""

import hashlib
import json

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.assets.contracts import AssetNotFound
from apps.assets.models import AssetDerivative, PublicAssetCopy, PublicCopyAttempt
from apps.assets.publication_contracts import AuthorizedEducationalMediaRelease
from apps.governance.outbox import append_outbox
from apps.professionals.post_models import EducationalPost
from apps.professionals.post_selectors import confirmed_post


def parent_source(identifier, at):
    from config.use_cases.marketplace import current_source

    return current_source(identifier, at)


def binding(user, post_uuid, revision_uuid, source_uuid, at, *, require_flag=True):
    def lifetime_parent(identifier, now):
        from types import SimpleNamespace

        from apps.professionals.publication_selectors import retained_publication

        value = retained_publication(identifier, now)
        return SimpleNamespace(revision_uuid=value.revision_id) if value else None

    facts = confirmed_post(
        user,
        post_uuid,
        revision_uuid,
        at,
        parent_source=parent_source if require_flag else lifetime_parent,
        retain_hidden=not require_flag,
    )
    if facts is None:
        raise AssetNotFound("Publication media unavailable")
    post, revision, _ = facts
    link = revision.images.filter(asset_id=source_uuid).select_related("asset").first()
    if link is None:
        raise AssetNotFound("Publication media unavailable")
    derivative = (
        AssetDerivative.objects.select_for_update()
        .filter(
            asset_id=source_uuid,
            purpose="post_preview",
            state="ready",
            processing_version=link.processing_version,
        )
        .first()
    )
    if derivative is None:
        raise AssetNotFound("Publication media unavailable")
    old = PublicAssetCopy.objects.filter(
        release_revision_uuid=revision.id,
        source_asset_id=source_uuid,
        purpose="educational_image",
        processing_version=link.processing_version,
    ).first()
    if old and (
        old.source_derivative_id != derivative.id
        or old.source_derivative_version != derivative.version
        or old.source_derivative_sha256 != derivative.sha256
    ):
        raise AssetNotFound("Publication media unavailable")
    release = AuthorizedEducationalMediaRelease(
        user.public_id,
        post.profile_id,
        post.id,
        revision.id,
        source_uuid,
        "educational_image",
        link.asset_version,
        link.processing_version,
        old.publication_version if old else post.version,
        old.generation if old else 1,
    )
    vector = [str(getattr(release, k)) for k in release.__dataclass_fields__]
    vector += [
        user.auth_version,
        post.version,
        str(revision.confirmed_at),
        str(derivative.id),
        derivative.version,
        derivative.sha256,
        str(revision.parent_revision_id),
    ]
    return release, hashlib.sha256(json.dumps(vector).encode()).hexdigest()


def validate_release(user, release, at):
    release.__post_init__()
    if release.purpose != "educational_image" or user.public_id != release.owner_uuid:
        raise AssetNotFound("Publication media unavailable")
    expected, digest = binding(
        user,
        release.publication_uuid,
        release.revision_uuid,
        release.source_asset_uuid,
        max(at, timezone.now()),
    )
    if expected != release:
        raise AssetNotFound("Publication media unavailable")
    return digest


def prepare(row, at):
    from apps.assets.public_copies import prepare_public_copy

    revision = row.requested_revision
    if revision is None or revision.confirmed_at is None:
        return
    user = User.objects.select_for_update().get(pk=row.profile.user_id)
    for link in revision.images.order_by("position"):
        release, _ = binding(user, row.id, revision.id, link.asset_id, at)
        prepare_public_copy(release, at, authorize=validate_release)


def activate(copy, at):
    from apps.assets.public_copies import release_for

    user = User.objects.select_for_update().get(pk=copy.owner_id)
    validate_release(user, release_for(copy), at)
    post = EducationalPost.objects.select_for_update().get(pk=copy.publication_uuid)
    if (
        post.state == "published"
        and post.current_revision_id == copy.release_revision_uuid
    ):
        return
    if post.requested_revision_id != copy.release_revision_uuid:
        raise AssetNotFound("Publication media unavailable")
    for link in post.requested_revision.images.order_by("position"):
        candidate = (
            PublicAssetCopy.objects.select_for_update()
            .filter(
                publication_uuid=post.id,
                release_revision_uuid=copy.release_revision_uuid,
                source_asset_id=link.asset_id,
                source_version=link.asset_version,
                processing_version=link.processing_version,
                purpose="educational_image",
                state="ready",
                revoked_at__isnull=True,
            )
            .first()
        )
        if (
            candidate is None
            or not PublicCopyAttempt.objects.filter(
                copy=candidate,
                generation=candidate.generation,
                state="ready",
                signature_expires_at__gt=max(at, timezone.now()),
            ).exists()
        ):
            return
        validate_release(user, release_for(candidate), max(at, timezone.now()))
    post.current_revision_id = copy.release_revision_uuid
    post.requested_revision = None
    post.state = "published"
    post.version += 1
    post.updated_at = max(at, timezone.now())
    post.save()
    append_outbox(
        "professional.post_changed",
        post.id,
        post.version,
        {"post_uuid": str(post.id), "user_uuid": str(user.public_id)},
        f"professional.post_changed:{post.id}:{post.version}",
    )


def validate_read(copy, at):
    from apps.assets.public_copies import release_for

    user = User.objects.select_for_update().get(pk=copy.owner_id)
    digest = validate_release(user, release_for(copy), at)
    post = EducationalPost.objects.select_for_update().get(pk=copy.publication_uuid)
    if (
        not EducationalPost.objects.filter(
            pk=copy.publication_uuid,
            state="published",
            current_revision_id=copy.release_revision_uuid,
        ).exists()
        or copy.state != "ready"
        or copy.revoked_at is not None
    ):
        raise AssetNotFound("Publication media unavailable")
    current_copies(user, post, post.current_revision)
    return digest


def current_copies(user, post, revision):
    """One complete-revision policy shared by text and direct media delivery."""
    if (
        not transaction.get_connection().in_atomic_block
        or revision is None
        or post.state != "published"
        or post.current_revision_id != revision.id
    ):
        raise AssetNotFound("Publication media unavailable")
    links = {b.asset_id: b for b in revision.images.all()}
    if not 1 <= len(links) <= 4:
        raise AssetNotFound("Publication media unavailable")
    rows = list(
        PublicAssetCopy.objects.select_for_update(of=("self",))
        .select_related("source_derivative")
        .filter(
            owner=user,
            profile_uuid=post.profile_id,
            publication_uuid=post.id,
            release_revision_uuid=revision.id,
            purpose="educational_image",
            source_asset_id__in=links,
            state="ready",
            revoked_at__isnull=True,
        )
        .order_by("id")
    )
    if len(rows) != len(links):
        raise AssetNotFound("Publication media unavailable")
    for row in rows:
        link = links[row.source_asset_id]
        derivative = row.source_derivative
        if (
            row.source_version != link.asset_version
            or row.processing_version != link.processing_version
            or derivative.asset_id != row.source_asset_id
            or derivative.state != "ready"
            or derivative.purpose != "post_preview"
            or derivative.version != row.source_derivative_version
            or derivative.sha256 != row.source_derivative_sha256
            or derivative.processing_version != row.processing_version
            or not PublicCopyAttempt.objects.filter(
                copy=row, generation=row.generation, state="ready"
            ).exists()
        ):
            raise AssetNotFound("Publication media unavailable")
    return {row.source_asset_id: row for row in rows}
