"""Separate sanitized owner previews and assigned staff evidence delivery."""

from .contracts import AssetNotFound, AuthorizedAssetRead
from .storage import get_private_store


def authorized_profile_download(actor, asset_uuid, purpose, at, **kwargs):
    # Raw/source purposes remain denied before identity, database or storage I/O.
    if purpose != "owner_preview":
        raise AssetNotFound("Asset unavailable")
    from hashlib import sha256
    from uuid import uuid4

    from django.db import transaction
    from django.utils import timezone

    from apps.accounts.contracts import SecurityOutcome
    from apps.accounts.sessions import locked_actor

    from .models import AssetDerivative
    from .policies import owned_asset, validate_context
    from .validation import MAX_BYTES, MEDIA_TYPES, raster_signature

    validate_context(actor, at)
    subject, record, store = (
        kwargs.get(name) for name in ("subject", "record", "store")
    )
    if not all(callable(value) for value in (subject, record, store)):
        raise AssetNotFound("Asset unavailable")
    with transaction.atomic():
        user = locked_actor(actor, "asset.owner_read", max(at, timezone.now()))
        try:
            row = owned_asset(user, asset_uuid, subject)
        except (ValueError, LookupError):
            raise AssetNotFound("Asset unavailable") from None
        if (
            row.purpose not in {"avatar", "cover", "logo"}
            or row.state != "ready"
            or row.revoked_at is not None
        ):
            raise AssetNotFound("Asset unavailable")
        attempt = (
            row.processing_attempts.select_for_update()
            .filter(processing_version=row.processing_version)
            .order_by("-attempt")
            .first()
        )
        if (
            attempt is None
            or attempt.state != "ready"
            or attempt.algorithm_version != "jpeg-png-pixels-v1"
            or attempt.scanner_engine != "ClamAV 1.5.4"
            or not attempt.scanner_signature.isdecimal()
        ):
            raise AssetNotFound("Asset unavailable")
        derivative = (
            AssetDerivative.objects.select_for_update()
            .filter(
                asset=row,
                purpose="owner_preview",
                state="ready",
                processing_version=row.processing_version,
                mime_type__in=MEDIA_TYPES,
            )
            .first()
        )
        if derivative is None:
            raise AssetNotFound("Asset unavailable")
        # An unavailable audit prevents private storage release.
        record(
            SecurityOutcome(
                "asset.read", "succeeded", row.id, uuid4(), (), "user_requested"
            )
        )
        try:
            content = store().read_limited(derivative.key, MAX_BYTES)
            if (
                not isinstance(content, bytes)
                or sha256(content).hexdigest() != derivative.sha256
            ):
                raise AssetNotFound("Asset unavailable")
            raster_signature(content[:8], derivative.mime_type)
        except (FileNotFoundError, ValueError):
            raise AssetNotFound("Asset unavailable") from None
        locked_actor(actor, "asset.owner_read", timezone.now())
        return AuthorizedAssetRead(row.id, derivative.id, derivative.mime_type, content)


def read_evidence_derivative(asset_uuid):
    """Internal call after assigned case authority, binding checks and audit."""
    from hashlib import sha256

    from django.db import connection
    from django.db.models import F

    from .models import AssetDerivative

    if not connection.in_atomic_block:
        raise RuntimeError("Evidence delivery requires assigned transaction")
    derivative = (
        AssetDerivative.objects.select_for_update()
        .filter(
            asset_id=asset_uuid,
            asset__state="ready",
            asset__revoked_at__isnull=True,
            processing_version=F("asset__processing_version"),
            purpose="evidence_preview",
            state="ready",
            mime_type__in=["image/jpeg", "image/png"],
        )
        .first()
    )
    if derivative is None:
        raise AssetNotFound("Asset unavailable")
    content = get_private_store().read_limited(derivative.key, 10_000_000)
    if (
        not isinstance(content, bytes)
        or sha256(content).hexdigest() != derivative.sha256
    ):
        raise AssetNotFound("Asset unavailable")
    return AuthorizedAssetRead(asset_uuid, derivative.id, derivative.mime_type, content)
