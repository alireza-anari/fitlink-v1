from dataclasses import replace

from django.conf import settings
from django.test import Client
from test_recovery_authorization import owner


def enabled(settings):
    settings.ACCOUNT_SECURITY = replace(
        settings.ACCOUNT_SECURITY, entry_enabled=True, staff_recovery_enabled=True
    )


def browser(user=None):
    user = user or owner()
    from django.db import transaction
    from django.utils import timezone
    from test_otp_issue import record
    from test_sessions import request_with_session

    from apps.accounts.sessions import issue_session, resolve_session, session_scope

    request = request_with_session()
    with transaction.atomic():
        issue_session(request, user, session_scope(user), timezone.now(), record)
    actor = resolve_session(request, timezone.now())
    client = Client(enforce_csrf_checks=True)
    client.cookies[settings.SESSION_COOKIE_NAME] = request.session.session_key
    token = bootstrap(client)
    return client, token, user, actor


def bootstrap(client):
    response = client.get("/accounts/entry/")
    assert response.status_code == 200
    assert response["Cache-Control"] == "no-store"
    return client.cookies[settings.CSRF_COOKIE_NAME].value


def post(client, token, path, data):
    return client.post(
        path, data, content_type="application/json", HTTP_X_CSRFTOKEN=token
    )
