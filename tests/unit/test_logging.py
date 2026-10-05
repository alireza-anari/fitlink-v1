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


def test_uvicorn_handlers_redact_after_default_config():
    import os
    import subprocess
    import sys

    script = """
import logging, logging.config, django, uvicorn
from django.conf import settings
uvicorn.Config("config.asgi:application", access_log=False)
django.setup()
try:
    raise ValueError("private-sentinel")
except ValueError:
    logging.getLogger("uvicorn.error").exception("private-sentinel")
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        env={
            **{k: v for k, v in os.environ.items() if k == "PATH"},
            "DJANGO_SETTINGS_MODULE": "config.settings.test",
        },
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "private-sentinel" not in result.stdout + result.stderr
    assert '"error_class": "ValueError"' in result.stderr


def test_actual_server_entrypoint_preserves_redaction_and_no_proxy_trust():
    import os
    import subprocess
    import sys

    script = """
import logging, uvicorn
from config.server import main

def run(*args, **kwargs):
    assert kwargs["access_log"] is False
    assert kwargs["proxy_headers"] is False
    uvicorn.Config(*args, **kwargs)
    try:
        raise ValueError("entrypoint-private-sentinel")
    except ValueError:
        logging.getLogger("uvicorn.error").exception("entrypoint-private-sentinel")
uvicorn.run = run
main()
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        env={
            **{k: v for k, v in os.environ.items() if k == "PATH"},
            "DJANGO_SETTINGS_MODULE": "config.settings.test",
        },
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "entrypoint-private-sentinel" not in result.stdout + result.stderr
    assert '"error_class": "ValueError"' in result.stderr
    assert '"event": "process.started"' in result.stderr
