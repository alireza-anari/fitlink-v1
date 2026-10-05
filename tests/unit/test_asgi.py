import httpx
import pytest
from asgiref.testing import ApplicationCommunicator

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


async def test_http_asgi_status():
    from config.asgi import application

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=application), base_url="http://testserver"
    ) as client:
        assert (await client.get("/api/v1/status/")).status_code == 200


async def test_no_business_websocket_route():
    from config.routing import websocket_urlpatterns

    assert websocket_urlpatterns == []


async def test_untrusted_origin_rejected():
    from config.asgi import application

    communicator = ApplicationCommunicator(
        application,
        {
            "type": "websocket",
            "path": "/ws/",
            "headers": [(b"origin", b"https://untrusted.invalid")],
            "query_string": b"",
        },
    )
    try:
        await communicator.send_input({"type": "websocket.connect"})
        assert (await communicator.receive_output(timeout=1))[
            "type"
        ] == "websocket.close"
    finally:
        communicator.stop()
