"""Decode untrusted bytes only in a bounded private subprocess."""

import importlib
import struct
import zlib
from io import BytesIO

import pytest
from PIL import Image, PngImagePlugin

pytestmark = pytest.mark.unit


def api():
    from importlib.util import find_spec

    assert find_spec("apps.assets.images"), "isolated sanitizer contract absent"
    return importlib.import_module("apps.assets.images")


def raster(fmt="PNG", size=(64, 48), metadata=True):
    image = Image.new("RGB", size, (32, 96, 128))
    output = BytesIO()
    if fmt == "PNG":
        info = PngImagePlugin.PngInfo()
        if metadata:
            info.add_text("Comment", "PRIVATE_SENTINEL")
            info.add_itxt("XML:com.adobe.xmp", "PRIVATE_SENTINEL")
        image.save(output, format=fmt, pnginfo=info, icc_profile=b"PRIVATE_SENTINEL")
    else:
        exif = Image.Exif()
        exif[270] = "PRIVATE_SENTINEL"
        image.save(
            output,
            format=fmt,
            exif=exif,
            icc_profile=b"PRIVATE_SENTINEL",
            comment=b"PRIVATE_SENTINEL",
        )
    return output.getvalue()


@pytest.mark.parametrize("fmt,mime", [("PNG", "image/png"), ("JPEG", "image/jpeg")])
@pytest.mark.parametrize(
    "purpose,edge",
    [
        ("avatar", 512),
        ("logo", 512),
        ("cover", 1600),
        ("identity_evidence", 1600),
        ("credential_evidence", 1600),
    ],
)
def test_clean_pixels_strip_all_metadata(fmt, mime, purpose, edge):
    result = api().sanitize(raster(fmt, (1800, 900)), mime, purpose)
    assert result.status == "clean"
    assert result.mime_type == "image/png"  # server-selected output
    assert result.width == edge and result.height == edge // 2
    assert b"PRIVATE_SENTINEL" not in result.data
    with Image.open(BytesIO(result.data)) as image:
        assert image.format == "PNG" and not image.info and not image.getexif()
        assert image.getpixel((0, 0)) == pytest.approx((32, 96, 128), abs=3)


def hostile(kind):
    good = raster(metadata=False)
    if kind == "truncated":
        return good[: len(good) // 2]
    if kind == "mismatch":
        return raster("JPEG")
    if kind == "invalid":
        return b"<svg><script>PRIVATE_SENTINEL</script></svg>"
    if kind == "multiframe":
        out = BytesIO()
        a = Image.new("RGB", (8, 8))
        b = Image.new("RGB", (8, 8), "red")
        a.save(out, format="PNG", save_all=True, append_images=[b], duration=10)
        return out.getvalue()
    # Correct IHDR CRC, invalid safe bounds are denied before large allocation.
    header = struct.pack(
        ">IIBBBBB", 10001 if kind == "dimension" else 5000, 5000, 8, 2, 0, 0, 0
    )
    return (
        good[:8]
        + struct.pack(">I", 13)
        + b"IHDR"
        + header
        + struct.pack(">I", zlib.crc32(b"IHDR" + header) & 0xFFFFFFFF)
        + good[33:]
    )


@pytest.mark.parametrize(
    "kind", ["truncated", "mismatch", "invalid", "multiframe", "dimension", "bomb"]
)
def test_bomb_truncated_multiframe_invalid_format(kind):
    result = api().sanitize(hostile(kind), "image/png", "avatar")
    assert result.status != "clean" and result.data == b""
    assert "PRIVATE_SENTINEL" not in repr(result)


def test_isolation_denies_network_disk_write_and_privilege():
    assert api().isolation_probe() == {
        "nonroot": True,
        "network_denied": True,
        "write_denied": True,
        "fork_denied": True,
    }


def test_decoder_absence_fails_closed(monkeypatch):
    images = api()
    monkeypatch.setattr(
        images, "DECODER_PATH", images.DECODER_PATH.with_name("absent.py")
    )
    result = images.sanitize(raster(), "image/png", "avatar")
    assert result.status == "unavailable" and result.data == b""


def test_parent_wait_timeout_is_fail_closed(monkeypatch):
    import subprocess

    images = api()

    def stalled(*args):
        raise subprocess.TimeoutExpired("private-decoder", 30)

    monkeypatch.setattr(images, "_run", stalled)
    result = images.sanitize(raster(), "image/png", "avatar")
    assert result.status == "timeout" and result.data == b""
