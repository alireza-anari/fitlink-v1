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
    try:
        from config.use_cases.public_media import (
            reconcile_public_media,
            scan_due_public_copies,
        )

        scan_due_public_copies(at, 100)
        reconcile_public_media(at, 100)
    except Exception:
        # Independent durable C04 due work retries next tick; preserve the
        # inherited private processing result and never log provider content.
        pass
    return processing


@shared_task(acks_late=True, reject_on_worker_lost=True, ignore_result=True)
def process_public_asset_copy(copy_uuid, generation, lease_uuid):
    try:
        identifier, lease = UUID(copy_uuid), UUID(lease_uuid)
    except (ValueError, TypeError, AttributeError):
        return "invalid"
    if type(generation) is not int or not 1 <= generation <= 8:
        return "invalid"
    try:
        from config.use_cases.public_media import process_public_copy

        return process_public_copy(identifier, generation, lease, timezone.now()).status
    except Exception:
        return "unavailable"
