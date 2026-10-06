import importlib
from uuid import uuid4

import pytest

pytestmark = pytest.mark.unit


def contract():
    module = importlib.import_module("apps.governance.outbox")
    assert hasattr(module, "scan_outbox"), "missing durable outbox scanner"
    return module


@pytest.mark.parametrize("attempt", [1, 2, 4, 7, 8])
def test_retry_delays_are_bounded_and_positive(attempt):
    assert 0 < contract().retry_seconds(attempt) <= 300


@pytest.mark.parametrize("attempt", [0, 9, True, -1])
def test_invalid_retry_attempt_is_rejected(attempt):
    with pytest.raises(ValueError):
        contract().retry_seconds(attempt)


@pytest.mark.parametrize(
    "event_type,schema,payload",
    [
        ("sms.send", 1, {}),
        ("account.security_changed", 2, {}),
        ("account.security_changed", 1, {"code": "001234"}),
        ("account.security_changed", 1, {"user_uuid": "bad"}),
        ("account.security_changed", 1, {}),
    ],
)
def test_unknown_or_sensitive_dispatch_envelope_fails_closed(
    event_type, schema, payload
):
    with pytest.raises(ValueError):
        contract().validate_dispatch(event_type, schema, uuid4(), 1, payload)
