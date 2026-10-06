#!/bin/sh
set -eu
root=$(pwd)
baseline=${C02_BASELINE_DIR:-$root/.runtime/c01}
python docker/c02_baseline.py "$baseline"
# Original immutable C01 tests/configuration and full real-service rehearsal.
(
  cd "$baseline"
  uv sync --frozen --group dev
  npm ci
  npm run build:css
  npm run check:js
  uv run --frozen python manage.py collectstatic --noinput --settings=config.settings.build --ignore=src/styles.css
  uv run --frozen ruff check .
  uv run --frozen ruff format --check .
  uv run --frozen mypy config/settings/env.py config/health.py apps/assets/storage.py
  uv run --frozen python manage.py check --settings=config.settings.test
  uv run --frozen pytest tests/unit -q --strict-markers
  uv run --frozen python docker/production_check.py
  C01_VERIFY_PROJECT=fitlink-c02-immutable-c01 sh docker/verify_foundation.sh
)
python docker/c02_baseline.py "$baseline"
project=fitlink-c02-exact-upgrade
env_file=$root/.env.c02-upgrade
[ -z "$(docker volume ls --filter label=com.docker.compose.project="$project" -q)" ] || {
  echo "Exact upgrade requires new isolated volumes; existing data retained" >&2
  exit 1
}
python docker/generate_env.py "$env_file"
mkdir "$root/.runtime/upgrade"
chmod 777 "$root/.runtime/upgrade"
c01() { docker compose -p "$project" -f "$baseline/compose.yaml" --env-file "$env_file" --profile test "$@"; }
c02() { docker compose -p "$project" -f "$root/compose.yaml" --env-file "$env_file" --profile test "$@"; }
cleanup() { c02 down --remove-orphans >/dev/null 2>&1 || true; }
trap cleanup EXIT
c01 config --quiet
c01 build checks
c01 up -d --wait db redis
c01 run --rm --no-deps checks uv run --frozen python manage.py migrate --noinput
c01 run --rm --no-deps -v "$root/docker/c02_upgrade_probe.py:/probe.py:ro" -v "$root/.runtime/upgrade:/rehearsal" checks uv run --frozen python /probe.py prepare /rehearsal/metadata.json
# Same db service/volume/network/password; only the code and additive schema change.
c02 config --quiet
c02 build checks
c02 run --rm --no-deps checks uv run --frozen python manage.py migrate --noinput
c02 run --rm --no-deps -v "$root/docker/c02_upgrade_probe.py:/probe.py:ro" -v "$root/.runtime/upgrade:/rehearsal" checks uv run --frozen python /probe.py verify /rehearsal/metadata.json
c02 run --rm --no-deps checks uv run --frozen python manage.py makemigrations --check --dry-run
cleanup
trap - EXIT
# Independent zero-state C02 DB and every existing Foundation/browser/restart gate.
sh docker/verify_foundation.sh
