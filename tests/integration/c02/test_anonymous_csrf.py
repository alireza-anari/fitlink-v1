from uuid import uuid4

import pytest
from api_helpers import bootstrap, enabled
from django.apps import apps
from django.test import Client

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/auth/otp/request/",
        "/api/v1/auth/otp/verify/",
        "/api/v1/recovery/requests/",
        f"/api/v1/recovery/requests/{uuid4()}/new-phone/request/",
        f"/api/v1/recovery/requests/{uuid4()}/new-phone/verify/",
    ],
)
@pytest.mark.parametrize("defect", ["missing", "wrong", "origin"])
def test_anonymous_csrf_rejects_before_any_security_side_effect(
    settings, monkeypatch, limiter, path, defect
):
    enabled(settings)
    from apps.accounts import otp, recovery
    from config.use_cases import identity

    def forbidden(*args, **kwargs):
        pytest.fail("CSRF rejection must precede limiter/provider mutation")

    monkeypatch.setattr(otp, "reserve_admission", forbidden)
    monkeypatch.setattr(recovery, "reserve_admission", forbidden)
    monkeypatch.setattr(identity, "configured_provider", forbidden)
    client = Client(enforce_csrf_checks=True)
    token = bootstrap(client)
    headers = {"HTTP_X_CSRFTOKEN": token}
    if defect == "missing":
        headers = {}
    elif defect == "wrong":
        headers["HTTP_X_CSRFTOKEN"] = "a" * 32
    else:
        headers["HTTP_ORIGIN"] = "https://foreign.example"
    response = client.post(
        path, {"phone": "09123456789"}, content_type="application/json", **headers
    )
    assert response.status_code == 403
    assert response["Cache-Control"] == "no-store"
    for model in ("OTPChallenge", "SecurityRateEvent", "RecoveryRequest", "User"):
        assert apps.get_model("accounts", model).objects.count() == 0
    assert apps.get_model("governance", "AuditEvent").objects.count() == 0
