from rest_framework import authentication, exceptions  # type: ignore[import-untyped]


class AccountSessionAuthentication(authentication.SessionAuthentication):
    def authenticate(self, request):
        actor = getattr(request._request, "account_actor", None)
        if actor is None:
            return None
        authenticated = super().authenticate(request)
        if authenticated is None:
            raise exceptions.AuthenticationFailed("Authentication required")
        return authenticated
