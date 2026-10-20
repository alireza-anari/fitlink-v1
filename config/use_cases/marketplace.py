"""Composition of current professional authority and the disposable public index."""

import hashlib
import json
from datetime import timedelta
from uuid import uuid4

from django.db import DatabaseError, transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.assets.models import PublicAssetCopy, PublicCopyAttempt
from apps.governance.flags import feature_enabled
from apps.marketplace import projections, selectors
from apps.marketplace.contracts import (
    MarketplaceUnavailable,
    ProjectionMetrics,
    ProjectionSource,
    PublicMedia,
    ReconcileResult,
    context,
)
from apps.marketplace.models import ProjectionRefreshState, PublicationScanCursor
from apps.professionals.models import ProfessionalProfile, ProfessionalPublication
from apps.professionals.publication_selectors import effective_publication
from apps.professionals.selectors import publication_eligibility


def lock_owners(identifiers):
    """Resolve immutable ownership hints, then acquire all User anchors in PK order."""
    owners = ProfessionalProfile.objects.filter(pk__in=identifiers).values("user_id")
    return tuple(User.objects.select_for_update().filter(pk__in=owners).order_by("pk"))


def current_source(identifier, at):
    if feature_enabled("marketplace", raise_unavailable=True) is not True:
        return None
    at = max(at, timezone.now())
    facts = effective_publication(identifier, at)
    if facts is None:
        return None
    media = []
    from config.use_cases.public_media import validate_public_copy_read

    for purpose in sorted(facts.snapshot.get("media_purposes", [])):
        copy = PublicAssetCopy.objects.filter(
            profile_uuid=identifier,
            publication_uuid=facts.publication_id,
            release_revision_uuid=facts.revision_id,
            purpose=purpose,
            state="ready",
            revoked_at__isnull=True,
        ).first()
        if (
            copy is None
            or not PublicCopyAttempt.objects.filter(
                copy=copy, generation=copy.generation, state="ready"
            ).exists()
        ):
            return None
        try:
            validate_public_copy_read(copy, max(at, timezone.now()))
        except (PermissionError, ValueError, LookupError):
            return None
        media.append(PublicMedia(purpose, copy.id))
    eligibility = publication_eligibility(identifier, max(at, timezone.now()))
    if not eligibility.eligible or not eligibility.identity_verified:
        return None
    boundaries = [
        facts.valid_until,
        eligibility.evidence_binding.identity.next_expiry_boundary,
    ]
    boundaries.extend(
        r.next_expiry_boundary
        for r in eligibility.evidence_binding.roles
        if r.kind in facts.snapshot["verified_roles"]
    )
    expiry = min((v for v in boundaries if v is not None), default=None)
    # Restricted digest is separate from public/searchable JSON. It is an
    # optimization only; every release above re-reads authoritative sources.
    binding = [
        str(facts.publication_id),
        str(facts.revision_id),
        facts.version,
        facts.source_profile_version,
        facts.snapshot,
        [(m.purpose, str(m.copy_uuid)) for m in media],
    ]
    digest = hashlib.sha256(json.dumps(binding, sort_keys=True).encode()).hexdigest()
    return ProjectionSource(
        identifier,
        facts.publication_id,
        facts.revision_id,
        facts.version,
        facts.source_profile_version,
        facts.slug,
        json.dumps(facts.snapshot, sort_keys=True, ensure_ascii=False),
        digest,
        expiry,
        tuple(media),
    )


def public_professional(identifier, at, *, release=None):
    try:
        return selectors.public_professional(
            identifier,
            at,
            lock_owners=lock_owners,
            current_source=current_source,
            release=release,
        )
    except DatabaseError:
        raise MarketplaceUnavailable("Marketplace temporarily unavailable") from None


def public_professionals(identifiers, at, *, release=None):
    try:
        return selectors.public_professionals(
            identifiers,
            at,
            lock_owners=lock_owners,
            current_source=current_source,
            release=release,
        )
    except DatabaseError:
        raise MarketplaceUnavailable("Marketplace temporarily unavailable") from None


def refresh_public_projection(identifier, at):
    try:
        return projections.refresh_public_projection(
            identifier, at, lock_owners=lock_owners, current_source=current_source
        )
    except DatabaseError:
        raise MarketplaceUnavailable("Marketplace temporarily unavailable") from None


