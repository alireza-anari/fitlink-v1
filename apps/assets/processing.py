"""Durable private processing. Transactions contain metadata, never long I/O."""

from datetime import timedelta
from hashlib import sha256
from io import BytesIO
from uuid import UUID, uuid4

from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.accounts.models import User
from apps.accounts.policies import require_account_action

from .images import sanitize
from .models import Asset, AssetDerivative, AssetProcessingAttempt
from .scanner import configured_scanner
from .storage import get_private_store

MAX_ATTEMPTS = 8
LEASE_SECONDS = 60
RETRY_SECONDS = 300


def request_processing(event, at):
    row = Asset.objects.filter(
        pk=event.aggregate_uuid,
        processing_version=event.aggregate_version,
        owner__public_id=event.payload["user_uuid"],
        state="quarantined",
    ).first()
    if row is None:
        return "skipped"
    AssetProcessingAttempt.objects.get_or_create(
        asset=row,
        processing_version=row.processing_version,
        attempt=1,
    )
    return "applied"


def _locked(asset_id, authority, at):
    hint = Asset.objects.filter(pk=asset_id).first()
    if hint is None or authority is None:
        return None
    user = User.objects.select_for_update().get(pk=hint.owner_id)
    require_account_action(user, "asset.owner_write", "normal")
    # Composition locks subject parents before Asset. User serializes commands.
    digest = authority(user, hint, at)
    asset = Asset.objects.select_for_update().get(pk=asset_id)
    if (
        asset.owner_id != user.pk
        or asset.revoked_at
        or asset.state not in {"quarantined", "processing"}
    ):
        return None
    return user, asset, digest


def _fenced(asset_id, pv, lease, authority, at):
    locked = _locked(asset_id, authority, at)
    if locked is None:
        return None
    user, asset, digest = locked
    attempt = (
        AssetProcessingAttempt.objects.select_for_update()
        .filter(
            asset=asset,
            processing_version=pv,
            lease_uuid=lease,
            state="running",
            lease_until__gt=at,
        )
        .first()
    )
    if (
        attempt is None
        or asset.processing_version != pv
        or attempt.owner_auth_version != user.auth_version
        or attempt.asset_version != asset.version
        or attempt.authority_hash != digest
    ):
        return None
    return asset, attempt


def _enqueue(asset_id, pv, lease):
    from .tasks import process_private_asset

    process_private_asset.apply_async(args=[str(asset_id), pv, str(lease)], retry=False)


def _retire(attempt, code):
    attempt.state, attempt.failure_code = "failed", code
    attempt.lease_uuid = attempt.lease_until = None
    attempt.save()


