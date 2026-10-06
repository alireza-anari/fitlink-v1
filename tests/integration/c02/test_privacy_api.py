from uuid import uuid4

import pytest
from api_helpers import browser, post
from django.apps import apps
from test_recovery_authorization import owner

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def test_privacy_confirmation_ownership_list_and_delete_cookie_denial():
    client, token, _, _ = browser()
    path = "/api/v1/privacy/requests/"
    data = {"kind": "export", "request_id": str(uuid4())}
    assert post(client, token, path, data).status_code == 403
    assert not apps.get_model("governance", "PrivacyRequest").objects.exists()
    response = post(client, token, path, {**data, "confirmed": True})
    assert response.status_code == 201
    request_id = response.json()["request_id"]
    assert client.get(path + request_id + "/").json()["status"] == "pending_execution"
    other, _, _, _ = browser(owner("+989123456780"))
    assert other.get(path + request_id + "/").status_code == 404
    assert other.get(path).json() == {"requests": []}
    assert len(client.get(path).json()["requests"]) == 1
    deleted = post(
        client,
        token,
        path,
        {"kind": "delete", "request_id": str(uuid4()), "confirmed": True},
    )
    assert deleted.status_code == 201
    assert client.get("/api/v1/account/me/").status_code == 403


def test_consent_never_grants_foreign_privacy_or_account_access():
    from django.utils import timezone
    from test_consent_core import granted

    from config.use_cases.privacy import request_privacy

    _, _, subject, grantee, actor, _, _, _ = granted()
    privacy_id = request_privacy(
        actor, "export", uuid4(), timezone.now(), confirmed=True
    )
    client, _, _, _ = browser(grantee)
    assert client.get(f"/api/v1/privacy/requests/{privacy_id}/").status_code == 404
    assert client.get("/api/v1/privacy/requests/").json() == {"requests": []}
    assert client.get("/api/v1/account/me/").json()["account_uuid"] == str(
        grantee.public_id
    )
    assert client.get(f"/api/v1/account/{subject.public_id}/").status_code == 404


def test_http_privacy_requires_recent_authoritative_control():
    from datetime import timedelta

    from django.utils import timezone

    client, token, _, actor = browser()
    apps.get_model("accounts", "AccountSessionControl").objects.filter(
        pk=actor.control_id
    ).update(authenticated_at=timezone.now() - timedelta(seconds=601))
    response = post(
        client,
        token,
        "/api/v1/privacy/requests/",
        {"kind": "delete", "request_id": str(uuid4()), "confirmed": True},
    )
    assert response.status_code == 403
    assert not apps.get_model("governance", "PrivacyRequest").objects.exists()
