"""Magic/declared raster coherence is admission only, never safety approval."""

import importlib
import importlib.util

import pytest

pytestmark = pytest.mark.unit


def validator():
    assert importlib.util.find_spec("apps.assets.validation"), "Raster admission absent"
    return importlib.import_module("apps.assets.validation")


@pytest.mark.parametrize(
    "media,prefix,want",
    [
        ("image/png", b"\x89PNG\r\n\x1a\n", "image/png"),
        ("image/jpeg", b"\xff\xd8\xff", "image/jpeg"),
    ],
)
def test_declared_raster_signature_is_only_admission(media, prefix, want):
    assert validator().raster_signature(prefix, media) == want


@pytest.mark.parametrize(
    "media,prefix",
    [
        ("image/png", b"<html>"),
        ("image/jpeg", b"\x89PNG\r\n\x1a\n"),
        ("image/png", b"%PDF-"),
        ("image/svg+xml", b"<svg>"),
        ("image/png", b"\x89PNG"),
    ],
)
def test_spoofed_type_extension_signature(media, prefix):
    with pytest.raises(ValueError):
        validator().raster_signature(prefix, media)


@pytest.mark.parametrize(
    "size,media",
    [
        (0, "image/png"),
        (True, "image/png"),
        (10_000_001, "image/png"),
        (1, "text/html"),
        (1, "image/gif"),
    ],
)
def test_declared_contract_rejects_unbounded_or_active_inputs(size, media):
    with pytest.raises(ValueError):
        validator().validate_declaration(size, media)
