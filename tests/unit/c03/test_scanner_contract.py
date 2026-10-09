"""Real bounded sockets; no mocked CLEAN response is scanner authority."""

import importlib
import socket
import threading
from datetime import UTC, datetime

import pytest

pytestmark = pytest.mark.unit


def api():
    from importlib.util import find_spec

    assert find_spec("apps.assets.scanner"), "bounded scanner contract absent"
    return importlib.import_module("apps.assets.scanner")


@pytest.mark.parametrize(
    "response,status",
    [
        ("stream: OK\0", "clean"),
        ("stream: Eicar FOUND\0", "malicious"),
        ("stream: Heuristics.Limits.Exceeded FOUND\0", "limit"),
        ("stream: UNKNOWN\0", "unknown"),
        ("stream: error ERROR\0", "error"),
        ("PRIVATE_SENTINEL\0", "unknown"),
    ],
)
def test_scanner_malicious_unknown_timeout_and_stale_signature_closed(response, status):
    scanner = api()
    at = datetime.now(UTC)
    result = scanner.interpret(
        response.encode(),
        "ClamAV 1.5.4/28000/" + at.strftime("%a %b %d %H:%M:%S %Y"),
        at,
    )
    assert result.status == status
    assert "PRIVATE_SENTINEL" not in repr(result)
    stale = scanner.interpret(
        b"stream: OK\0", "ClamAV 1.5.4/1/Mon Jan 01 00:00:00 2024", at
    )
    assert stale.status == "stale"
    assert scanner.interpret(b"stream: OK\0", "unknown", at).status != "clean"


def server(response=None):
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen(2)

    def handle():
        try:
            with listener.accept()[0] as conn:
                conn.settimeout(1)
                conn.recv(1024)
                if response is not None:
                    conn.sendall(response)
                else:
                    threading.Event().wait(0.5)
        finally:
            listener.close()

    thread = threading.Thread(target=handle)
    thread.start()
    return listener.getsockname()[1], thread


def test_scanner_actual_timeout_and_response_cap():
    scanner = api()
    for response, status in [(None, "timeout"), (b"x" * 2048, "unknown")]:
        port, thread = server(response)
        result = scanner.ClamScanner("127.0.0.1", port, timeout=0.1).scan(
            b"PNG", datetime.now(UTC)
        )
        thread.join(2)
        assert result.status == status


def test_scanner_over_limit_before_socket():
    result = api().ClamScanner("127.0.0.1", 1).scan(b"x" * 10000001, datetime.now(UTC))
    assert result.status == "limit"
