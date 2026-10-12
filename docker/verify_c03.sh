#!/bin/sh
# Task 14 RED harness. No final acceptance until every planned phase is installed.
set -eu
umask 077
root=$(pwd)
baseline=$root/.runtime/c02
project=fitlink-c03-task14-upgrade
private=$root/.runtime/task14-private
evidence=$root/.runtime/c03-task14-evidence
env_file=$root/.env.c03-task14-upgrade
python docker/c03_baseline.py "$baseline"
python docker/c02_baseline.py "$root/.runtime/c01"
# Reject names before acquiring cleanup ownership. Never delete existing data.
for owned in fitlink-c02-immutable-c01 fitlink-c02-exact-upgrade fitlink-foundation-verify "$project"; do
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
  "$@" >"$private/$stage.log" 2>&1 || result=$?
  printf '{"stage":"%s","exit_code":%s}\n' "$stage" "$result" >>"$evidence/upgrade.jsonl"
  printf 'C03_TASK14 stage=%s exit_code=%s\n' "$stage" "$result"
  # Only constant probe markers may leave private logs. Never print failures,
  # pytest locals, session rows, credential environment or snapshot contents.
  python - "$private/$stage.log" <<'PY'
import re
import sys
from pathlib import Path
from docker.c03_upgrade_probe import private_log_metadata

for line in Path(sys.argv[1]).read_text(errors="replace").splitlines():
    if re.fullmatch(r"C03_TASK14 [A-Za-z_]+(?: [A-Za-z_]+)?(?: line=[0-9]+)?", line):
        print(line, flush=True)
import json
print("C03_TASK14_DIAGNOSTIC " + json.dumps(private_log_metadata(sys.argv[1])), flush=True)
PY
  test "$result" -eq 0
}
original_c02() (
  cd "$baseline"
  C02_BASELINE_DIR="$root/.runtime/c01" sh docker/verify_c02.sh
)
# Invoke the immutable complete original, including its separate C01 proof.
run_step exact_original_c02 original_c02
run_step exact_c02_after_runtime python docker/c03_baseline.py "$baseline"
python docker/generate_env.py "$env_file"
mkdir "$private/preservation"
chmod 700 "$private/preservation"
c02() { docker compose -p "$project" -f "$baseline/compose.yaml" --env-file "$env_file" --profile test "$@"; }
c03() { docker compose -p "$project" -f "$root/compose.yaml" --env-file "$env_file" --profile test "$@"; }
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
  -v "$private/preservation:/rehearsal" checks uv run --frozen python /probe.py prepare /rehearsal/metadata.json
# The same project/db/container/volume/network/env file stay in place.
run_step c03_config c03 config --quiet
run_step c03_build c03 build checks
run_step c03_migrate c03 run --rm --no-deps checks uv run --frozen python manage.py migrate --noinput
run_step c03_migrate_noop c03 run --rm --no-deps checks uv run --frozen python manage.py migrate --noinput
run_step c03_drift c03 run --rm --no-deps checks uv run --frozen python manage.py makemigrations --check --dry-run
run_step c03_migrations c03 run --rm --no-deps checks uv run --frozen python manage.py showmigrations
run_step populated_preservation c03 run --rm --no-deps --user "$(id -u):$(id -g)" \
  -v "$root/docker/c03_upgrade_probe.py:/probe.py:ro" \
  -v "$private/preservation:/rehearsal" checks uv run --frozen python /probe.py verify /rehearsal/metadata.json
# Intentionally fail closed: replay, constraints and independent clean gates
# cannot be claimed from the above migration harness.
exit 1
