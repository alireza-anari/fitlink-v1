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


def _binding(user, publication_uuid, revision_uuid, purpose, at, *, require_flag=True):
    if (
        not all(isinstance(v, UUID) for v in (publication_uuid, revision_uuid))
        or not isinstance(purpose, str)
        or purpose not in {"avatar", "cover", "logo"}
        or not isinstance(at, datetime)
        or not timezone.is_aware(at)
        or (require_flag and feature_enabled("marketplace") is not True)
    ):
        raise AssetNotFound("Publication media unavailable")
    at = max(at, timezone.now())
    publication = ProfessionalPublication.objects.filter(
        pk=publication_uuid,
        profile__user=user,
    ).first()
    if publication is None:
        raise AssetNotFound("Publication media unavailable")
    if require_flag:
        facts = confirmed_media_publication(publication.profile_id, revision_uuid, at)
    else:
        from apps.professionals.publication_selectors import retained_publication

        facts = retained_publication(publication.profile_id, at, revision_uuid)
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
    if old is not None and (
        old.source_derivative_id != derivative.id
        or old.source_derivative_version != derivative.version
        or old.source_derivative_sha256 != derivative.sha256
    ):
        raise AssetNotFound("Publication media unavailable")
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
    if release.purpose == "educational_image":
        from config.use_cases.post_media import validate_release as validate_post

        return validate_post(user, release, at)
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


def activate_publication_media(copy, at):
    """Publish only a complete confirmed revision; caller holds the owner anchor."""
    from apps.assets.models import PublicCopyAttempt
    from apps.assets.public_copies import release_for
    from apps.governance.outbox import append_outbox

    if copy.purpose == "educational_image":
        from config.use_cases.post_media import activate

        return activate(copy, at)

    if not transaction.get_connection().in_atomic_block:
        raise AssetNotFound("Publication media unavailable")
    user = User.objects.select_for_update().get(pk=copy.owner_id)
    validate_release(user, release_for(copy), at)
    publication = ProfessionalPublication.objects.select_for_update().get(
        pk=copy.publication_uuid
    )
    if (
        publication.state == "published"
        and publication.current_revision_id == copy.release_revision_uuid
    ):
        return
    if publication.requested_revision_id != copy.release_revision_uuid:
        raise AssetNotFound("Publication media unavailable")
    bindings = list(
        PublicationMediaBinding.objects.filter(revision_id=copy.release_revision_uuid)
    )
    for binding in bindings:
        candidate = (
            PublicAssetCopy.objects.select_for_update()
            .filter(
                publication_uuid=publication.id,
                release_revision_uuid=copy.release_revision_uuid,
                source_asset_id=binding.asset_id,
                purpose=binding.purpose,
                source_version=binding.asset_version,
                processing_version=binding.processing_version,
                state="ready",
                revoked_at__isnull=True,
            )
            .first()
        )
        if candidate is None:
            return
        if not PublicCopyAttempt.objects.filter(
            copy=candidate,
            generation=candidate.generation,
            state="ready",
            signature_expires_at__gt=max(at, timezone.now()),
        ).exists():
            return
        validate_release(user, release_for(candidate), max(at, timezone.now()))
    publication.current_revision_id = copy.release_revision_uuid
    publication.requested_revision = None
    publication.state = "published"
    publication.version += 1
    publication.updated_at = max(at, timezone.now())
    publication.save()
    append_outbox(
        "professional.publication_changed",
        publication.id,
        publication.version,
        {"publication_uuid": str(publication.id), "user_uuid": str(user.public_id)},
        f"professional.publication_changed:{publication.id}:{publication.version}",
    )


def process_public_copy(identifier, generation, lease, at):
    from apps.assets.public_copies import process_public_copy as process

    return process(
        identifier,
        generation,
        lease,
        at,
        authorize=validate_release,
        activate=activate_publication_media,
    )


def validate_public_copy_read(copy, at):
    from apps.assets.public_copies import release_for
    from apps.professionals.publication_selectors import effective_publication

    if copy.purpose == "educational_image":
        from config.use_cases.post_media import validate_read

        return validate_read(copy, at)

    user = User.objects.select_for_update().get(pk=copy.owner_id)
    digest = validate_release(user, release_for(copy), max(at, timezone.now()))
    facts = effective_publication(copy.profile_uuid, max(at, timezone.now()))
    if (
        facts is None
        or facts.publication_id != copy.publication_uuid
        or facts.revision_id != copy.release_revision_uuid
        or copy.state != "ready"
        or copy.revoked_at is not None
    ):
        raise AssetNotFound("Publication media unavailable")
    return digest


