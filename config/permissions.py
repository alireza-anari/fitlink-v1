from django.db import DatabaseError
from django.utils import timezone
from rest_framework import exceptions, permissions  # type: ignore[import-untyped]

from apps.accounts.sessions import actor_user


class AccountUnavailable(exceptions.APIException):
    status_code = 503
    default_detail = {"status": "unavailable"}
    default_code = "unavailable"


class AccountActionPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        actor = getattr(request._request, "account_actor", None)
        action = getattr(view, "account_action", None)
        if actor is None or not isinstance(action, str):
            return False
        try:
            actor_user(actor, action, timezone.now())
        except PermissionError:
            return False
        except DatabaseError:
            raise AccountUnavailable() from None
        return True
