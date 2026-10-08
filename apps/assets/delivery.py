"""Task 4 never authorizes source delivery, including an owner's own bytes."""

from django.db import transaction

from apps.accounts.sessions import locked_actor

from .contracts import AssetNotFound
from .policies import validate_context


def authorized_profile_download(actor, asset_uuid, purpose, at, **kwargs):
    validate_context(actor, at)
    with transaction.atomic():
        locked_actor(actor, "asset.owner_read", at)
    raise AssetNotFound("Asset unavailable")
