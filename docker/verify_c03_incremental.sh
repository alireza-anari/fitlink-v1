#!/bin/sh
# Explicit cumulative C03 selections. Extend in each owning task, never skip.
set -eu

uv run --frozen python - <<'PY'
import os
import sys

import django
from redis import Redis

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")
django.setup()
from django.conf import settings
from django.db import connection

try:
    if connection.vendor != "postgresql":
        raise RuntimeError("PostgreSQL required")
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        if cursor.fetchone() != (1,):
            raise RuntimeError("PostgreSQL readiness")
    redis = Redis.from_url(
        settings.OTP_RATE_REDIS_URL, socket_connect_timeout=2, socket_timeout=2
    )
    if not redis.ping():
        raise RuntimeError("Redis readiness")
except Exception:
    print("C03 PostgreSQL/Redis readiness failed", flush=True)
    sys.exit(1)
print("C03 real PostgreSQL and Redis readiness passed", flush=True)
PY

# Task 1 schema RED/GREEN; all installed cases are mandatory.
uv run --frozen pytest tests/unit/c03/test_ci_contract.py tests/unit/c03/test_schema_contract.py tests/integration/c03/test_c03_migrations.py tests/integration/c03/test_evidence_guards.py -q --strict-markers
