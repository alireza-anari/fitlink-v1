"""Required actual private ClamAV and signature readiness, never fake-only PASS."""

from datetime import timedelta
from io import BytesIO

import pytest
from django.utils import timezone
from PIL import Image

from apps.assets.storage import S3PrivateStore

from .processing_helpers import api, prepared
from .test_asset_processing import claimed

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def scanner():
    from importlib.util import find_spec

    assert find_spec("apps.assets.scanner"), "scanner unavailable"
    from apps.assets.scanner import configured_scanner

    return configured_scanner()


def test_real_scanner_clean_malicious_and_signature_readiness():
    s = scanner()
    at = timezone.now()
    output = BytesIO()
    Image.new("RGB", (8, 8)).save(output, format="PNG")
    clean = s.scan(output.getvalue(), at)
    assert (
        clean.status == "clean" and clean.engine == "ClamAV 1.5.4" and clean.signature
    )
    # Industry test string, no real malware or private source.
    eicar = b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
    assert s.scan(eicar, at).status == "malicious"
    assert s.scan(output.getvalue(), at + timedelta(days=4)).status == "stale"
    assert s.scan(b"x" * 10000001, at).status == "limit"
    assert s.scan(output.getvalue(), at).status == "clean"


def test_real_private_minio_scanner_and_sanitizer(monkeypatch):
    store = S3PrivateStore()
    s = prepared(monkeypatch, store=store)
    attempt = claimed(s)
    try:
        assert (
            api().process_asset(
                s.asset.id,
                1,
                attempt.lease_uuid,
                timezone.now(),
                store=store,
                scanner=scanner(),
            )
            == "ready"
        )
        child = s.asset.derivatives.get(state="ready")
        assert child.mime_type == "image/png" and child.width == 64
        assert store.read_limited(s.asset.source_key, 10000000) == s.data
        assert store.read_limited(child.key, 10000000) != s.data
        assert store.backend.default_acl is None
    finally:
        store.delete(s.asset.source_key)
        for child in s.asset.derivatives.all():
            store.delete(child.key)


def test_real_daemon_stream_limit_and_incomplete_stream_timeout():
    import socket
    import struct

    s = scanner()
    assert s.scan(b"synthetic", timezone.now()).status == "clean"
    # Bypass the client's admission cap only in this synthetic service test:
    # the actual daemon must reject an announced oversized INSTREAM chunk.
    with socket.create_connection((s.host, s.port), timeout=2) as conn:
        conn.settimeout(2)
        conn.sendall(b"zINSTREAM\0" + struct.pack(">I", 10_000_001))
        response = conn.recv(512)
        assert b"size limit exceeded" in response.lower()
    # Real incomplete daemon stream, bounded caller timeout; no fake server.
    with socket.create_connection((s.host, s.port), timeout=2) as conn:
        conn.settimeout(0.1)
        conn.sendall(b"zINSTREAM\0" + struct.pack(">I", 8) + b"x")
        with pytest.raises(TimeoutError):
            conn.recv(512)
    assert s.scan(b"synthetic", timezone.now()).status == "clean"


def test_real_daemon_unknown_reply_never_becomes_clean():
    import socket
    import time

    from apps.assets.scanner import interpret

    s = scanner()
    at = timezone.now()
    assert s.scan(b"synthetic", at).status == "clean"
    version = (
        s._command(b"zVERSION\0", None, time.monotonic() + 2)
        .rstrip(b"\0")
        .decode("ascii")
    )
    with socket.create_connection((s.host, s.port), timeout=2) as conn:
        conn.settimeout(2)
        conn.sendall(b"zC03_UNKNOWN\0")
        reply = conn.recv(512)
        assert reply and interpret(reply, version, at).status == "unknown"
    assert s.scan(b"synthetic", timezone.now()).status == "clean"