def reconcile_public_copy_lifetime(identifier, at):
    from apps.assets.public_copies import reconcile_public_copy_lifetime as reconcile

    def current(user, copy, now):
        try:
            if copy.purpose == "educational_image":
                from config.use_cases.post_media import binding

                binding(
                    user,
                    copy.publication_uuid,
                    copy.release_revision_uuid,
                    copy.source_asset_id,
                    now,
                    require_flag=False,
                )
                return True
            _binding(
                user,
                copy.publication_uuid,
                copy.release_revision_uuid,
                copy.purpose,
                now,
                require_flag=False,
            )
            return True
        except (PermissionError, ValueError, LookupError):
            return False

    return reconcile(identifier, at, authorize=current)


def cleanup_public_copy(
    identifier, generation, policy_uuid, at, *, publication_store=None
):
    from apps.assets.cleanup import cleanup_public_copy as cleanup
    from config.use_cases.c03_privacy import _asset_held, _cleanup_subject

    return cleanup(
        identifier,
        generation,
        policy_uuid,
        at,
        subject_validator=_cleanup_subject,
        hold_validator=_asset_held,
        publication_store=publication_store,
    )


def reconcile_public_media(at, batch_size=100):
    """Reuse attempt due timestamps; no second cursor or scheduler infrastructure."""
    from datetime import timedelta

    from django.db.models import F, Q

    from apps.assets.models import PublicCopyAttempt

    if (
        not isinstance(at, datetime)
        or not timezone.is_aware(at)
        or type(batch_size) is not int
        or not 1 <= batch_size <= 100
        or transaction.get_connection().in_atomic_block
    ):
        return 0
    ids = list(
        PublicCopyAttempt.objects.filter(
            next_attempt_at__lte=at,
        )
        .filter(
            Q(
                state__in=["pending", "running", "ready"],
                generation=F("copy__generation"),
            )
            | Q(copy__state__in=["revoked", "failed", "deletion_pending", "deleted"])
            | Q(generation__lt=F("copy__generation")),
        )
        .order_by(
            "next_attempt_at",
            "id",
        )
        .values_list("id", flat=True)[:batch_size]
    )
    count = 0
    for identifier in ids:
        hint = (
            PublicCopyAttempt.objects.select_related("copy")
            .filter(pk=identifier)
            .first()
        )
        if hint is None:
            continue
        reconcile_public_copy_lifetime(hint.copy_id, at)
        row = PublicAssetCopy.objects.get(pk=hint.copy_id)
        if row.state in {"revoked", "deleted"}:
            from apps.assets.public_copies import renew_revoked_public_copy

            renew_revoked_public_copy(row.id, at, authorize=validate_release)
            row.refresh_from_db()
        if (
            row.state in {"failed", "revoked", "deletion_pending", "deleted"}
            or hint.generation < row.generation
        ):
            # Same C03 policy lookup/binding and hold semantics; missing policy
            # retains bytes. Only the private publication namespace is erasable.
            from apps.governance.privacy_models import RetentionPolicy

            policy_id = (
                RetentionPolicy.objects.filter(
                    data_class="profile_media",
                    purpose=row.purpose,
                    status="effective",
                    approved_by__isnull=False,
                    approved_at__lte=at,
                    effective_at__lte=at,
                    duration_seconds__gt=0,
                )
                .exclude(backup_reference="")
                .order_by("id")
                .values_list("id", flat=True)
                .first()
            )
            if policy_id is not None:
                cleanup_public_copy(row.id, hint.generation, policy_id, at)
        with transaction.atomic():
            User.objects.select_for_update().get(pk=row.owner_id)
            attempt = PublicCopyAttempt.objects.select_for_update().get(pk=identifier)
            attempt.next_attempt_at = max(at, timezone.now()) + timedelta(seconds=30)
            attempt.updated_at = max(at, timezone.now())
            attempt.save()
        count += 1
    return count
