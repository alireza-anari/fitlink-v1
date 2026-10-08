"""Owner UUID lookup cannot confer account or professional authority."""

from datetime import datetime
from uuid import UUID

from django.utils import timezone

from apps.accounts.models import User
from apps.accounts.sessions import AccountActor

from .contracts import ProfileNotFound
from .models import AthleteProfile


def validate_context(actor: AccountActor, at: datetime) -> None:
    if not isinstance(at, datetime) or not timezone.is_aware(at):
        raise ValueError("Invalid profile command time")
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


def owned_profile(
    user: User, profile_uuid: UUID, *, lock: bool = False
) -> AthleteProfile:
    if not isinstance(profile_uuid, UUID):
        raise ProfileNotFound("Profile unavailable")
    query = AthleteProfile.objects.all()
    if lock:
        query = query.select_for_update()
    row = query.filter(pk=profile_uuid, user=user).exclude(status="archived").first()
    if row is None:
        raise ProfileNotFound("Profile unavailable")
    return row
