#!/bin/sh
# Exact immutable C02, populated same-database upgrade and independent clean C03.
set -eu
if [ "${C03_TASK14_CHILD:-}" != 1 ]; then
  exec env C03_TASK14_CHILD=1 timeout -k 20s 3300s sh "$0"
fi
umask 077
root=$(pwd)
baseline=$root/.runtime/c02
project=fitlink-c03-task14-upgrade
clean_project=fitlink-c03-task14-clean
private=$root/.runtime/task14-private
evidence=$root/.runtime/c03-task14-evidence
env_file=$root/.env.c03-task14-upgrade
python docker/c03_baseline.py "$baseline"
python docker/c02_baseline.py "$root/.runtime/c01"
python docker/c02_baseline.py "$baseline/.runtime/c01"
# Reject names before acquiring cleanup ownership. Never delete existing data.
for owned in fitlink-c02-immutable-c01 fitlink-c02-exact-upgrade fitlink-foundation-verify "$project" "$clean_project"; do
  test -z "$(docker ps -aq --filter label=com.docker.compose.project="$owned")"
  test -z "$(docker network ls -q --filter label=com.docker.compose.project="$owned")"
  test -z "$(docker volume ls -q --filter label=com.docker.compose.project="$owned")"
  for volume in db-data redis-data minio-data beat-data scanner-signatures; do
    test -z "$(docker volume ls -q --filter name="^${owned}_${volume}$")"
  done
