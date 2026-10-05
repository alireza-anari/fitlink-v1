"""Current account resolution after Django's authentication middleware."""

from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.db import SessionStore
from django.db import DatabaseError
from django.http import JsonResponse
from django.utils import timezone

from apps.accounts.sessions import actor_user, resolve_session

PUBLIC_FOUNDATION_PATHS = frozenset(
    {"/", "/health/live/", "/health/ready/", "/api/v1/status/"}
)


class AccountMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.account_actor = None
        if request.path in PUBLIC_FOUNDATION_PATHS:
            return self.get_response(request)
        try:
            at = timezone.now()
            actor = resolve_session(request, at)
            request.user = (
                actor_user(actor, "account.self", at) if actor else AnonymousUser()
            )
            request.account_actor = actor
        except PermissionError:
            request.user = AnonymousUser()
        except DatabaseError:
            request.user = AnonymousUser()
            request.session = SessionStore()
            response = JsonResponse({"status": "unavailable"}, status=503)
            response["Cache-Control"] = "no-store"
            return response
        return self.get_response(request)
