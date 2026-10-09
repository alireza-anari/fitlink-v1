"""Synthetic raster through actual owned Task 4 upload commands."""

import importlib
from datetime import timedelta
from io import BytesIO
from uuid import uuid4

from django.db import connection
from django.utils import timezone
from PIL import Image

from apps.assets.models import Asset
from apps.assets.storage import FakePrivateStore
from apps.governance.outbox_models import OutboxEvent
from config.use_cases import profile_assets

from .upload_helpers import owner


def api():
    from importlib.util import find_spec

    assert find_spec("apps.assets.processing"), "processing command absent"
    return importlib.import_module("apps.assets.processing")


def prepared(monkeypatch, data=None, store=None):
    s = owner()
    if data is None:
        output = BytesIO()
        Image.new("RGB", (64, 48), (32, 96, 128)).save(output, format="PNG")
        data = output.getvalue()
    store = store or FakePrivateStore()
    monkeypatch.setattr(profile_assets, "get_private_store", lambda: store)
    dto = profile_assets.begin_profile_upload(
        s.actor,
        "avatar",
        s.profile.id,
        uuid4(),
        timezone.now(),
        declared_size=len(data),
        declared_type="image/png",
    )
    dto = profile_assets.receive_profile_upload(
        s.actor, dto.id, dto.version, BytesIO(data), timezone.now()
    )
    dto = profile_assets.finalize_profile_upload(
        s.actor, dto.id, dto.version, uuid4(), timezone.now()
    )
    s.asset = Asset.objects.get(pk=dto.id)
    s.store = store
    s.data = data
    s.event = OutboxEvent.objects.get(event_type="asset.processing_requested")
    s.event.state = "leased"
    s.event.lease_uuid = uuid4()
    s.event.lease_until = timezone.now() + timedelta(seconds=60)
    s.event.save()
    return s


class Scanner:
    def __init__(self, status="clean", hook=None):
        self.status = status
        self.hook = hook
        self.calls = 0

    def scan(self, data, at):
        assert not connection.in_atomic_block
        self.calls += 1
        if self.hook:
            self.hook()
        from apps.assets.scanner import ScanResult

        return ScanResult(self.status, "ClamAV 1.5.4", "28000")
