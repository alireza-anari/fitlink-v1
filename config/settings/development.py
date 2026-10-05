from .base import *  # noqa: F403

DEBUG = True
if DATABASES["default"]["HOST"] not in {"db", "localhost", "127.0.0.1"}:  # noqa: F405
    env.invalid("POSTGRES_HOST")  # noqa: F405
if DATABASES["default"]["NAME"] != "fitlink":  # noqa: F405
    env.invalid("POSTGRES_DB")  # noqa: F405

env.require_local_redis(
    (REDIS_URL, CELERY_BROKER_URL, CELERY_RESULT_BACKEND, CHANNEL_REDIS_URL)
)  # noqa: F405

from urllib.parse import urlsplit

if urlsplit(S3_ENDPOINT_URL).hostname not in {"localhost", "127.0.0.1", "minio"}:  # noqa: F405
    env.invalid("S3_ENDPOINT_URL")  # noqa: F405
