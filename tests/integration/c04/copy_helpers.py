"""Fake I/O adapters only; ownership/confirmation and PostgreSQL remain real."""

from datetime import timedelta
from hashlib import sha256
from io import BytesIO

from django.apps import apps
from django.db import connection
from django.utils import timezone
from PIL import Image

from apps.assets.images import SanitizedImage
from apps.assets.scanner import ScanResult
from apps.assets.storage import FakePrivateStore
from tests.integration.c04.publication_helpers import module
from tests.integration.c04.test_public_copies import api, selected


def copy_model(name="PublicAssetCopy"):
    found = next(
        (m for m in apps.get_models() if m._meta.label == "assets." + name), None
    )
    assert found is not None, "Missing isolated publication copy inventory"
    return found


class ObservedStore(FakePrivateStore):
    def __init__(self):
        super().__init__()
        self.reads = []
        self.after_write = None
        self.signed_reads = 0

    def put(self, key, data, content_type):
        assert not connection.in_atomic_block
        super().put(key, data, content_type)
        if self.after_write and key.startswith("publication/"):
            self.after_write()

    def read_limited(self, key, max_bytes):
        assert not connection.in_atomic_block
        self.reads.append(key)
        return super().read_limited(key, max_bytes)

    def head(self, key):
        assert not connection.in_atomic_block
        return super().head(key)

    def signed_read_url(self, *args, **kwargs):
        self.signed_reads += 1
        raise AssertionError("Private signer must never be used")


class Scanner:
    def __init__(self, status="clean", hook=None):
        self.status, self.hook = status, hook

    def scan(self, data, at):
        assert not connection.in_atomic_block
        if self.hook:
            self.hook()
        return ScanResult(self.status, "ClamAV 1.5.4", "28000", at + timedelta(hours=1))


def clean(data, mime, purpose):
    assert not connection.in_atomic_block
    return SanitizedImage("clean", data, "image/png", 64, 48)


def pending(settings, *, claim=True):
    copy_model()
    subject, asset, draft = selected(settings)
    derivative = asset.derivatives.get(purpose="owner_preview")
    data = BytesIO()
    Image.new("RGB", (64, 48), (32, 96, 128)).save(data, format="PNG")
    body = data.getvalue()
    derivative.sha256 = sha256(body).hexdigest()
    derivative.save(update_fields=["sha256"])
    store = ObservedStore()
    store.put(derivative.key, body, "image/png")
    service = api()
    release = service.authorize_public_media(
        draft.publication_id, draft.revision_id, "avatar", timezone.now()
    )
    boundary = module("apps.assets.public_copies")
    dto = boundary.prepare_public_copy(
        release, timezone.now(), authorize=service.validate_release
    )
    queued = []
    if not claim:
        return subject, asset, draft, derivative, store, dto, None
    assert (
        boundary.scan_due_public_copies(
            timezone.now(),
            100,
            authorize=service.validate_release,
            enqueue=lambda *args: queued.append(args),
        )
        == 1
    )
    assert len(queued) == 1
    return subject, asset, draft, derivative, store, dto, queued[0]


def process(store, job, *, scanner=None, at=None):
    boundary = module("apps.assets.public_copies")
    wrapped = module("apps.assets.public_storage").PublicationObjectStore(store)
    return boundary.process_public_copy(
        *job,
        at or timezone.now(),
        authorize=api().validate_release,
        activate=api().activate_publication_media,
        source_store=store,
        publication_store=wrapped,
        scanner=scanner or Scanner(),
        sanitize=clean,
    )


def withdraw(subject, draft):
    from uuid import uuid4

    from apps.professionals.publication_models import ProfessionalPublication
    from config.use_cases.publication import unpublish_profile

    row = ProfessionalPublication.objects.get(pk=draft.publication_id)
    return unpublish_profile(
        subject.actor, row.id, row.version, uuid4(), timezone.now()
    )
