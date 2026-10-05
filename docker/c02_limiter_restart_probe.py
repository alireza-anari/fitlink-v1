"""Actual isolated CI Redis restart/reset versus durable PostgreSQL quota."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.test"

import django  # noqa: E402

django.setup()

from django.conf import settings  # noqa: E402
from django.utils import timezone  # noqa: E402

from apps.accounts.limiter import redis_client, reserve_admission  # noqa: E402
from apps.accounts.security_models import SecurityRateEvent  # noqa: E402

assert settings.SETTINGS_ENV == "test"
assert settings.DATABASES["default"]["NAME"] == "fitlink"
assert settings.DATABASES["default"]["HOST"] in {"127.0.0.1", "localhost"}
assert redis_client().connection_pool.connection_kwargs["db"] == 4
mode = sys.argv[1]
if mode == "prepare":
    assert SecurityRateEvent.objects.count() == 0
    redis_client().flushdb()
    for _ in range(5):
        assert reserve_admission(
            "+989888888888", "127.0.0.254", "send", timezone.now()
        ).allowed
    assert SecurityRateEvent.objects.count() == 5
elif mode == "verify":
    # The Redis service genuinely restarted between these process invocations.
    # Also discard any saved counters: durable protection must survive both.
    redis_client().flushdb()
    assert not reserve_admission(
        "+989888888888", "127.0.0.253", "send", timezone.now()
    ).allowed
    assert SecurityRateEvent.objects.count() == 5
else:
    raise ValueError("Invalid probe phase")
print("Durable quota restart probe passed: " + mode)
