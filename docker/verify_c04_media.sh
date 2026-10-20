#!/bin/sh
set -eu
if [ "${C04_MEDIA_GATE_CHILD:-}" != 1 ]; then
  exec env C04_MEDIA_GATE_CHILD=1 timeout -k 10s 900s sh "$0"
fi
# Separate hosted runner; reuse the inherited supervisor's exact owned label.
project=fitlink-c03-private-processing
env_file=.env.c04-media
test -z "$(docker ps -aq --filter label=com.docker.compose.project="$project")"
test -z "$(docker volume ls -q --filter label=com.docker.compose.project="$project")"
python docker/generate_env.py "$env_file"
dc() { docker compose -p "$project" --env-file "$env_file" --profile test "$@"; }
mkdir -p .runtime/c04-media-evidence
chmod 777 .runtime/c04-media-evidence
stage=compose_validation
cleanup() {
  result=$?
  printf '{"event":"media_shell_exit","stage":"%s","returncode":%s}\n' "$stage" "$result" >> .runtime/c04-media-evidence/shell.jsonl
  dc down --remove-orphans >/dev/null 2>&1 || true
}
trap cleanup EXIT
python docker/c03_compose_check.py "$project" "$env_file"
stage=build
dc build scanner scanner-signatures minio minio-init checks worker asset-beat
stage=bootstrap
dc up -d --wait db redis minio scanner
stage=bucket_initialization
dc run --rm minio-init
stage=migration
dc run --rm --no-deps checks uv run --frozen python manage.py migrate --noinput
stage=scanner_health
dc exec -T scanner clamdscan --config-file=/etc/clamav/clamd.c03.conf --ping=1
stage=behavioral_tests
dc run --rm --no-deps checks timeout -k 10s 180s uv run --frozen python docker/c04_gate.py tests/unit/c04/test_public_copy_contract.py tests/integration/c04/test_public_media_services.py --ds=config.settings.development -q --strict-markers --tb=short --show-capture=no
stage=worker_prepare
dc run --rm --no-deps checks timeout -k 5s 60s uv run --frozen python docker/c04_media_probe.py worker-prepare
stage=worker_start
COMPOSE_FILE="${COMPOSE_FILE:-compose.yaml}:docker/compose.c04-media-worker.yml" dc up -d --wait worker
stage=worker_written
dc run --rm --no-deps checks timeout -k 5s 40s uv run --frozen python docker/c04_media_probe.py worker-written
stage=worker_kill
dc kill -s SIGKILL worker
stage=worker_restart
COMPOSE_FILE="${COMPOSE_FILE:-compose.yaml}:docker/compose.c04-media-worker.yml" dc up -d --wait --force-recreate worker
stage=worker_recover
dc run --rm --no-deps checks timeout -k 5s 60s uv run --frozen python docker/c04_media_probe.py worker-recover
stage=beat_start
dc up -d asset-beat
stage=periodic_verify
dc run --rm --no-deps checks timeout -k 5s 60s uv run --frozen python docker/c04_media_probe.py periodic-verify
stage=scanner_stop
dc stop scanner
stage=scanner_outage
dc run --rm --no-deps checks timeout -k 5s 40s uv run --frozen python docker/c04_media_probe.py scanner-outage
stage=scanner_restart
dc up -d --wait scanner
stage=scanner_restored
dc run --rm --no-deps checks timeout -k 5s 60s uv run --frozen python docker/c04_media_probe.py scanner-restored
stage=projection_worker
dc run --rm --no-deps checks timeout -k 5s 90s uv run --frozen python docker/c04_media_probe.py projection-worker
stage=projection_broker_stop
dc stop redis
stage=projection_broker_outage
dc run --rm --no-deps checks timeout -k 5s 40s uv run --frozen python docker/c04_media_probe.py projection-outage
stage=projection_broker_restart
dc up -d --wait redis
stage=projection_broker_recovery
dc run --rm --no-deps checks timeout -k 5s 90s uv run --frozen python docker/c04_media_probe.py projection-restored
stage=complete
