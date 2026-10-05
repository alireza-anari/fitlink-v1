import os

from apps.accounts.security_config import load_security_config

from .base import *  # noqa: F403
from .base import (
    CELERY_BROKER_URL,
    CELERY_RESULT_BACKEND,
    CHANNEL_REDIS_URL,
    DATABASES,
    OTP_RATE_REDIS_URL,
    REDIS_URL,
    STORAGES,
    env,
)

DEBUG = False
STORAGE_BACKEND = "fake"
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
if DATABASES["default"]["HOST"] not in {"db", "localhost", "127.0.0.1"}:
    env.invalid("POSTGRES_HOST")
if DATABASES["default"]["NAME"] != "fitlink":
    env.invalid("POSTGRES_DB")

env.require_local_redis(
    (
        REDIS_URL,
        CELERY_BROKER_URL,
        CELERY_RESULT_BACKEND,
        CHANNEL_REDIS_URL,
        OTP_RATE_REDIS_URL,
    )
)

STORAGES["default"] = {"BACKEND": "django.core.files.storage.InMemoryStorage"}


ACCOUNT_SECURITY = load_security_config(os.environ, production=False)

SETTINGS_ENV = "test"

env.require_rate_redis(OTP_RATE_REDIS_URL)
