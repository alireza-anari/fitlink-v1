import importlib

import pytest
from test_environment import boot

pytestmark = pytest.mark.unit


def production_env():
    return {
        "DJANGO_SECRET_KEY": "X" * 60,
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
    dev = importlib.import_module("config.settings.development")
    test = importlib.import_module("config.settings.test")
    assert dev.DEBUG is True and test.DEBUG is False
    assert test.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql"
    assert test.STORAGE_BACKEND == "fake"
