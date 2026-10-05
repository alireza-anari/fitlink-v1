import importlib
import importlib.util

import pytest


@pytest.fixture
def limiter():
    assert importlib.util.find_spec("apps.accounts.limiter"), (
        "missing real dual-store limiter"
    )
    module = importlib.import_module("apps.accounts.limiter")
    client = module.redis_client()
    assert client.connection_pool.connection_kwargs["db"] == 4
    client.flushdb()
    yield module
    client.flushdb()
