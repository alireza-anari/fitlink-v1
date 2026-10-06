import importlib
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier
from uuid import uuid4

import pytest
from django.apps import apps
from django.db import close_old_connections, transaction
from django.utils import timezone
from test_phone_change import actor_for
from test_recovery_authorization import owner

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def contract():
    module = importlib.import_module("apps.governance.outbox")
    assert hasattr(module, "scan_outbox"), "missing durable outbox execution"
    return module


def event():
    module = contract()
    user = owner()
    with transaction.atomic():
        result = module.append_outbox(
            "account.security_changed",
            user.public_id,
            1,
            {"user_uuid": str(user.public_id)},
            str(uuid4()),
        )
    return (
        module,
        apps.get_model("governance", "OutboxEvent").objects.get(pk=result),
        user,
    )


def capture(monkeypatch, module):
    sent = []
    monkeypatch.setattr(
        module,
        "enqueue_event",
        lambda event_id, lease_id: sent.append((event_id, lease_id)),
    )
    return sent


def test_concurrent_scanners_claim_one_owner(monkeypatch):
    module, row, _ = event()
    sent = capture(monkeypatch, module)
    barrier = Barrier(2)

    def scan(_):
        close_old_connections()
        try:
            barrier.wait(timeout=10)
            return module.scan_outbox(timezone.now(), 1)
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sum(pool.map(scan, range(2))) == 1
    assert len(sent) == 1
    row.refresh_from_db()
    assert row.state == "leased" and row.attempts == 1 and row.lease_uuid == sent[0][1]


def test_duplicate_delivery_has_one_durable_effect_and_receipt(monkeypatch):
    module, row, _ = event()
    sent = capture(monkeypatch, module)
    now = timezone.now()
    module.scan_outbox(now)
    token = sent[0][1]
    assert module.dispatch_event(row.id, now, lease_uuid=token)
    assert module.dispatch_event(row.id, now, lease_uuid=token)
    row.refresh_from_db()
    assert row.state == "sent"
    assert apps.get_model("governance", "OutboxDeliveryReceipt").objects.count() == 1


def test_stale_lease_owner_cannot_execute_and_expiry_recovers(monkeypatch):
    module, row, _ = event()
    sent = capture(monkeypatch, module)
    now = timezone.now()
    module.scan_outbox(now)
    old = sent[0][1]
    module.scan_outbox(now + timedelta(seconds=60))
    new = sent[1][1]
    assert old != new and not module.dispatch_event(
        row.id, now + timedelta(seconds=60), lease_uuid=old
    )
    assert module.dispatch_event(row.id, now + timedelta(seconds=60), lease_uuid=new)
    assert apps.get_model("governance", "OutboxDeliveryReceipt").objects.count() == 1


def test_broker_failures_are_durable_bounded_and_exhausted(monkeypatch):
    module, row, _ = event()

    def fail(*args):
        raise RuntimeError("private-provider-error-do-not-log")

    monkeypatch.setattr(module, "enqueue_event", fail)
    at = timezone.now()
    for attempt in range(1, 9):
        assert module.scan_outbox(at) == 1
        row.refresh_from_db()
        assert row.attempts == attempt and row.last_error_code == "broker_unavailable"
        if attempt < 8:
            assert 0 < (row.available_at - at).total_seconds() <= 300
            at = row.available_at
    assert row.state == "exhausted" and row.exhausted_at is not None
    assert module.scan_outbox(at + timedelta(hours=1)) == 0


def test_handler_failure_rolls_back_receipt_then_retry_succeeds(monkeypatch):
    from config import event_handlers

    module, row, _ = event()
    sent = capture(monkeypatch, module)
    now = timezone.now()
    original = event_handlers.HANDLERS

    def fail(event, at):
        raise RuntimeError("handler unavailable")

    monkeypatch.setattr(event_handlers, "HANDLERS", {row.event_type: fail})
    module.scan_outbox(now)
    assert not module.dispatch_event(row.id, now, lease_uuid=sent[0][1])
    assert not apps.get_model("governance", "OutboxDeliveryReceipt").objects.exists()
    row.refresh_from_db()
    assert row.state == "pending" and row.last_error_code == "handler_unavailable"
    monkeypatch.setattr(event_handlers, "HANDLERS", original)
    module.scan_outbox(row.available_at)
    assert module.dispatch_event(row.id, row.available_at, lease_uuid=sent[-1][1])


def test_missing_registered_handler_exhausts_without_dynamic_import(monkeypatch):
    from config import event_handlers

    module, row, _ = event()
    sent = capture(monkeypatch, module)
    monkeypatch.setattr(event_handlers, "HANDLERS", {})
    at = timezone.now()
    module.scan_outbox(at)
    assert not module.dispatch_event(row.id, at, lease_uuid=sent[0][1])
    row.refresh_from_db()
    assert row.state == "exhausted" and row.last_error_code == "invalid_event"


def test_stale_identity_version_receipt_skips_effect(monkeypatch):
    module, row, user = event()
    type(user).objects.filter(pk=user.pk).update(auth_version=2)
    actor, _ = actor_for(type(user).objects.get(pk=user.pk))
    sent = capture(monkeypatch, module)
    at = timezone.now()
    module.scan_outbox(at)
    assert module.dispatch_event(row.id, at, lease_uuid=sent[0][1])
    assert (
        apps.get_model("governance", "OutboxDeliveryReceipt").objects.get().result
        == "skipped"
    )
    assert (
        apps.get_model("accounts", "AccountSessionControl")
        .objects.get(pk=actor.control_id)
        .revoked_at
        is None
    )


