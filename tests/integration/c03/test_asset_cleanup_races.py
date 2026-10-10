"""Independent PostgreSQL participants and late immutable private writes."""

from concurrent.futures import ThreadPoolExecutor, TimeoutError
from datetime import timedelta
from io import BytesIO
from threading import Barrier, Event
from uuid import uuid4

import pytest
from django.core.exceptions import PermissionDenied
from django.db import connection, transaction
from django.utils import timezone

from apps.assets.models import Asset
from config.use_cases import profile_assets

from .profile_helpers import in_connection
from .test_asset_holds import (
    absent,
    api,
    authority,
    cleanup,
    hold,
    media,
    policy,
    privacy_case,
    revoke,
    subject,
)
from .test_professional_setup import owner

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def test_hold_vs_cleanup_race(settings):
    assert connection.vendor == "postgresql"
    s = owner()
    asset, store = media(s)
    revoke(asset)
    rule, record, case = policy(s, asset), subject(asset), privacy_case(s)
    staff, step = authority(settings, case)
    barrier = Barrier(2)

    def apply():
        barrier.wait(timeout=10)
        at = timezone.now()
        try:
            return api(
                "apply_c03_hold",
                staff.actor,
                record,
                case,
                "security",
                "hold_applied",
                at + timedelta(seconds=10),
                at + timedelta(minutes=2),
                step,
                at,
            )
        except (PermissionError, PermissionDenied):
            return "denied"

    def erase():
        barrier.wait(timeout=10)
        return api(
            "cleanup_asset",
            asset.id,
            record.version,
            rule.id,
            timezone.now(),
            store=store,
        )

    with ThreadPoolExecutor(2) as pool:
        first, second = (
            pool.submit(in_connection, apply),
            pool.submit(in_connection, erase),
        )
        held, result = first.result(timeout=30), second.result(timeout=30)
    if held != "denied":
        assert result == "held"
        assert store.head(asset.source_key).size > 0
        assert store.head(asset.derivatives.get().key).size > 0
    else:
        assert result == "deleted"
        absent(store, asset.source_key)


def test_hold_cannot_attach_after_committed_delete_reservation(settings):
    s = owner()
    asset, store = media(s)
    revoke(asset)
    record, case, rule = subject(asset), privacy_case(s), policy(s, asset)
    staff, step = authority(settings, case)
    entered, resume = Event(), Event()

    class Blocked:
        def delete(self, key):
            assert not connection.in_atomic_block
            entered.set()
            assert resume.wait(timeout=15)
            store.delete(key)

        def head(self, key):
            return store.head(key)

    with ThreadPoolExecutor(2) as pool:
        future = pool.submit(
            in_connection,
            lambda: api(
                "cleanup_asset",
                asset.id,
                record.version,
                rule.id,
                timezone.now(),
                store=Blocked(),
            ),
        )
        try:
            assert entered.wait(timeout=10)
            at = timezone.now()
            asset.refresh_from_db()
            assert asset.state == "deletion_pending"
            with pytest.raises((PermissionError, PermissionDenied)):
                api(
                    "apply_c03_hold",
                    staff.actor,
                    subject(asset),
                    case,
                    "security",
                    "hold_applied",
                    at + timedelta(seconds=10),
                    at + timedelta(minutes=2),
                    step,
                    at,
                )
        finally:
            resume.set()
        assert future.result(timeout=30) == "deleted"


def test_cleanup_policy_change_during_io_never_reports_completion():
    s = owner()
    asset, store = media(s)
    revoke(asset)
    rule = policy(s, asset)

    class Superseding:
        def delete(self, key):
            assert not connection.in_atomic_block
            store.delete(key)
            rule.status = "superseded"
            rule.version += 1
            rule.save()

        def head(self, key):
            return store.head(key)

    assert cleanup(asset, rule, Superseding()) in {"conflict", "policy_required"}
    asset.refresh_from_db()
    assert asset.state == "deletion_pending"


