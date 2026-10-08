"""Real PostgreSQL connections pin reservation/I/O and stale-authority races."""

from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from threading import Barrier, Event
from uuid import UUID, uuid4

import pytest
from django.db import connection
from django.utils import timezone

from apps.accounts.sessions import revoke_sessions
from apps.assets.models import Asset
from apps.governance.audit import append_event
from apps.governance.outbox_models import OutboxEvent

from .profile_helpers import in_connection
from .upload_helpers import PNG, begin, body, owner, shared_store

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.mark.parametrize("invalidate", ["logout", "abandon", "archive"])
def test_receive_io_reservation_has_no_database_lock_and_rechecks_authority(
    invalidate, monkeypatch
):
    s = owner()
    dto, _ = begin(s)
    store = shared_store(monkeypatch)
    from config.use_cases import profile_assets as commands

    entered, release = Event(), Event()
    actual = store.put_stream

    def paused(*args, **kwargs):
        assert not connection.in_atomic_block, "Storage I/O holds DB transaction"
        entered.set()
        assert release.wait(timeout=15)
        return actual(*args, **kwargs)

    monkeypatch.setattr(store, "put_stream", paused)
    identifier = UUID(dto["id"])
    with ThreadPoolExecutor(max_workers=2) as pool:
        receiving = pool.submit(
            in_connection,
            lambda: commands.receive_profile_upload(
                s.actor, identifier, 1, BytesIO(PNG), timezone.now()
            ),
        )
        assert entered.wait(timeout=15)

        def invalidate_now():
            if invalidate == "logout":
                revoke_sessions(
                    s.user,
                    "current",
                    timezone.now(),
                    append_event,
                    control_id=s.actor.control_id,
                )
            elif invalidate == "archive":
                s.profile.__class__.objects.filter(pk=s.profile.pk).update(
                    state="archived"
                )
            else:
                current = Asset.objects.get(pk=identifier)
                commands.abandon_profile_upload(
                    s.actor, identifier, current.version, uuid4(), timezone.now()
                )

        invalidating = pool.submit(in_connection, invalidate_now)
        try:
            invalidating.result(timeout=5)
        finally:
            release.set()
        with pytest.raises((PermissionError, LookupError, ValueError)):
            receiving.result(timeout=15)
    row = Asset.objects.get(pk=identifier)
    assert row.accepted_at is None and row.state != "ready"
    assert not OutboxEvent.objects.filter(
        event_type="asset.processing_requested"
    ).exists()


@pytest.mark.parametrize("invalidate", ["abandon", "logout"])
def test_finalize_abandon_and_logout_races(invalidate, monkeypatch):
    s = owner()
    dto, _ = begin(s)
    store = shared_store(monkeypatch)
    response = body(s, dto)
    assert response.status_code == 200
    dto = response.json()
    from config.use_cases import profile_assets as commands

    entered, release = Event(), Event()
    actual = store.read_limited

    def paused(*args, **kwargs):
        assert not connection.in_atomic_block
        entered.set()
        assert release.wait(timeout=15)
        return actual(*args, **kwargs)

    monkeypatch.setattr(store, "read_limited", paused)
    identifier = UUID(dto["id"])
    with ThreadPoolExecutor(max_workers=2) as pool:
        finalizing = pool.submit(
            in_connection,
            lambda: commands.finalize_profile_upload(
                s.actor, identifier, dto["version"], uuid4(), timezone.now()
            ),
        )
        assert entered.wait(timeout=15)

        def invalidate_now():
            if invalidate == "logout":
                revoke_sessions(
                    s.user,
                    "current",
                    timezone.now(),
                    append_event,
                    control_id=s.actor.control_id,
                )
            else:
                commands.abandon_profile_upload(
                    s.actor, identifier, dto["version"], uuid4(), timezone.now()
                )

        invalidating = pool.submit(in_connection, invalidate_now)
        try:
            invalidating.result(timeout=5)
        finally:
            release.set()
        with pytest.raises((PermissionError, ValueError)):
            finalizing.result(timeout=15)
    assert Asset.objects.get(pk=identifier).accepted_at is None
    assert not OutboxEvent.objects.filter(
        event_type="asset.processing_requested"
    ).exists()


def test_same_operation_finalize_race_has_one_processing_effect(monkeypatch):
    s = owner()
    dto, _ = begin(s)
    shared_store(monkeypatch)
    response = body(s, dto)
    assert response.status_code == 200
    dto = response.json()
    from config.use_cases import profile_assets as commands

    barrier, operation = Barrier(2), uuid4()

    def command():
        barrier.wait(timeout=10)
        return commands.finalize_profile_upload(
            s.actor, UUID(dto["id"]), dto["version"], operation, timezone.now()
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(in_connection, command) for _ in range(2)]
        results = [f.result(timeout=15) for f in futures]
    assert results[0] == results[1]
    assert (
        OutboxEvent.objects.filter(event_type="asset.processing_requested").count() == 1
    )


def test_concurrent_pending_upload_quota_is_serialized(monkeypatch):
    s = owner()
    begin(s)
    shared_store(monkeypatch)
    for _ in range(8):
        begin(s)
    from config.use_cases import profile_assets as commands

    barrier = Barrier(2)

    def command():
        barrier.wait(timeout=10)
        try:
            return commands.begin_profile_upload(
                s.actor,
                "avatar",
                s.profile.id,
                uuid4(),
                timezone.now(),
                declared_size=len(PNG),
                declared_type="image/png",
            ).state
        except commands.UploadQuota:
            return "quota"

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(in_connection, command) for _ in range(2)]
        results = [f.result(timeout=15) for f in futures]
    assert sorted(results) == ["pending_upload", "quota"]
    assert Asset.objects.filter(state="pending_upload").count() == 10
