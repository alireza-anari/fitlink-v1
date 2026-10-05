"""Offline deploy checks with ephemeral synthetic configuration, never secrets."""

import os
import secrets
import subprocess
import sys

values = {
    "DJANGO_SETTINGS_MODULE": "config.settings.production",
    "DJANGO_SECRET_KEY": secrets.token_urlsafe(64),
    "DJANGO_ALLOWED_HOSTS": "foundation.invalid",
    "POSTGRES_DB": "fitlink",
    "POSTGRES_USER": "app",
    "POSTGRES_PASSWORD": secrets.token_urlsafe(32),
    "POSTGRES_HOST": "postgres.foundation.invalid",
    "POSTGRES_PORT": "5432",
    "POSTGRES_SSLMODE": "verify-full",
    "STORAGE_BACKEND": "s3",
    "S3_ENDPOINT_URL": "https://storage.foundation.invalid",
    "S3_BUCKET_NAME": "foundation-private",
    "S3_REGION": "us-east-1",
    "S3_ACCESS_KEY_ID": secrets.token_urlsafe(24),
    "S3_SECRET_ACCESS_KEY": secrets.token_urlsafe(32),
}
for name, database in (
    ("REDIS_URL", 0),
    ("CELERY_BROKER_URL", 1),
    ("CELERY_RESULT_BACKEND", 2),
    ("CHANNEL_REDIS_URL", 3),
):
    values[name] = (
        f"rediss://app:{secrets.token_urlsafe(24)}@redis.foundation.invalid:6379/{database}"
    )
result = subprocess.run(
    [sys.executable, "manage.py", "check", "--deploy", "--fail-level=WARNING"],
    env={
        **{k: v for k, v in os.environ.items() if k in {"PATH", "SYSTEMROOT"}},
        **values,
    },
    check=False,
)
raise SystemExit(result.returncode)
