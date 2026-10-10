"""Bounded baseline field inventory; retention grants no ordinary access."""

from .validation import NON_SENSITIVE_FIELDS, OPTIONAL_DEFAULTS

BASELINE_FIELDS = (*NON_SENSITIVE_FIELDS, *OPTIONAL_DEFAULTS)
# Submitted history is immutable. Clear draft fields or create a correction;
# full privileged erasure/export is deferred to the reviewed privacy pipeline.


def enumerate_athlete_inventory(owner_uuid):
    """All installed baselines/history, without any submitted answers."""
    from apps.assets.privacy import MAX_INVENTORY, InventoryRecord, bounded_rows

    from .baseline_models import BaselineAssessment
    from .models import AthleteProfile
    from .receipt_models import ProfileCommandReceipt

    records = []
    for row in bounded_rows(AthleteProfile.objects.filter(user__public_id=owner_uuid)):
        if (
            row.current_baseline_id is not None
            and row.current_baseline.athlete_id != row.id
        ):
            raise PermissionError("Inventory subject denied")
        records.append(
            InventoryRecord(
                "athlete_profile",
                row.id,
                owner_uuid,
                row.version,
                "athlete_profile",
                row.status,
            )
        )
    for row in bounded_rows(
        BaselineAssessment.objects.filter(athlete__user__public_id=owner_uuid)
    ):
        if row.parent_id is not None and row.parent.athlete_id != row.athlete_id:
            raise PermissionError("Inventory subject denied")
        records.append(
            InventoryRecord(
                "athlete_baseline",
                row.id,
                owner_uuid,
                row.version,
                "athlete_baseline",
                row.state,
                row.athlete_id,
            )
        )
    for row in bounded_rows(
        ProfileCommandReceipt.objects.filter(owner__public_id=owner_uuid)
    ):
        records.append(
            InventoryRecord(
                "athlete_receipt",
                row.id,
                owner_uuid,
                row.resulting_version,
                "command_receipt",
            )
        )
    if len(records) > MAX_INVENTORY:
        raise PermissionError("Inventory bound exceeded")
    return tuple(records)