done
test ! -e "$private"
test ! -e "$evidence"
test ! -e "$env_file"
mkdir "$private" "$evidence"
chmod 700 "$private" "$evidence"
run_step() {
  stage=$1
  shift
  result=0
  # A background child keeps errexit active inside gate functions. An OR-list
  # around the function call would disable it and hide earlier failed commands.
  "$@" >"$private/$stage.log" 2>&1 &
  step_pid=$!
  wait "$step_pid" || result=$?
  # Only constant probe markers may leave private logs. Never print failures,
  # pytest locals, session rows, credential environment or snapshot contents.
  metadata_result=0
  python - "$private/$stage.log" <<'PY' || metadata_result=$?
import re
import sys
from pathlib import Path
from docker.c03_upgrade_probe import private_log_metadata

for line in Path(sys.argv[1]).read_text(errors="replace").splitlines():
    if re.fullmatch(r"C03_TASK14 [A-Za-z_]+(?: [A-Za-z_]+)?(?: line=[0-9]+)?", line):
        print(line, flush=True)
import json
print("C03_TASK14_DIAGNOSTIC " + json.dumps(private_log_metadata(sys.argv[1])), flush=True)
with Path(sys.argv[1]).open(errors="replace") as stream:
    if any(re.search(r"\b[1-9][0-9]* skipped\b", line) for line in stream):
        raise SystemExit(1)
PY
  test "$metadata_result" -eq 0 || result=1
  printf '{"stage":"%s","exit_code":%s}\n' "$stage" "$result" >>"$evidence/upgrade.jsonl"
  printf 'C03_TASK14 stage=%s exit_code=%s\n' "$stage" "$result"
  test "$result" -eq 0
}
original_c02() (
  cd "$baseline"
  # Original public static/dependency outputs must remain readable by the
  # immutable nonroot containers. The outer captured log stays mode0600.
  umask 022
  uv lock --check
  uv sync --frozen --group dev
  npm ci
  npm run build:css
  npm run check:js
  uv run --frozen python manage.py collectstatic --noinput --settings=config.settings.build --ignore=src/styles.css
  uv run --frozen ruff check .
  uv run --frozen ruff format --check .
  uv run --frozen mypy config/settings/env.py config/health.py apps/assets/storage.py apps/accounts apps/governance config/use_cases config/account_middleware.py config/authentication.py config/permissions.py
  uv run --frozen python manage.py check --settings=config.settings.test
  uv run --frozen pytest tests/unit -q --strict-markers --tb=short --show-capture=no
  uv run --frozen python docker/production_check.py
  C02_BASELINE_DIR="$baseline/.runtime/c01" sh docker/verify_c02.sh
)
# Invoke the immutable complete original, including its separate C01 proof.
run_step exact_original_c02 original_c02
run_step exact_c02_after_runtime python docker/c03_baseline.py "$baseline"
current_source_quality() (
  umask 022
  uv lock --check
  uv sync --frozen --group dev
  npm ci
  npm run build:css
  npm run check:js
  uv run --frozen python manage.py collectstatic --noinput --settings=config.settings.build --ignore=src/styles.css
  uv run --frozen ruff check .
  uv run --frozen ruff format --check .
  uv run --frozen mypy config/settings/env.py config/health.py apps/assets/storage.py apps/accounts apps/governance config/use_cases config/account_middleware.py config/authentication.py config/permissions.py
  uv run --frozen python manage.py check --settings=config.settings.test
  uv run --frozen python docker/production_check.py
  git diff --check
)
run_step current_frozen_quality current_source_quality
python docker/generate_env.py "$env_file"
mkdir "$root/.runtime/c03-foundation-evidence"
chmod 777 "$root/.runtime/c03-foundation-evidence"
export C03_FOUNDATION_TRIAGE=1
mkdir "$private/preservation"
chmod 700 "$private/preservation"
c02() { docker compose -p "$project" -f "$baseline/compose.yaml" --env-file "$env_file" --profile test "$@"; }
c03() { timeout -k 10s 900s docker compose -p "$project" -f "$root/compose.yaml" --env-file "$env_file" --profile test "$@"; }
cleanup() {
  cleanup_status=0
  c03 down --remove-orphans >>"$private/cleanup.log" 2>&1 || cleanup_status=$?
  test -z "$(docker ps -aq --filter label=com.docker.compose.project="$project")" || cleanup_status=1
  test -z "$(docker network ls -q --filter label=com.docker.compose.project="$project")" || cleanup_status=1
  printf '{"stage":"upgrade_cleanup","exit_code":%s}\n' "$cleanup_status" >>"$evidence/upgrade.jsonl"
  # Volumes and the 0600 preservation snapshot intentionally remain isolated.
  return "$cleanup_status"
}
trap 'exit_status=$?; trap - EXIT; cleanup || exit_status=1; exit "$exit_status"' EXIT
run_step c02_config c02 config --quiet
run_step c02_build c02 build checks
run_step c02_services c02 up -d --wait db redis
run_step c02_migrate c02 run --rm --no-deps checks uv run --frozen python manage.py migrate --noinput
run_step c02_populate c02 run --rm --no-deps --user "$(id -u):$(id -g)" \
  -v "$root/docker/c03_upgrade_probe.py:/probe.py:ro" \
  -v "$private/preservation:/rehearsal" checks /opt/venv/bin/python /probe.py prepare /rehearsal/metadata.json
# The same project/db/container/volume/network/env file stay in place.
run_step c03_config c03 config --quiet
run_step c03_build c03 build checks
# Review exact SQL for every new installed migration before forward application.
for app in assets athletes professionals governance; do
  for migration in "$root/apps/$app/migrations/"[0-9]*.py; do
    name=$(basename "$migration" .py)
    test ! -e "$baseline/apps/$app/migrations/$name.py" || continue
    run_step "sql_${app}_${name}" c03 run --rm --no-deps checks uv run --frozen python manage.py sqlmigrate "$app" "$name"
  done
