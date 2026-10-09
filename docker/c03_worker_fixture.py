"""Hosted test-only crash barrier, loaded explicitly by the isolated probe worker."""

import time
from uuid import UUID

from celery import shared_task
from django.conf import settings
from django.utils import timezone
from redis import Redis

from apps.assets.scanner import configured_scanner
from config.use_cases.asset_processing import process_asset

STAGE = "c03:private-processing:crash-stage"


class CrashBarrierScanner:
    def scan(self, data, at):
        result = configured_scanner().scan(data, at)
        assert result.status == "clean"
        redis = Redis.from_url(
            settings.OTP_RATE_REDIS_URL, socket_connect_timeout=2, socket_timeout=2
        )
        redis.set(STAGE, "scanned", ex=60)
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            time.sleep(0.1)
        raise TimeoutError("Probe barrier expired")


@shared_task(acks_late=True, reject_on_worker_lost=True, ignore_result=True)
def crash_probe(asset_uuid, processing_version, lease_uuid):
    return process_asset(
        UUID(asset_uuid),
        processing_version,
        UUID(lease_uuid),
        timezone.now(),
        scanner=CrashBarrierScanner(),
    )