def test_orphan_late_upload_reconciled(monkeypatch):
    s = owner()
    from .test_asset_holds import private_store

    store = private_store()
    entered, resume = Event(), Event()
    data = b"\x89PNG\r\n\x1a\nlate upload"

    class Late:
        def put_stream(self, key, content, mime, limit):
            assert not connection.in_atomic_block
            entered.set()
            assert resume.wait(timeout=15)
            store.put_stream(key, content, mime, limit)

    monkeypatch.setattr(profile_assets, "get_private_store", lambda: Late())
    dto = profile_assets.begin_profile_upload(
        s.actor,
        "avatar",
        s.profile.id,
        uuid4(),
        timezone.now(),
        declared_size=len(data),
        declared_type="image/png",
    )
    asset = Asset.objects.get(pk=dto.id)
    rule = policy(s, asset)
    # A never-accepted source uses quarantine policy, not ordinary profile media.
    rule.data_class = "asset_quarantine"
    rule.save()

    def receive():
        try:
            return profile_assets.receive_profile_upload(
                s.actor, asset.id, asset.version, BytesIO(data), timezone.now()
            )
        except (LookupError, PermissionError, RuntimeError, ValueError):
            return "denied"

    with ThreadPoolExecutor(2) as pool:
        upload = pool.submit(in_connection, receive)
        try:
            assert entered.wait(timeout=10)
            asset.refresh_from_db()
            profile_assets.abandon_profile_upload(
                s.actor, asset.id, asset.version, uuid4(), timezone.now()
            )
            asset.refresh_from_db()
            assert (
                cleanup(asset, rule, store, timezone.now() + timedelta(seconds=2))
                == "deleted"
            )
        finally:
            resume.set()
        assert upload.result(timeout=30) == "denied"
    assert store.head(asset.source_key).size == len(data)
    assert (
        cleanup(asset, rule, store, timezone.now() + timedelta(seconds=3)) == "deleted"
    )
    absent(store, asset.source_key)


def test_bounded_reconciler_recovers_expired_upload_without_policy(
    monkeypatch, settings
):
    import importlib.util

    assert importlib.util.find_spec("apps.assets.processing_worker")
    from apps.assets.processing_worker import scan_cleanup_assets

    s = owner()
    at = timezone.now()
    asset = Asset.objects.create(
        owner=s.user,
        subject_kind="professional_profile",
        subject_uuid=s.profile.id,
        purpose="avatar",
        source_key="quarantine/" + uuid4().hex,
        state="receiving",
        upload_expires_at=at - timedelta(seconds=1),
    )
    settings.ASSET_CLEANUP_ENABLED = True
    assert scan_cleanup_assets(at, 101) == 0
    scan_cleanup_assets(at, 1)
    asset.refresh_from_db()
    assert asset.state == "abandoned" and asset.revoked_at is not None
    assert asset.state != "deleted"


def test_orphan_late_derivative_write_is_reconciled(monkeypatch, settings):
    from apps.assets.models import AssetProcessingAttempt
    from apps.assets.processing_worker import scan_cleanup_assets

    from .processing_helpers import Scanner, prepared
    from .processing_helpers import api as processing
    from .test_asset_holds import private_store

    store = private_store()
    s = prepared(monkeypatch, store=store)
    worker = processing()
    worker.request_processing(s.event, timezone.now())
    assert worker.scan_due_assets(timezone.now(), 1, enqueue=lambda *args: None) == 1
    attempt = AssetProcessingAttempt.objects.get(asset=s.asset, state="running")
    entered, resume = Event(), Event()

    class LateDerivative:
        def read_limited(self, *args):
            return store.read_limited(*args)

        def head(self, key):
            return store.head(key)

        def put_stream(self, *args):
            assert not connection.in_atomic_block
            entered.set()
            assert resume.wait(timeout=15)
            return store.put_stream(*args)

    with ThreadPoolExecutor(2) as pool:
        future = pool.submit(
            in_connection,
            lambda: worker.process_asset(
                s.asset.id,
                1,
                attempt.lease_uuid,
                timezone.now(),
                store=LateDerivative(),
                scanner=Scanner(),
            ),
        )
        try:
            assert entered.wait(timeout=35)
            s.asset.refresh_from_db()
            revoke(s.asset, timezone.now() - timedelta(seconds=2))
            assert cleanup(s.asset, policy(s, s.asset), store) == "deleted"
        finally:
            resume.set()
        assert future.result(timeout=35) != "ready"
    child = s.asset.derivatives.get()
    assert child.state == "deleted" and store.head(child.key).size > 0
    settings.ASSET_CLEANUP_ENABLED = True
    assert scan_cleanup_assets(timezone.now(), 1, store=store) == 1
    absent(store, child.key)
    absent(store, s.asset.source_key)