done
run_step c03_migrate c03 run --rm --no-deps checks uv run --frozen python manage.py migrate --noinput
run_step c03_migrate_noop c03 run --rm --no-deps checks uv run --frozen python manage.py migrate --noinput
run_step c03_drift c03 run --rm --no-deps checks uv run --frozen python manage.py makemigrations --check --dry-run
run_step c03_migrations c03 run --rm --no-deps checks uv run --frozen python manage.py showmigrations
run_step populated_preservation c03 run --rm --no-deps --user "$(id -u):$(id -g)" \
  -v "$root/docker/c03_upgrade_probe.py:/probe.py:ro" \
  -v "$private/preservation:/rehearsal" checks /opt/venv/bin/python /probe.py verify /rehearsal/metadata.json
# Deliberate C03 commands only after exact preservation and session checks.
run_step upgrade_private_build c03 build scanner scanner-signatures minio minio-init
run_step upgrade_private_services c03 up -d --wait minio scanner
run_step upgrade_private_init c03 run --rm minio-init
run_step upgrade_scanner_health c03 exec -T scanner clamdscan --config-file=/etc/clamav/clamd.c03.conf --ping=1
probe() { c03 run --rm --no-deps --user "$(id -u):$(id -g)" -v "$private/preservation:/rehearsal" checks /opt/venv/bin/python docker/c03_upgrade_probe.py "$@" /rehearsal/metadata.json; }
run_step upgraded_capabilities probe replay
run_step upgraded_constraints probe constraints
run_step upgraded_c02_backend c03 run --rm --no-deps checks uv run --frozen pytest tests/integration/c02 -q --strict-markers --tb=no --show-capture=no
run_step upgraded_browser_build c03 build web browser worker
run_step upgraded_web c03 up -d --wait web worker
run_step upgraded_c02_browser c03 run --rm --no-deps browser uv run --frozen pytest tests/e2e/c02 -q --strict-markers --tracing=off --screenshot=off --video=off
run_step upgrade_cleanup cleanup
# Independent zero-state project with distinct fresh volumes and credentials.
clean_env=$root/.env.c03-task14-clean
python docker/generate_env.py "$clean_env"
cat > "$private/clean-compose.yml" <<'CLEAN_COMPOSE'
services:
  browser:
    network_mode: !reset null
    networks: [default, scan-private]
  worker:
    command:
      ["uv", "run", "--frozen", "celery", "--quiet", "-A", "config.celery:app",
       "worker", "--loglevel=WARNING", "--concurrency=1", "--hostname=foundation@%h",
       "-I", "docker.c03_asset_restart_probe"]
