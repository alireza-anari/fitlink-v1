"""Independent PostgreSQL connections pin profile/User lock serialization."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Event
from uuid import uuid4

import pytest
from django.db import connections
from django.utils import timezone

from apps.accounts.sessions import revoke_sessions
from apps.accounts.state import transition_account_state
from apps.governance.audit import append_event

from .profile_helpers import (
    create,
    in_connection,
    independent_create,
    make_actor,
    module,
    profile_model,
    read,
)

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.mark.parametrize("label", ["athletes", "professionals"])
def test_profile_create_race(label):
    s = make_actor()
    barrier = Barrier(2)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(
            pool.map(lambda _: independent_create(label, s.actor, barrier), range(2))
        )
    assert results[0].id == results[1].id
    assert profile_model(label).objects.count() == 1
    Receipt = module(f"apps.{label}.receipt_models").ProfileCommandReceipt
    assert Receipt.objects.count() == 2


@pytest.mark.parametrize("label", ["athletes", "professionals"])
def test_same_operation_create_race_has_one_receipt(label):
    s = make_actor()
    barrier, operation = Barrier(2), uuid4()

    def command():
        barrier.wait(timeout=10)
        return create(label, s.actor, operation, timezone.now())

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(in_connection, command) for _ in range(2)]
        results = [future.result(timeout=15) for future in futures]
    assert results[0] == results[1]
    assert profile_model(label).objects.count() == 1
    assert (
        module(f"apps.{label}.receipt_models").ProfileCommandReceipt.objects.count()
        == 1
    )


@pytest.mark.parametrize("label", ["athletes", "professionals"])
@pytest.mark.parametrize(
    "transition", ["restricted", "suspended", "pending_deletion", "logout"]
)
@pytest.mark.parametrize("first", ["create", "invalidate"])
def test_create_state_and_logout_races_preserve_current_authority(
    label, transition, first, monkeypatch
):
    s = make_actor()
    entered, release = Event(), Event()
    wiring = module(f"config.use_cases.{label[:-1]}_profile")
    actual = wiring.append_event

    def paused_record(*args, **kwargs):
        result = actual(*args, **kwargs)
        entered.set()
        assert release.wait(timeout=10)
        return result

    def invalidate():
        def record(outcome):
            append_event(outcome)
            if first == "invalidate":
                entered.set()
                assert release.wait(timeout=10)

        if transition == "logout":
            revoke_sessions(
                s.user, "current", timezone.now(), record, control_id=s.actor.control_id
            )
        else:
            transition_account_state(
                s.user.public_id,
                s.actor.auth_version,
                transition,
                timezone.now(),
                record,
            )

    def creation():
        return create(label, s.actor, uuid4(), timezone.now())

    connections.close_all()
    with ThreadPoolExecutor(max_workers=2) as pool:
        if first == "create":
            monkeypatch.setattr(wiring, "append_event", paused_record)
            creating = pool.submit(in_connection, creation)
            assert entered.wait(timeout=10)
            invalidating = pool.submit(in_connection, invalidate)
            release.set()
            creating.result(timeout=15)
            invalidating.result(timeout=15)
            assert profile_model(label).objects.count() == 1
        else:
            invalidating = pool.submit(in_connection, invalidate)
            assert entered.wait(timeout=10)
            creating = pool.submit(in_connection, creation)
            release.set()
            invalidating.result(timeout=15)
            with pytest.raises(PermissionError):
                creating.result(timeout=15)
            assert profile_model(label).objects.count() == 0
    with pytest.raises(PermissionError):
        read(label, s.actor, timezone.now())
    with pytest.raises(PermissionError):
        create(label, s.actor, uuid4(), timezone.now())
