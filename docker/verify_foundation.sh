#!/bin/sh
set -eu
project=${C01_VERIFY_PROJECT:-fitlink-foundation-verify}
env_file=${C01_VERIFY_ENV_FILE:-.env.verify}
# Existing project volumes cannot establish a genuinely clean startup gate.
[ -z "$(docker volume ls --filter label=com.docker.compose.project="$project" -q)" ] || {
  echo "Choose a new isolated verification project; existing volumes retained" >&2
  exit 1
}
python docker/generate_env.py "$env_file"
dc() { docker compose -p "$project" --env-file "$env_file" --profile test "$@"; }
cleanup() { dc down --remove-orphans >/dev/null 2>&1 || true; }
trap cleanup EXIT
# Quiet configuration validation never prints interpolated credentials.
dc config --quiet
dc build web worker beat minio minio-init checks browser
docker build --target production -t fitlink-foundation-production .
dc up -d --wait db redis minio
dc run --rm minio-init
dc run --rm web uv run --frozen python manage.py migrate --noinput
dc up -d --wait web worker beat
dc run --rm checks uv run --frozen python manage.py check
dc run --rm checks uv run --frozen python manage.py makemigrations --check --dry-run
# pytest creates a fresh PostgreSQL test DB from zero; no reuse-db option.
dc run --rm checks uv run --frozen pytest tests/unit tests/integration -q --strict-markers
# Exactly one Beat container; only the authorized C02 outbox scan.
[ "$(dc ps -q beat | wc -l)" -eq 1 ]
dc exec -T beat uv run --frozen python docker/healthcheck.py beat
dc exec -T worker uv run --frozen python docker/healthcheck.py worker
dc run --rm browser uv run --frozen pytest tests/e2e/test_foundation_smoke.py -q -m e2e --strict-markers
# Separate evidence: native C02 HTTP against a static-aware live_server using
# real PostgreSQL/Redis and a private in-memory SMS collector.
dc run --rm browser uv run --frozen pytest tests/e2e/c02 -q -m e2e --strict-markers
# Preserve volumes and exercise actual worker/broker/channel reconnection.
dc run --rm checks uv run --frozen python docker/c02_outbox_restart_probe.py prepare
dc restart redis
dc up -d --wait redis
attempt=0
until dc exec -T worker uv run --frozen python docker/healthcheck.py worker; do
  attempt=$((attempt + 1)); [ "$attempt" -lt 15 ] || exit 1
  sleep 2
done
dc run --rm checks uv run --frozen python docker/c02_outbox_restart_probe.py verify
dc run --rm checks uv run --frozen pytest tests/integration/test_redis.py tests/integration/test_channel_layer.py tests/integration/test_celery_roundtrip.py -q --strict-markers
# Private storage remains functional after a real server restart.
dc restart minio
dc up -d --wait minio
dc run --rm minio-init
dc run --rm checks uv run --frozen pytest tests/integration/test_minio_storage.py -q --strict-markers
dc run --rm browser uv run --frozen pytest tests/e2e/test_foundation_smoke.py -q -m e2e --strict-markers
