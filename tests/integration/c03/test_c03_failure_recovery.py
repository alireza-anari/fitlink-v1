"""Task 13 durable crash inventory, current authority and bounded exhaustion.

Deterministic private boundaries exercise real PostgreSQL transitions; the
separate mandatory restart gate kills the actual non-eager worker with real
private MinIO and ClamAV at these same boundaries.
"""

from datetime import timedelta
from io import BytesIO
from uuid import uuid4

import pytest
from django.utils import timezone

from apps.assets.models import AssetProcessingAttempt

from .baseline_helpers import command, grant, read, save
from .processing_helpers import Scanner, api, prepared
from .profile_helpers import create
from .test_asset_holds import hold, private_store, subject
from .test_asset_processing import claimed

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


class AbruptLoss(BaseException):
    """Bypass ordinary exception handling exactly as process death would."""


class WriteFault:
    def __init__(self, store, *, after=False, abrupt=True, hook=None):
        self.store, self.after, self.abrupt, self.hook = store, after, abrupt, hook

    def __getattr__(self, name):
        return getattr(self.store, name)

    def put_stream(self, key, stream, content_type, max_bytes):
        if self.after:
            data = stream.read(max_bytes + 1)
            try:
                self.store.put_stream(key, BytesIO(data), content_type, max_bytes)
            except ValueError:
                assert self.store.read_limited(key, max_bytes) == data
        if self.hook:
            self.hook()
            return
        if self.abrupt:
            raise AbruptLoss()
        raise ConnectionError("PRIVATE_SENTINEL")


def run(s, attempt, *, store=None, scanner=None):
    return api().process_asset(
        s.asset.id,
        1,
        attempt.lease_uuid,
        timezone.now(),
        store=store or s.store,
        scanner=scanner or Scanner(),
    )


def reclaim(s, attempt):
    AssetProcessingAttempt.objects.filter(pk=attempt.pk).update(
        lease_until=timezone.now() - timedelta(seconds=1)
    )
    assert api().scan_due_assets(timezone.now(), 1, enqueue=lambda *args: None) == 1
    return AssetProcessingAttempt.objects.get(asset=s.asset, state="running")


@pytest.mark.parametrize("after", [False, True])
def test_processor_crash_before_after_derivative_write_before_commit(
    monkeypatch, after
):
    s = prepared(monkeypatch, store=private_store())
    attempt = claimed(s)
    with pytest.raises(AbruptLoss):
        run(s, attempt, store=WriteFault(s.store, after=after))
    s.asset.refresh_from_db()
    derivative = s.asset.derivatives.get()
    assert s.asset.state == "processing" and derivative.state == "pending"
    assert s.store.read_limited(s.asset.source_key, 10_000_000) == s.data
    if after:
        before = s.store.read_limited(derivative.key, 10_000_000)
        assert before
    else:
        with pytest.raises(FileNotFoundError):
            s.store.head(derivative.key)
    recovered = reclaim(s, attempt)
    assert run(s, attempt) == "denied"
    assert run(s, recovered) == "ready"
    assert run(s, recovered) == "denied"
    assert s.asset.derivatives.count() == 1
    derivative.refresh_from_db()
    assert derivative.state == "ready"
    if after:
        assert s.store.read_limited(derivative.key, 10_000_000) == before
    assert (
        AssetProcessingAttempt.objects.filter(asset=s.asset, state="ready").count() == 1
    )


@pytest.mark.parametrize("fault", ["scanner", "storage", "broker"])
def test_scanner_storage_broker_failure_recovered(monkeypatch, fault):
    s = prepared(monkeypatch, store=private_store())
    p = api()
    if fault == "broker":
        p.request_processing(s.event, timezone.now())

        def unavailable(*args):
            raise ConnectionError("PRIVATE_SENTINEL")

        assert p.scan_due_assets(timezone.now(), 1, enqueue=unavailable) == 1
    else:
        attempt = claimed(s)
        if fault == "scanner":
            assert run(s, attempt, scanner=Scanner("error")) == "scan_error"
        else:
            assert (
                run(s, attempt, store=WriteFault(s.store, abrupt=False))
                == "storage_unavailable"
            )
    s.asset.refresh_from_db()
    assert s.asset.state != "ready"
    assert not s.asset.derivatives.filter(state="ready").exists()
    pending = AssetProcessingAttempt.objects.get(asset=s.asset, state="pending")
    assert "PRIVATE_SENTINEL" not in repr(pending.__dict__)
    AssetProcessingAttempt.objects.filter(pk=pending.pk).update(
        lease_until=timezone.now() - timedelta(seconds=1)
    )
    assert p.scan_due_assets(timezone.now(), 1, enqueue=lambda *args: None) == 1
    assert (
        run(s, AssetProcessingAttempt.objects.get(asset=s.asset, state="running"))
        == "ready"
    )
    assert s.asset.derivatives.count() == 1


@pytest.mark.parametrize("change", ["account", "revocation", "hold", "consent"])
def test_current_state_consent_hold_during_job(monkeypatch, settings, change):
    s = prepared(monkeypatch, store=private_store())
    attempt = claimed(s)

    if change == "consent":
        profile = create("athletes", s.actor, uuid4(), s.at)
        baseline = command("begin_baseline", s.actor, profile.version, uuid4(), s.at)
        consent_id = grant(s, baseline)
        baseline = save(s, baseline, "basics", {"height_cm": "170.0"})

    def mutate():
        if change == "account":
            s.user.state = "restricted"
            s.user.save()
        elif change == "revocation":
            s.asset.state, s.asset.revoked_at = "revoked", timezone.now()
            s.asset.version += 1
            s.asset.save()
        elif change == "hold":
            hold(settings, s, subject(s.asset))
        else:
            command(
                "revoke_baseline_storage",
                s.actor,
                baseline.id,
                consent_id,
                1,
                uuid4(),
                timezone.now(),
            )

    result = run(s, attempt, scanner=Scanner(hook=mutate))
    if change == "consent":
        assert result == "ready"
        assert read(s, baseline, timezone.now()).answers["height_cm"] is None
        assert not read(s, baseline, timezone.now()).optional_access
    else:
        assert result == "denied"
        assert not s.asset.derivatives.filter(state="ready").exists()
    assert s.store.read_limited(s.asset.source_key, 10_000_000) == s.data
    # Installed self-storage consent is baseline_storage, never invented media
    # sharing authority. Baseline withdrawal races remain mandatory in cumulative CI.


def test_bounded_exhaustion_never_ready(monkeypatch):
    s = prepared(monkeypatch, store=private_store())
    current = claimed(s)
    for number in range(1, 9):
        assert current.attempt == number
        with pytest.raises(AbruptLoss):
            run(s, current, store=WriteFault(s.store, after=number > 1))
        AssetProcessingAttempt.objects.filter(pk=current.pk).update(
            lease_until=timezone.now() - timedelta(seconds=1)
        )
        count = api().scan_due_assets(timezone.now(), 1, enqueue=lambda *args: None)
        if number < 8:
            assert count == 1
            current = AssetProcessingAttempt.objects.get(asset=s.asset, state="running")
        else:
            assert count == 0
    s.asset.refresh_from_db()
    assert s.asset.state == "rejected" and s.asset.rejection_code == "exhausted"
    assert not s.asset.derivatives.filter(state="ready").exists()
    assert s.asset.derivatives.count() == 1
    assert s.store.read_limited(s.asset.source_key, 10_000_000) == s.data
