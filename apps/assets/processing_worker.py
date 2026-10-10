"""Durable bounded cleanup scan; broker prompts carry no deletion authority."""

from datetime import datetime
from uuid import uuid4

from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.governance.privacy_models import RetentionPolicy

from .models import Asset
from .privacy import asset_data_class


def scan_cleanup_assets(at, batch_size=100, *, store=None):
    if (
        not settings.ASSET_CLEANUP_ENABLED
        or type(batch_size) is not int
        or not 1 <= batch_size <= 100
        or not isinstance(at, datetime)
        or not timezone.is_aware(at)
        or transaction.get_connection().in_atomic_block
    ):
        return 0
    # Installed current-state predicates remain authoritative after missed events.
    query = Asset.objects.filter(
        Q(state__in=["rejected", "abandoned", "revoked", "deletion_pending", "deleted"])
        | Q(
            state__in=["pending_upload", "receiving", "quarantined"],
            accepted_at__isnull=True,
            upload_expires_at__lte=at,
        )
        | (Q(owner__is_active=False) | ~Q(owner__state="active"))
    ).order_by("updated_at", "pk")
    identifiers = list(query.values_list("id", flat=True)[:batch_size])
    from config.use_cases.c03_privacy import cleanup_asset, reconcile_asset_lifetime

    for identifier in identifiers:
        try:
            reconcile_asset_lifetime(identifier, at)
            row = Asset.objects.filter(pk=identifier).first()
            if row is None:
                continue
            policy = RetentionPolicy.objects.filter(
                data_class=asset_data_class(row),
                purpose=row.purpose,
                status="effective",
            ).first()
            cleanup_asset(
                identifier,
                row.version,
                policy.id if policy else uuid4(),
                at,
                store=store,
            )
            # Fair rotation includes held/missing-policy rows and deleted keys,
            # so a late old writer is discovered without a listing of the bucket.
            Asset.objects.filter(pk=identifier).update(updated_at=at)
        except Exception:
            # Current-state release still denies. A later tick retries metadata;
            # no arbitrary exception/private key is persisted or logged.
            continue
    return len(identifiers)
