from datetime import timedelta
from types import SimpleNamespace
from urllib.parse import urlencode

import pytest
from django.test import Client, RequestFactory
from django.utils import timezone

pytestmark = pytest.mark.unit


def test_limiter_outage_api_is_generic_503(monkeypatch):
    from apps.accounts.limiter import LimiterUnavailable
    from config.use_cases import identity

    def unavailable(*args):
        raise LimiterUnavailable("private backend details")

    monkeypatch.setattr(identity, "request_login_otp", unavailable)
    response = Client().post(
        "/api/v1/auth/otp/request/",
        {"phone": "09123456789"},
        content_type="application/json",
    )
    assert response.status_code == 503
    assert response.json() == {"status": "unavailable"}
    assert response["Cache-Control"] == "no-store"


def test_limiter_outage_native_keeps_generic_retry_form(monkeypatch):
    from apps.accounts import views
    from apps.accounts.limiter import LimiterUnavailable

    monkeypatch.setattr(views.entry, "professional_entry_available", lambda: False)

    def unavailable(*args):
        raise LimiterUnavailable("private backend details")

    monkeypatch.setattr(views.identity, "request_login_otp", unavailable)
    response = Client().post(
        "/accounts/entry/",
        urlencode(
            {
                "phone": "09123456789",
                "calendar": "gregorian",
                "birth_date": "1990-01-01",
                "adult_attested": "on",
                "entry_hint": "athlete",
            }
        ),
        content_type="application/x-www-form-urlencoded",
    )
    assert response.status_code == 200
    assert "کمی بعد دوباره تلاش کنید" in response.content.decode()
    assert b"private backend details" not in response.content
    assert response["Cache-Control"] == "no-store"


@pytest.mark.parametrize(
    "defect", ["expired", "future", "retired", "applied", "version", "phone"]
)
def test_unusable_phone_intent_allows_restart_without_proof_disclosure(
    monkeypatch, defect
):
    from apps.accounts import sessions, views
    from apps.accounts.recovery_models import PhoneChangeIntent

    at = timezone.now()
    owner = SimpleNamespace(auth_version=4, phone="+989123456789")
    row = PhoneChangeIntent(
        old_phone=owner.phone,
        issued_auth_version=4,
        created_at=at - timedelta(minutes=1),
        expires_at=at + timedelta(minutes=1),
        old_phone_verified_at=at,
        new_phone_verified_at=at,
    )
    if defect == "expired":
        row.expires_at = at
    if defect == "future":
        row.created_at = at + timedelta(seconds=1)
    if defect == "retired":
        row.retired_at = at
    if defect == "applied":
        row.applied_at = at
    if defect == "version":
        row.issued_auth_version = 3
    if defect == "phone":
        row.old_phone = "+989123456780"
    monkeypatch.setattr(sessions, "actor_user", lambda *args: owner)
    monkeypatch.setattr(
        PhoneChangeIntent.objects,
        "filter",
        lambda **kwargs: SimpleNamespace(first=lambda: row),
    )
    monkeypatch.setattr(views, "current_actor", lambda *args: object())
    request = RequestFactory().get("/accounts/phone-change/")
    request.session = {"c02_change_uuid": str(row.id)}
    response = views.phone_change_page(request)
    assert "شروع تغییر شماره" in response.content.decode()
    assert "اعمال تغییر و خروج" not in response.content.decode()
