"""Owner/session-serialized selections; every displayed target is read freshly."""

import hashlib
import json
from uuid import UUID

from django.db import transaction
from django.utils import timezone

from .contracts import MarketplaceClosed, MarketplaceUnavailable, context
from .selection_contracts import (
    ComparisonDTO,
    ComparisonScope,
    FavoriteDTO,
    SelectionConflict,
    validate_comparison_command,
    validate_favorite,
)
from .selection_models import (
    ComparisonCollection,
    ComparisonEntry,
    ComparisonReceipt,
    Favorite,
    FavoriteReceipt,
)


def _hash(*values):
    return hashlib.sha256(json.dumps(values, default=str).encode()).hexdigest()


def _favorite_ids(actor):
    ids = tuple(
        Favorite.objects.filter(owner__public_id=actor.user_uuid)
        .order_by("professional_uuid")
        .values_list("professional_uuid", flat=True)[:101]
    )
    if len(ids) > 100:
        raise MarketplaceUnavailable("Selection refresh required")
    return ids


def set_favorite(actor, identifier, selected, operation, at, *, authorize, current):
    validate_favorite(identifier, selected, operation)
    context(identifier, at)
    with transaction.atomic():
        now = max(at, timezone.now())
        owner = authorize(actor, (identifier,) if selected else (), now)
        digest = _hash(identifier, selected)
        receipt = FavoriteReceipt.objects.filter(
            owner=owner, operation_uuid=operation
        ).first()
        if receipt:
            if receipt.request_hash != digest:
                raise SelectionConflict("Selection operation conflict")
            # An old receipt never grants a new public read or stale selection.
            active = Favorite.objects.filter(
                owner=owner, professional_uuid=identifier
            ).exists()
            return FavoriteDTO(
                selected and active and current((identifier,), now)[0] is not None
            )
        if selected:
            if current((identifier,), now)[0] is None:
                raise MarketplaceClosed("Professional unavailable")
            Favorite.objects.get_or_create(owner=owner, professional_uuid=identifier)
        else:
            Favorite.objects.filter(owner=owner, professional_uuid=identifier).delete()
        FavoriteReceipt.objects.create(
            owner=owner,
            operation_uuid=operation,
            request_hash=digest,
            selected=selected,
        )
        return FavoriteDTO(selected)


def list_favorites(actor, at, *, authorize, current, release=None):
    context(UUID(int=0), at)
    with transaction.atomic():
        ids = _favorite_ids(actor)
        authorize(actor, ids, max(at, timezone.now()))
        if ids != _favorite_ids(actor):
            raise SelectionConflict("Selection changed")

        def finish(rows):
            result = tuple(row for row in rows if row is not None)
            return release(result) if release else result

        result = current(ids, max(at, timezone.now()), release=finish)
        authorize(actor, ids, max(at, timezone.now()))
        return result


def _query(scope):
    if not isinstance(scope, ComparisonScope):
        raise ValueError("Invalid comparison scope")
    scope.__post_init__()
    if scope.actor is not None:
        return ComparisonCollection.objects.filter(
            owner__public_id=scope.actor.user_uuid
        )
    return ComparisonCollection.objects.filter(
        owner__isnull=True, session_digest=scope.session_digest
    )


def _ids(collection):
    return tuple(
        ComparisonEntry.objects.filter(collection=collection)
        .order_by("slot")
        .values_list("professional_uuid", flat=True)
    )


def _locked(scope, target, at, authorize, *, create=True):
    hint = _query(scope).first()
    expected = _ids(hint) if hint else ()
    identifiers = tuple(dict.fromkeys((*expected, *((target,) if target else ()))))
    owner = authorize(scope, identifiers, at)
    if hint is None:
        if not create:
            hint = _query(scope).select_for_update().first()
            if hint is None:
                return None
        else:
            hint, _ = ComparisonCollection.objects.get_or_create(
                **(
                    {"owner": owner}
                    if owner is not None
                    else {"session_digest": scope.session_digest}
                )
            )
    row = _query(scope).select_for_update().get(pk=hint.pk)
    if expected != _ids(row):
        raise SelectionConflict("Selection changed")
    return row


def _read(row, at, current, release=None):
    def finish(rows):
        result = ComparisonDTO(
            row.version, tuple(dto for dto in rows if dto is not None)
        )
        return release(result) if release else result

    return current(_ids(row), max(at, timezone.now()), release=finish)


def read_comparison(scope, at, *, authorize, current, release=None):
    context(UUID(int=0), at)
    with transaction.atomic():
        row = _locked(scope, None, max(at, timezone.now()), authorize, create=False)
        if row is None:
            empty = ComparisonDTO(1, ())
            result = release(empty) if release else empty
        else:
            result = _read(row, at, current, release)
        authorize(scope, _ids(row) if row is not None else (), max(at, timezone.now()))
        return result


def change_comparison(
    scope, command, identifier, version, operation, at, *, authorize, current, enabled
):
    validate_comparison_command(command, identifier, version, operation)
    context(UUID(int=0), at)
    with transaction.atomic():
        now = max(at, timezone.now())
        row = _locked(scope, identifier if command == "add" else None, now, authorize)
        digest = _hash(command, identifier, version)
        receipt = ComparisonReceipt.objects.filter(
            collection=row, operation_uuid=operation
        ).first()
        if receipt:
            if receipt.request_hash != digest:
                raise SelectionConflict("Selection operation conflict")
            result = _read(row, at, current)
            authorize(scope, _ids(row), max(at, timezone.now()))
            return result
        if row.version != version:
            raise SelectionConflict("Selection version conflict")
        entries = ComparisonEntry.objects.filter(collection=row)
        if command == "add":
            if enabled() is not True or current((identifier,), now)[0] is None:
                raise MarketplaceClosed("Professional unavailable")
            if not entries.filter(professional_uuid=identifier).exists():
                used = set(entries.values_list("slot", flat=True))
                free = next((slot for slot in range(1, 4) if slot not in used), None)
                if free is None:
                    raise SelectionConflict("Comparison limit reached")
                ComparisonEntry.objects.create(
                    collection=row, professional_uuid=identifier, slot=free
                )
        elif command == "remove":
            entries.filter(professional_uuid=identifier).delete()
        else:
            entries.delete()
        row.version += 1
        row.updated_at = max(at, timezone.now())
        row.save(update_fields=["version", "updated_at"])
        ComparisonReceipt.objects.create(
            collection=row, operation_uuid=operation, request_hash=digest
        )
        result = _read(row, at, current)
        authorize(scope, _ids(row), max(at, timezone.now()))
        return result
