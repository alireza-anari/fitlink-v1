"""Recover durable leases after real process loss and missed broker prompts."""

import importlib
from datetime import timedelta
from uuid import uuid4

import pytest
from django.utils import timezone

from apps.assets.models import AssetProcessingAttempt

from .processing_helpers import Scanner, api, prepared
from .test_asset_processing import claimed

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def test_broker_failure_is_durable(monkeypatch):
    s = prepared(monkeypatch)
    p = api()
    p.request_processing(s.event, timezone.now())

    def outage(*args):
        raise ConnectionError("PRIVATE_SENTINEL")

    assert p.scan_due_assets(timezone.now(), 1, enqueue=outage) == 1
    attempt = AssetProcessingAttempt.objects.get(asset=s.asset)
    assert attempt.state == "pending" and attempt.failure_code == "broker_unavailable"
    assert "PRIVATE_SENTINEL" not in repr(attempt.__dict__)


def test_lost_worker_lease_recovers_once(monkeypatch):
    s = prepared(monkeypatch)
    first = claimed(s)
    p = api()
    AssetProcessingAttempt.objects.filter(pk=first.pk).update(
        lease_until=timezone.now() - timedelta(seconds=1)
    )
    assert p.scan_due_assets(timezone.now(), 1, enqueue=lambda *args: None) == 1
    second = AssetProcessingAttempt.objects.get(asset=s.asset, state="running")
    assert second.attempt == 2 and second.lease_uuid != first.lease_uuid
    assert (
        p.process_asset(
            s.asset.id,
            1,
            first.lease_uuid,
            timezone.now(),
            store=s.store,
            scanner=Scanner(),
        )
        != "ready"
    )
    assert (
        p.process_asset(
            s.asset.id,
            1,
            second.lease_uuid,
            timezone.now(),
            store=s.store,
            scanner=Scanner(),
        )
        == "ready"
    )
    assert s.asset.derivatives.count() == 1


def test_exhaustion_never_ready(monkeypatch):
    s = prepared(monkeypatch)
    first = claimed(s)
    p = api()
    AssetProcessingAttempt.objects.filter(pk=first.pk).update(
        attempt=8, lease_until=timezone.now() - timedelta(seconds=1)
    )
    assert p.scan_due_assets(timezone.now(), 1, enqueue=lambda *args: None) == 0
    assert not AssetProcessingAttempt.objects.filter(
        asset=s.asset, state__in=["pending", "running"]
    ).exists()
    s.asset.refresh_from_db()
    assert s.asset.state == "rejected" and s.asset.rejection_code == "exhausted"


def test_worker_task_is_non_eager_uuid_only(settings):
    from importlib.util import find_spec

    assert find_spec("apps.assets.tasks"), "processing worker task absent"
    task = importlib.import_module("apps.assets.tasks").process_private_asset
    assert not settings.CELERY_TASK_ALWAYS_EAGER
    assert task.acks_late and task.reject_on_worker_lost
    assert task.run("PRIVATE_SENTINEL", 1, str(uuid4())) != "ready"


def test_broker_outage_is_bounded_and_never_ready(monkeypatch):
    s = prepared(monkeypatch)
    p = api()
    p.request_processing(s.event, timezone.now())

    def outage(*args):
        raise ConnectionError("PRIVATE_SENTINEL")

    at = timezone.now()
    for _ in range(9):
        p.scan_due_assets(at, 1, enqueue=outage)
        attempt = (
            AssetProcessingAttempt.objects.filter(asset=s.asset)
            .order_by("-attempt")
            .first()
        )
        at = (attempt.lease_until or at) + timedelta(seconds=301)
    s.asset.refresh_from_db()
    assert s.asset.state == "rejected" and s.asset.rejection_code == "exhausted"
    assert not s.asset.derivatives.exists()
    assert not AssetProcessingAttempt.objects.filter(
        asset=s.asset, state__in=["pending", "running"]
    ).exists()


def test_processing_records_algorithm_version(monkeypatch):
    s = prepared(monkeypatch)
    attempt = claimed(s)
    assert attempt.algorithm_version == "jpeg-png-pixels-v1"


def test_disabled_runtime_does_not_claim_pending_work(monkeypatch, settings):
    s = prepared(monkeypatch)
    p = api()
    p.request_processing(s.event, timezone.now())
    settings.ASSET_PROCESSING_ENABLED = False
    assert p.scan_due_assets(timezone.now(), 1) == 0
    assert AssetProcessingAttempt.objects.get(asset=s.asset).state == "pending"
