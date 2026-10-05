"""Transient, bounded OTP transport; no production adapter is installed."""

import re
import threading
from collections import deque
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from dataclasses import dataclass, field
from typing import Protocol
from uuid import UUID

from django.conf import settings


@dataclass(frozen=True)
class DeliveryResult:
    state: str

    def __post_init__(self):
        if self.state not in {"accepted", "failed", "unknown"}:
            raise ValueError("Invalid SMS outcome")


@dataclass(frozen=True)
class SmsMessage:
    phone: str = field(repr=False)
    code: str = field(repr=False)
    correlation_id: UUID


class SmsProvider(Protocol):
    def send_otp(
        self, phone: str, code: str, correlation_id: UUID, timeout_seconds: int
    ) -> DeliveryResult: ...


class MockSmsProvider:
    """Threadsafe bounded fixture collector, available only in dev/test Python."""

    def __init__(self, state: str = "accepted"):
        if getattr(settings, "SETTINGS_ENV", "production") not in {
            "test",
            "development",
        }:
            raise ValueError("SMS adapter unavailable")
        self._state = DeliveryResult(state).state
        self._messages: deque[SmsMessage] = deque()
        self._lock = threading.Lock()

    def send_otp(
        self, phone: str, code: str, correlation_id: UUID, timeout_seconds: int
    ) -> DeliveryResult:
        if (
            getattr(settings, "SETTINGS_ENV", "production")
            not in {"test", "development"}
            or not re.fullmatch(r"\+989[0-9]{9}", phone)
            or not re.fullmatch(r"[0-9]{6}", code)
            or not 1 <= timeout_seconds <= 3
        ):
            raise ValueError("SMS adapter unavailable")
        with self._lock:
            if len(self._messages) >= 1000:
                return DeliveryResult("unknown")
            self._messages.append(SmsMessage(phone, code, correlation_id))
        return DeliveryResult(self._state)

    def drain(self) -> tuple[SmsMessage, ...]:
        with self._lock:
            result = tuple(self._messages)
            self._messages.clear()
            return result


# Capacity remains occupied until a timed-out transport actually completes;
# a stuck adapter cannot cause unbounded threads or queued plaintext messages.
_pool = ThreadPoolExecutor(max_workers=8, thread_name_prefix="otp-transport")
_capacity = threading.BoundedSemaphore(8)


def bounded_send(
    provider: SmsProvider,
    phone: str,
    code: str,
    correlation_id: UUID,
    timeout_seconds: int,
) -> DeliveryResult:
    if type(timeout_seconds) is not int or not 1 <= timeout_seconds <= 3:
        raise ValueError("Invalid SMS timeout")
    if not _capacity.acquire(blocking=False):
        return DeliveryResult("unknown")
    try:
        future = _pool.submit(
            provider.send_otp, phone, code, correlation_id, timeout_seconds
        )
    except Exception:
        _capacity.release()
        return DeliveryResult("unknown")
    future.add_done_callback(lambda ignored: _capacity.release())
    try:
        result = future.result(timeout=timeout_seconds)
        return (
            result if isinstance(result, DeliveryResult) else DeliveryResult("unknown")
        )
    except (TimeoutError, Exception):
        # Neither provider error text nor transient arguments reach logs.
        return DeliveryResult("unknown")


_mock_provider: MockSmsProvider | None = None
_provider_lock = threading.Lock()


def configured_provider() -> SmsProvider:
    global _mock_provider
    if (
        settings.ACCOUNT_SECURITY.sms_provider != "mock"
        or settings.SETTINGS_ENV not in {"test", "development"}
    ):
        raise ValueError("SMS adapter unavailable")
    with _provider_lock:
        if _mock_provider is None:
            _mock_provider = MockSmsProvider()
        return _mock_provider
