"""Fresh release fencing and durable single private effect."""

from datetime import timedelta
from uuid import uuid4

import pytest
from django.utils import timezone

from apps.assets.models import Asset, AssetDerivative, AssetProcessingAttempt
from apps.governance.outbox import dispatch_event
from apps.governance.outbox_models import OutboxDeliveryReceipt

from .processing_helpers import Scanner, api, prepared

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def test_crash_after_outbox_receipt_before_prompt_recovers(monkeypatch):
    s = prepared(monkeypatch)
    assert dispatch_event(s.event.id, timezone.now(), lease_uuid=s.event.lease_uuid)
    assert OutboxDeliveryReceipt.objects.filter(event=s.event).count() == 1
    assert (
        AssetProcessingAttempt.objects.filter(asset=s.asset, state="pending").count()
        == 1
    )
    assert s.asset.derivatives.count() == 0
    # Durable discovery, no prompt/broker dependency and no long I/O in handler.
    worker = api()
    assert worker.scan_due_assets(timezone.now(), 1, enqueue=lambda *args: None) == 1
    attempt = AssetProcessingAttempt.objects.get(asset=s.asset, state="running")
    result = worker.process_asset(
        s.asset.id,
        s.asset.processing_version,
        attempt.lease_uuid,
        timezone.now(),
        store=s.store,
        scanner=Scanner(),
    )
    assert result == "ready"
    s.asset.refresh_from_db()
    assert s.asset.state == "ready"
    assert s.asset.derivatives.count() == 1


def claimed(s):
    p = api()
    p.request_processing(s.event, timezone.now())
    assert p.scan_due_assets(timezone.now(), 1, enqueue=lambda *args: None) == 1
    return AssetProcessingAttempt.objects.get(asset=s.asset, state="running")


def test_duplicate_derivative_effect(monkeypatch):
    s = prepared(monkeypatch)
    attempt = claimed(s)
    p = api()
    scanner = Scanner()
    for _ in range(2):
        p.process_asset(
            s.asset.id,
            1,
            attempt.lease_uuid,
            timezone.now(),
            store=s.store,
            scanner=scanner,
        )
    assert AssetDerivative.objects.filter(asset=s.asset, state="ready").count() == 1
    assert scanner.calls == 1
    derivative = s.asset.derivatives.get()
    assert derivative.key.startswith("derivatives/") and s.data != s.store.read(
        derivative.key
    )
    assert s.store.read(s.asset.source_key) == s.data


@pytest.mark.parametrize("state", ["restricted", "suspended", "pending_deletion"])
def test_processing_deleted_owner_cannot_release(state, monkeypatch):
    s = prepared(monkeypatch)
    attempt = claimed(s)

    def deny():
        s.user.state = state
        s.user.is_active = state != "suspended"
        s.user.auth_version += 1
        s.user.save()

    assert (
        api().process_asset(
            s.asset.id,
            1,
            attempt.lease_uuid,
            timezone.now(),
            store=s.store,
            scanner=Scanner(hook=deny),
        )
        != "ready"
    )
    s.asset.refresh_from_db()
    assert s.asset.state != "ready"
    assert not s.asset.derivatives.filter(state="ready").exists()


@pytest.mark.parametrize(
    "defect",
    [
        "stale_lease",
        "expired_lease",
        "archived",
        "abandoned",
        "version",
        "auth_version",
    ],
)
def test_processing_stale_lease_or_binding_cannot_release(defect, monkeypatch):
    s = prepared(monkeypatch)
    attempt = claimed(s)

    def mutate():
        if defect == "stale_lease":
            AssetProcessingAttempt.objects.filter(pk=attempt.pk).update(
                lease_uuid=uuid4()
            )
        elif defect == "expired_lease":
            AssetProcessingAttempt.objects.filter(pk=attempt.pk).update(
                lease_until=timezone.now() - timedelta(seconds=1)
            )
        elif defect == "archived":
            s.profile.state = "archived"
            s.profile.save()
        elif defect == "abandoned":
            Asset.objects.filter(pk=s.asset.pk).update(
                state="abandoned", revoked_at=timezone.now()
            )
        elif defect == "auth_version":
            s.user.auth_version += 1
            s.user.save()
        else:
            Asset.objects.filter(pk=s.asset.pk).update(processing_version=2)

    assert (
        api().process_asset(
            s.asset.id,
            1,
            attempt.lease_uuid,
            timezone.now(),
            store=s.store,
            scanner=Scanner(hook=mutate),
        )
        != "ready"
    )
    assert not s.asset.derivatives.filter(state="ready").exists()


@pytest.mark.parametrize(
    "status", ["malicious", "unknown", "error", "timeout", "stale", "limit"]
)
def test_unknown_and_exhausted_scanner_states_never_ready(status, monkeypatch):
    s = prepared(monkeypatch)
    attempt = claimed(s)
    assert (
        api().process_asset(
            s.asset.id,
            1,
            attempt.lease_uuid,
            timezone.now(),
            store=s.store,
            scanner=Scanner(status),
        )
        != "ready"
    )
    s.asset.refresh_from_db()
    assert s.asset.state != "ready"
    assert not s.asset.derivatives.exists()


def test_clean_scanner_alone_never_ready(monkeypatch):
    s = prepared(monkeypatch, b"\x89PNG\r\n\x1a\ninvalid decoder bytes")
    attempt = claimed(s)
    assert (
        api().process_asset(
            s.asset.id,
            1,
            attempt.lease_uuid,
            timezone.now(),
            store=s.store,
            scanner=Scanner(),
        )
        != "ready"
    )
    assert not s.asset.derivatives.exists()
