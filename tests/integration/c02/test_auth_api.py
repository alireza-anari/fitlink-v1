from uuid import uuid4

import pytest
from api_helpers import bootstrap, browser, enabled, post
from django.apps import apps
from django.conf import settings as django_settings
from django.test import Client
from django.utils import timezone
from test_recovery_authorization import owner

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def test_real_http_otp_login_rotates_csrf_and_issues_only_session(
    settings, monkeypatch, limiter
):
    enabled(settings)
    from apps.accounts.sms import MockSmsProvider
    from config.use_cases import identity

    provider = MockSmsProvider()
    monkeypatch.setattr(identity, "configured_provider", lambda: provider)
    client = Client(enforce_csrf_checks=True)
    token = bootstrap(client)
    requested = post(
        client, token, "/api/v1/auth/otp/request/", {"phone": "۰۹۱۲۳۴۵۶۷۸۹"}
    )
    assert requested.status_code == 200
    data = requested.json()
    assert set(data) == {"status", "challenge_id", "resend_after_seconds"}
    code = provider.drain()[0].code
    verified = post(
        client,
        token,
        "/api/v1/auth/otp/verify/",
        {
            "phone": "09123456789",
            "challenge_id": data["challenge_id"],
            "code": code,
            "birth_date": "1990-01-01",
            "calendar": "gregorian",
            "adult_attested": True,
        },
    )
    assert verified.status_code == 200
    assert set(verified.json()) == {"status", "account_uuid", "scope"}
    assert django_settings.SESSION_COOKIE_NAME in verified.cookies
    assert client.cookies[django_settings.CSRF_COOKIE_NAME].value != token
    assert client.get("/api/v1/account/me/").status_code == 200
    assert verified["Cache-Control"] == "no-store"


@pytest.mark.parametrize("defect", ["version", "revoked", "suspended"])
def test_current_server_state_denies_stale_cookie(defect):
    client, _, user, actor = browser()
    if defect == "version":
        type(user).objects.filter(pk=user.pk).update(auth_version=2)
    elif defect == "revoked":
        apps.get_model("accounts", "AccountSessionControl").objects.filter(
            pk=actor.control_id
        ).update(revoked_at=timezone.now())
    else:
        type(user).objects.filter(pk=user.pk).update(state="suspended", is_active=False)
    response = client.get("/api/v1/account/me/")
    assert response.status_code == 403
    assert response["Cache-Control"] == "no-store"


def test_owned_preferences_reject_authority_and_other_users():
    client, token, user, _ = browser()
    other = owner("+989123456780")
    response = client.patch(
        "/api/v1/account/me/",
        {"locale": "en", "timezone": "UTC"},
        content_type="application/json",
        HTTP_X_CSRFTOKEN=token,
    )
    assert response.status_code == 200
    user.refresh_from_db()
    other.refresh_from_db()
    assert user.locale == "en" and other.locale == "fa"
    for data in (
        {"is_staff": True},
        {"user_uuid": str(other.public_id)},
        {"phone": other.phone},
    ):
        assert (
            client.patch(
                "/api/v1/account/me/",
                data,
                content_type="application/json",
                HTTP_X_CSRFTOKEN=token,
            ).status_code
            == 400
        )
    assert set(client.get("/api/v1/account/me/").json()) == {
        "account_uuid",
        "state",
        "scope",
        "locale",
        "timezone",
    }
    assert client.get(f"/api/v1/account/{other.public_id}/").status_code == 404


def test_control_only_account_can_read_and_logout_but_cannot_change_phone():
    user = owner()
    type(user).objects.filter(pk=user.pk).update(state="restricted")
    user.refresh_from_db()
    client, token, _, _ = browser(user)
    assert client.get("/api/v1/account/me/").status_code == 200
    assert (
        post(
            client, token, "/api/v1/account/phone-change/", {"new_phone": "09123456780"}
        ).status_code
        == 403
    )
    assert post(client, token, "/api/v1/auth/logout/", {}).status_code == 200
    assert client.get("/api/v1/account/me/").status_code == 403


def test_cross_user_phone_intent_denied_before_proof_or_conflict():
    from config.use_cases.identity import begin_phone_change

    _, _, _, other_actor = browser()
    change = begin_phone_change(other_actor, "09123456780", timezone.now())
    client, token, _, _ = browser(owner("+989123456781"))
    for suffix, data in (
        ("proof/request/", {"kind": "old"}),
        (
            "proof/verify/",
            {"kind": "old", "challenge_id": str(uuid4()), "code": "123456"},
        ),
        ("apply/", {}),
    ):
        response = post(
            client,
            token,
            "/api/v1/account/phone-change/" + suffix,
            {"change_uuid": str(change), **data},
        )
        assert response.status_code == 404


