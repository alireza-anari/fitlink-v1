import pytest
from django.test import Client

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/auth/otp/request/",
        "/api/v1/auth/otp/verify/",
        "/api/v1/recovery/requests/",
        "/api/v1/recovery/requests/00000000-0000-0000-0000-000000000001/new-phone/request/",
        "/api/v1/recovery/requests/00000000-0000-0000-0000-000000000001/new-phone/verify/",
    ],
)
@pytest.mark.parametrize("defect", ["missing", "wrong", "origin"])
def test_anonymous_rejection_needs_no_database_or_provider(path, defect, monkeypatch):
    from config.use_cases import identity, recovery

    def forbidden(*args, **kwargs):
        pytest.fail("Command called before CSRF rejection")

    for module, name in (
        (identity, "request_login_otp"),
        (identity, "verify_login_otp"),
        (recovery, "open_recovery"),
        (recovery, "request_recovery_otp"),
        (recovery, "verify_recovery_otp"),
    ):
        monkeypatch.setattr(module, name, forbidden)
    client = Client(enforce_csrf_checks=True)
    assert client.get("/accounts/entry/").status_code == 200
    token = client.cookies["csrftoken"].value
    headers = {}
    if defect == "wrong":
        headers["HTTP_X_CSRFTOKEN"] = "a" * 32
    elif defect == "origin":
        headers = {"HTTP_X_CSRFTOKEN": token, "HTTP_ORIGIN": "https://foreign.example"}
    response = client.post(
        path, {"phone": "09123456789"}, content_type="application/json", **headers
    )
    assert response.status_code == 403
    assert response.json() == {"status": "denied"}
    assert response["Cache-Control"] == "no-store"
    assert "Access-Control-Allow-Origin" not in response


@pytest.mark.parametrize(
    "data",
    [
        {"phone": "x" * 5000},
        {"phone": "09123456789", "provider": "unsafe"},
        {"phone": ["09123456789"]},
    ],
)
def test_invalid_or_oversized_payload_does_not_enter_command(data, monkeypatch):
    from config.use_cases import identity

    def forbidden(*args, **kwargs):
        pytest.fail("Invalid payload reached identity command")

    monkeypatch.setattr(identity, "request_login_otp", forbidden)
    client = Client(enforce_csrf_checks=True)
    client.get("/accounts/entry/")
    response = client.post(
        "/api/v1/auth/otp/request/",
        data,
        content_type="application/json",
        HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value,
    )
    assert response.status_code == 400
    assert response.json() == {"status": "invalid"}
    assert response["Cache-Control"] == "no-store"
