import re
from urllib.parse import urlsplit

from .base import *  # noqa: F403
from .base import DATABASES, STORAGES, env

DEBUG = False
SECRET_KEY = env.str_value("DJANGO_SECRET_KEY", required=True)
if len(SECRET_KEY) < 50 or re.search(
    r"test|local|example|development|placeholder", SECRET_KEY, re.I
):
    env.invalid("DJANGO_SECRET_KEY")
ALLOWED_HOSTS = list(env.csv_value("DJANGO_ALLOWED_HOSTS", required=True))
if any(
    not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.-]*", host)
    or host in {"localhost", "web", "testserver", "127.0.0.1"}
    for host in ALLOWED_HOSTS
):
    env.invalid("DJANGO_ALLOWED_HOSTS")


def secure_url(key: str, scheme: str, auth: bool = False) -> str:
    value = env.str_value(key, required=True)
    try:
        url = urlsplit(value)
        if (
            url.scheme != scheme
            or not url.hostname
            or url.hostname in {"localhost", "redis", "minio", "127.0.0.1"}
            or (auth and (not url.username or not url.password))
            or url.fragment
        ):
            env.invalid(key)
        _ = url.port
    except ValueError:
        env.invalid(key)
    return value


CSRF_TRUSTED_ORIGINS = list(env.csv_value("DJANGO_CSRF_TRUSTED_ORIGINS"))
for origin in CSRF_TRUSTED_ORIGINS:
    parsed = urlsplit(origin)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or "*" in origin
        or parsed.path
        or parsed.query
        or parsed.fragment
    ):
        env.invalid("DJANGO_CSRF_TRUSTED_ORIGINS")
for key in ("NAME", "USER", "PASSWORD", "HOST"):
    DATABASES["default"][key] = env.str_value(
        "POSTGRES_" + ("DB" if key == "NAME" else key), required=True
    )
if DATABASES["default"]["HOST"] in {"db", "localhost", "127.0.0.1"}:
    env.invalid("POSTGRES_HOST")
DATABASES["default"]["PORT"] = env.int_value("POSTGRES_PORT", minimum=1)
sslmode = env.str_value("POSTGRES_SSLMODE", "verify-full")
if sslmode != "verify-full":
    env.invalid("POSTGRES_SSLMODE")
DATABASES["default"]["OPTIONS"]["sslmode"] = sslmode
REDIS_URL = secure_url("REDIS_URL", "rediss", True)
CELERY_BROKER_URL = secure_url("CELERY_BROKER_URL", "rediss", True)
CELERY_RESULT_BACKEND = secure_url("CELERY_RESULT_BACKEND", "rediss", True)
CHANNEL_REDIS_URL = secure_url("CHANNEL_REDIS_URL", "rediss", True)
STORAGE_BACKEND = env.str_value("STORAGE_BACKEND", required=True)
if STORAGE_BACKEND != "s3":
    env.invalid("STORAGE_BACKEND")
S3_ENDPOINT_URL = secure_url("S3_ENDPOINT_URL", "https")
for key in ("S3_BUCKET_NAME", "S3_REGION", "S3_ACCESS_KEY_ID", "S3_SECRET_ACCESS_KEY"):
    value = env.str_value(key, required=True)
    if re.search(r"minioadmin|placeholder|changeme|local-default", value, re.I):
        env.invalid(key)
STORAGES["staticfiles"] = {
    "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
}
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True

import ssl

CELERY_BROKER_USE_SSL = {"ssl_cert_reqs": ssl.CERT_REQUIRED}
CELERY_REDIS_BACKEND_USE_SSL = {"ssl_cert_reqs": ssl.CERT_REQUIRED}
