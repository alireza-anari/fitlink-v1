"""Fail-closed image boundary; input bytes never appear in diagnostics."""

import json
import os
import selectors
import signal
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

DECODER_PATH = Path(__file__).with_name("image_decoder.py")


@dataclass(frozen=True)
class SanitizedImage:
    status: str
    data: bytes = field(default=b"", repr=False)
    mime_type: str = ""
    width: int = 0
    height: int = 0


def sanitize(data: bytes, mime_type: str, purpose: str) -> SanitizedImage:
    edges = {
        "avatar": 512,
        "logo": 512,
        "cover": 1600,
        "identity_evidence": 1600,
        "credential_evidence": 1600,
    }
    if (
        not isinstance(data, bytes)
        or not 0 < len(data) <= 10_000_000
        or mime_type not in {"image/png", "image/jpeg"}
        or purpose not in edges
    ):
        return SanitizedImage("invalid")
    try:
        raw = _run(data, [mime_type, str(edges[purpose])])
        header, body = raw.split(b"\n", 1)
        result = json.loads(header)
        if (
            result.get("status") != "clean"
            or not body.startswith(b"\x89PNG\r\n\x1a\n")
            or not 1 <= result["width"] <= edges[purpose]
            or not 1 <= result["height"] <= edges[purpose]
        ):
            return SanitizedImage("invalid")
        return SanitizedImage(
            "clean", body, "image/png", result["width"], result["height"]
        )
    except (TimeoutError, subprocess.TimeoutExpired):
        return SanitizedImage("timeout")
    except (OSError, ValueError, KeyError, TypeError):
        return SanitizedImage("unavailable")


def isolation_probe() -> dict[str, bool]:
    try:
        return json.loads(_run(b"", ["probe"]))
    except (OSError, ValueError, TimeoutError, subprocess.TimeoutExpired):
        return {}


def _run(data: bytes, args: list[str]) -> bytes:
    if not DECODER_PATH.is_file():
        raise FileNotFoundError
    # No app settings, secrets, paths or image content in argv/environment.
    with subprocess.Popen(
        [sys.executable, "-I", "-B", str(DECODER_PATH), *args],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        env={"LANG": "C.UTF-8", "C03_DECODER_PARENT_PID": str(os.getpid())},
        close_fds=True,
        start_new_session=True,
    ) as child:
        assert child.stdin is not None and child.stdout is not None
        output = bytearray()
        position = 0
        deadline = time.monotonic() + 30
        with selectors.DefaultSelector() as selector:
            os.set_blocking(child.stdin.fileno(), False)
            os.set_blocking(child.stdout.fileno(), False)
            selector.register(child.stdout, selectors.EVENT_READ)
            if data:
                selector.register(child.stdin, selectors.EVENT_WRITE)
            else:
                child.stdin.close()
            try:
                while selector.get_map():
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise TimeoutError
                    for key, _ in selector.select(min(remaining, 0.1)):
                        if key.fileobj is child.stdin:
                            position += os.write(
                                child.stdin.fileno(), data[position : position + 65536]
                            )
                            if position == len(data):
                                selector.unregister(child.stdin)
                                child.stdin.close()
                        else:
                            chunk = os.read(child.stdout.fileno(), 65536)
                            if not chunk:
                                selector.unregister(child.stdout)
                            output.extend(chunk)
                            if len(output) > 10_000_256:
                                raise ValueError("Decoder output limit")
                child.wait(timeout=max(0.01, deadline - time.monotonic()))
                if child.returncode:
                    raise ValueError("Decoder unavailable")
                return bytes(output)
            finally:
                if child.poll() is None:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait(timeout=2)
