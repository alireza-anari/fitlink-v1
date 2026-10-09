"""Bounded private scan result; raw daemon messages never escape this boundary."""

import re
import socket
import struct
import time
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta


@dataclass(frozen=True)
class ScanResult:
    status: str
    engine: str = ""
    signature: str = ""
    expires_at: datetime | None = None


def interpret(response: bytes, version: str, at) -> ScanResult:
    match = re.fullmatch(r"ClamAV (1\.5\.4)/(\d{1,10})/(.{24})", version)
    if not match or not isinstance(at, datetime) or at.tzinfo is None:
        return ScanResult("stale")
    try:
        stamp = datetime.strptime(match[3], "%a %b %d %H:%M:%S %Y").replace(tzinfo=UTC)
    except ValueError:
        return ScanResult("stale")
    age = at - stamp
    if not -timedelta(minutes=5) <= age <= timedelta(hours=72):
        return ScanResult("stale")
    engine, signature = "ClamAV " + match[1], match[2]
    if response == b"stream: OK\0":
        status = "clean"
    elif response.startswith(b"stream: ") and response.endswith(b" FOUND\0"):
        status = "limit" if b"Limits.Exceeded" in response else "malicious"
    elif response.startswith(b"stream: ") and response.endswith(b" ERROR\0"):
        status = "error"
    else:
        status = "unknown"
    return ScanResult(status, engine, signature, stamp + timedelta(hours=72))


class ClamScanner:
    def __init__(self, host: str, port: int, timeout: float = 10):
        if not host or type(port) is not int or not 1 <= port <= 65535:
            raise ValueError("Invalid private scanner")
        if not 0 < timeout <= 10:
            raise ValueError("Invalid scanner timeout")
        self.host, self.port, self.timeout = host, port, timeout

    def scan(self, data: bytes, at) -> ScanResult:
        if not isinstance(data, bytes) or not 0 < len(data) <= 10_000_000:
            return ScanResult("limit")
        deadline = time.monotonic() + self.timeout
        try:
            version = (
                self._command(b"zVERSION\0", None, deadline)
                .rstrip(b"\0")
                .decode("ascii")
            )
            if interpret(b"stream: OK\0", version, at).status != "clean":
                return ScanResult("stale")
            response = self._command(b"zINSTREAM\0", data, deadline)
            current = (
                self._command(b"zVERSION\0", None, deadline)
                .rstrip(b"\0")
                .decode("ascii")
            )
            if current != version:
                return ScanResult("stale")
            return interpret(response, current, at)
        except TimeoutError:
            return ScanResult("timeout")
        except ValueError:
            return ScanResult("unknown")
        except (OSError, UnicodeError):
            return ScanResult("error")

    def _command(self, command: bytes, data: bytes | None, deadline: float) -> bytes:
        def remaining():
            value = deadline - time.monotonic()
            if value <= 0:
                raise TimeoutError
            return value

        with socket.create_connection((self.host, self.port), remaining()) as conn:
            conn.settimeout(remaining())
            conn.sendall(command)
            if data is not None:
                for offset in range(0, len(data), 65536):
                    chunk = data[offset : offset + 65536]
                    conn.settimeout(remaining())
                    conn.sendall(struct.pack(">I", len(chunk)) + chunk)
                conn.sendall(b"\0\0\0\0")
            response = bytearray()
            while not response.endswith(b"\0"):
                conn.settimeout(remaining())
                part = conn.recv(513 - len(response))
                if not part:
                    raise ValueError("Invalid scanner response")
                response.extend(part)
                if len(response) > 512:
                    raise ValueError("Invalid scanner response")
            return bytes(response)


def configured_scanner() -> ClamScanner:
    from django.conf import settings

    if not settings.ASSET_PROCESSING_ENABLED:
        raise ValueError("Private processing disabled")
    return ClamScanner(settings.ASSET_SCANNER_HOST, settings.ASSET_SCANNER_PORT)
