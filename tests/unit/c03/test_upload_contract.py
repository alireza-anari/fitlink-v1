"""Bounded store operations must not publish oversized or overwrite sources."""

import importlib
import importlib.util
from io import BytesIO

import pytest

from apps.assets.storage import FakePrivateStore

pytestmark = pytest.mark.unit


def test_real_asgi_application_rejects_oversized_ingress_before_parsing():
    import asyncio

    from asgiref.testing import ApplicationCommunicator

    from config.asgi import application

    async def run():
        identifier = "00000000-0000-0000-0000-000000000001"
        communicator = ApplicationCommunicator(
            application,
            {
                "type": "http",
                "asgi": {"version": "3.0"},
                "http_version": "1.1",
                "scheme": "http",
                "method": "POST",
                "path": f"/api/v1/profile-assets/{identifier}/body/",
                "query_string": b"",
                "headers": [
                    (b"host", b"testserver"),
                    (b"content-type", b"multipart/form-data; boundary=x"),
                ],
                "server": ("testserver", 80),
            },
        )
        for _ in range(152):
            await communicator.send_input(
                {"type": "http.request", "body": b"x" * 65536, "more_body": True}
            )
        await communicator.send_input(
            {"type": "http.request", "body": b"x" * 65536, "more_body": False}
        )
        response = await communicator.receive_output(timeout=10)
        assert response["status"] == 400
        assert (b"Cache-Control", b"no-store") in response["headers"] or (
            b"cache-control",
            b"no-store",
        ) in response["headers"]
        await communicator.wait(timeout=10)

    asyncio.run(run())


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


@pytest.mark.parametrize("header", [[], [(b"content-length", b"1")]])
def test_asgi_upload_cap_before_django_body_spooling(header):
    import asyncio

    assert importlib.util.find_spec("config.upload_ingress"), "Early ingress cap absent"
    ingress = importlib.import_module("config.upload_ingress")
    sent, delivered = [], []

    async def application(scope, receive, send):
        delivered.append(True)

    async def receive():
        return {"type": "http.request", "body": b"x" * 65536, "more_body": True}

    async def send(message):
        sent.append(message)

    scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/v1/profile-assets/00000000-0000-0000-0000-000000000001/body/",
        "headers": header,
    }
    asyncio.run(ingress.UploadBodyLimit(application)(scope, receive, send))
    assert delivered == []
    assert sent[0]["status"] == 400
    assert (b"cache-control", b"no-store") in sent[0]["headers"]
