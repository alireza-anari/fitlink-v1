import importlib
import importlib.util
import os
import subprocess
import sys

import pytest
from django.conf import settings
from test_environment import boot
from test_settings import production_env

from apps.accounts.contracts import AccountSecurityPolicy

pytestmark = pytest.mark.unit


def contract():
    assert importlib.util.find_spec("apps.accounts.limiter"), (
        "missing atomic limiter contract"
    )
    return importlib.import_module("apps.accounts.limiter")


def test_quota_defaults_and_distinct_namespaces():
    limiter = contract()
    policy = AccountSecurityPolicy()
    assert limiter.limits("send", policy) == (5, 20)
    assert limiter.limits("verify_failure", policy) == (10, 60)
    assert limiter.limits("recovery_intake", policy) == (3, 10)
    with pytest.raises(ValueError):
        limiter.limits("caller_kind", policy)


def test_recovery_intake_has_approved_separate_daily_window():
    limiter = contract()
    policy = AccountSecurityPolicy()
    assert limiter.window_seconds("send", policy) == 3600
    assert limiter.window_seconds("verify_failure", policy) == 3600
    assert limiter.window_seconds("recovery_intake", policy) == 86400


def test_canonical_key_space_contains_no_phone_ip_or_secret():
    limiter = contract()
    expected = limiter.rate_keys("+989123456789", "127.0.0.1", "send")
    assert expected == limiter.rate_keys("۰۹۱۲۳۴۵۶۷۸۹", "::ffff:127.0.0.1", "send")
    assert "09123456789" not in repr(expected)
    assert "+989123456789" not in repr(expected)
    assert "127.0.0.1" not in repr(expected)
    assert expected != limiter.rate_keys("+989123456789", "127.0.0.1", "verify_failure")
    assert settings.OTP_RATE_REDIS_URL.endswith("/4")


@pytest.mark.parametrize(
    "url",
    [
        "redis://cache.example:6379/4",
        "rediss://app:p@cache.example:6379/0",
        "rediss://app:p@cache.example:6379/4?ssl_cert_reqs=none",
    ],
)
def test_production_rate_redis_rejects_wrong_tls_db_and_query(url):
    contract()
    result = boot(
        "config.settings.production", (production_env() | {"OTP_RATE_REDIS_URL": url})
    )
    assert result.returncode != 0
    assert url not in result.stderr


def test_production_rate_redis_tls_checks_hostname():
    contract()
    script = """
import django
django.setup()
from apps.accounts.limiter import redis_client
import ssl
options = redis_client().connection_pool.connection_kwargs
assert options['ssl_cert_reqs'] == ssl.CERT_REQUIRED
assert options['ssl_check_hostname'] is True
assert options['socket_timeout'] <= 2
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        env={
            **{k: v for k, v in os.environ.items() if k == "PATH"},
            **(
                production_env()
                | {"OTP_RATE_REDIS_URL": "rediss://app:p@cache.example:6379/4"}
            ),
            "DJANGO_SETTINGS_MODULE": "config.settings.production",
        },
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
