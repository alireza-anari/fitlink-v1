"""Independent PostgreSQL participants and late immutable private writes."""

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from io import BytesIO
from threading import Barrier, Event
from uuid import uuid4

import pytest
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.utils import timezone

from apps.assets.models import Asset
from config.use_cases import profile_assets

from .profile_helpers import in_connection
from .test_asset_holds import (
    absent,
    api,
    authority,
    cleanup,
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