@pytest.mark.parametrize("finalized", [False, True])
def test_expired_received_source_only_retires_before_acceptance(
    monkeypatch, settings, finalized
):
    from apps.assets.processing_worker import scan_cleanup_assets

    from .test_asset_holds import private_store
    from .upload_helpers import PNG

    s, store = owner(), private_store()
    monkeypatch.setattr(profile_assets, "get_private_store", lambda: store)
    dto = profile_assets.begin_profile_upload(
        s.actor,
        "avatar",
        s.profile.id,
        uuid4(),
        timezone.now(),
        declared_size=len(PNG),
        declared_type="image/png",
    )
    dto = profile_assets.receive_profile_upload(
        s.actor, dto.id, dto.version, BytesIO(PNG), timezone.now()
    )
    if finalized:
        dto = profile_assets.finalize_profile_upload(
            s.actor, dto.id, dto.version, uuid4(), timezone.now()
        )
    asset = Asset.objects.get(pk=dto.id)
    assert asset.state == "quarantined"
    at = timezone.now()
    Asset.objects.filter(pk=asset.id).update(
        upload_expires_at=at - timedelta(seconds=1)
    )
    rule = policy(s, asset)
    if not finalized:
        rule.data_class = "asset_quarantine"
        rule.save()
    settings.ASSET_CLEANUP_ENABLED = True
    assert scan_cleanup_assets(at, 1, store=store) == int(not finalized)
    asset.refresh_from_db()
    assert asset.state == ("quarantined" if finalized else "abandoned")
    assert store.head(asset.source_key).size == len(PNG)
    assert scan_cleanup_assets(at + timedelta(seconds=2), 1, store=store) == int(
        not finalized
    )
    asset.refresh_from_db()
    if finalized:
        assert asset.state == "quarantined" and asset.revoked_at is None
        assert store.head(asset.source_key).size == len(PNG)
    else:
        assert asset.state == "deleted"
        absent(store, asset.source_key)


@pytest.mark.parametrize("failure", ["scanner", "exhaustion"])
@pytest.mark.parametrize("held", [False, True])
def test_terminal_processing_source_retires_under_policy(
    monkeypatch, settings, failure, held
):
    from apps.assets.models import AssetProcessingAttempt
    from apps.assets.processing_worker import scan_cleanup_assets

    from .processing_helpers import Scanner, prepared
    from .processing_helpers import api as processing
    from .test_asset_holds import private_store

    s = prepared(monkeypatch, store=private_store())
    if held:
        hold(settings, s, subject(s.asset))
    worker = processing()
    worker.request_processing(s.event, timezone.now())
    assert worker.scan_due_assets(timezone.now(), 1, enqueue=lambda *args: None) == 1
    attempt = AssetProcessingAttempt.objects.get(asset=s.asset, state="running")
    if failure == "scanner":
        assert (
            worker.process_asset(
                s.asset.id,
                1,
                attempt.lease_uuid,
                timezone.now(),
                store=s.store,
                scanner=Scanner("malicious"),
            )
            == "scan_malicious"
        )
    else:
        AssetProcessingAttempt.objects.filter(pk=attempt.pk).update(
            attempt=8, lease_until=timezone.now() - timedelta(seconds=1)
        )
        assert (
            worker.scan_due_assets(timezone.now(), 1, enqueue=lambda *args: None) == 0
        )
    s.asset.refresh_from_db()
    assert s.asset.state == "rejected" and s.asset.accepted_at is not None
    policy(s, s.asset)
    settings.ASSET_CLEANUP_ENABLED = True
    at = timezone.now()
    assert scan_cleanup_assets(at, 1, store=s.store) == 1
    s.asset.refresh_from_db()
    # Terminal rejection is revoked metadata first; policy time starts here.
    assert s.asset.state == "revoked" and s.asset.revoked_at == at
    assert s.store.head(s.asset.source_key).size == len(s.data)
    assert scan_cleanup_assets(at + timedelta(seconds=2), 1, store=s.store) == 1
    s.asset.refresh_from_db()
    if held:
        assert s.asset.state == "revoked"
        assert s.store.head(s.asset.source_key).size == len(s.data)
    else:
        assert s.asset.state == "deleted"
        absent(s.store, s.asset.source_key)


