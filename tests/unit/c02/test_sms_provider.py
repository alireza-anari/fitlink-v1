import importlib
import importlib.util
import threading
import time
from uuid import uuid4

import pytest

pytestmark = pytest.mark.unit


def contract():
    assert importlib.util.find_spec("apps.accounts.sms"), "missing bounded SMS contract"
    return importlib.import_module("apps.accounts.sms")


@pytest.mark.parametrize("state", ["accepted", "failed", "unknown"])
def test_mock_delivery_state_and_private_memory_collector(state):
    sms = contract()
    provider = sms.MockSmsProvider(state)
    correlation = uuid4()
    result = provider.send_otp("+989123456789", "001234", correlation, 3)
    assert result.state == state
    messages = provider.drain()
    assert len(messages) == 1 and messages[0].code == "001234"
    assert messages[0].correlation_id == correlation
    assert "001234" not in repr(messages[0])
    assert "+989123456789" not in repr(messages[0])
    assert not provider.drain()


def test_mock_cannot_be_created_in_production(settings):
    sms = contract()
    settings.SETTINGS_ENV = "production"
    with pytest.raises(ValueError, match="SMS adapter unavailable"):
        sms.MockSmsProvider()


def test_provider_exception_is_uniform_and_does_not_log_values(caplog):
    sms = contract()

    class Broken:
        def send_otp(self, phone, code, correlation_id, timeout_seconds):
            raise RuntimeError("private-provider-001234-+989123456789")

    result = sms.bounded_send(Broken(), "+989123456789", "001234", uuid4(), 3)
    assert result.state == "unknown"
    assert "001234" not in repr(result) + caplog.text
    assert "+989123456789" not in repr(result) + caplog.text


def test_hanging_provider_returns_unknown_within_configured_bound():
    sms = contract()
    release = threading.Event()

    class Hanging:
        def send_otp(self, *args):
            release.wait(timeout=10)
            return sms.DeliveryResult("accepted")

    start = time.monotonic()
    try:
        result = sms.bounded_send(Hanging(), "+989123456789", "001234", uuid4(), 1)
        assert result.state == "unknown" and time.monotonic() - start < 2
    finally:
        release.set()
