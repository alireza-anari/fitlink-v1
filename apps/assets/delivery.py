"""Task 4 never authorizes source delivery, including an owner's own bytes."""

from .contracts import AssetNotFound, AuthorizedAssetRead
from .storage import get_private_store


def authorized_profile_download(actor, asset_uuid, purpose, at, **kwargs):
    # Task 4 has no raw-source delivery capability to authorize. Uniform denial
    # precedes identity/existence checks and all database/storage access.
    raise AssetNotFound("Asset unavailable")


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