def test_assigned_case_hold_serializes_current_verifier_grant(settings, monkeypatch):
    from apps.governance import retention
    from apps.governance.privacy_models import RecordHold
    from apps.governance.staff_models import StaffCapabilityGrant

    from .test_asset_holds import commands
    from .verification_helpers import assign, reviewer, submitted

    s = submitted()
    staff = reviewer(settings, s.case.id)
    s.case = assign(s, staff)
    case = s.profile.verifications.get(pk=s.case.id)
    record = retention.ValidatedRecordSubject(
        "professional_verification", case.id, s.user.public_id, case.version
    )
    staff, step = authority(settings, case.id, staff)
    locked, validating, resume = Event(), Event(), Event()
    validate = commands.validate_c03_hold_case

    def observed(*args, **kwargs):
        validating.set()
        return validate(*args, **kwargs)

    monkeypatch.setattr(commands, "validate_c03_hold_case", observed)

    def revoke_grant():
        with transaction.atomic():
            grant = StaffCapabilityGrant.objects.select_for_update().get(
                pk=staff.grant.id
            )
            grant.revoked_at = timezone.now()
            grant.save()
            locked.set()
            assert resume.wait(timeout=15)

    def apply():
        at = timezone.now()
        try:
            return api(
                "apply_c03_hold",
                staff.actor,
                record,
                case.id,
                "security",
                "hold_applied",
                at + timedelta(seconds=10),
                at + timedelta(minutes=2),
                step,
                at,
            )
        except (PermissionError, PermissionDenied):
            return "denied"

    with ThreadPoolExecutor(2) as pool:
        revocation = pool.submit(in_connection, revoke_grant)
        assert locked.wait(timeout=10)
        applying = pool.submit(in_connection, apply)
        try:
            assert validating.wait(timeout=10)
            # The grant write has not committed. A current-authority read must
            # wait for its row, rather than authorize from its former snapshot.
            with pytest.raises(TimeoutError):
                applying.result(timeout=1)
        finally:
            resume.set()
        revocation.result(timeout=15)
        assert applying.result(timeout=15) == "denied"
    assert not RecordHold.objects.exists()


def test_delayed_tick_starts_retention_at_actual_terminal_retirement(settings):
    from apps.assets.processing_worker import scan_cleanup_assets

    s = owner()
    asset, store = media(s)
    asset.state, asset.rejection_code = "rejected", "exhausted"
    asset.version += 1
    asset.save()
    policy(s, asset)
    settings.ASSET_CLEANUP_ENABLED = True
    started = timezone.now()
    assert scan_cleanup_assets(started - timedelta(minutes=2), 1, store=store) == 1
    asset.refresh_from_db()
    assert asset.state == "revoked" and asset.revoked_at >= started
    assert store.head(asset.source_key).size > 0
    assert (
        scan_cleanup_assets(asset.revoked_at + timedelta(seconds=2), 1, store=store)
        == 1
    )
    asset.refresh_from_db()
    assert asset.state == "deleted"
    absent(store, asset.source_key)
