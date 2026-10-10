"""Native owner routes enforce CSRF, bounds and server-selected redirects."""

from types import SimpleNamespace
from uuid import uuid4

import pytest
from django.template.loader import render_to_string
from django.test import Client, RequestFactory

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "route", ["/athlete/setup/", "/professional/setup/", "/professional/verification/"]
)
def test_native_csrf_precedes_commands_without_session(route):
    response = Client(enforce_csrf_checks=True).post(route, {"action": "create"})
    assert response.status_code == 403
    assert "no-store" in response.headers.get("Cache-Control", "")


@pytest.mark.parametrize(
    "state,control",
    [("pending_upload", 'name="file"'), ("quarantined", "ارسال برای پردازش")],
)
def test_native_upload_uses_existing_service_states(state, control):
    body = render_to_string(
        "professionals/setup.html",
        {
            "profile": SimpleNamespace(id=uuid4(), version=1),
            "asset": SimpleNamespace(
                id=uuid4(), version=3, state=state, purpose="avatar"
            ),
            "can_finalize": True,
        },
    )
    assert control in body and "رها کردن بارگذاری" in body


def owner_post(monkeypatch, data):
    from apps.assets import views as helpers
    from apps.professionals import views

    actor = SimpleNamespace(user_uuid=uuid4())
    profile = SimpleNamespace(version=7, setup_step="credentials")
    monkeypatch.setattr(helpers, "current_actor", lambda *args: actor)
    monkeypatch.setattr(views, "own_professional_profile", lambda *args: profile)
    # RequestFactory requires explicit urlencoding when content_type is supplied.
    from urllib.parse import urlencode

    request = RequestFactory().post(
        "/professional/setup/?step=credentials",
        urlencode(data),
        content_type="application/x-www-form-urlencoded",
    )
    request._dont_enforce_csrf_checks = True
    request.session = {views.session_key(actor, "credential"): str(uuid4())}
    return views, actor, request


def test_native_withdraw_targets_the_displayed_exact_credential(monkeypatch):
    identifier = uuid4()
    views, actor, request = owner_post(
        monkeypatch,
        {
            "action": "credential_withdraw",
            "credential_uuid": str(identifier),
            "expected_version": "1",
            "operation_id": str(uuid4()),
        },
    )
    calls = []
    monkeypatch.setattr(
        views.commands,
        "withdraw_credential",
        lambda actor, target, **kwargs: calls.append(target),
    )
    response = views.setup(request)
    assert response.status_code == 302 and calls == [identifier]


def test_native_new_credential_uses_profile_cas_not_credential_version(monkeypatch):
    views, actor, request = owner_post(
        monkeypatch,
        {
            "action": "credential_create",
            "expected_profile_version": "7",
            "expected_version": "1",
            "operation_id": str(uuid4()),
            "category": "identity",
            "type_code": "document",
            "issuer": "issuer",
            "title": "title",
            "calendar": "gregorian",
        },
    )
    versions = []

    def create(actor, payload, **kwargs):
        versions.append(kwargs["expected_profile_version"])
        return SimpleNamespace(id=uuid4())

    monkeypatch.setattr(views.commands, "create_credential", create)
    response = views.setup(request)
    assert response.status_code == 302 and versions == [7]


def test_native_current_consent_can_revoke_after_session_loss_and_no_repeat_grant():
    body = render_to_string(
        "athletes/baseline.html",
        {
            "baseline": SimpleNamespace(state="draft", optional_access=True),
            "can_revoke": False,
            "storage_seconds": 3600,
        },
    )
    assert "پس‌گرفتن این اجازه" in body
    assert "تأیید نگهداری خصوصی" not in body


def test_native_verification_reprepare_uses_profile_cas(monkeypatch):
    from urllib.parse import urlencode

    from apps.assets import views as helpers
    from apps.professionals import views

    actor = SimpleNamespace(user_uuid=uuid4())
    case = SimpleNamespace(id=uuid4(), version=2, state="draft")
    monkeypatch.setattr(helpers, "current_actor", lambda *args: actor)
    monkeypatch.setattr(
        views, "own_professional_profile", lambda *args: SimpleNamespace(version=7)
    )
    monkeypatch.setattr(views, "own_verification", lambda *args: case)
    request = RequestFactory().post(
        "/professional/verification/",
        urlencode(
            {
                "action": "prepare",
                "expected_version": "2",
                "expected_profile_version": "7",
                "operation_id": str(uuid4()),
                "requested_targets": "identity",
            }
        ),
        content_type="application/x-www-form-urlencoded",
    )
    request._dont_enforce_csrf_checks = True
    request.session = {views.session_key(actor, "verification"): str(case.id)}
    versions = []

    def prepare(actor, targets, **kwargs):
        versions.append(kwargs["expected_profile_version"])
        return case

    monkeypatch.setattr(views.verification, "prepare_verification", prepare)
    response = views.verification_page(request)
    assert response.status_code == 302 and versions == [7]


@pytest.mark.parametrize(
    "route", ["/athlete/setup/", "/professional/setup/", "/professional/preview/"]
)
def test_safe_native_login_redirect(route):
    response = Client().get(
        route,
        {"next": "https://invalid.example/"},
        HTTP_REFERER="https://invalid.example/",
    )
    assert response.status_code == 302 and response.url == "/accounts/entry/"
    assert "no-store" in response.headers.get("Cache-Control", "")