def reconcile_publications(at, batch_size=100):
    """Leased durable keyset scan repairs missing projections and expired work.

    The scan lease never authorizes output. An interrupted scan repeats its
    source IDs after lease expiry; refresh locks each current owner first.
    """
    if type(batch_size) is not int or not 1 <= batch_size <= 100:
        raise ValueError("Invalid publication reconciliation bound")
    context(uuid4(), at)
    if transaction.get_connection().in_atomic_block:
        raise ValueError("Reconciliation requires an independent transaction")
    now = max(at, timezone.now())
    lease = uuid4()
    with transaction.atomic():
        cursor, _ = PublicationScanCursor.objects.get_or_create(name="publications")
        cursor = PublicationScanCursor.objects.select_for_update().get(pk=cursor.pk)
        if cursor.lease_until is not None and cursor.lease_until > now:
            return ReconcileResult(0, 0, 0)
        cursor.lease_uuid = lease
        cursor.lease_until = now + timedelta(seconds=60)
        cursor.version += 1
        cursor.updated_at = now
        cursor.save()
        after = cursor.after_uuid
    # Deduplicate bounded dirty candidates and a forward source batch. Reserve
    # at least half the batch for the initial scan so dirty work cannot starve it.
    dirty = list(
        ProjectionRefreshState.objects.filter(due_at__lte=now)
        .order_by("due_at", "profile_uuid")
        .values_list("profile_uuid", flat=True)[: batch_size // 2]
    )
    source = ProfessionalPublication.objects.order_by("profile_id")
    if after is not None:
        source = source.filter(profile_id__gt=after)
    scanned = list(
        source.values_list("profile_id", flat=True)[: batch_size - len(dirty)]
    )
    identifiers = tuple(dict.fromkeys(dirty + scanned))
    processed = tombstones = failures = 0
    for identifier in identifiers:
        try:
            result = refresh_public_projection(identifier, max(at, timezone.now()))
            processed += 1
            tombstones += result.state == "tombstone"
        except (DatabaseError, MarketplaceUnavailable):
            failures += 1
    with transaction.atomic():
        cursor = PublicationScanCursor.objects.select_for_update().get(
            name="publications"
        )
        if cursor.lease_uuid == lease:
            # Keep the source cursor on failures. Due records likewise survive.
            if not failures:
                cursor.after_uuid = scanned[-1] if scanned else None
            cursor.lease_uuid = cursor.lease_until = None
            cursor.version += 1
            cursor.updated_at = max(at, timezone.now())
            cursor.save()
    return ReconcileResult(processed, tombstones, failures)


def mark_profile_due(identifier, at):
    context(identifier, at)
    projections.mark_projection_due(identifier, at)


def mark_publications_due(at):
    """One durable global rescan intent; no unbounded owner or projection lock."""
    context(uuid4(), at)
    with transaction.atomic():
        row, _ = PublicationScanCursor.objects.get_or_create(name="publications")
        row = PublicationScanCursor.objects.select_for_update().get(pk=row.pk)
        row.after_uuid = None
        # Invalidate the earlier scan's final cursor write. Its per-owner work
        # still uses fresh source authority and cannot restore an old snapshot.
        row.lease_uuid = row.lease_until = None
        row.version += 1
        row.updated_at = max(at, timezone.now())
        row.save()


def projection_metrics(at, *, failures=0, purges=0):
    """Private aggregate counters; failures/purges describe the current scan only."""
    from apps.governance.outbox_models import OutboxEvent

    context(uuid4(), at)
    due = ProjectionRefreshState.objects.filter(due_at__lte=at)
    missing = ProfessionalPublication.objects.exclude(
        profile_id__in=ProjectionRefreshState.objects.values("profile_uuid")
    )
    times = [
        due.order_by("due_at").values_list("due_at", flat=True).first(),
        missing.order_by("created_at").values_list("created_at", flat=True).first(),
    ]
    oldest = min((value for value in times if value is not None), default=at)
    events = OutboxEvent.objects.filter(event_type="professional.publication_changed")
    return ProjectionMetrics(
        backlog=due.count() + missing.count(),
        oldest_age_seconds=max(0, int((at - oldest).total_seconds())),
        failures=failures
        + events.exclude(last_error_code="").exclude(state="sent").count(),
        exhausted=events.filter(state="exhausted").count(),
        purges=purges,
    )


def search_public_professionals(criteria, cursor, at, *, release=None):
    from apps.marketplace.contracts import MarketplaceClosed
    from apps.marketplace.search import search_public_professionals as search

    try:
        if feature_enabled("marketplace", raise_unavailable=True) is not True:
            raise MarketplaceClosed("Marketplace unavailable")
        return search(
            criteria,
            cursor,
            at,
            lock_owners=lock_owners,
            current_source=current_source,
            request_refresh=mark_publications_due,
            release=release,
        )
    except DatabaseError:
        raise MarketplaceUnavailable("Marketplace temporarily unavailable") from None
