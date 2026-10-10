"""Required private preview routes replace the Task 10 absence expectation."""

import pytest
from django.test import Client

pytestmark = pytest.mark.unit


def test_task4_ingress_cache_header_remains_exact():
    response = Client().get("/api/v1/profile-assets/begin/")
    assert response.status_code == 403
    assert response["Cache-Control"] == "no-store"


@pytest.mark.parametrize(
    "route", ["/professional/preview/", "/api/v1/professional/preview/"]
)
def test_owner_preview_routes_require_session_and_private_headers(route):
    response = Client(enforce_csrf_checks=True).get(route)
    if route.startswith("/api/"):
        assert response.status_code == 403
        assert response.json() == {"status": "denied"}
    else:
        assert response.status_code in {302, 403}
        if response.status_code == 302:
            assert response.url == "/accounts/entry/"
    assert "no-store" in response.headers.get("Cache-Control", "")
    assert response.headers.get("X-Robots-Tag") == "noindex, nofollow"
