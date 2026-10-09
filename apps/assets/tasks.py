"""Private processing task IDs only, with durable broker-loss reconciliation."""

from uuid import UUID

from celery import shared_task  # type: ignore[import-untyped]
from django.utils import timezone

from .processing import process_asset


@shared_task(acks_late=True, reject_on_worker_lost=True, ignore_result=True)
def process_private_asset(asset_uuid, processing_version, lease_uuid):
    try:
        asset_id, lease_id = UUID(asset_uuid), UUID(lease_uuid)
    except (ValueError, TypeError, AttributeError):
        return "invalid"
    return process_asset(asset_id, processing_version, lease_id, timezone.now())