def scan_due_assets(at, batch_size=100, *, enqueue=None, authority=None):
    if type(batch_size) is not int or not 1 <= batch_size <= 100 or authority is None:
        return 0
    enqueue = enqueue or _enqueue
    due = (
        AssetProcessingAttempt.objects.filter(
            state__in=["pending", "running"],
        )
        .filter(Q(lease_until__isnull=True) | Q(lease_until__lte=at))
        .order_by("created_at", "id")
    )
    ids = list(due.values_list("asset_id", flat=True).distinct()[:batch_size])
    count = 0
    for asset_id in ids:
        try:
            with transaction.atomic():
                locked = _locked(asset_id, authority, at)
                if locked is None:
                    continue
                user, asset, digest = locked
                attempt = (
                    AssetProcessingAttempt.objects.select_for_update()
                    .filter(
                        asset=asset,
                        processing_version=asset.processing_version,
                    )
                    .order_by("-attempt")
                    .first()
                )
                if attempt is None or attempt.state not in {"pending", "running"}:
                    continue
                if attempt.lease_until and attempt.lease_until > at:
                    continue
                if attempt.state == "running":
                    _retire(attempt, "lease_expired")
                    if attempt.attempt >= MAX_ATTEMPTS:
                        asset.state, asset.rejection_code = "rejected", "exhausted"
                        asset.version += 1
                        asset.save()
                        continue
                    attempt = AssetProcessingAttempt.objects.create(
                        asset=asset,
                        processing_version=asset.processing_version,
                        attempt=attempt.attempt + 1,
                    )
                if attempt.attempt > MAX_ATTEMPTS:
                    _retire(attempt, "exhausted")
                    asset.state, asset.rejection_code = "rejected", "exhausted"
                    asset.version += 1
                    asset.save()
                    continue
                asset.state = "processing"
                asset.version += 1
                asset.save()
                attempt.state, attempt.failure_code = "running", ""
                attempt.lease_uuid = uuid4()
                attempt.lease_until = at + timedelta(seconds=LEASE_SECONDS)
                attempt.owner_auth_version = user.auth_version
                attempt.asset_version, attempt.authority_hash = asset.version, digest
                attempt.save()
                lease, pv = attempt.lease_uuid, asset.processing_version
        except (PermissionError, ValueError, LookupError):
            continue
        count += 1
        try:
            enqueue(asset_id, pv, lease)
        except Exception:
            # A broker may have accepted before its reply was lost. Fence that
            # old message by replacing its lease before retry; no exception text.
            with transaction.atomic():
                attempt = (
                    AssetProcessingAttempt.objects.select_for_update()
                    .filter(
                        asset_id=asset_id,
                        processing_version=pv,
                        state="running",
                        lease_uuid=lease,
                    )
                    .first()
                )
                if attempt:
                    attempt.state, attempt.failure_code = (
                        "pending",
                        "broker_unavailable",
                    )
                    attempt.lease_uuid = uuid4()
                    attempt.lease_until = at + timedelta(seconds=RETRY_SECONDS)
                    attempt.save()
    return count


def _failure(asset_id, pv, lease, code, at, *, fatal=False):
    # Lease ownership alone permits recording failure, never permits release.
    with transaction.atomic():
        asset = Asset.objects.select_for_update().filter(pk=asset_id).first()
        if asset is None or asset.processing_version != pv:
            return "denied"
        attempt = (
            AssetProcessingAttempt.objects.select_for_update()
            .filter(
                asset=asset,
                processing_version=pv,
                state="running",
                lease_uuid=lease,
            )
            .first()
        )
        if attempt is None:
            return "denied"
        number = attempt.attempt
        _retire(attempt, code)
        if asset.revoked_at or asset.state not in {"quarantined", "processing"}:
            return "denied"
        if fatal or number >= MAX_ATTEMPTS:
            asset.state = "rejected"
            asset.rejection_code = code if fatal else "exhausted"
        else:
            asset.state = "quarantined"
            AssetProcessingAttempt.objects.get_or_create(
                asset=asset,
                processing_version=pv,
                attempt=number + 1,
                defaults={
                    "lease_uuid": uuid4(),
                    "lease_until": at + timedelta(seconds=RETRY_SECONDS),
                },
            )
        asset.version += 1
        asset.save()
    return code


