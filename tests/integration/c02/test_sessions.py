import importlib
import importlib.util
from datetime import date

import pytest
from django.apps import apps
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.test import RequestFactory
from django.utils import timezone
from test_otp_consume import PHONE, sent
from test_otp_issue import record

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def service():
    assert importlib.util.find_spec("apps.accounts.sessions"), (
        "missing versioned database session controls"
    )
    return importlib.import_module("apps.accounts.sessions")


def request_with_session(key=None):
    request = RequestFactory().post("/api/v1/accounts/logout/")
    request.session = SessionStore(session_key=key)
    request.user = AnonymousUser()
    return request


def login(limiter, user=None):
    service()
    from config.use_cases.identity import verify_login_otp

    request = request_with_session()
    request.session["anonymous"] = True
    request.session.save()
    old = request.session.session_key
    now = timezone.now()
    challenge, code = sent(now)
    result = verify_login_otp(
        request,
        PHONE,
        challenge,
        code,
        "127.0.0.1",
        birth_date=date(1990, 1, 1),
        adult_attested=True,
    )
    assert result.valid
    return request, old


def test_fixation_rotates_key_and_payload_has_no_roles(limiter):
    request, old = login(limiter)
    assert (
        request.session.session_key != old
        and not Session.objects.filter(pk=old).exists()
    )
    assert service().resolve_session(request, timezone.now()) is not None
    assert service().resolve_session(request_with_session(old), timezone.now()) is None
    payload = request.session.load()
    assert payload["fitlink_auth_version"] == 1 and payload["fitlink_scope"] == "normal"
    assert not {"role", "capability", "code", "otp"} & payload.keys()
    row = apps.get_model("accounts", "AccountSessionControl").objects.get()
    assert request.session.session_key not in row.session_digest


@pytest.mark.parametrize("failure", ["missing", "revoked", "version", "scope"])
def test_missing_stale_or_revoked_control_denies(limiter, failure):
    request, _ = login(limiter)
    model = apps.get_model("accounts", "AccountSessionControl")
    if failure == "missing":
        model.objects.all().delete()
    elif failure == "revoked":
        model.objects.update(revoked_at=timezone.now())
    elif failure == "version":
        apps.get_model("accounts", "User").objects.update(auth_version=2)
    else:
        request.session["fitlink_scope"] = "account_control"
        request.session.save()
    assert service().resolve_session(request, timezone.now()) is None


@pytest.mark.parametrize("scope", ["current", "all"])
def test_single_and_global_logout_synchronous(limiter, scope):
    request, _ = login(limiter)
    actor = service().resolve_session(request, timezone.now())
    user = apps.get_model("accounts", "User").objects.get(public_id=actor.user_uuid)
    other = request_with_session()
    from django.db import transaction

    with transaction.atomic():
        locked = (
            apps.get_model("accounts", "User")
            .objects.select_for_update()
            .get(pk=user.pk)
        )
        service().issue_session(other, locked, "normal", timezone.now(), record)
    service().revoke_sessions(
        user, scope, timezone.now(), record, control_id=actor.control_id
    )
    assert (service().resolve_session(other, timezone.now()) is not None) is (
        scope == "current"
    )
    assert service().resolve_session(request, timezone.now()) is None
    user.refresh_from_db()
    assert user.auth_version == (2 if scope == "all" else 1)


def test_audit_failure_rolls_back_session_and_clears_request(limiter):
    service()
    from config.use_cases import identity

    request = request_with_session()
    challenge, code = sent(timezone.now())

    def failed(outcome, **kwargs):
        if outcome.action == "account.login":
            raise RuntimeError("audit unavailable")
        original(outcome, **kwargs)

    original = identity.record_security_outcome
    identity.record_security_outcome = failed
    try:
        with pytest.raises(RuntimeError):
            identity.verify_login_otp(
                request,
                PHONE,
                challenge,
                code,
                "127.0.0.1",
                birth_date=date(1990, 1, 1),
                adult_attested=True,
            )
    finally:
        identity.record_security_outcome = original
    assert not request.session.session_key and not request.user.is_authenticated
    assert not apps.get_model("accounts", "User").objects.exists()
    assert not apps.get_model("accounts", "AccountSessionControl").objects.exists()


def test_cross_user_selectors_deny_detail_list_and_count(limiter):
    service()
    from apps.accounts import selectors

    request, _ = login(limiter)
    actor = service().resolve_session(request, timezone.now())
    stranger = apps.get_model("accounts", "User").objects.create_user("+989123456788")
    assert selectors.visible_account(actor, stranger.public_id) is None
    assert list(
        selectors.visible_accounts(actor).values_list("public_id", flat=True)
    ) == [actor.user_uuid]
    assert selectors.visible_accounts(actor).count() == 1


def test_real_cookie_csrf_and_database_failure_closed(limiter):
    service()
    from config.permissions import AccountActionPermission
    from django.conf import settings
    from django.db import OperationalError, connection
    from django.middleware.csrf import get_token
    from django.test import Client, override_settings
    from django.urls import path
    from rest_framework.response import Response
    from rest_framework.views import APIView

    from config.health import liveness

    class Protected(APIView):
        permission_classes = [AccountActionPermission]
        account_action = "account.self"

        def get(self, request):
            return Response({"status": "ok"})

        def post(self, request):
            return Response({"status": "ok"})

    global urlpatterns
    urlpatterns = [
        path("protected/", Protected.as_view()),
        path("health/live/", liveness),
    ]
    request, _ = login(limiter)
    client = Client(enforce_csrf_checks=True)
    client.cookies[settings.SESSION_COOKIE_NAME] = request.session.session_key
    with override_settings(ROOT_URLCONF=__name__):
        assert client.get("/protected/").status_code == 200
        assert client.post("/protected/").status_code == 403
        token = get_token(request)
        client.cookies[settings.CSRF_COOKIE_NAME] = request.META["CSRF_COOKIE"]
        assert client.post("/protected/", HTTP_X_CSRFTOKEN=token).status_code == 200

        def outage(execute, sql, params, many, context):
            raise OperationalError("private database failure")

        with connection.execute_wrapper(outage):
            response = client.get("/protected/")
            assert response.status_code == 503 and response.json() == {
                "status": "unavailable"
            }
            assert client.get("/health/live/").status_code == 200
