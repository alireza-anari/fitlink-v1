"""Publication-copy metadata; every command requires current server authority."""

import re
from datetime import datetime

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.accounts.policies import require_account_action

from .contracts import AssetNotFound
from .models import Asset, AssetDerivative, PublicAssetCopy, PublicCopyAttempt
from .public_storage import get_publication_store, publication_key
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
            subject_kind="educational_post"
            if release.purpose == "educational_image"
            else "professional_profile",
            subject_uuid=release.publication_uuid
            if release.purpose == "educational_image"
            else release.profile_uuid,
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
            purpose="post_preview"
            if release.purpose == "educational_image"
            else "owner_preview",
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
                source_derivative_sha256=derivative.sha256,
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
            or row.source_derivative_sha256 != derivative.sha256
            or row.publication_version != release.publication_version
            or row.generation != release.generation
            or row.state not in {"pending", "running", "ready"}
        ):
            raise AssetNotFound("Publication media unavailable")
        return project_copy(row)


def release_for(row):
    from .publication_contracts import AuthorizedEducationalMediaRelease

    constructor = (
        AuthorizedEducationalMediaRelease
        if row.purpose == "educational_image"
        else AuthorizedPublicMediaRelease
    )
    return constructor(
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
        or row.source_derivative_sha256 != derivative.sha256
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
                        attempt.retired_at = attempt.retired_at or now
                        attempt.updated_at = now
                        attempt.save()
                        row.state, row.revoked_at = "failed", now
                        row.version += 1
                        row.updated_at = now
                        row.save()
                        continue
                    attempt.state, attempt.failure_code = "failed", "lease_expired"
                    attempt.lease_uuid = attempt.lease_until = None
                    attempt.retired_at = attempt.retired_at or now
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


def fenced_copy(identifier, generation, lease, authorize, at):
    user, row, derivative, digest = locked_copy(identifier, authorize, at)
    attempt = (
        PublicCopyAttempt.objects.select_for_update()
        .filter(
            copy=row,
            generation=generation,
            state="running",
            lease_uuid=lease,
            lease_until__gt=at,
        )
        .first()
    )
    if (
        attempt is None
        or row.generation != generation
        or row.state != "running"
        or row.owner_auth_version != user.auth_version
        or attempt.authority_hash != digest
    ):
        raise AssetNotFound("Publication media unavailable")
    return row, attempt, derivative


def copy_failure(identifier, generation, lease, code, at, *, fatal=False):
    from datetime import timedelta

    hint = PublicAssetCopy.objects.filter(pk=identifier).first()
    if hint is None:
        return
    with transaction.atomic():
        User.objects.select_for_update().get(pk=hint.owner_id)
        row = PublicAssetCopy.objects.select_for_update().get(pk=identifier)
        attempt = (
            PublicCopyAttempt.objects.select_for_update()
            .filter(
                copy=row,
                generation=generation,
                state="running",
                lease_uuid=lease,
            )
            .first()
        )
        if attempt is None or row.generation != generation or row.state != "running":
            return
        attempt.state, attempt.failure_code = "failed", code
        attempt.lease_uuid = attempt.lease_until = None
        attempt.retired_at = attempt.retired_at or at
        attempt.next_attempt_at = at + timedelta(seconds=300)
        attempt.updated_at = at
        attempt.save()
        if fatal:
            row.state, row.revoked_at = "failed", at
            row.version += 1
            row.updated_at = at
            row.save()


def process_public_copy(
    identifier,
    generation,
    lease,
    at,
    *,
    authorize=None,
    activate=None,
    source_store=None,
    publication_store=None,
    scanner=None,
    sanitize=None,
):
    from hashlib import sha256
    from uuid import UUID

    from django.conf import settings

    from .images import sanitize as decode
    from .publication_contracts import MAX_PUBLIC_IMAGE_BYTES, CopyResult
    from .scanner import configured_scanner
    from .storage import get_private_store

    def result(status):
        return CopyResult(identifier, generation, status)

    if (
        not isinstance(identifier, UUID)
        or not isinstance(lease, UUID)
        or type(generation) is not int
        or not 1 <= generation <= 8
        or not isinstance(at, datetime)
        or not timezone.is_aware(at)
        or not callable(authorize)
        or not callable(activate)
        or transaction.get_connection().in_atomic_block
    ):
        return result("denied")
    if (
        source_store is None or publication_store is None or scanner is None
    ) and not settings.ASSET_PROCESSING_ENABLED:
        return result("unavailable")

    def now():
        return max(at, timezone.now())

    try:
        with transaction.atomic():
            row, attempt, derivative = fenced_copy(
                identifier, generation, lease, authorize, now()
            )
            key, source_hash, mime, purpose = (
                derivative.key,
                derivative.sha256,
                derivative.mime_type,
                row.purpose,
            )
    except (PermissionError, LookupError, ValueError):
        return result("denied")

    def fail(code, *, fatal=False):
        copy_failure(identifier, generation, lease, code, now(), fatal=fatal)
        return result(code)

    try:
        source_store = source_store or get_private_store()
        publication_store = publication_store or get_publication_store()
        scanner = scanner or configured_scanner()
        metadata = source_store.head(key)
        source = source_store.read_limited(key, MAX_PUBLIC_IMAGE_BYTES)
        if (
            not 0 < metadata.size <= MAX_PUBLIC_IMAGE_BYTES
            or metadata.size != len(source)
            or metadata.content_type != mime
            or sha256(source).hexdigest() != source_hash
        ):
            return fail("source_changed", fatal=True)
    except Exception:
        return fail("storage_unavailable")
    try:
        verdict = scanner.scan(source, now())
        if verdict.status != "clean":
            status = (
                verdict.status
                if verdict.status
                in {"malicious", "limit", "unknown", "error", "timeout", "stale"}
                else "unknown"
            )
            return fail("scan_" + status, fatal=status in {"malicious", "limit"})
        if (
            verdict.engine != "ClamAV 1.5.4"
            or not isinstance(verdict.signature, str)
            or not verdict.signature.isdecimal()
            or len(verdict.signature) > 10
            or not isinstance(verdict.expires_at, datetime)
            or not timezone.is_aware(verdict.expires_at)
            or verdict.expires_at <= now()
        ):
            return fail("scan_unknown")
    except Exception:
        return fail("scanner_unavailable")
    image = (sanitize or decode)(source, mime, purpose)
    if image.status != "clean":
        return fail(
            "decode_" + image.status
            if image.status in {"invalid", "timeout", "unavailable"}
            else "decode_unknown",
            fatal=image.status == "invalid",
        )
    if (
        not isinstance(image.data, bytes)
        or not 0 < len(image.data) <= MAX_PUBLIC_IMAGE_BYTES
        or not image.data.startswith(b"\x89PNG\r\n\x1a\n")
        or image.mime_type != "image/png"
        or type(image.width) is not int
        or type(image.height) is not int
        or not 1
        <= image.width
        <= (1600 if purpose in {"cover", "educational_image"} else 512)
        or not 1
        <= image.height
        <= (1600 if purpose in {"cover", "educational_image"} else 512)
    ):
        return fail("decode_invalid", fatal=True)
    digest = sha256(image.data).hexdigest()
    try:
        with transaction.atomic():
            row, attempt, derivative = fenced_copy(
                identifier, generation, lease, authorize, now()
            )
            attempt.sha256, attempt.mime_type = digest, image.mime_type
            attempt.width, attempt.height, attempt.size = (
                image.width,
                image.height,
                len(image.data),
            )
            attempt.scanner_engine, attempt.scanner_signature = (
                verdict.engine,
                verdict.signature,
            )
            attempt.signature_expires_at = verdict.expires_at
            attempt.updated_at = now()
            attempt.save()
            output_key = attempt.key
    except (PermissionError, LookupError, ValueError):
        return result("denied")
    try:
        try:
            publication_store.put(output_key, image.data, image.mime_type)
        except ValueError:
            if (
                publication_store.read_limited(output_key, MAX_PUBLIC_IMAGE_BYTES)
                != image.data
            ):
                raise
        metadata = publication_store.head(output_key)
        output = publication_store.read_limited(output_key, MAX_PUBLIC_IMAGE_BYTES)
        if (
            metadata.size != len(image.data)
            or metadata.content_type != image.mime_type
            or sha256(output).hexdigest() != digest
            or sha256(
                source_store.read_limited(key, MAX_PUBLIC_IMAGE_BYTES)
            ).hexdigest()
            != source_hash
        ):
            return fail("output_mismatch", fatal=True)
    except Exception:
        return fail("storage_unavailable")
    try:
        with transaction.atomic():
            row, attempt, derivative = fenced_copy(
                identifier, generation, lease, authorize, now()
            )
            if attempt.signature_expires_at <= now():
                return result("denied")
            attempt.state, attempt.lease_uuid, attempt.lease_until = "ready", None, None
            attempt.updated_at = now()
            attempt.save()
            row.state = "ready"
            row.version += 1
            row.updated_at = now()
            row.save()
            activate(row, now())
    except (PermissionError, LookupError, ValueError):
        return result("denied")
    return result("ready")


def read_public_copy(identifier, at, *, authorize=None, publication_store=None):
    """Buffer outside locks, then reauthorize exact bytes before returning them."""
    from hashlib import sha256
    from uuid import UUID

    from .contracts import AuthorizedAssetRead, UploadUnavailable
    from .publication_contracts import MAX_PUBLIC_IMAGE_BYTES

    if (
        not isinstance(identifier, UUID)
        or not isinstance(at, datetime)
        or not timezone.is_aware(at)
        or not callable(authorize)
        or transaction.get_connection().in_atomic_block
    ):
        raise AssetNotFound("Publication media unavailable")

    def capture():
        now = max(at, timezone.now())
        hint = (
            PublicAssetCopy.objects.select_related("owner")
            .filter(pk=identifier)
            .first()
        )
        if hint is None:
            raise AssetNotFound("Publication media unavailable")
        User.objects.select_for_update().get(pk=hint.owner_id)
        # Composition takes profile/source locks before this module's copy lock.
        digest = authorize(hint, now)
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise AssetNotFound("Publication media unavailable")
        row = PublicAssetCopy.objects.select_for_update().get(pk=identifier)
        if row.state != "ready" or row.revoked_at or row.version != hint.version:
            raise AssetNotFound("Publication media unavailable")
        attempt = (
            PublicCopyAttempt.objects.select_for_update()
            .filter(
                copy=row,
                generation=row.generation,
                state="ready",
            )
            .first()
        )
        if attempt is None:
            raise AssetNotFound("Publication media unavailable")
        return (
            row.version,
            row.generation,
            attempt.id,
            attempt.key,
            attempt.sha256,
            attempt.mime_type,
            attempt.size,
        )

    with transaction.atomic():
        expected = capture()
    try:
        body = (publication_store or get_publication_store()).read_limited(
            expected[3], MAX_PUBLIC_IMAGE_BYTES
        )
        if len(body) != expected[6] or sha256(body).hexdigest() != expected[4]:
            raise ValueError("Publication output mismatch")
    except Exception:
        raise UploadUnavailable("Publication media unavailable") from None
    with transaction.atomic():
        if capture() != expected:
            raise AssetNotFound("Publication media unavailable")
        return AuthorizedAssetRead(identifier, expected[2], expected[5], body)


def reconcile_public_copy_lifetime(identifier, at, *, authorize=None):
    from uuid import UUID

    if (
        not isinstance(identifier, UUID)
        or not isinstance(at, datetime)
        or not timezone.is_aware(at)
        or not callable(authorize)
    ):
        return "denied"
    with transaction.atomic():
        hint = PublicAssetCopy.objects.filter(pk=identifier).first()
        if hint is None:
            return "denied"
        user = User.objects.select_for_update().get(pk=hint.owner_id)
        valid = authorize(user, hint, max(at, timezone.now()))
        row = PublicAssetCopy.objects.select_for_update().get(pk=identifier)
        if row.state not in {"pending", "running", "ready"}:
            return row.state
        if valid is True:
            return row.state
        if valid is not False:
            return "denied"
        row.state, row.revoked_at = "revoked", max(at, timezone.now())
        row.updated_at = row.revoked_at
        row.version += 1
        row.save()
        for attempt in PublicCopyAttempt.objects.select_for_update().filter(
            copy=row,
            state__in=["pending", "running"],
        ):
            attempt.state, attempt.failure_code = "failed", "authority_lost"
            attempt.lease_uuid = attempt.lease_until = None
            attempt.retired_at = attempt.retired_at or row.updated_at
            attempt.updated_at = row.updated_at
            attempt.save()
        return "revoked"
