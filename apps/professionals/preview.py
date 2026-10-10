"""Fail-closed private preview boundary pending observed hosted behavior."""

from django.db import transaction

from apps.accounts.sessions import locked_actor

from .contracts import ProfileNotFound
from .policies import validate_context
from .setup import locked_profile


def owner_preview(actor, at):
    validate_context(actor, at)
    with transaction.atomic():
        user = locked_actor(actor, "professional.profile_read", at)
        locked_profile(user)
        raise ProfileNotFound("Preview unavailable")
