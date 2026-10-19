"""Browser triage exposes finite categories without private exception payloads."""

import json

import pytest
from playwright.async_api import Error

from docker.c03_pytest_triage import failure_data

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    ("message", "category"),
    [
        ("Navigation is interrupted by another navigation", "navigation_interrupted"),
        ("net::ERR_CONNECTION_REFUSED", "connection_refused"),
        ("net::ERR_ABORTED", "request_aborted"),
        ("Target page, context or browser has been closed", "target_closed"),
        ("net::ERR_HTTP_RESPONSE_CODE_FAILURE", "http_response_failure"),
        ("net::ERR_EMPTY_RESPONSE", "empty_response"),
        ("net::ERR_CONNECTION_RESET", "connection_reset"),
        ("net::ERR_CONNECTION_CLOSED", "connection_closed"),
        ("Frame was detached", "frame_detached"),
        ("Page crashed", "page_crashed"),
        ("unrecognized failure", "other"),
    ],
)
def test_browser_failure_category_never_exposes_payload(message, category):
    secret = "private-token-and-health-payload"
    try:
        raise Error(message + " " + secret)
    except Error:
        info = pytest.ExceptionInfo.from_current()
    metadata = failure_data(info)
    assert metadata.get("browser_failure_category") == category
    assert secret not in json.dumps(metadata)
    assert message not in json.dumps(metadata)


def test_non_browser_exception_has_no_browser_category():
    try:
        raise ValueError("private-token")
    except ValueError:
        info = pytest.ExceptionInfo.from_current()
    assert "browser_failure_category" not in failure_data(info)
