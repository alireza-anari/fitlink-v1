import os
from urllib.parse import urlsplit

from apps.accounts.security_config import load_security_config

from .base import *  # noqa: F403
from .base import (
    CELERY_BROKER_URL,
    CELERY_RESULT_BACKEND,
    CHANNEL_REDIS_URL,
    DATABASES,
    REDIS_URL,
    S3_ENDPOINT_URL,
    env,
)

DEBUG = True
if DATABASES["default"]["HOST"] not in {"db", "localhost", "127.0.0.1"}:
    env.invalid("POSTGRES_HOST")
if DATABASES["default"]["NAME"] != "fitlink":
    env.invalid("POSTGRES_DB")

env.require_local_redis(
    (REDIS_URL, CELERY_BROKER_URL, CELERY_RESULT_BACKEND, CHANNEL_REDIS_URL)
)


if urlsplit(S3_ENDPOINT_URL).hostname not in {"localhost", "127.0.0.1", "minio"}:
    env.invalid("S3_ENDPOINT_URL")


ACCOUNT_SECURITY = load_security_config(os.environ, production=False)

SETTINGS_ENV = "development"
