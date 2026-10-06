import os
import subprocess
import sys
import time
from datetime import timedelta
from pathlib import Path
from uuid import uuid4

import pytest
from django.apps import apps
from django.db import connection
from django.utils import timezone
from test_outbox_races import capture, event

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def worker_environment():
    env = dict(os.environ)
    env["DJANGO_SETTINGS_MODULE"] = "outbox_worker_settings"
    env["PYTHONPATH"] = str(Path.cwd() / "tests/unit")
    env["C02_WORKER_TEST_DATABASE"] = connection.settings_dict["NAME"]
    env["POSTGRES_DB"] = "fitlink"
    env["POSTGRES_HOST"] = connection.settings_dict["HOST"]
    env["POSTGRES_PORT"] = str(connection.settings_dict["PORT"])
    return env


def test_actual_non_eager_worker_commits_receipt_and_duplicate_is_safe(
    monkeypatch, tmp_path
):
    from apps.governance.tasks import deliver_event
    from config.celery import app

    assert app.conf.task_always_eager is False
    module, row, _ = event()
    queue = "outbox-" + uuid4().hex
    env = worker_environment()
    # A separate queue isolates this real worker and test DB from Compose worker.
    with (tmp_path / "worker.log").open("wb") as log:
        worker = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "celery",
                "--quiet",
                "-A",
                "config.celery:app",
                "worker",
                "--pool=solo",
                "--concurrency=1",
                "--loglevel=WARNING",
                "--queues",
                queue,
                "--hostname",
                queue + "@%h",
                "--without-gossip",
                "--without-mingle",
            ],
            env=env,
            stdout=log,
            stderr=log,
        )
        try:
            monkeypatch.setattr(
                module,
                "enqueue_event",
                lambda event_id, lease_id: deliver_event.apply_async(
                    args=[str(event_id), str(lease_id)], queue=queue, retry=False
                ),
            )
            at = timezone.now()
            assert module.scan_outbox(at) == 1
            row.refresh_from_db()
            lease = row.lease_uuid
            deadline = time.monotonic() + 25
            while time.monotonic() < deadline:
                row.refresh_from_db()
                if row.state == "sent":
                    break
                assert worker.poll() is None
                time.sleep(0.2)
            assert row.state == "sent"
            duplicate = deliver_event.apply_async(
                args=[str(row.id), str(lease)], queue=queue
            )
            try:
                assert duplicate.get(timeout=15) is True
            finally:
                duplicate.forget()
            assert (
                apps.get_model("governance", "OutboxDeliveryReceipt").objects.count()
                == 1
            )
        finally:
            worker.terminate()
            try:
                worker.wait(timeout=10)
            except subprocess.TimeoutExpired:
                worker.kill()
                worker.wait(timeout=5)


def test_worker_process_crash_rolls_back_effect_then_expired_lease_recovers(
    monkeypatch,
):
    module, row, _ = event()
    sent = capture(monkeypatch, module)
    at = timezone.now()
    module.scan_outbox(at)
    token = sent[0][1]
    # Kill a separate dispatcher process after a real durable write, before commit.
    script = """
import os, django
from uuid import UUID
from django.utils import timezone
django.setup()
from apps.governance.outbox import dispatch_event
from apps.accounts.security_models import AccountSessionControl
from config import event_handlers
def crash(event, at):
    from apps.governance.outbox_models import OutboxDeliveryReceipt
    OutboxDeliveryReceipt.objects.create(
        event=event, handler=event.event_type, effect_key='crash-boundary',
        result='applied', completed_at=at
    )
    os._exit(17)
event_handlers.HANDLERS = {'account.security_changed': crash}
dispatch_event(
    UUID(os.environ['TEST_EVENT']), timezone.now(),
    lease_uuid=UUID(os.environ['TEST_LEASE'])
)
"""
    env = worker_environment()
    env["TEST_EVENT"], env["TEST_LEASE"] = str(row.id), str(token)
    process = subprocess.run(
        [sys.executable, "-c", script], env=env, capture_output=True, timeout=15
    )
    assert process.returncode == 17
    assert not apps.get_model("governance", "OutboxDeliveryReceipt").objects.exists()
    row.refresh_from_db()
    assert row.state == "leased"
    module.scan_outbox(at + timedelta(seconds=60))
    assert module.dispatch_event(
        row.id, at + timedelta(seconds=60), lease_uuid=sent[-1][1]
    )
    assert apps.get_model("governance", "OutboxDeliveryReceipt").objects.count() == 1


def test_real_broker_unavailability_persists_retry_then_restored_broker_succeeds(
    monkeypatch,
):
    from kombu import Connection, Producer

    from apps.governance.tasks import deliver_event
    from config.celery import app

    module, row, _ = event()

    def unavailable(event_id, lease_id):
        # Real TCP refusal, not a mocked broker response.
        with Connection(
            "redis://127.0.0.1:1/1",
            connect_timeout=1,
            transport_options={"socket_connect_timeout": 1, "socket_timeout": 1},
        ) as broker:
            Producer(broker).publish(
                {"event": str(event_id), "lease": str(lease_id)},
                serializer="json",
                retry=False,
            )

    monkeypatch.setattr(module, "enqueue_event", unavailable)
    module.scan_outbox(timezone.now())
    row.refresh_from_db()
    assert row.state == "pending" and row.last_error_code == "broker_unavailable"
    # Verify the actual configured Redis broker accepts a UUID-only task again.
    queue = "outbox-recovery-" + uuid4().hex
    monkeypatch.setattr(
        module,
        "enqueue_event",
        lambda event_id, lease_id: deliver_event.apply_async(
            args=[str(event_id), str(lease_id)], queue=queue, retry=False
        ),
    )
    assert module.scan_outbox(row.available_at) == 1
    row.refresh_from_db()
    assert row.state == "leased" and row.attempts == 2
    with app.connection_for_write() as broker:
        with broker.SimpleQueue(queue) as messages:
            message = messages.get(block=True, timeout=5)
            assert message.payload[0] == [str(row.id), str(row.lease_uuid)]
            message.ack()
    assert module.dispatch_event(row.id, row.available_at, lease_uuid=row.lease_uuid)
