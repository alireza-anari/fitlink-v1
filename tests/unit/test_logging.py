import json
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor

import pytest
from django.http import HttpResponse
from django.test import RequestFactory

pytestmark = pytest.mark.unit


def test_exception_visible_without_sensitive_content():
    from config.logging import JsonFormatter

    try:
        raise ValueError("credential-body-otp-secret")
    except ValueError:
        record = logging.LogRecord(
            "app",
            logging.ERROR,
            __file__,
            1,
            "secret-message",
            (),
            __import__("sys").exc_info(),
        )
    record.authorization = "Bearer private"
    output = JsonFormatter().format(record)
    value = json.loads(output)
    assert value["error_class"] == "ValueError" and value["frames"]
    assert "secret" not in output and "Bearer" not in output


@pytest.mark.parametrize("header", ["", "x" * 10000, str(uuid.uuid4())])
def test_request_id_and_redaction(header):
    from config.logging import request_id
    from config.middleware import RequestIdMiddleware

    seen = []

    def view(request):
        seen.append(request_id.get())
        return HttpResponse("ok")

    response = RequestIdMiddleware(view)(
        RequestFactory().get("/?token=private", HTTP_X_REQUEST_ID=header)
    )
    assert str(uuid.UUID(response["X-Request-ID"])) == seen[0]
    if len(header) == 36:
        assert seen[0] == header
    assert request_id.get() == "-"


def test_concurrent_correlation_isolated():
    from config.logging import request_id
    from config.middleware import RequestIdMiddleware

    def invoke(value):
        def view(request):
            assert request_id.get() == value
            return HttpResponse("ok")

        return RequestIdMiddleware(view)(
            RequestFactory().get("/", HTTP_X_REQUEST_ID=value)
        )["X-Request-ID"]

    values = [str(uuid.uuid4()) for _ in range(8)]
    with ThreadPoolExecutor(max_workers=4) as pool:
        assert list(pool.map(invoke, values)) == values
