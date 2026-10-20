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
            publication_store=wrapped,
            authorize=api().validate_public_copy_read,
        )


@pytest.mark.parametrize("phase", ["before_read", "during_read", "reconcile"])
def test_private_derivative_version_change_cannot_reauthorize_old_copy(settings, phase):
    from apps.assets.contracts import AssetNotFound

    person, asset, draft, derivative, store, dto, job = pending(settings)
    assert process(store, job).status == "ready"
    service = api()
    boundary = module("apps.assets.public_copies")
    wrapped = module("apps.assets.public_storage").PublicationObjectStore(store)

    def change_version():
        derivative.version += 1
        derivative.save(update_fields=["version"])

    if phase == "during_read":
        original = store.read_limited

        def change_after_read(key, maximum):
            body = original(key, maximum)
            if key.startswith("publication/"):
                change_version()
            return body

        store.read_limited = change_after_read
    else:
        change_version()
    if phase == "reconcile":
        assert (
            service.reconcile_public_copy_lifetime(dto.id, timezone.now()) == "revoked"
        )
    with pytest.raises(AssetNotFound):
        boundary.read_public_copy(
            dto.id,
            timezone.now(),
            publication_store=wrapped,
            authorize=service.validate_public_copy_read,
        )


def test_public_read_requires_positive_current_authority_digest(settings):
    from apps.assets.contracts import AssetNotFound

    person, asset, draft, derivative, store, dto, job = pending(settings)
    assert process(store, job).status == "ready"
    wrapped = module("apps.assets.public_storage").PublicationObjectStore(store)
    with pytest.raises(AssetNotFound):
        module("apps.assets.public_copies").read_public_copy(
            dto.id,
            timezone.now(),
            authorize=lambda copy, at: None,
            publication_store=wrapped,
        )


def test_source_hold_denied_after_committed_public_copy_delete_reservation(settings):
    from django.core.exceptions import PermissionDenied

    from tests.integration.c03.test_asset_holds import hold
    from tests.integration.c03.test_asset_holds import subject as record

    person, asset, draft, derivative, store, dto, job = pending(settings, claim=False)
    row = copy_model().objects.get(pk=dto.id)
    row.state, row.revoked_at = "deletion_pending", timezone.now()
    row.updated_at = row.revoked_at
    row.version += 1
    row.save()
    with pytest.raises((PermissionError, PermissionDenied)):
        hold(settings, person, record(asset))


def test_public_copy_inventory_is_owned_bounded_metadata_without_storage_keys(settings):
    from apps.assets.privacy import enumerate_asset_inventory

    person, asset, draft, derivative, store, dto, job = pending(settings, claim=False)
    records = enumerate_asset_inventory(person.user.public_id, timezone.now())
    found = [r for r in records if r.record_uuid == dto.id]
    assert len(found) == 1, "Public copy missing from owner privacy inventory"
    assert found[0].parent_uuid == asset.id
    assert found[0].owner_uuid == person.user.public_id
    assert "publication/" not in repr(found[0])


def erase_ready_copy(settings):
    from tests.integration.c03.test_asset_holds import policy

    person, asset, draft, derivative, store, dto, job = pending(settings)
    assert process(store, job).status == "ready"
    row = copy_model().objects.get(pk=dto.id)
    attempt = row.attempts.get(generation=row.generation)
    rule = policy(person, asset)
    withdraw(person, draft)
    at = timezone.now()
    assert api().reconcile_public_copy_lifetime(row.id, at) == "revoked"
    wrapped = module("apps.assets.public_storage").PublicationObjectStore(store)
    return person, asset, derivative, store, row, attempt, rule, at, wrapped


def test_policy_cleanup_erases_public_copy_only_and_reerases_late_writer(settings):
    person, asset, derivative, store, row, attempt, rule, at, wrapped = (
        erase_ready_copy(settings)
    )
    original = store.read_limited(derivative.key, 10_000_000)
    pixels = store.read_limited(attempt.key, 10_000_000)
    assert (
        api().cleanup_public_copy(
            row.id,
            row.generation,
            rule.id,
            at + timedelta(seconds=2),
            publication_store=wrapped,
        )
        == "deleted"
    )
    assert attempt.key not in store.objects
    assert store.read_limited(derivative.key, 10_000_000) == original
    row.refresh_from_db()
    assert row.state == "deleted"
    # An expired writer cannot restore read authority. Retained inventory lets
    # a later cleanup remove its object again, rather than losing the key.
    store.put(attempt.key, pixels, "image/png")
    assert (
        api().cleanup_public_copy(
            row.id,
            row.generation,
            rule.id,
            at + timedelta(seconds=3),
            publication_store=wrapped,
        )
        == "deleted"
    )
    assert attempt.key not in store.objects
    assert store.read_limited(derivative.key, 10_000_000) == original


