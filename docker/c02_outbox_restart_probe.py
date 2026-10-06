"""Isolated Compose rehearsal: persisted retry survives actual broker restart."""

import os
import sys
import time
from datetime import date, timedelta
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
import django  # noqa: E402

django.setup()
from django.db import transaction  # noqa: E402
from django.utils import timezone  # noqa: E402
from kombu import Connection, Producer  # noqa: E402

from apps.accounts.models import User  # noqa: E402
from apps.governance import outbox  # noqa: E402
from apps.governance.outbox_models import (  # noqa: E402
    OutboxDeliveryReceipt,
    OutboxEvent,
)

KEY = "c02:outbox:broker-restart-probe"


def prepare():
    at = timezone.now()
    with transaction.atomic():
        user = User.objects.create_user(
            "+989100000001",
            birth_date=date(1990, 1, 1),
            adult_attested_at=at,
            adult_attestation_version="adult-v1",
        )
        event_id = outbox.append_outbox(
            "account.security_changed",
            user.public_id,
            user.auth_version,
            {"user_uuid": str(user.public_id)},
            KEY,
        )
        OutboxEvent.objects.filter(pk=event_id).update(
            available_at=at + timedelta(hours=1)
        )

    def unavailable(event_id, lease_id):
        with Connection(
            "redis://127.0.0.1:1/1",
            connect_timeout=1,
            transport_options={"socket_connect_timeout": 1, "socket_timeout": 1},
        ) as broker:
            Producer(broker).publish(
                {"event_uuid": str(event_id), "lease_uuid": str(lease_id)},
                serializer="json",
                retry=False,
            )

    outbox.enqueue_event = unavailable
    assert outbox.scan_outbox(at + timedelta(hours=1)) == 1
    row = OutboxEvent.objects.get(pk=event_id)
    assert row.state == "pending" and row.last_error_code == "broker_unavailable"
    assert not OutboxDeliveryReceipt.objects.filter(event=row).exists()


def verify():
    row = OutboxEvent.objects.get(dedup_key=KEY)
    assert outbox.scan_outbox(row.available_at) == 1
    deadline = time.monotonic() + 25
    while time.monotonic() < deadline:
        row.refresh_from_db()
        if row.state == "sent":
            break
        time.sleep(0.2)
    assert (
        row.state == "sent"
        and OutboxDeliveryReceipt.objects.filter(event=row).count() == 1
    )
    # Duplicate delivery does not duplicate the durable handler receipt/effect.
    assert outbox.dispatch_event(row.id, timezone.now(), lease_uuid=uuid4())
    assert OutboxDeliveryReceipt.objects.filter(event=row).count() == 1


if __name__ == "__main__":
    {"prepare": prepare, "verify": verify}[sys.argv[1]]()
    print("Durable outbox broker restart probe passed: " + sys.argv[1])
