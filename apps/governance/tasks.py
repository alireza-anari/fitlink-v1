from uuid import UUID

from django.utils import timezone

from config.celery import app

from .outbox import dispatch_event, scan_outbox


@app.task(
    name="apps.governance.tasks.deliver_event",
    acks_late=True,
    reject_on_worker_lost=True,
)
def deliver_event(event_uuid: str, lease_uuid: str) -> bool:
    try:
        return dispatch_event(
            UUID(event_uuid), timezone.now(), lease_uuid=UUID(lease_uuid)
        )
    except (ValueError, TypeError, AttributeError):
        return False


@app.task(name="apps.governance.tasks.scan_pending")
def scan_pending() -> int:
    return scan_outbox(timezone.now(), 100)
