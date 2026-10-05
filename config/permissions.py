from django.utils import timezone
from rest_framework.permissions import BasePermission  # type: ignore[import-untyped]

from apps.accounts.sessions import actor_user


class AccountActionPermission(BasePermission):
    def has_permission(self, request, view):
        actor = getattr(request._request, "account_actor", None)
        action = getattr(view, "account_action", None)
        if actor is None or not isinstance(action, str):
            return False
        try:
            actor_user(actor, action, timezone.now())
        except PermissionError:
            return False
        return True
