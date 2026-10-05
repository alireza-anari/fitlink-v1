from .base import *  # noqa: F403

DEBUG = False
STORAGE_BACKEND = "fake"
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
if DATABASES["default"]["HOST"] not in {"db", "localhost", "127.0.0.1"}:  # noqa: F405
    env.invalid("POSTGRES_HOST")  # noqa: F405
if DATABASES["default"]["NAME"] != "fitlink":  # noqa: F405
    env.invalid("POSTGRES_DB")  # noqa: F405

env.require_local_redis(
    (REDIS_URL, CELERY_BROKER_URL, CELERY_RESULT_BACKEND, CHANNEL_REDIS_URL)
)  # noqa: F405
