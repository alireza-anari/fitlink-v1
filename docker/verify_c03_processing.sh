#!/bin/sh
set -eu
if [ "${C03_PROCESSING_GATE_CHILD:-}" != 1 ]; then
  exec env C03_PROCESSING_GATE_CHILD=1 timeout -k 10s 900s sh "$0"
fi
project=fitlink-c03-private-processing
env_file=.env.c03-processing
[ -z "$(docker volume ls --filter label=com.docker.compose.project="$project" -q)" ] || exit 1
python docker/generate_env.py "$env_file"
dc() { docker compose -p "$project" --env-file "$env_file" --profile test "$@"; }
cleanup() { dc down --remove-orphans >/dev/null 2>&1 || true; }
trap cleanup EXIT
python docker/c03_compose_check.py "$project" "$env_file"
dc build scanner scanner-signatures minio minio-init checks worker
dc up -d --wait db redis minio scanner
dc run --rm minio-init
dc run --rm --no-deps checks uv run --frozen python manage.py migrate --noinput
# Real scanner health/version/signatures verified before behavior tests.
dc exec -T scanner clamdscan --config-file=/etc/clamav/clamd.c03.conf --ping=1
dc run --rm --no-deps checks timeout -k 10s 180s uv run --frozen python -m pytest tests/unit/c03/test_image_sanitization.py tests/unit/c03/test_scanner_contract.py tests/integration/c03/test_asset_processing.py tests/integration/c03/test_processing_worker.py tests/integration/c03/test_scanner_service.py -vv --strict-markers -o faulthandler_timeout=30
# Real non-eager worker consumes a durable attempt after a missed prompt. Kill
# during a scanner barrier, restart the actual broker, expire only the fixture
# lease and recover through the production reconciler/task with unchanged bounds.
dc run --rm --no-deps checks timeout -k 5s 60s uv run --frozen python docker/c03_processing_probe.py prepare
COMPOSE_FILE="${COMPOSE_FILE:-compose.yaml}:docker/compose.c03-worker-probe.yml" dc up -d --wait worker
dc run --rm --no-deps checks timeout -k 5s 40s uv run --frozen python docker/c03_processing_probe.py start
dc kill -s SIGKILL worker
dc restart redis
dc up -d --wait redis
dc up -d --wait --force-recreate worker
dc run --rm --no-deps checks timeout -k 5s 40s uv run --frozen python docker/c03_processing_probe.py recover
dc stop scanner
dc run --rm --no-deps checks timeout -k 5s 30s uv run --frozen python docker/c03_processing_probe.py scanner-outage
dc up -d --wait scanner
dc run --rm --no-deps checks timeout -k 5s 30s uv run --frozen python docker/c03_processing_probe.py scanner-restored