@pytest.mark.parametrize("late_writer", [False, True])
@pytest.mark.parametrize("observation", ["deletion_time", "audit_effect"])
def test_cleanup_replay_preserves_first_erasure_metadata(
    settings, late_writer, observation
):
    from apps.governance.audit_models import AuditEvent

    person, asset, derivative, store, row, attempt, rule, at, wrapped = (
        erase_ready_copy(settings)
    )
    pixels = store.read_limited(attempt.key, 10_000_000)
    assert (
        api().cleanup_public_copy(
            row.id,
            row.generation,
            rule.id,
            at + timedelta(seconds=2),
            publication_store=wrapped,
        )
        == "deleted"
    )
    attempt.refresh_from_db()
    first_deleted_at = attempt.deleted_at
    events = AuditEvent.objects.filter(
        action="asset.deleted", subject_uuid=attempt.id
    )
    assert events.count() == 1
    if late_writer:
        store.put(attempt.key, pixels, "image/png")
    assert (
        api().cleanup_public_copy(
            row.id,
            row.generation,
            rule.id,
            at + timedelta(seconds=3),
            publication_store=wrapped,
        )
        == "deleted"
    )
    assert attempt.key not in store.objects
    attempt.refresh_from_db()
    if observation == "deletion_time":
        assert attempt.deleted_at == first_deleted_at
    else:
        assert events.count() == 1


def test_cleanup_audit_failure_retains_reservation_and_retries(settings, monkeypatch):
    from apps.assets import cleanup

    person, asset, derivative, store, row, attempt, rule, at, wrapped = (
        erase_ready_copy(settings)
    )
    original = cleanup.append_event

    def fail(*args, **kwargs):
        raise RuntimeError("PRIVATE-AUDIT-SENTINEL")

    monkeypatch.setattr(cleanup, "append_event", fail)
    assert (
        api().cleanup_public_copy(
            row.id,
            row.generation,
            rule.id,
            at + timedelta(seconds=2),
            publication_store=wrapped,
        )
        == "retry"
    )
    row.refresh_from_db()
    assert row.state == "deletion_pending"
    assert row.attempts.get(pk=attempt.id).state == "deletion_pending"
    monkeypatch.setattr(cleanup, "append_event", original)
    assert (
        api().cleanup_public_copy(
            row.id,
            row.generation,
            rule.id,
            at + timedelta(seconds=3),
            publication_store=wrapped,
        )
        == "deleted"
    )


def test_old_generation_cleanup_preserves_current_ready_copy(settings):
    from tests.integration.c03.test_asset_holds import policy

    person, asset, draft, derivative, store, dto, job = pending(settings)

    class Crash(BaseException):
        pass

    def crash():
        raise Crash

    store.after_write = crash
    with pytest.raises(Crash):
        process(store, job)
    first = copy_model("PublicCopyAttempt").objects.get(copy_id=dto.id, generation=1)
    later = first.lease_until + timedelta(seconds=1)
    store.after_write = None
    queue = []
    assert (
        module("apps.assets.public_copies").scan_due_public_copies(
            later,
            100,
            authorize=api().validate_release,
            enqueue=lambda *args: queue.append(args),
        )
        == 1
    )
    assert process(store, queue[0], at=later).status == "ready"
    row = copy_model().objects.get(pk=dto.id)
    rule = policy(person, asset)
    wrapped = module("apps.assets.public_storage").PublicationObjectStore(store)
    assert (
        api().cleanup_public_copy(
            row.id, 1, rule.id, later + timedelta(seconds=2), publication_store=wrapped
        )
        == "deleted"
    )
    assert first.key not in store.objects
    row.refresh_from_db()
    assert row.state == "ready" and row.generation == 2
    assert effective(person, at=later + timedelta(seconds=2)) is not None
    assert (
        module("apps.assets.public_copies")
        .read_public_copy(
            row.id,
            later + timedelta(seconds=2),
            authorize=api().validate_public_copy_read,
            publication_store=wrapped,
        )
        .content
    )
