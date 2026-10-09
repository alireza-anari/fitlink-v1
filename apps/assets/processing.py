"""Durable private processing boundary; no raw bytes in broker messages."""

from apps.assets.models import Asset, AssetProcessingAttempt


def request_processing(event, at):
    row = Asset.objects.filter(
        pk=event.aggregate_uuid,
        processing_version=event.aggregate_version,
        owner__public_id=event.payload["user_uuid"],
        state="quarantined",
    ).first()
    if row is None:
        return "skipped"
    AssetProcessingAttempt.objects.get_or_create(
        asset=row,
        processing_version=row.processing_version,
        attempt=1,
    )
    return "applied"


def scan_due_assets(at, batch_size=100, *, enqueue=None):
    return 0


def process_asset(
    asset_uuid, processing_version, lease_uuid, at, *, store=None, scanner=None
):
    return "unavailable"