CLEAN_COMPOSE
clean() { timeout -k 10s 900s docker compose -p "$clean_project" -f "$root/compose.yaml" -f "$private/clean-compose.yml" --env-file "$clean_env" --profile test "$@"; }
clean_cleanup() {
  result=0
  clean down --remove-orphans >>"$private/cleanup.log" 2>&1 || result=$?
  test -z "$(docker ps -aq --filter label=com.docker.compose.project="$clean_project")" || result=1
  test -z "$(docker network ls -q --filter label=com.docker.compose.project="$clean_project")" || result=1
  printf '{"stage":"clean_cleanup","exit_code":%s}\n' "$result" >>"$evidence/upgrade.jsonl"
  return "$result"
}
trap 'exit_status=$?; trap - EXIT; cleanup || exit_status=1; clean_cleanup || exit_status=1; exit "$exit_status"' EXIT
run_step clean_build clean build web worker beat checks browser minio minio-init scanner scanner-signatures
run_step clean_services clean up -d --wait db redis minio scanner
run_step clean_minio clean run --rm minio-init
run_step clean_migrate clean run --rm --no-deps checks uv run --frozen python manage.py migrate --noinput
run_step independent_clean clean run --rm --no-deps checks uv run --frozen python docker/c03_upgrade_probe.py clean unused
run_step clean_noop clean run --rm --no-deps checks uv run --frozen python manage.py migrate --noinput
run_step clean_drift clean run --rm --no-deps checks uv run --frozen python manage.py makemigrations --check --dry-run
run_step clean_showmigrations clean run --rm --no-deps checks uv run --frozen python manage.py showmigrations
run_step clean_runtime clean up -d --wait web worker beat
run_step clean_scanner clean exec -T scanner clamdscan --config-file=/etc/clamav/clamd.c03.conf --ping=1
run_step complete_backend clean run --rm --no-deps checks uv run --frozen pytest tests/unit tests/integration -q --strict-markers --tb=no --show-capture=no
run_step focused_task14 clean run --rm --no-deps checks uv run --frozen pytest tests/unit/c03/test_exact_baseline.py tests/unit/c03/test_final_rehearsal.py tests/integration/c03/test_upgrade_from_c02.py -q --strict-markers --tb=no --show-capture=no
browser_gate() {
  case "$1" in
    --task11-owner) selection='tests/e2e/c03/test_owner_setup.py tests/e2e/c03/test_private_uploads.py' ;;
    --task12-staff) selection=tests/e2e/c03/test_staff_verification.py ;;
    *) return 1 ;;
  esac
  # Only these literal installed selections are split into separate arguments.
  clean run --rm --no-deps browser uv run --frozen pytest $selection -q --strict-markers --tracing=off --screenshot=off --video=off
}
run_step clean_owner_browser browser_gate --task11-owner
run_step clean_staff_browser browser_gate --task12-staff
run_step clean_c02_browser clean run --rm --no-deps browser uv run --frozen pytest tests/e2e/c02 tests/e2e/test_foundation_smoke.py -q --strict-markers --tracing=off --screenshot=off --video=off
restart_probe() { clean run --rm --no-deps checks timeout -k 5s 60s uv run --frozen python docker/c03_asset_restart_probe.py "$@"; }
mkdir -p "$root/.runtime/c03-triage"
chmod 777 "$root/.runtime/c03-triage"
for stage in before after; do
  run_step "restart_${stage}_prepare" restart_probe prepare "$stage"
  run_step "restart_${stage}_start" restart_probe start "$stage"
  run_step "restart_${stage}_kill" clean kill -s SIGKILL worker
  run_step "restart_${stage}_services" clean restart redis minio scanner
  run_step "restart_${stage}_healthy" clean up -d --wait redis minio scanner
  run_step "restart_${stage}_worker" clean up -d --wait --force-recreate worker
  run_step "restart_${stage}_verify" restart_probe verify "$stage"
done
for stage in scanner storage broker; do
  case "$stage" in scanner) service=scanner ;; storage) service=minio ;; broker) service=redis ;; esac
  run_step "fault_${stage}_prepare" restart_probe prepare "$stage"
  run_step "fault_${stage}_stop" clean stop "$service"
  run_step "fault_${stage}_denied" restart_probe fault "$stage"
  run_step "fault_${stage}_healthy" clean up -d --wait "$service"
  run_step "fault_${stage}_recovered" restart_probe verify "$stage"
done
run_step clean_worker_health clean exec -T worker uv run --frozen python docker/healthcheck.py worker
run_step clean_beat_health clean exec -T beat uv run --frozen python docker/healthcheck.py beat
run_step clean_outbox_prepare clean run --rm --no-deps checks uv run --frozen python docker/c02_outbox_restart_probe.py prepare
run_step clean_redis_restart clean restart redis
run_step clean_redis_healthy clean up -d --wait redis
run_step clean_outbox_verify clean run --rm --no-deps checks uv run --frozen python docker/c02_outbox_restart_probe.py verify
run_step clean_real_services clean run --rm --no-deps checks uv run --frozen pytest tests/integration/test_redis.py tests/integration/test_channel_layer.py tests/integration/test_celery_roundtrip.py tests/integration/test_minio_storage.py tests/integration/c03/test_scanner_service.py -q --strict-markers --tb=no --show-capture=no
run_step timeout_ownership uv run --frozen python docker/c03_timeout_probe.py
run_step clean_cleanup clean_cleanup
trap - EXIT
printf 'C03_TASK14 final_rehearsal_passed\n'