def test_domain_rollback_never_creates_delivery(monkeypatch):
    module = contract()
    with pytest.raises(RuntimeError), transaction.atomic():
        user = owner()
        module.append_outbox(
            "account.security_changed",
            user.public_id,
            1,
            {"user_uuid": str(user.public_id)},
            str(uuid4()),
        )
        raise RuntimeError("domain rollback")
    sent = capture(monkeypatch, module)
    assert module.scan_outbox(timezone.now()) == 0 and not sent


def test_security_effect_cleans_only_stale_controls_and_is_idempotent(monkeypatch):
    module, row, user = event()
    old, _ = actor_for(user)
    type(user).objects.filter(pk=user.pk).update(auth_version=2)
    user.refresh_from_db()
    fresh, _ = actor_for(user)
    type(row).objects.filter(pk=row.pk).update(aggregate_version=2)
    sent = capture(monkeypatch, module)
    now = timezone.now()
    module.scan_outbox(now)
    assert module.dispatch_event(row.id, now, lease_uuid=sent[0][1])
    controls = apps.get_model("accounts", "AccountSessionControl")
    assert controls.objects.get(pk=old.control_id).revoked_at == now
    assert controls.objects.get(pk=fresh.control_id).revoked_at is None
    assert module.dispatch_event(
        row.id, now + timedelta(seconds=1), lease_uuid=sent[0][1]
    )
    assert controls.objects.get(pk=old.control_id).revoked_at == now


def test_privileged_retry_requires_case_bound_fresh_authority_and_resets_once(
    settings, monkeypatch
):
    from dataclasses import replace

    from django.core.exceptions import PermissionDenied

    from apps.governance.staff import MockStepUpProvider, issue_mock_step_up

    module, row, user = event()

    def fail(*args):
        raise RuntimeError("broker unavailable")

    monkeypatch.setattr(module, "enqueue_event", fail)
    now = timezone.now()
    for _ in range(8):
        module.scan_outbox(now)
        row.refresh_from_db()
        now = row.available_at
    staff = owner("+989123456788")
    actor, _ = actor_for(staff)
    with pytest.raises(PermissionDenied):
        module.retry_exhausted(actor, row.id, 8, uuid4(), "operator_retry", now)
    settings.ACCOUNT_SECURITY = replace(
        settings.ACCOUNT_SECURITY, step_up_provider="mock"
    )
    issuer = owner("+989123456787")
    apps.get_model("governance", "StaffCapabilityGrant").objects.create(
        user=staff,
        capability="security_audit",
        valid_from=now,
        valid_until=now + timedelta(hours=1),
        granted_by=issuer,
        reason_code="operator_retry",
    )
    provider = MockStepUpProvider()
    assertion = provider.prepare(staff.public_id, "security_audit", row.id, now)
    with transaction.atomic():
        step = issue_mock_step_up(
            staff,
            "security_audit",
            row.id,
            assertion.raw_assertion,
            issuer,
            now,
            provider,
        )
    module.retry_exhausted(actor, row.id, 8, step, "operator_retry", now)
    with pytest.raises(PermissionDenied):
        module.retry_exhausted(actor, row.id, 8, step, "operator_retry", now)
    row.refresh_from_db()
    assert row.state == "pending" and row.attempts == 0
    assert (
        apps.get_model("governance", "AuditEvent")
        .objects.filter(action="outbox.retry", subject_uuid=row.id)
        .count()
        == 1
    )


@pytest.mark.parametrize(
    "kind",
    [
        "consent.granted",
        "consent.revoked",
        "privacy.intake_recorded",
        "feature_flag.changed",
    ],
)
def test_each_metadata_handler_records_one_version_bound_effect(monkeypatch, kind):
    from apps.governance.consents import validate_scope
    from config.use_cases.consent import grant_consent, revoke_consent
    from config.use_cases.privacy import request_privacy

    module = contract()
    user = owner()
    actor, _ = actor_for(user)
    at = timezone.now()
    if kind.startswith("consent."):
        grantee = owner("+989123456782")
        scope = validate_scope(
            actor,
            grantee.public_id,
            "account_metadata",
            "account_metadata",
            user.public_id,
            1,
            at + timedelta(hours=1),
            at,
        )
        result = grant_consent(actor, scope, "v1", "a" * 64, at)
        if kind == "consent.revoked":
            revoke_consent(actor, result, 1, at)
    elif kind == "privacy.intake_recorded":
        result = request_privacy(actor, "export", uuid4(), at, confirmed=True)
    else:
        flag = apps.get_model("governance", "FeatureFlag").objects.get_or_create(
            key="marketplace"
        )[0]
        with transaction.atomic():
            module.append_outbox(
                kind, flag.id, flag.version, {"flag_uuid": str(flag.id)}, str(uuid4())
            )
        result = flag.id
    row = apps.get_model("governance", "OutboxEvent").objects.get(
        event_type=kind, aggregate_uuid=result
    )
    sent = capture(monkeypatch, module)
    at = timezone.now()
    module.scan_outbox(at)
    token = next(lease for event_id, lease in sent if event_id == row.id)
    assert module.dispatch_event(row.id, at, lease_uuid=token)
    assert module.dispatch_event(row.id, at, lease_uuid=token)
    receipts = apps.get_model("governance", "OutboxDeliveryReceipt").objects.filter(
        event=row
    )
    assert receipts.count() == 1 and receipts.get().result == "applied"
