"""Actual scanner, broker restart and SIGKILL worker recovery; synthetic bytes only."""

import json
import os
import sys
import time
from datetime import date, timedelta
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from uuid import uuid4

import django

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()
from django.conf import settings  # noqa: E402
from django.db import transaction  # noqa: E402
from django.utils import timezone  # noqa: E402
from PIL import Image  # noqa: E402
from redis import Redis  # noqa: E402

from apps.accounts.models import User  # noqa: E402
from apps.assets.images import isolation_probe  # noqa: E402
from apps.assets.models import Asset, AssetProcessingAttempt  # noqa: E402
from apps.assets.scanner import configured_scanner  # noqa: E402
from apps.assets.storage import S3PrivateStore  # noqa: E402
from apps.governance.outbox import append_outbox, dispatch_event  # noqa: E402
from apps.governance.outbox_models import (  # noqa: E402
    OutboxDeliveryReceipt,
    OutboxEvent,
)
from apps.professionals.models import ProfessionalProfile  # noqa: E402
from config.use_cases.asset_processing import scan_due_assets  # noqa: E402
from docker.c03_worker_fixture import STAGE, crash_probe  # noqa: E402

PHONE = "+989100000005"


def evidence(stage):
    with Path(".runtime/c03-triage/probe.jsonl").open("a") as stream:
        stream.write(json.dumps({"event": "real_worker_probe", "stage": stage}) + "\n")


def row():
    return Asset.objects.get(owner__phone=PHONE)


def prepare():
    isolation = isolation_probe()
    assert all(
        isolation.get(k)
        for k in ("nonroot", "network_denied", "write_denied", "fork_denied")
    )
    at = timezone.now()
    output = BytesIO()
    Image.new("RGB", (64, 48), (32, 96, 128)).save(output, format="PNG")
    data = output.getvalue()
    assert configured_scanner().scan(data, at).status == "clean"
    user = User.objects.create_user(
        PHONE,
        birth_date=date(1990, 1, 1),
        adult_attested_at=at,
        adult_attestation_version="adult-v1",
    )
    profile = ProfessionalProfile.objects.create(user=user)
    asset = Asset.objects.create(
        owner=user,
        subject_kind="professional_profile",
        subject_uuid=profile.id,
        purpose="avatar",
        state="quarantined",
        declared_size=len(data),
        actual_size=len(data),
        declared_type="image/png",
        detected_type="image/png",
        source_key=f"sources/{uuid4()}.png",
        sha256=sha256(data).hexdigest(),
        accepted_at=at,
        finalized_at=at,
        upload_expires_at=at + timedelta(minutes=5),
    )
    S3PrivateStore().put_stream(
        asset.source_key, BytesIO(data), "image/png", 10_000_000
    )
    with transaction.atomic():
        event_id = append_outbox(
            "asset.processing_requested",
            asset.id,
            1,
            {"asset_uuid": str(asset.id), "user_uuid": str(user.public_id)},
            f"asset.processing_requested:{asset.id}:1",
        )
    event = OutboxEvent.objects.get(pk=event_id)
    lease = uuid4()
    event.state, event.lease_uuid, event.lease_until = (
        "leased",
        lease,
        at + timedelta(seconds=60),
    )
    event.save()
    assert dispatch_event(event.id, at, lease_uuid=lease)
    assert OutboxDeliveryReceipt.objects.filter(event=event).count() == 1
    assert (
        AssetProcessingAttempt.objects.filter(asset=asset, state="pending").count() == 1
    )
    assert not asset.derivatives.exists()
    evidence("receipt_committed_without_prompt")


def start():
    def enqueue(asset_id, pv, lease):
        crash_probe.apply_async(args=[str(asset_id), pv, str(lease)], retry=False)

    assert scan_due_assets(timezone.now(), 1, enqueue=enqueue) == 1
    redis = Redis.from_url(
        settings.OTP_RATE_REDIS_URL, socket_connect_timeout=2, socket_timeout=2
    )
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        if redis.get(STAGE) == b"scanned":
            assert row().state == "processing" and not row().derivatives.exists()
            evidence("real_worker_scanned_before_sigkill")
            return
        time.sleep(0.1)
    raise AssertionError("Actual worker crash barrier unavailable")


def recover():
    asset = row()
    attempt = AssetProcessingAttempt.objects.get(asset=asset, state="running")
    AssetProcessingAttempt.objects.filter(pk=attempt.pk).update(
        lease_until=timezone.now() - timedelta(seconds=1)
    )
    assert scan_due_assets(timezone.now(), 1) == 1
    deadline = time.monotonic() + 25
    while time.monotonic() < deadline:
        asset.refresh_from_db()
        if asset.state == "ready":
            break
        time.sleep(0.1)
    assert asset.state == "ready"
    assert asset.derivatives.filter(state="ready").count() == 1
    assert (
        AssetProcessingAttempt.objects.filter(
            asset=asset, state="ready", attempt=2
        ).count()
        == 1
    )
    assert AssetProcessingAttempt.objects.get(pk=attempt.pk).state == "failed"
    derivative = asset.derivatives.get()
    store = S3PrivateStore()
    assert (
        sha256(store.read_limited(asset.source_key, 10_000_000)).hexdigest()
        == asset.sha256
    )
    assert (
        sha256(store.read_limited(derivative.key, 10_000_000)).hexdigest()
        == derivative.sha256
    )
    from apps.assets.tasks import process_private_asset

    # Stale redelivery is an actual broker task, never an eager call.
    process_private_asset.apply_async(
        args=[str(asset.id), 1, str(attempt.lease_uuid)], retry=False
    )
    assert scan_due_assets(timezone.now(), 1) == 0
    evidence("broker_restart_expired_lease_recovered_once")


def scanner_outage():
    assert configured_scanner().scan(b"synthetic", timezone.now()).status != "clean"
    assert row().derivatives.count() == 1
    evidence("injected_real_scanner_outage_denied")


def scanner_restored():
    data = S3PrivateStore().read_limited(row().source_key, 10_000_000)
    assert configured_scanner().scan(data, timezone.now()).status == "clean"
    assert row().derivatives.count() == 1
    evidence("real_scanner_post_fault_healthy")


if __name__ == "__main__":
    {
        "prepare": prepare,
        "start": start,
        "recover": recover,
        "scanner-outage": scanner_outage,
        "scanner-restored": scanner_restored,
    }[sys.argv[1]]()
