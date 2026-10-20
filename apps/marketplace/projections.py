"""Owner-serialized derived writes; stale jobs never carry public snapshots."""

import json
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .contracts import RefreshResult, context
from .models import ProjectionRefreshState, PublicLocation, PublicProfessionalProjection
from .normalization import normalize_persian
from .search_index import index_values, search_vector


def mark_projection_due(identifier, at):
    context(identifier, at)
    ProjectionRefreshState.objects.update_or_create(
        profile_uuid=identifier,
        defaults={"due_at": at, "updated_at": max(at, timezone.now())},
    )


def refresh_public_projection(identifier, at, *, lock_owners=None, current_source=None):
    context(identifier, at)
    if not callable(lock_owners) or not callable(current_source):
        raise ValueError("Missing source authority")
    with transaction.atomic():
        lock_owners((identifier,))
        now = max(at, timezone.now())
        source = current_source(identifier, now)
        row = (
            PublicProfessionalProjection.objects.select_for_update()
            .filter(pk=identifier)
            .first()
        )
        metadata = (
            ProjectionRefreshState.objects.select_for_update()
            .filter(pk=identifier)
            .first()
        )
        # The index is disposable; retained due state owns generation continuity.
        generation = (
            max(
                row.generation if row else 0,
                metadata.generation if metadata else 0,
            )
            + 1
        )
        state = "active" if source is not None else "tombstone"
        defaults = dict(
            state=state,
            generation=generation,
            snapshot={},
            publication_uuid=None,
            revision_uuid=None,
            slug="",
            refreshed_at=now,
            updated_at=now,
            next_expiry=None,
        )
        if source is not None:
            defaults.update(
                publication_uuid=source.publication_uuid,
                revision_uuid=source.revision_uuid,
                publication_version=source.publication_version,
                source_version=source.source_version,
                slug=source.slug,
                snapshot=json.loads(source.snapshot_json),
                next_expiry=source.next_expiry,
            )
        defaults.update(index_values(defaults["snapshot"]))
        row, _ = PublicProfessionalProjection.objects.update_or_create(
            profile_uuid=identifier, defaults=defaults
        )
        PublicProfessionalProjection.objects.filter(pk=identifier).update(
            search_vector=search_vector()
        )
        PublicLocation.objects.filter(projection=row).delete()
        if source is not None:
            PublicLocation.objects.bulk_create(
                [
                    PublicLocation(
                        projection=row,
                        normalized_region=normalize_persian(location["region"]),
                        normalized_city=normalize_persian(location["city"]),
                        **location,
                    )
                    for location in defaults["snapshot"].get("locations", [])
                ]
            )
        due = now + timedelta(seconds=30)
        if source is not None and source.next_expiry is not None:
            due = min(due, source.next_expiry)
        ProjectionRefreshState.objects.update_or_create(
            profile_uuid=identifier,
            defaults=dict(
                generation=generation,
                authority_hash=source.authority_hash if source else "",
                due_at=due,
                updated_at=now,
            ),
        )
        return RefreshResult(identifier, generation, state)
