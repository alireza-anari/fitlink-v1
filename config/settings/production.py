import ipaddress
import os
import re
import ssl
from urllib.parse import urlsplit

from apps.accounts.security_config import load_security_config

from .base import *  # noqa: F403
from .base import DATABASES, STORAGES, env

DEBUG = False
SECRET_KEY = env.str_value("DJANGO_SECRET_KEY", required=True)
if (
    len(SECRET_KEY) < 50
    or len(set(SECRET_KEY)) < 5
    or SECRET_KEY.startswith("django-insecure-")
    or re.search(r"test|local|example|development|placeholder", SECRET_KEY, re.I)
):
    env.invalid("DJANGO_SECRET_KEY")


def valid_host(key: str, value: str) -> None:
    host = value.lower().rstrip(".")
    if host in {"localhost", "web", "testserver", "db", "redis", "minio"}:
        env.invalid(key)
    try:
        address = ipaddress.ip_address(host.strip("[]"))
    except ValueError:
        if len(host) > 253 or not re.fullmatch(
            r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)*"
            r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?",
            host,
        ):
            env.invalid(key)
    else:
        if address.is_loopback or address.is_unspecified:
            env.invalid(key)


ALLOWED_HOSTS = list(env.csv_value("DJANGO_ALLOWED_HOSTS", required=True))
for host in ALLOWED_HOSTS:
    valid_host("DJANGO_ALLOWED_HOSTS", host)


def secure_url(key: str, scheme: str, auth: bool = False) -> str:
    value = env.str_value(key, required=True)
    try:
        url = urlsplit(value)
        if (
            url.scheme != scheme
            or not url.hostname
            or url.query
            or (not auth and (url.username is not None or url.password is not None))
            or (auth and (not url.username or not url.password))
            or url.fragment
        ):
            env.invalid(key)
        valid_host(key, url.hostname or "")
        if url.port is not None and not 1 <= url.port <= 65535:
            env.invalid(key)
        if auth and not re.fullmatch(r"/[0-9]+", url.path):
            env.invalid(key)
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
valid_host("POSTGRES_HOST", str(DATABASES["default"]["HOST"]))
if str(DATABASES["default"]["PASSWORD"]).lower() in {
    "changeme",
    "password",
    "secret",
    "fitlink",
    "minioadmin",
}:
    env.invalid("POSTGRES_PASSWORD")
DATABASES["default"]["PORT"] = env.int_value("POSTGRES_PORT", minimum=1)
if DATABASES["default"]["PORT"] > 65535:
    env.invalid("POSTGRES_PORT")
sslmode = env.str_value("POSTGRES_SSLMODE", "verify-full")
if sslmode != "verify-full":
    env.invalid("POSTGRES_SSLMODE")
DATABASES["default"]["OPTIONS"]["sslmode"] = sslmode
REDIS_URL = secure_url("REDIS_URL", "rediss", True)
CELERY_BROKER_URL = secure_url("CELERY_BROKER_URL", "rediss", True)
CELERY_RESULT_BACKEND = secure_url("CELERY_RESULT_BACKEND", "rediss", True)
CHANNEL_REDIS_URL = secure_url("CHANNEL_REDIS_URL", "rediss", True)
OTP_RATE_REDIS_URL = secure_url("OTP_RATE_REDIS_URL", "rediss", True)
env.require_rate_redis(OTP_RATE_REDIS_URL)
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


CELERY_BROKER_USE_SSL = {"ssl_cert_reqs": ssl.CERT_REQUIRED}
CELERY_REDIS_BACKEND_USE_SSL = {"ssl_cert_reqs": ssl.CERT_REQUIRED}


ACCOUNT_SECURITY = load_security_config(os.environ, production=True)

SETTINGS_ENV = "production"
