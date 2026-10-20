"""No snapshots, queries or authorization objects enter broker payloads."""

from celery import shared_task  # type: ignore[import-untyped]
from django.utils import timezone


@shared_task(acks_late=True, reject_on_worker_lost=True, ignore_result=True)
def reconcile_publications():
    from config.use_cases.marketplace import reconcile_publications as reconcile

    try:
        result = reconcile(timezone.now(), 100)
        return {
            "processed": result.processed,
            "tombstones": result.tombstones,
            "failures": result.failures,
        }
    except Exception:
        return {"processed": 0, "tombstones": 0, "failures": 1}
