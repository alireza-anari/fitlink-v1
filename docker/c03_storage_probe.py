"""Fail closed on actual PostgreSQL/Redis/private MinIO unavailability."""

import os
import sys
from pathlib import Path

import django
from redis import Redis

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from docker.c03_storage_errors import error_category


def main() -> int:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")
    try:
        django.setup()
        from django.conf import settings
        from django.db import connection

        from apps.assets.storage import S3PrivateStore

        if connection.vendor != "postgresql":
            raise RuntimeError("PostgreSQL required")
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            if cursor.fetchone() != (1,):
                raise RuntimeError("PostgreSQL unavailable")
        if not Redis.from_url(
            settings.OTP_RATE_REDIS_URL, socket_connect_timeout=2, socket_timeout=2
        ).ping():
            raise RuntimeError("Redis unavailable")
        store = S3PrivateStore()
        store.backend.connection.meta.client.head_bucket(Bucket=settings.S3_BUCKET_NAME)
    except Exception as error:
        print("C03_STORAGE_ERROR " + error_category(error), flush=True)
        print("C03 PostgreSQL/Redis/private MinIO readiness failed", flush=True)
        return 1
    print("C03 real PostgreSQL/Redis/private MinIO readiness passed", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
