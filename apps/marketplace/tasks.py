"""No snapshots, queries or authorization objects enter broker payloads."""

import logging

from celery import shared_task  # type: ignore[import-untyped]
from django.utils import timezone

from .contracts import ProjectionMetrics


def alert_projection_exhaustion(metrics):
    if not isinstance(metrics, ProjectionMetrics):
        raise ValueError("Invalid projection metrics")
    if metrics.exhausted:
        logging.getLogger(__name__).warning(
            "Projection outbox exhausted",
            extra={"event": "marketplace.projection_exhausted", "dependency": "outbox"},
        )


@shared_task(acks_late=True, reject_on_worker_lost=True, ignore_result=True)
def reconcile_publications():
    from config.use_cases.marketplace import projection_metrics
    from config.use_cases.marketplace import reconcile_publications as reconcile

    try:
        result = reconcile(timezone.now(), 100)
        metrics = projection_metrics(
            timezone.now(), failures=result.failures, purges=result.tombstones
        )
        alert_projection_exhaustion(metrics)
        return {
            "processed": result.processed,
            "tombstones": result.tombstones,
            **metrics.as_dict(),
        }
    except Exception:
        return {"processed": 0, "tombstones": 0, "failures": 1}
