"""Owned finite inventory for derived C04 records; no new hold authority."""

from apps.assets.privacy import MAX_INVENTORY, InventoryRecord, bounded_rows
from apps.marketplace.models import (
    ProjectionRefreshState,
    PublicLocation,
    PublicProfessionalProjection,
)
from apps.professionals.models import ProfessionalProfile


def enumerate_marketplace_inventory(owner_uuid):
    identifiers = ProfessionalProfile.objects.filter(user__public_id=owner_uuid).values(
        "id"
    )
    result = []
    for model, kind in [
        (PublicProfessionalProjection, "public_projection"),
        (ProjectionRefreshState, "public_projection_refresh"),
    ]:
        for row in bounded_rows(model.objects.filter(profile_uuid__in=identifiers)):
            result.append(
                InventoryRecord(
                    kind,
                    row.profile_uuid,
                    owner_uuid,
                    row.generation,
                    "professional_profile",
                    getattr(row, "state", ""),
                    row.profile_uuid,
                    classification="derived_public_projection",
                    deletion_behavior="suppress_projection",
                )
            )
    for row in bounded_rows(
        PublicLocation.objects.filter(projection_id__in=identifiers)
    ):
        result.append(
            InventoryRecord(
                "public_projection_location",
                row.id,
                owner_uuid,
                1,
                "professional_profile",
                parent_uuid=row.projection_id,
                classification="derived_public_projection",
                deletion_behavior="suppress_projection",
            )
        )
    if len(result) > MAX_INVENTORY:
        raise PermissionError("Inventory bound exceeded")
    return tuple(result)
