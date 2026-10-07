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

# Task 1 additive SQL must remain inspectable on the authoritative hosted service.
uv run --frozen python manage.py sqlmigrate assets 0001 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate assets 0002 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate assets 0003 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate athletes 0001 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate athletes 0002 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate athletes 0003 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate athletes 0004 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate governance 0011 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate governance 0012 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate governance 0013 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate professionals 0001 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate professionals 0002 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate professionals 0003 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate professionals 0004 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate professionals 0005 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate professionals 0006 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate professionals 0007 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate professionals 0008 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate professionals 0009 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate professionals 0010 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate athletes 0005 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate athletes 0006 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate professionals 0011 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate professionals 0012 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate assets 0004 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate professionals 0013 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate assets 0005 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate assets 0006 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate athletes 0007 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate athletes 0008 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate professionals 0014 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate professionals 0015 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate assets 0007 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate professionals 0016 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate athletes 0009 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate professionals 0017 --settings=config.settings.test
uv run --frozen python manage.py makemigrations --check --dry-run --settings=config.settings.test
uv run --frozen mypy apps/athletes apps/professionals apps/assets

# Task 1 schema RED/GREEN; all installed cases are mandatory.
uv run --frozen pytest tests/unit/c03/test_ci_contract.py tests/unit/c03/test_schema_contract.py tests/integration/c03/test_c03_migrations.py tests/integration/c03/test_evidence_guards.py -q --strict-markers
