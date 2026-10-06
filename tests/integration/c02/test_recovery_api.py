from uuid import uuid4

import pytest
from api_helpers import bootstrap, browser, enabled, post
from django.test import Client

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def test_anonymous_receipt_cookie_is_required_and_coarse(settings, limiter):
    enabled(settings)
    client = Client(enforce_csrf_checks=True)
    token = bootstrap(client)
    path = "/api/v1/recovery/requests/"
    response = post(
        client, token, path, {"old_phone": "09123456789", "new_phone": "09123456780"}
    )
    assert response.status_code == 202
    assert set(response.json()) == {"request_id", "status"}
    case = response.json()["request_id"]
    status_path = path + case + "/status/"
    assert client.get(status_path).json() == {"status": "received"}
    assert Client().get(status_path).status_code == 404
    receipt = response.cookies["fitlink_recovery_receipt"]
    assert receipt["secure"] and receipt["httponly"] and receipt["samesite"] == "Strict"
    assert "receipt" not in response.json()
    assert client.get(path + str(uuid4()) + "/status/").status_code == 404


def test_bare_staff_or_feature_switch_cannot_grant_recovery_authority(settings):
    enabled(settings)
    from django.apps import apps

    from apps.governance.flag_models import FEATURE_KEYS

    for key in FEATURE_KEYS:
        apps.get_model("governance", "FeatureFlag").objects.update_or_create(
            key=key, defaults={"enabled": True}
        )
    assert (
        apps.get_model("governance", "FeatureFlag").objects.filter(enabled=True).count()
        == 4
    )
    client, token, user, _ = browser()
    type(user).objects.filter(pk=user.pk).update(is_staff=True, is_superuser=True)
    case = uuid4()
    path = f"/api/v1/staff/recovery/{case}/"
    assert client.get(
        path, {"step_up_id": str(uuid4()), "reason_code": "case_review"}
    ).status_code in {403, 404}
    assert post(
        client,
        token,
        path + "apply/",
        {
            "expected_version": 1,
            "step_up_id": str(uuid4()),
            "reason_code": "case_review",
        },
    ).status_code in {403, 404}


def test_real_receipt_proof_and_assigned_staff_http_apply(
    settings, monkeypatch, limiter
):
    from test_recovery_apply import approved
    from test_recovery_authorization import owner

    from apps.accounts.sms import MockSmsProvider
    from config.use_cases import recovery

    target = owner()
    old_client, _, _, _ = browser(target)
    _, _, receipt, _, staff, _, step, case = approved(settings)
    provider = MockSmsProvider()
    monkeypatch.setattr(recovery, "configured_provider", lambda: provider)
    claimant = Client(enforce_csrf_checks=True)
    token = bootstrap(claimant)
    claimant.cookies["fitlink_recovery_receipt"] = receipt.raw_receipt
    base = f"/api/v1/recovery/requests/{case.id}/new-phone/"
    requested = post(claimant, token, base + "request/", {})
    assert requested.status_code == 200
    code = provider.drain()[0].code
    assert (
        post(
            claimant,
            token,
            base + "verify/",
            {"challenge_id": requested.json()["challenge_id"], "code": code},
        ).status_code
        == 200
    )
    assert claimant.get("/api/v1/account/me/").status_code == 403
    case.refresh_from_db()
    staff_client, staff_token, _, _ = browser(staff)
    path = f"/api/v1/staff/recovery/{case.id}/"
    authority = {"step_up_id": str(step), "reason_code": "identity_verified"}
    detail = staff_client.get(path, authority)
    assert detail.status_code == 200
    assert set(detail.json()) == {"request_id", "state", "version", "evidence_status"}
    applied = post(
        staff_client,
        staff_token,
        path + "apply/",
        {**authority, "expected_version": case.version},
    )
    assert applied.status_code == 200
    target.refresh_from_db()
    assert target.phone == "+989123456780"
    assert old_client.get("/api/v1/account/me/").status_code == 403


def test_existing_and_unknown_intake_have_same_nonidentifying_response(
    settings, limiter
):
    enabled(settings)
    from test_recovery_authorization import owner

    owner()
    shapes = []
    for old in ("09123456789", "09123456781"):
        client = Client(enforce_csrf_checks=True)
        token = bootstrap(client)
        response = post(
            client,
            token,
            "/api/v1/recovery/requests/",
            {
                "old_phone": old,
                "new_phone": "09123456780",
                "contact_preference": "new_phone",
            },
        )
        shapes.append(
            (
                response.status_code,
                set(response.json()),
                response.json()["status"],
                response["Cache-Control"],
                response["Content-Type"],
            )
        )
        assert "fitlink_recovery_receipt" in response.cookies
        case = response.json()["request_id"]
        assert client.get(f"/api/v1/recovery/requests/{case}/status/").json() == {
            "status": "received"
        }
    assert (
        shapes[0]
        == shapes[1]
        == (202, {"request_id", "status"}, "received", "no-store", "application/json")
    )
