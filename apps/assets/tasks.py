"""Private processing task IDs only, with durable broker-loss reconciliation."""

from uuid import UUID

from celery import shared_task  # type: ignore[import-untyped]
from django.utils import timezone

from config.use_cases.asset_processing import process_asset, scan_due_assets

from .processing_worker import scan_cleanup_assets


@shared_task(acks_late=True, reject_on_worker_lost=True, ignore_result=True)
def process_private_asset(asset_uuid, processing_version, lease_uuid):
    try:
        asset_id, lease_id = UUID(asset_uuid), UUID(lease_uuid)
    except (ValueError, TypeError, AttributeError):
        return "invalid"
    try:
        return process_asset(asset_id, processing_version, lease_id, timezone.now())
    except Exception:
        # Durable expired lease recovers; broker logs receive no private exception.
        return "unavailable"


@shared_task(ignore_result=True)
def reconcile_private_assets():
    at = timezone.now()
    processing = scan_due_assets(at, 100)
    scan_cleanup_assets(at, 100)
    return processing
