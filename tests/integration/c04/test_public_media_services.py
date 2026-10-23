"""Mandatory real MinIO/ClamAV/isolated decoder; no fake-service substitution."""

import os
from hashlib import sha256
from io import BytesIO
from urllib.error import HTTPError
from urllib.request import urlopen

import pytest
from django.utils import timezone
from PIL import Image, PngImagePlugin
from PIL.TiffImagePlugin import IFDRational

from apps.assets.scanner import configured_scanner
from apps.assets.storage import S3PrivateStore
from tests.integration.c04.publication_helpers import effective, module
from tests.integration.c04.test_public_copies import api, selected

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def raster(*, eicar=False):
    info = PngImagePlugin.PngInfo()
    info.add_text("GPSLatitude", "PRIVATE_GPS_SENTINEL")
    info.add_itxt("XML:com.adobe.xmp", "<script>PRIVATE_ACTIVE_SENTINEL</script>")
    if eicar:
        info.add_text(
            "test",
            "X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*",
        )
    exif = Image.Exif()
    exif[270] = "PRIVATE_EXIF_SENTINEL"
    exif[34853] = {
        1: "N",
        2: (IFDRational(35), IFDRational(1), IFDRational(1)),
        3: "E",
        4: (IFDRational(51), IFDRational(1), IFDRational(1)),
    }
    out = BytesIO()
    Image.new("RGB", (64, 48), (32, 96, 128)).save(
        out, format="PNG", pnginfo=info, exif=exif
    )
    return out.getvalue()


@pytest.mark.parametrize("malicious", [False, True])
def test_educational_ingress_real_quarantine_scan_decoder_and_public_copy(
    settings,
    corpus,
    malicious,
):
    from uuid import uuid4

    from apps.assets.models import Asset, PublicAssetCopy
    from apps.assets.public_copies import read_public_copy, scan_due_public_copies
    from apps.governance.outbox_models import OutboxEvent
    from apps.professionals.post_contracts import PostImageInput, PostInput
    from config.use_cases import asset_processing, public_media
    from config.use_cases import public_content as content
    from tests.integration.c04.post_helpers import draft

    real_service_settings(settings)
    subject, _ = corpus()
    post = draft(subject)
    body = raster(eicar=malicious)
    upload = content.begin_post_upload(
        subject.actor,
        post.id,
        uuid4(),
        timezone.now(),
        declared_size=len(body),
        declared_type="image/png",
    )
    upload = content.receive_post_upload(
        subject.actor, upload.id, upload.version, BytesIO(body), timezone.now()
    )
    upload = content.finalize_post_upload(
        subject.actor, upload.id, upload.version, uuid4(), timezone.now()
    )
    assert upload.state == "quarantined"
    assert content.public_post(post.id, timezone.now()) is None
    event = OutboxEvent.objects.get(
        event_type="asset.processing_requested", aggregate_uuid=upload.id
    )
    assert asset_processing.request_processing(event, timezone.now()) == "applied"
    queue = []
    assert (
        asset_processing.scan_due_assets(
            timezone.now(), 100, enqueue=lambda *args: queue.append(args)
        )
        == 1
    )
    outcome = asset_processing.process_asset(*queue[0], timezone.now())
    asset = Asset.objects.get(pk=upload.id)
    if malicious:
        assert outcome != "ready" and asset.state != "ready"
        assert not asset.derivatives.filter(state="ready").exists()
        with pytest.raises((ValueError, LookupError, PermissionError)):
            content.save_post(
                subject.actor,
                post.id,
                PostInput("آموزش", (PostImageInput(asset.id, "شرح"),)),
                post.version,
                uuid4(),
                timezone.now(),
            )
        assert not PublicAssetCopy.objects.filter(publication_uuid=post.id).exists()
        return
    assert outcome == "ready" and asset.state == "ready"
    derivative = asset.derivatives.get(purpose="post_preview", state="ready")
    store = S3PrivateStore()
    preview = store.read_limited(derivative.key, 10_000_000)
    assert b"PRIVATE_" not in preview
    unsigned_denied(settings, asset.source_key)
    unsigned_denied(settings, derivative.key)
    post = content.save_post(
        subject.actor,
        post.id,
        PostInput("آموزش", (PostImageInput(asset.id, "شرح"),)),
        post.version,
        uuid4(),
        timezone.now(),
    )
    post = content.publish_post(
        subject.actor, post.id, True, post.version, uuid4(), timezone.now()
    )
    assert content.public_post(post.id, timezone.now()) is None
    queued = []
    assert (
        scan_due_public_copies(
            timezone.now(),
            100,
            authorize=public_media.validate_release,
            enqueue=lambda *args: queued.append(args),
        )
        == 1
    )
    assert (
        public_media.process_public_copy(*queued[0], timezone.now()).status == "ready"
    )
    copy = PublicAssetCopy.objects.get(publication_uuid=post.id)
    dto = content.public_post(post.id, timezone.now())
    assert dto is not None and dto.images[0].copy_uuid == copy.id
    output = read_public_copy(
        copy.id, timezone.now(), authorize=public_media.validate_public_copy_read
    )
    assert output.content.startswith(b"\x89PNG") and b"PRIVATE_" not in output.content
    key = module("apps.assets.public_storage").publication_key(copy.id, copy.generation)
    unsigned_denied(settings, key)


def real_service_settings(settings):
    # The inherited pytest --ds=test default intentionally uses fake storage.
    # Only explicitly provisioned real services can override that fixture value.
    assert os.environ.get("STORAGE_BACKEND") == "s3"
    assert os.environ.get("ASSET_PROCESSING_ENABLED", "").casefold() in {"true", "1"}
    settings.STORAGE_BACKEND = "s3"
    settings.ASSET_PROCESSING_ENABLED = True


