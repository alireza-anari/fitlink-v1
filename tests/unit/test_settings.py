import pytest
from test_environment import boot

pytestmark = pytest.mark.unit


def production_env():
    return {
        "ACCOUNT_SECURITY_KEYS_JSON": (
            '{"validation":"AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8="}'
        ),
        "ACCOUNT_SECURITY_ACTIVE_KEY_ID": "validation",
        "DJANGO_SECRET_KEY": (
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
        ),
        "DJANGO_ALLOWED_HOSTS": "fitlink.example",
        "POSTGRES_DB": "fitlink",
        "POSTGRES_USER": "app",
        "POSTGRES_PASSWORD": "ephemeral-validation",
        "POSTGRES_HOST": "db.example",
        "POSTGRES_PORT": "5432",
        "POSTGRES_SSLMODE": "verify-full",
        "REDIS_URL": "rediss://app:ephemeral@cache.example:6379/0",
        "CELERY_BROKER_URL": "rediss://app:ephemeral@cache.example:6379/1",
        "CELERY_RESULT_BACKEND": "rediss://app:ephemeral@cache.example:6379/2",
        "CHANNEL_REDIS_URL": "rediss://app:ephemeral@cache.example:6379/3",
        "STORAGE_BACKEND": "s3",
        "S3_ENDPOINT_URL": "https://storage.example",
        "S3_BUCKET_NAME": "private-assets",
        "S3_REGION": "region-1",
        "S3_ACCESS_KEY_ID": "ephemeral-app-key",
        "S3_SECRET_ACCESS_KEY": "ephemeral-app-secret",
    }


@pytest.mark.parametrize(
    "key,value",
    [("DJANGO_ALLOWED_HOSTS", "*"), ("DJANGO_SECRET_KEY", "local-test-key")],
)
def test_production_rejects_wildcard_hosts_and_local_defaults(key, value):
    values = production_env()
    values[key] = value
    result = boot("config.settings.production", values)
    assert result.returncode != 0 and key in result.stderr
    assert value not in result.stderr or value == "*"


@pytest.mark.parametrize(
    "key,value",
    [
        ("REDIS_URL", "redis://host/0"),
        ("CELERY_BROKER_URL", "rediss://host/1"),
        ("S3_ENDPOINT_URL", "http://host"),
        ("POSTGRES_SSLMODE", "disable"),
    ],
)
def test_production_requires_tls_dependencies(key, value):
    values = production_env()
    values[key] = value
    result = boot("config.settings.production", values)
    assert result.returncode != 0 and key in result.stderr
    assert value not in result.stderr


def test_valid_production_boot():
    result = boot("config.settings.production", production_env())
    assert result.returncode == 0, result.stderr


def test_development_and_test_are_separate_overlays():
    import os
    import subprocess
    import sys

    # pytest changes the active DATABASES dict to test_fitlink; importing a
    # different overlay in-process would reuse that mutated shared base dict.
    script = """
import importlib, sys
module = importlib.import_module(sys.argv[1])
assert module.DEBUG is (sys.argv[2] == "True")
assert module.DATABASES["default"]["NAME"] == "fitlink"
assert module.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql"
if sys.argv[2] == "False":
    assert module.STORAGE_BACKEND == "fake"
"""
    for module, debug in (("development", "True"), ("test", "False")):
        result = subprocess.run(
            [sys.executable, "-c", script, "config.settings." + module, debug],
            env={key: value for key, value in os.environ.items() if key == "PATH"},
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    "key,value",
    [
        ("DJANGO_SECRET_KEY", "X" * 60),
        ("REDIS_URL", "rediss://app:p@cache.example:6379/0?ssl_cert_reqs=none"),
        ("CHANNEL_REDIS_URL", "rediss://app:p@[::1]:6379/3"),
        ("S3_ENDPOINT_URL", "https://bad host"),
        ("POSTGRES_HOST", "::1"),
        ("POSTGRES_PORT", "65536"),
        ("POSTGRES_PASSWORD", "changeme"),
    ],
)
def test_production_rejects_unsafe_config(key, value):
    values = production_env()
    values[key] = value
    result = boot("config.settings.production", values)
    assert result.returncode != 0 and key in result.stderr
    assert value not in result.stderr


def test_production_redis_client_verifies_certificate_and_hostname():
    import os
    import subprocess
    import sys

    script = """
import ssl, django
from django.conf import settings
from redis import Redis
from redis.asyncio import Redis as AsyncRedis
django.setup()
for name in ("REDIS_URL", "CELERY_BROKER_URL",
             "CELERY_RESULT_BACKEND", "CHANNEL_REDIS_URL"):
    for kind in (Redis, AsyncRedis):
        pool = kind.from_url(getattr(settings,name)).connection_pool
        connection = pool.connection_class(**pool.connection_kwargs)
        assert connection.cert_reqs == ssl.CERT_REQUIRED
        assert connection.check_hostname is True
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        env={
            **{k: v for k, v in os.environ.items() if k == "PATH"},
            **production_env(),
            "DJANGO_SETTINGS_MODULE": "config.settings.production",
        },
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
