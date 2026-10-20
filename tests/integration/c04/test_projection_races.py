"""Actual PostgreSQL owner anchors serialize refresh and current read/revocation."""

import time
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Event

import pytest
from django.db import connection, transaction
from django.utils import timezone

from tests.integration.c03.profile_helpers import in_connection
from tests.integration.c03.test_verification_decision_races import ordered_connections
from tests.integration.c03.test_verification_revocation import revoke
from tests.integration.c04.test_public_projection import api, published

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.mark.parametrize("first", ["refresh", "revoke"])
def test_refresh_revocation_both_commit_orders(settings, first):
    subject, draft = published(settings)

    def refresh():
        return api().refresh_public_projection(subject.profile.id, timezone.now())

    def invalidate():
        return revoke(subject, "identity")

    ordered_connections(
        *((refresh, invalidate) if first == "refresh" else (invalidate, refresh))
    )
    assert api().public_professional(subject.profile.id, timezone.now()) is None
    assert (
        api().refresh_public_projection(subject.profile.id, timezone.now()).state
        == "tombstone"
    )


def test_sorted_multi_owner_locks_do_not_deadlock(settings):
    # One eligible owner plus a different real profile is enough to require two
    # User anchors even though the second profile has never been published.
    from tests.integration.c03.test_professional_setup import owner

    subject, draft = published(settings)
    second = owner("+989123456789")
    identifiers = (subject.profile.id, second.profile.id)
    barrier = Barrier(2)

    def read(order):
        barrier.wait(timeout=10)
        return api().public_professionals(order, timezone.now())

    with ThreadPoolExecutor(max_workers=2) as pool:
        a = pool.submit(in_connection, lambda: read(identifiers))
        b = pool.submit(in_connection, lambda: read(tuple(reversed(identifiers))))
        left, right = a.result(timeout=20), b.result(timeout=20)
    assert left[0] is not None and left[1] is None
    assert right[0] is None and right[1] is not None


@pytest.mark.parametrize("first", ["read", "revoke"])
def test_final_read_release_serializes_with_actual_identity_revoke(settings, first):
    subject, draft = published(settings)
    held, release, contender = Event(), Event(), Event()
    pids = {}

    def pid(name):
        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_backend_pid()")
            pids[name] = cursor.fetchone()[0]

    def read():
        pid("read")
        if first == "revoke":
            contender.set()

        def render(dto):
            if first == "read":
                held.set()
                assert release.wait(timeout=10)
            return dto.as_public_dict() if dto is not None else None

        return api().public_professional(
            subject.profile.id, timezone.now(), release=render
        )

    def invalidate():
        pid("revoke")
        if first == "read":
            contender.set()
        with transaction.atomic():
            result = revoke(subject, "identity")
            if first == "revoke":
                held.set()
                assert release.wait(timeout=10)
            return result

    with ThreadPoolExecutor(max_workers=2) as pool:
        leader = pool.submit(in_connection, read if first == "read" else invalidate)
        try:
            assert held.wait(timeout=10)
            follower = pool.submit(
                in_connection, invalidate if first == "read" else read
            )
            assert contender.wait(timeout=10)
            waiting = "revoke" if first == "read" else "read"
            deadline = time.monotonic() + 5
            blocked = []
            while time.monotonic() < deadline:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT pg_blocking_pids(%s)", [pids[waiting]])
                    blocked = cursor.fetchone()[0]
                if pids[first] in blocked:
                    break
                Event().wait(0.02)
            assert pids[first] in blocked, (
                "Expected actual PostgreSQL owner-anchor wait"
            )
        finally:
            release.set()
        a, b = leader.result(timeout=20), follower.result(timeout=20)
    assert (a is not None) if first == "read" else (b is None)
    assert api().public_professional(subject.profile.id, timezone.now()) is None
