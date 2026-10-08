#!/bin/sh
# Task 4 owning gate: real private MinIO, never a fake-only storage PASS.
set -eu
if [ "${C03_STORAGE_GATE_CHILD:-}" != 1 ]; then
  exec env C03_STORAGE_GATE_CHILD=1 timeout -k 10s 900s sh "$0"
fi
project=fitlink-c03-private-storage
env_file=.env.c03-storage
[ -z "$(docker volume ls --filter label=com.docker.compose.project="$project" -q)" ] || {
  echo "Private storage gate requires new isolated volumes; existing data retained" >&2
  exit 1
}
python docker/generate_env.py "$env_file"
dc() { docker compose -p "$project" --env-file "$env_file" --profile test "$@"; }
cleanup() { dc down --remove-orphans >/dev/null 2>&1 || true; }
trap cleanup EXIT
dc config --quiet
dc build minio minio-init checks
dc up -d --wait db redis minio
dc run --rm minio-init
dc run --rm --no-deps checks uv run --frozen python manage.py migrate --noinput
dc run --rm --no-deps checks uv run --frozen python docker/c03_storage_probe.py
dc run --rm --no-deps checks timeout -k 10s 180s uv run --frozen pytest tests/unit/test_storage.py tests/unit/c03/test_upload_contract.py tests/unit/c03/test_asset_validation.py tests/integration/c03/test_upload_lifecycle.py tests/integration/c03/test_upload_races.py tests/integration/c03/test_private_assets.py tests/integration/test_minio_storage.py -vv --strict-markers -o faulthandler_timeout=30
