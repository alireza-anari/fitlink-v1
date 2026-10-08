"""Bounded store operations must not publish oversized or overwrite sources."""

import importlib
import importlib.util
from io import BytesIO

import pytest

from apps.assets.storage import FakePrivateStore

pytestmark = pytest.mark.unit


def test_size_limit_without_content_length():
    store = FakePrivateStore()
    assert callable(getattr(store, "put_stream", None)), "Bounded ingress absent"
    with pytest.raises(ValueError):
        store.put_stream(
            "quarantine/opaque", BytesIO(b"x" * 10_000_001), "image/png", 10_000_000
        )
    assert store.objects == {}


def test_stream_boundary_and_source_write_once():
    store = FakePrivateStore()
    assert callable(getattr(store, "put_stream", None)), "Bounded ingress absent"
    store.put_stream(
        "quarantine/opaque", BytesIO(b"x" * 10_000_000), "image/png", 10_000_000
    )
    assert len(store.read_limited("quarantine/opaque", 10_000_000)) == 10_000_000
    with pytest.raises(ValueError):
        store.put_stream(
            "quarantine/opaque", BytesIO(b"changed"), "image/png", 10_000_000
        )
    assert len(store.objects["quarantine/opaque"]) == 10_000_000


def test_bounded_read_rejects_existing_oversized_object():
    store = FakePrivateStore()
    store.put("quarantine/opaque", b"x" * 100, "image/png")
    assert callable(getattr(store, "read_limited", None)), "Bounded reader absent"
    with pytest.raises(ValueError):
        store.read_limited("quarantine/opaque", 99)


def test_multipart_actual_request_cap_even_with_lying_header():
    assert importlib.util.find_spec("apps.assets.api"), "Multipart ingress absent"
    api = importlib.import_module("apps.assets.api")
    parser = api.BoundedMultipartParser()
    from types import SimpleNamespace

    request = SimpleNamespace(
        META={"CONTENT_LENGTH": "1"}, encoding="utf-8", upload_handlers=[]
    )
    from rest_framework.exceptions import ParseError

    with pytest.raises(ParseError):
        parser.parse(
            BytesIO(b"x" * 10_000_001),
            "multipart/form-data; boundary=x",
            {"request": request},
        )