def test_dual_phone_proof_http_apply_invalidates_old_session(
    settings, monkeypatch, limiter
):
    enabled(settings)
    from apps.accounts.sms import MockSmsProvider
    from config.use_cases import identity

    provider = MockSmsProvider()
    monkeypatch.setattr(identity, "configured_provider", lambda: provider)
    client, token, user, _ = browser()
    base = "/api/v1/account/phone-change/"
    begun = post(client, token, base, {"new_phone": "09123456780"})
    assert begun.status_code == 201
    change = begun.json()["change_uuid"]
    for kind in ("old", "new"):
        requested = post(
            client,
            token,
            base + "proof/request/",
            {"change_uuid": change, "kind": kind},
        )
        assert requested.status_code == 200
        code = provider.drain()[0].code
        assert (
            post(
                client,
                token,
                base + "proof/verify/",
                {
                    "change_uuid": change,
                    "kind": kind,
                    "challenge_id": requested.json()["challenge_id"],
                    "code": code,
                },
            ).status_code
            == 200
        )
    assert (
        post(client, token, base + "apply/", {"change_uuid": change}).status_code == 200
    )
    user.refresh_from_db()
    assert user.phone == "+989123456780"
    assert client.get("/api/v1/account/me/").status_code == 403


@pytest.mark.parametrize("failure", ["audit", "session_save"])
def test_http_login_failure_never_emits_authenticated_cookie(
    settings, monkeypatch, limiter, failure
):
    enabled(settings)
    from django.contrib.sessions.backends.db import SessionStore
    from django.db import DatabaseError

    from apps.accounts.sms import MockSmsProvider
    from config.use_cases import identity

    provider = MockSmsProvider()
    monkeypatch.setattr(identity, "configured_provider", lambda: provider)
    client = Client(enforce_csrf_checks=True)
    token = bootstrap(client)
    requested = post(
        client, token, "/api/v1/auth/otp/request/", {"phone": "09123456789"}
    )
    code = provider.drain()[0].code
    if failure == "audit":
        original = identity.record_security_outcome

        def fail(outcome, **kwargs):
            if outcome.action == "account.login":
                raise DatabaseError("synthetic audit failure")
            return original(outcome, **kwargs)

        monkeypatch.setattr(identity, "record_security_outcome", fail)
    else:
        original_save = SessionStore.save

        def failed_save(self, *args, **kwargs):
            if self.get("_auth_user_id"):
                raise DatabaseError("synthetic session failure")
            return original_save(self, *args, **kwargs)

        monkeypatch.setattr(SessionStore, "save", failed_save)
    response = post(
        client,
        token,
        "/api/v1/auth/otp/verify/",
        {
            "phone": "09123456789",
            "challenge_id": requested.json()["challenge_id"],
            "code": code,
            "birth_date": "1990-01-01",
            "calendar": "gregorian",
            "adult_attested": True,
        },
    )
    assert response.status_code == 503
    assert django_settings.SESSION_COOKIE_NAME not in response.cookies
    assert not apps.get_model("accounts", "User").objects.exists()
    assert not apps.get_model("accounts", "AccountSessionControl").objects.exists()
    assert client.get("/api/v1/account/me/").status_code == 403


def test_unknown_and_existing_phone_errors_have_uniform_http_shape(
    settings, monkeypatch, limiter
):
    enabled(settings)
    from apps.accounts.sms import MockSmsProvider
    from config.use_cases import identity

    owner()
    provider = MockSmsProvider()
    monkeypatch.setattr(identity, "configured_provider", lambda: provider)
    shapes = []
    for phone in ("09123456789", "09123456781"):
        client = Client(enforce_csrf_checks=True)
        token = bootstrap(client)
        request = post(client, token, "/api/v1/auth/otp/request/", {"phone": phone})
        assert request.status_code == 200
        issued = provider.drain()[0].code
        wrong = "000000" if issued != "000000" else "111111"
        response = post(
            client,
            token,
            "/api/v1/auth/otp/verify/",
            {
                "phone": phone,
                "challenge_id": request.json()["challenge_id"],
                "code": wrong,
            },
        )
        assert django_settings.SESSION_COOKIE_NAME not in response.cookies
        shapes.append(
            (
                response.status_code,
                response.json(),
                response["Cache-Control"],
                response["Content-Type"],
            )
        )
    assert (
        shapes[0]
        == shapes[1]
        == (400, {"status": "invalid"}, "no-store", "application/json")
    )


@pytest.mark.parametrize("route,other_status", [("logout", 200), ("logout-all", 403)])
def test_http_logout_scope_revokes_exact_current_or_all_controls(route, other_status):
    client, token, user, _ = browser()
    other, _, _, _ = browser(user)
    response = post(client, token, f"/api/v1/auth/{route}/", {})
    assert response.status_code == 200
    assert client.get("/api/v1/account/me/").status_code == 403
    assert other.get("/api/v1/account/me/").status_code == other_status
