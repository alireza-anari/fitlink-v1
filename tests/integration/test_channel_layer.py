import asyncio
import uuid

import pytest
from channels.layers import get_channel_layer

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


async def test_redis_channel_send_receive():
    layer = get_channel_layer()
    channel = await layer.new_channel("foundation.")
    group = "foundation." + uuid.uuid4().hex
    try:
        await layer.group_add(group, channel)
        await layer.group_send(group, {"type": "probe", "status": "ok"})
        assert (await asyncio.wait_for(layer.receive(channel), 5))["status"] == "ok"
    finally:
        await layer.group_discard(group, channel)
        await layer.close_pools()


async def test_channel_layer_restart_reconnect():
    layer = get_channel_layer()
    await layer.close_pools()
    channel = await layer.new_channel("foundation.")
    await layer.send(channel, {"type": "probe"})
    assert (await asyncio.wait_for(layer.receive(channel), 5))["type"] == "probe"
    await layer.close_pools()
