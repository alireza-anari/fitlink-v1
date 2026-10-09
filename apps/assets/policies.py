"""Fresh account authority and exact owned asset lookup."""

from datetime import datetime
from uuid import UUID

from django.utils import timezone

from apps.accounts.sessions import AccountActor

from .contracts import AssetNotFound
from .models import Asset


def validate_context(actor: AccountActor, at: datetime) -> None:
    if not isinstance(at, datetime) or not timezone.is_aware(at):
        raise ValueError("Invalid upload time")
    if (
        not isinstance(actor, AccountActor)
        or not isinstance(actor.user_uuid, UUID)
        or not isinstance(actor.control_id, UUID)
        or type(actor.auth_version) is not int
        or actor.auth_version < 1
        or not isinstance(actor.authenticated_at, datetime)
        or not timezone.is_aware(actor.authenticated_at)
        or actor.authenticated_at > at
    ):
        raise PermissionError("Account action denied")


def owned_asset(user, identifier, subject) -> Asset:
    if not isinstance(identifier, UUID):
        raise AssetNotFound("Asset unavailable")
    candidate = Asset.objects.filter(pk=identifier, owner=user).first()
    if candidate is None:
        raise AssetNotFound("Asset unavailable")
    # Owner -> profile/credential -> asset, before revealing state/version.
    binding = subject(user, candidate.purpose, candidate.subject_uuid)
    row = Asset.objects.select_for_update().filter(pk=identifier, owner=user).first()
    if (
        row is None
        or row.subject_kind != binding.kind
        or row.subject_uuid != binding.id
        or row.purpose != candidate.purpose
        or row.classification != "private_source"
    ):
        raise AssetNotFound("Asset unavailable")
    return row
