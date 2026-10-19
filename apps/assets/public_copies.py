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


def release_for(row):
    return AuthorizedPublicMediaRelease(
        row.owner.public_id,
        row.profile_uuid,
        row.publication_uuid,
        row.release_revision_uuid,
        row.source_asset_id,
        row.purpose,
        row.source_version,
        row.processing_version,
        row.publication_version,
        row.generation,
    )


def locked_copy(identifier, authorize, at):
    hint = PublicAssetCopy.objects.select_related("owner").filter(pk=identifier).first()
    if hint is None:
        raise AssetNotFound("Publication media unavailable")
    release = release_for(hint)
    user, asset, derivative, digest = locked_source(release, authorize, at)
    row = PublicAssetCopy.objects.select_for_update().get(pk=identifier, owner=user)
    if (
        row.generation != release.generation
        or row.source_asset_id != asset.id
        or row.source_derivative_id != derivative.id
        or row.source_derivative_version != derivative.version
        or row.state not in {"pending", "running", "ready"}
    ):
        raise AssetNotFound("Publication media unavailable")
    return user, row, derivative, digest


def enqueue_copy(identifier, generation, lease):
    from .tasks import process_public_asset_copy

    process_public_asset_copy.apply_async(
        args=[str(identifier), generation, str(lease)],
        retry=False,
    )


def scan_due_public_copies(at, batch_size=100, *, authorize=None, enqueue=None):
    from datetime import timedelta
    from uuid import uuid4

    from django.db.models import F, Q

    if (
        not isinstance(at, datetime)
        or not timezone.is_aware(at)
        or type(batch_size) is not int
        or not 1 <= batch_size <= 100
        or not callable(authorize)
        or transaction.get_connection().in_atomic_block
    ):
        return 0
    due = (
        PublicCopyAttempt.objects.filter(
            copy__state__in=["pending", "running"],
            generation=F("copy__generation"),
        )
        .filter(
            Q(state__in=["pending", "failed"], next_attempt_at__lte=at)
            | Q(state="running", lease_until__lte=at)
        )
        .order_by("next_attempt_at", "created_at", "id")
    )
    identifiers = list(due.values_list("copy_id", flat=True)[:batch_size])
    sent = 0
    for identifier in identifiers:
        try:
            with transaction.atomic():
                now = max(at, timezone.now())
                user, row, derivative, digest = locked_copy(identifier, authorize, now)
                attempt = PublicCopyAttempt.objects.select_for_update().get(
                    copy=row,
                    generation=row.generation,
                )
                if attempt.state == "running" and attempt.lease_until > now:
                    continue
                if (
                    attempt.state in {"failed", "pending"}
                    and attempt.next_attempt_at > now
                ):
                    continue
                if attempt.state not in {"running", "pending", "failed"}:
                    continue
                if attempt.state in {"running", "failed"}:
                    if row.generation >= 8:
                        attempt.state, attempt.failure_code = "failed", "attempt_limit"
                        attempt.lease_uuid = attempt.lease_until = None
                        attempt.updated_at = now
                        attempt.save()
                        row.state, row.revoked_at = "failed", now
                        row.version += 1
                        row.updated_at = now
                        row.save()
                        continue
                    attempt.state, attempt.failure_code = "failed", "lease_expired"
                    attempt.lease_uuid = attempt.lease_until = None
                    attempt.updated_at = now
                    attempt.save()
                    attempt = PublicCopyAttempt.objects.create(
                        copy=row,
                        generation=row.generation + 1,
                        key=publication_key(row.id, row.generation + 1),
                        next_attempt_at=now,
                        created_at=now,
                        updated_at=now,
                    )
                    row.generation += 1
                row.state, row.owner_auth_version = "running", user.auth_version
                row.version += 1
                row.updated_at = now
                row.save()
                # Generation changes are part of the authority vector. Capture
                # after the current generation commits within this transaction.
                digest = authorize(user, release_for(row), max(now, timezone.now()))
                if not isinstance(digest, str) or not re.fullmatch(
                    r"[0-9a-f]{64}", digest
                ):
                    raise AssetNotFound("Publication media unavailable")
                attempt.state = "running"
                attempt.authority_hash = digest
                attempt.lease_uuid = uuid4()
                attempt.lease_until = now + timedelta(seconds=60)
                attempt.updated_at = now
                attempt.save()
                prompt = row.id, row.generation, attempt.lease_uuid
            # Broker I/O never runs with domain/transaction locks held. The
            # committed lease recovers a missing prompt without an outbox lock.
        except (PermissionError, ValueError, LookupError):
            continue
        try:
            (enqueue or enqueue_copy)(*prompt)
            sent += 1
        except Exception:
            # The broker may have accepted before its reply was lost. Retain
            # the committed lease; recovery always changes generation and key.
            continue
    return sent
