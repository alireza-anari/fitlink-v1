"""Deterministic buffered release and durable inventory races on PostgreSQL."""

from datetime import timedelta

import pytest
from django.utils import timezone

from tests.integration.c04.copy_helpers import copy_model, pending, process, withdraw
from tests.integration.c04.publication_helpers import effective, module
from tests.integration.c04.test_public_copies import api

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def test_copy_is_new_object_not_private_derivative_url(settings):
    subject, asset, draft, derivative, store, dto, job = pending(settings)
    old_keys = set(store.objects)
    result = process(store, job)
    assert result.status == "ready"
    row = copy_model().objects.get(pk=dto.id)
    assert row.state == "ready"
    attempt = copy_model("PublicCopyAttempt").objects.get(
        copy=row, generation=row.generation
    )
    assert attempt.key.startswith("publication/")
    assert attempt.key != derivative.key and attempt.key != asset.source_key
    assert set(store.objects) - old_keys == {attempt.key}
    assert asset.source_key not in store.reads and store.signed_reads == 0
    assert effective(subject) is not None


def test_revoke_during_io_prevents_ready_release(settings):
    subject, asset, draft, derivative, store, dto, job = pending(settings)
    store.after_write = lambda: withdraw(subject, draft)
    result = process(store, job)
    assert result.status == "denied"
    assert effective(subject) is None
    assert copy_model().objects.get(pk=dto.id).state != "ready"
    assert any(key.startswith("publication/") for key in store.objects)
    assert copy_model("PublicCopyAttempt").objects.filter(copy_id=dto.id).exists()


def test_crash_after_write_before_commit_is_idempotent(settings):
    subject, asset, draft, derivative, store, dto, job = pending(settings)

    class ControlledCrash(BaseException):
        pass

    def crash():
        raise ControlledCrash

    store.after_write = crash
    with pytest.raises(ControlledCrash):
        process(store, job)
    assert effective(subject) is None
    first = copy_model("PublicCopyAttempt").objects.get(
        copy_id=dto.id, generation=job[1]
    )
    assert first.key in store.objects
    later = first.lease_until + timedelta(seconds=1)
    store.after_write = None
    queue = []
    boundary = module("apps.assets.public_copies")
    assert (
        boundary.scan_due_public_copies(
            later,
            100,
            authorize=api().validate_release,
            enqueue=lambda *args: queue.append(args),
        )
        == 1
    )
    assert queue[0][1] > job[1]
    assert process(store, queue[0], at=later).status == "ready"
    assert copy_model("PublicCopyAttempt").objects.filter(copy_id=dto.id).count() == 2
    assert first.key in store.objects
    assert effective(subject, at=later) is not None


@pytest.mark.parametrize("status", ["malicious", "timeout", "stale", "error"])
def test_scanner_failure_never_marks_copy_ready(settings, status):
    from tests.integration.c04.copy_helpers import Scanner

    subject, asset, draft, derivative, store, dto, job = pending(settings)
    assert process(store, job, scanner=Scanner(status)).status != "ready"
    assert effective(subject) is None
    assert not any(key.startswith("publication/") for key in store.objects)


def test_withdraw_before_buffered_release_denies_existing_bytes(settings):
    from apps.assets.contracts import AssetNotFound

    subject, asset, draft, derivative, store, dto, job = pending(settings)
    assert process(store, job).status == "ready"
    wrapped = module("apps.assets.public_storage").PublicationObjectStore(store)

    def authorize(copy, at):
        return api().validate_public_copy_read(copy, at)

    original = store.read_limited

    def revoke_after_read(key, max_bytes):
        data = original(key, max_bytes)
        if key.startswith("publication/"):
            withdraw(subject, draft)
        return data

    store.read_limited = revoke_after_read
    with pytest.raises((AssetNotFound, PermissionError)):
        module("apps.assets.public_copies").read_public_copy(
            dto.id, timezone.now(), authorize=authorize, publication_store=wrapped
        )
    assert effective(subject) is None


def test_held_copy_never_remains_public(settings):
    from apps.assets.contracts import AssetNotFound
    from tests.integration.c03.test_asset_holds import hold, policy
    from tests.integration.c03.test_asset_holds import subject as record

    person, asset, draft, derivative, store, dto, job = pending(settings)
    assert process(store, job).status == "ready"
    attempt = copy_model("PublicCopyAttempt").objects.get(
        copy_id=dto.id, generation=job[1]
    )
    rule = policy(person, asset)
    hold(settings, person, record(asset))
    withdraw(person, draft)
    service = api()
    at = timezone.now()
    service.reconcile_public_copy_lifetime(dto.id, at)
    wrapped = module("apps.assets.public_storage").PublicationObjectStore(store)
    assert (
        service.cleanup_public_copy(
            dto.id,
            job[1],
            rule.id,
            at + timedelta(seconds=2),
            publication_store=wrapped,
        )
        == "held"
    )
    assert attempt.key in store.objects
    with pytest.raises((AssetNotFound, PermissionError)):
        module("apps.assets.public_copies").read_public_copy(
            dto.id,
            at,
            authorize=service.validate_public_copy_read,
            publication_store=wrapped,
        )
    assert effective(person) is None


def test_private_derivative_checksum_change_cannot_reauthorize_old_copy(settings):
    from apps.assets.contracts import AssetNotFound

    subject, asset, draft, derivative, store, dto, job = pending(settings)
    assert process(store, job).status == "ready"
    # C03's checksum constraint permits a different valid checksum without a
    # derivative version bump. A ready public copy must retain its own binding.
    derivative.sha256 = "0" * 64
    derivative.save(update_fields=["sha256"])
    boundary = module("apps.assets.public_copies")
    wrapped = module("apps.assets.public_storage").PublicationObjectStore(store)
    with pytest.raises(AssetNotFound):
        boundary.read_public_copy(
            dto.id,
            timezone.now(),
            store=wrapped,
            authorize=api().validate_public_copy_read,
        )
