"""Task 4 never authorizes source delivery, including an owner's own bytes."""

from .contracts import AssetNotFound


def authorized_profile_download(actor, asset_uuid, purpose, at, **kwargs):
    # Task 4 has no raw-source delivery capability to authorize. Uniform denial
    # precedes identity/existence checks and all database/storage access.
    raise AssetNotFound("Asset unavailable")
