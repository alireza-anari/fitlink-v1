"""Native owner routes enforce CSRF, bounds and server-selected redirects."""

import pytest
from django.test import Client

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "route", ["/athlete/setup/", "/professional/setup/", "/professional/verification/"]
)
def test_native_csrf_precedes_commands_without_session(route):
    response = Client(enforce_csrf_checks=True).post(route, {"action": "create"})
    assert response.status_code == 403
    assert "no-store" in response.headers.get("Cache-Control", "")


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
