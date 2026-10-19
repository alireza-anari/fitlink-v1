"""Mandatory real MinIO/ClamAV/isolated decoder; no fake-service substitution."""

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


def prepared_real(settings, monkeypatch, *, malicious=False, wrong_mime=False):
    assert settings.STORAGE_BACKEND == "s3"
    assert settings.ASSET_PROCESSING_ENABLED is True
    store = S3PrivateStore()
    scanner = configured_scanner()
    health = BytesIO()
    Image.new("RGB", (8, 8)).save(health, format="PNG")
    assert scanner.scan(health.getvalue(), timezone.now()).status == "clean"
    person, asset, draft = selected(settings)
    derivative = asset.derivatives.get(purpose="owner_preview")
    body = raster(eicar=malicious)
    derivative.sha256 = sha256(body).hexdigest()
    derivative.mime_type = "image/jpeg" if wrong_mime else "image/png"
    derivative.save(update_fields=["sha256", "mime_type"])
    store.put(derivative.key, body, derivative.mime_type)
    assert store.head(derivative.key).size == len(body)
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
