from types import SimpleNamespace
from urllib.parse import urlencode, urlsplit
from uuid import uuid4

import pytest
from django.test import Client
from django.utils import timezone

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("action", ["evidence", "decision", "apply"])
def test_staff_success_redirects_to_authorized_get_and_reload_never_replays(
    monkeypatch, action
):
    from django.test import RequestFactory

    from apps.accounts import staff_views

    case, step = uuid4(), uuid4()
    row = SimpleNamespace(id=case, state="approved", version=4)
    calls = []
    reads = []
    actor = object()
    monkeypatch.setattr(staff_views, "current_actor", lambda *args: actor)

    def detail(actual_actor, actual_case, actual_step, reason, at):
        assert (actual_actor, actual_case, actual_step, reason) == (
            actor,
            case,
            step,
            "identity_verified",
        )
        reads.append(row.version)
        return row

    def command(**kwargs):
        assert kwargs["expected_version"] == 4
        calls.append(action)
        row.version += 1

    monkeypatch.setattr(staff_views.recovery, "recovery_detail", detail)
    monkeypatch.setattr(
        staff_views.recovery,
        {
            "evidence": "add_recovery_evidence",
            "decision": "decide_recovery",
            "apply": "apply_recovery",
        }[action],
        command,
    )
    path = f"/staff/recovery/{case}/"
    factory = RequestFactory()
    request = factory.post(
        path,
        urlencode(
            {
                "action": action,
                "step_up_id": str(step),
                "reason_code": "identity_verified",
                "expected_version": "4",
                "classification": "identity_match",
                "outcome": "verified",
                "checksum": "a" * 64,
                "reference": str(uuid4()),
                "decision": "approved",
            }
        ),
        content_type="application/x-www-form-urlencoded",
    )
    request._dont_enforce_csrf_checks = True
    request.session = {}
    response = staff_views.staff_recovery_page(request, case)
    assert calls == [action]
    assert response.status_code == 302
    assert urlsplit(response["Location"]).path == path
    assert not urlsplit(response["Location"]).netloc
    assert response["Cache-Control"] == "no-store"
    row.version += 1  # Separate new-phone proof advances the durable version.
    for _ in range(2):
        get = factory.get(response["Location"])
        get.session = request.session
        rendered = staff_views.staff_recovery_page(get, case)
        assert rendered.status_code == 200
        assert 'value="6"' in rendered.content.decode()
    assert calls == [action]
    assert reads[-2:] == [6, 6]

    def denied(*args):
        raise PermissionError("private authority detail")

    monkeypatch.setattr(staff_views.recovery, "recovery_detail", denied)
    revoked = staff_views.staff_recovery_page(get, case)
    assert revoked.status_code == 404
    assert b"private authority detail" not in revoked.content
    assert calls == [action]


@pytest.mark.parametrize("old,new", [(False, False), (True, False), (True, True)])
def test_phone_change_display_reads_actual_proof_fields(monkeypatch, old, new):
    from apps.accounts import sessions
    from apps.accounts.models import User
    from apps.accounts.recovery_models import PhoneChangeIntent
    from config.use_cases.identity import phone_change_display

    owner = User(phone="+989123456789")
    change = PhoneChangeIntent(
        user=owner,
        old_phone_verified_at=timezone.now() if old else None,
        new_phone_verified_at=timezone.now() if new else None,
    )

    # The DB boundary returns a real model, retaining its actual field contract.
    class Result:
        def first(self):
            return change

    def owned_filter(**kwargs):
        assert kwargs == {"pk": change.id, "user": owner}
        return Result()

    monkeypatch.setattr(sessions, "actor_user", lambda *args: owner)
    monkeypatch.setattr(PhoneChangeIntent.objects, "filter", owned_filter)
    assert phone_change_display(object(), change.id, timezone.now()) == {
        "change_uuid": change.id,
        "old_verified": old,
        "new_verified": new,
    }


def test_staff_html_post_requires_csrf_before_any_case_access():
    response = Client(enforce_csrf_checks=True).post(
        f"/staff/recovery/{uuid4()}/", {"action": "apply"}
    )
    assert response.status_code == 403
    assert response["Cache-Control"] == "no-store"


def test_staff_read_outage_returns_generic_unavailable_without_private_case(
    monkeypatch,
):
    from django.db import DatabaseError

    from apps.accounts import staff_views

    monkeypatch.setattr(staff_views, "current_actor", lambda *args: object())

    def unavailable(*args):
        raise DatabaseError("private database detail")

    monkeypatch.setattr(staff_views.recovery, "recovery_detail", unavailable)
    response = Client().get(
        f"/staff/recovery/{uuid4()}/",
        {"step_up_id": str(uuid4()), "reason_code": "identity_verified"},
    )
    assert response.status_code == 503
    assert response["Cache-Control"] == "no-store"
    assert b"private database detail" not in response.content


@pytest.mark.parametrize(
    "path",
    [
        "/accounts/entry/",
        "/accounts/verify/",
        "/accounts/me/",
        "/accounts/phone-change/",
        "/accounts/recovery/",
        "/privacy/requests/",
    ],
)
def test_native_html_csrf_precedes_any_identity_or_provider_effect(path):
    response = Client(enforce_csrf_checks=True).post(path, {"action": "verify"})
    assert response.status_code == 403
    assert response["Cache-Control"] == "no-store"