def process_asset(
    asset_uuid,
    processing_version,
    lease_uuid,
    at,
    *,
    store=None,
    scanner=None,
    authority=None,
):
    if (
        not isinstance(asset_uuid, UUID)
        or not isinstance(lease_uuid, UUID)
        or type(processing_version) is not int
        or processing_version < 1
        or authority is None
    ):
        return "denied"
    # Tests supply explicit private boundaries. Unconfigured runtime remains shut.
    if (store is None or scanner is None) and not settings.ASSET_PROCESSING_ENABLED:
        return "unavailable"
    pv, lease = processing_version, lease_uuid

    def now():
        return max(at, timezone.now())

    try:
        with transaction.atomic():
            fenced = _fenced(asset_uuid, pv, lease, authority, now())
            if fenced is None:
                return "denied"
            asset, attempt = fenced
            key, size, mime, source_hash, purpose = (
                asset.source_key,
                asset.actual_size,
                asset.detected_type,
                asset.sha256,
                asset.purpose,
            )
    except (PermissionError, ValueError, LookupError):
        return "denied"
    try:
        store = store or get_private_store()
        scanner = scanner or configured_scanner()
        metadata = store.head(key)
        source = store.read_limited(key, 10_000_000)
        if (
            size is None
            or metadata.size != size
            or metadata.content_type != mime
            or len(source) != size
            or sha256(source).hexdigest() != source_hash
        ):
            return _failure(asset_uuid, pv, lease, "source_changed", now(), fatal=True)
    except Exception:
        return _failure(asset_uuid, pv, lease, "storage_unavailable", now())
    try:
        verdict = scanner.scan(source, now())
        if verdict.status != "clean":
            code = (
                verdict.status
                if verdict.status
                in {"malicious", "limit", "unknown", "error", "timeout", "stale"}
                else "unknown"
            )
            return _failure(
                asset_uuid,
                pv,
                lease,
                "scan_" + code,
                now(),
                fatal=code in {"malicious", "limit"},
            )
        if (
            verdict.engine != "ClamAV 1.5.4"
            or not verdict.signature.isdecimal()
            or len(verdict.signature) > 10
        ):
            return _failure(asset_uuid, pv, lease, "scan_unknown", now())
    except Exception:
        return _failure(asset_uuid, pv, lease, "scanner_unavailable", now())
    image = sanitize(source, mime, purpose)
    if image.status != "clean":
        return _failure(
            asset_uuid,
            pv,
            lease,
            "decode_" + image.status,
            now(),
            fatal=image.status == "invalid",
        )
    digest = sha256(image.data).hexdigest()
    derivative_purpose = (
        "evidence_preview" if purpose.endswith("evidence") else "owner_preview"
    )
    try:
        with transaction.atomic():
            fenced = _fenced(asset_uuid, pv, lease, authority, now())
            if fenced is None:
                return "denied"
            asset, attempt = fenced
            derivative, _ = AssetDerivative.objects.get_or_create(
                asset=asset,
                processing_version=pv,
                purpose=derivative_purpose,
                defaults={
                    "key": f"derivatives/{uuid4()}.png",
                    "sha256": digest,
                    "width": image.width,
                    "height": image.height,
                    "mime_type": image.mime_type,
                },
            )
            if (
                derivative.state != "pending"
                or derivative.sha256 != digest
                or derivative.width != image.width
                or derivative.height != image.height
                or derivative.mime_type != image.mime_type
            ):
                return "denied"
        # Inventory commits before write. Crash leftovers remain private, tracked
        # and reusable only if exact bytes match; never overwrite or delete them.
        try:
            store.put_stream(
                derivative.key, BytesIO(image.data), image.mime_type, 10_000_000
            )
        except ValueError:
            if store.read_limited(derivative.key, 10_000_000) != image.data:
                raise ValueError("Private derivative mismatch") from None
        if (
            store.head(derivative.key).content_type != image.mime_type
            or store.read_limited(derivative.key, 10_000_000) != image.data
            or sha256(store.read_limited(key, 10_000_000)).hexdigest() != source_hash
        ):
            return _failure(asset_uuid, pv, lease, "storage_changed", now(), fatal=True)
        with transaction.atomic():
            fenced = _fenced(asset_uuid, pv, lease, authority, now())
            if fenced is None:
                return "denied"
            asset, attempt = fenced
            if verdict.expires_at is not None and verdict.expires_at <= now():
                return "denied"
            derivative = AssetDerivative.objects.select_for_update().get(
                pk=derivative.pk
            )
            if derivative.state != "pending":
                return "denied"
            derivative.state, derivative.version = "ready", derivative.version + 1
            derivative.save()
            attempt.state = "ready"
            attempt.lease_uuid = attempt.lease_until = None
            attempt.scanner_engine, attempt.scanner_signature = (
                verdict.engine,
                verdict.signature,
            )
            attempt.save()
            asset.state, asset.rejection_code = "ready", ""
            asset.version += 1
            asset.save()
        return "ready"
    except (PermissionError, ValueError, LookupError):
        return _failure(asset_uuid, pv, lease, "release_denied", now())
    except Exception:
        return _failure(asset_uuid, pv, lease, "storage_unavailable", now())