def prepared_real(settings, monkeypatch, *, malicious=False, wrong_mime=False):
    real_service_settings(settings)
    assert settings.STORAGE_BACKEND == "s3"
    assert settings.ASSET_PROCESSING_ENABLED is True
    store = S3PrivateStore()
    scanner = configured_scanner()
    health = BytesIO()
    Image.new("RGB", (8, 8)).save(health, format="PNG")
    assert scanner.scan(health.getvalue(), timezone.now()).status == "clean"
    person, asset, draft = selected(settings, confirmed=False)
    derivative = asset.derivatives.get(purpose="owner_preview")
    body = (
        b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
        if malicious
        else raster()
    )
    if malicious:
        assert scanner.scan(body, timezone.now()).status == "malicious"
    derivative.sha256 = sha256(body).hexdigest()
    derivative.mime_type = "image/jpeg" if wrong_mime else "image/png"
    derivative.save(update_fields=["sha256", "mime_type"])
    store.put(derivative.key, body, derivative.mime_type)
    assert store.head(derivative.key).size == len(body)
    from tests.integration.c04.publication_helpers import confirm

    confirm(person, draft)
    service = api()
    release = service.authorize_public_media(
        draft.publication_id, draft.revision_id, "avatar", timezone.now()
    )
    boundary = module("apps.assets.public_copies")
    dto = boundary.prepare_public_copy(
        release, timezone.now(), authorize=service.validate_release
    )
    reads, signed = [], []
    original = S3PrivateStore.read_limited

    def observed_read(self, key, maximum):
        assert key != asset.source_key
        reads.append(key)
        return original(self, key, maximum)

    def denied_signer(*args, **kwargs):
        signed.append(True)
        raise AssertionError("Private signer forbidden for publication")

    monkeypatch.setattr(S3PrivateStore, "read_limited", observed_read)
    monkeypatch.setattr(S3PrivateStore, "signed_read_url", denied_signer)
    scan = getattr(boundary, "scan_due_public_copies", None)
    assert callable(scan), "Missing durable public-copy claim command"
    queue = []
    assert (
        scan(
            timezone.now(),
            100,
            authorize=service.validate_release,
            enqueue=lambda *args: queue.append(args),
        )
        == 1
    )
    assert len(queue) == 1
    return person, asset, derivative, body, store, dto, queue[0], reads, signed


def unsigned_denied(settings, key):
    url = f"{settings.S3_ENDPOINT_URL}/{settings.S3_BUCKET_NAME}/{key}"
    with pytest.raises(HTTPError) as response:
        with urlopen(url, timeout=5) as stream:
            stream.read(1)
    assert response.value.code == 403
    response.value.close()


def test_exif_gps_active_payload_removed_in_new_real_private_origin_object(
    settings, monkeypatch
):
    person, asset, derivative, original, store, dto, job, reads, signed = prepared_real(
        settings, monkeypatch
    )
    process = getattr(api(), "process_public_copy", None)
    assert callable(process), "Missing real public-copy processing composition"
    result = process(*job, timezone.now())
    assert result.status == "ready"
    key = module("apps.assets.public_storage").publication_key(dto.id, dto.generation)
    output = store.read_limited(key, 10_000_000)
    assert output.startswith(b"\x89PNG\r\n\x1a\n")
    assert b"PRIVATE_" not in output
    with Image.open(BytesIO(output)) as image:
        assert image.format == "PNG" and image.size == (64, 48)
        assert not image.info and not image.getexif()
    assert store.read_limited(derivative.key, 10_000_000) == original
    assert asset.source_key not in reads and not signed
    assert effective(person) is not None
    unsigned_denied(settings, key)
    unsigned_denied(settings, derivative.key)
    from datetime import timedelta
    from uuid import uuid4

    from apps.assets.models import PublicAssetCopy
    from apps.assets.public_storage import get_publication_store
    from apps.professionals.publication_models import ProfessionalPublication
    from config.use_cases.publication import unpublish_profile
    from tests.integration.c03.test_asset_holds import policy

    copy = PublicAssetCopy.objects.get(pk=dto.id)
    publication = ProfessionalPublication.objects.get(pk=copy.publication_uuid)
    rule = policy(person, asset)
    unpublish_profile(
        person.actor, publication.id, publication.version, uuid4(), timezone.now()
    )
    at = timezone.now()
    assert api().reconcile_public_copy_lifetime(copy.id, at) == "revoked"
    assert (
        api().cleanup_public_copy(
            copy.id,
            copy.generation,
            rule.id,
            at + timedelta(seconds=2),
            publication_store=get_publication_store(),
        )
        == "deleted"
    )
    with pytest.raises(FileNotFoundError):
        store.head(key)
    assert store.read_limited(derivative.key, 10_000_000) == original


@pytest.mark.parametrize("malicious,wrong_mime", [(True, False), (False, True)])
def test_real_scanner_or_mime_rejection_never_creates_ready_copy(
    settings, monkeypatch, malicious, wrong_mime
):
    person, asset, derivative, original, store, dto, job, reads, signed = prepared_real(
        settings, monkeypatch, malicious=malicious, wrong_mime=wrong_mime
    )
    process = getattr(api(), "process_public_copy", None)
    assert callable(process), "Missing real public-copy processing composition"
    assert process(*job, timezone.now()).status != "ready"
    assert effective(person) is None
    key = module("apps.assets.public_storage").publication_key(dto.id, dto.generation)
    with pytest.raises(FileNotFoundError):
        store.head(key)
    assert not signed and asset.source_key not in reads
