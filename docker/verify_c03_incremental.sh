#!/bin/sh
# Explicit cumulative C03 selections. Extend in each owning task, never skip.
set -eu

# Bound the entire C03 gate, including readiness/SQL/type checking and cleanup.
# A timed-out process is a failed gate; the inherited job timeout is unchanged.
if [ "${C03_GATE_CHILD:-}" != 1 ]; then
  exec env C03_GATE_CHILD=1 timeout -k 10s 300s sh "$0"
fi
echo "C03 cumulative gate: readiness"

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
echo "C03 cumulative gate: additive SQL and migration drift"
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
uv run --frozen python manage.py sqlmigrate governance 0014 --settings=config.settings.test
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
uv run --frozen python manage.py sqlmigrate assets 0008 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate assets 0009 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate professionals 0016 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate athletes 0009 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate athletes 0010 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate professionals 0017 --settings=config.settings.test
uv run --frozen python manage.py makemigrations --check --dry-run --settings=config.settings.test
uv run --frozen mypy apps/athletes apps/professionals apps/assets

# Task 1 schema RED/GREEN; all installed cases are mandatory.
echo "C03 cumulative gate: installed schema contracts"
timeout -k 10s 180s uv run --frozen pytest tests/unit/c03/test_ci_contract.py tests/unit/c03/test_schema_contract.py tests/integration/c03/test_c03_migrations.py tests/integration/c03/test_evidence_guards.py -vv --strict-markers -o faulthandler_timeout=30

# Task 2 explicit owner, current session, receipt and PostgreSQL race gates.
timeout -k 10s 180s uv run --frozen pytest tests/unit/c03/test_profile_policy.py tests/integration/c03/test_owned_profiles.py tests/integration/c03/test_profile_races.py -vv --strict-markers -o faulthandler_timeout=30

# Task 3 private snapshots, bounded consent callback and PostgreSQL races.
timeout -k 10s 180s uv run --frozen pytest tests/unit/c03/test_baseline_fields.py tests/unit/c03/test_consent_callback_contract.py tests/integration/c03/test_baseline_workflow.py tests/integration/c03/test_baseline_consent.py tests/integration/c03/test_baseline_races.py -vv --strict-markers -o faulthandler_timeout=30

# Task 4 PostgreSQL ingress/state/authority races. Real private-store suites are
# separately mandatory in the exact-C03-only docker/verify_c03_storage.sh job.
timeout -k 10s 180s uv run --frozen pytest tests/unit/c03/test_gate_diagnostics.py tests/unit/c03/test_upload_contract.py tests/unit/c03/test_asset_validation.py tests/unit/c03/test_source_non_delivery.py tests/integration/c03/test_upload_lifecycle.py tests/integration/c03/test_upload_races.py -vv --strict-markers -o faulthandler_timeout=30

# Task 6 private setup, immutable credentials and exact per-target races.
task6_exit=0
C03_FOUNDATION_TRIAGE=1 C03_FOUNDATION_EVIDENCE_DIRECTORY=.runtime/c03-diagnostics timeout -k 10s 180s uv run --frozen pytest tests/unit/c03/test_professional_fields.py tests/unit/c03/test_verification_binding.py tests/integration/c03/test_professional_setup.py tests/integration/c03/test_credential_revisions.py tests/integration/c03/test_bound_edit_races.py -q --strict-markers -o faulthandler_timeout=30 || task6_exit=$?
uv run --frozen python - <<'PY'
import json
from pathlib import Path

counts = {"passed": 0, "failed": 0, "skipped": 0}
for path in sorted(Path(".runtime/c03-diagnostics").glob("foundation-*.jsonl")):
    for line in path.read_text().splitlines():
        event = json.loads(line)
        if event.get("event") == "test_report" and event.get("phase") == "call":
            outcome = event.get("outcome")
            if outcome in counts:
                counts[outcome] += 1
        if event.get("event") in {"pytest_exit", "pytest_internalerror"} or (
            event.get("event") == "test_report" and event.get("outcome") != "passed"
        ):
            print("C03_TASK6 " + json.dumps(event, sort_keys=True), flush=True)
print("C03_TASK6_COUNTS " + json.dumps(counts, sort_keys=True), flush=True)
PY
[ "$task6_exit" -eq 0 ] || exit "$task6_exit"

# Task 7 assigned verification intake and real PostgreSQL races.
task7_exit=0
C03_FOUNDATION_TRIAGE=1 C03_FOUNDATION_EVIDENCE_DIRECTORY=.runtime/c03-diagnostics timeout -k 10s 180s uv run --frozen pytest tests/unit/c03/test_verification_contract.py tests/integration/c03/test_verification_submission.py tests/integration/c03/test_verification_staff.py tests/integration/c03/test_verification_assignment_races.py -q --strict-markers -o faulthandler_timeout=30 || task7_exit=$?
uv run --frozen python - <<'PY'
import json
from pathlib import Path

selected = (
    "tests/unit/c03/test_verification_contract.py::",
    "tests/integration/c03/test_verification_submission.py::",
    "tests/integration/c03/test_verification_staff.py::",
    "tests/integration/c03/test_verification_assignment_races.py::",
)
counts = {"passed": 0, "failed": 0, "skipped": 0}
for path in sorted(Path(".runtime/c03-diagnostics").glob("foundation-*.jsonl")):
    events = [json.loads(line) for line in path.read_text().splitlines()]
    if not any(event.get("node", "").startswith(selected) for event in events):
        continue
    for event in events:
        if (event.get("event") == "test_report"
                and event.get("phase") == "call"
                and event.get("node", "").startswith(selected)):
            outcome = event.get("outcome")
            if outcome in counts:
                counts[outcome] += 1
        if event.get("event") in {"pytest_exit", "pytest_internalerror"} or (
            event.get("event") == "test_report"
            and event.get("node", "").startswith(selected)
            and event.get("outcome") != "passed"
        ):
            print("C03_TASK7 " + json.dumps(event, sort_keys=True), flush=True)
print("C03_TASK7_COUNTS " + json.dumps(counts, sort_keys=True), flush=True)
PY
exit "$task7_exit"
