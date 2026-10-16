#!/bin/sh
# Exact immutable C02, populated same-database upgrade and independent clean C03.
set -eu
if [ "${C03_TASK14_CHILD:-}" != 1 ]; then
  exec env C03_TASK14_CHILD=1 timeout -k 20s 3300s sh "$0" "$@"
fi
umask 077
root=$(pwd)
baseline=$root/.runtime/c02
project=fitlink-c03-task14-upgrade
clean_project=fitlink-c03-task14-clean
private=$root/.runtime/task14-private
evidence=$root/.runtime/c03-task14-evidence
env_file=$root/.env.c03-task14-upgrade
clone_diagnostic_only=0
case "${1:-}" in
  '') ;;
  --native-processing-diagnostic)
    project=fitlink-c03-task14-native-diagnostic
    private=$root/.runtime/task14-native-private
    evidence=$root/.runtime/c03-task14-native-evidence
    env_file=$root/.env.c03-task14-native-diagnostic
    ;;
  --clone-diagnostic)
    clone_diagnostic_only=1
    project=fitlink-c03-task14-clone-diagnostic
    clean_project=fitlink-c03-task14-clone-clean
    private=$root/.runtime/task14-clone-private
    evidence=$root/.runtime/c03-task14-clone-evidence
    env_file=$root/.env.c03-task14-clone-diagnostic
    ;;
  *) exit 1 ;;
esac
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
for line in Path(sys.argv[1]).read_text(errors="replace").splitlines():
    if line.startswith("C03_TASK14_RUNTIME "):
        result = json.loads(line.removeprefix("C03_TASK14_RUNTIME "))
        bools = {"pid_one", "python_expected", "native_png", "native_jpeg",
                 "platform_supported", "cwd_expected", "decoder_expected",
                 "capabilities_zero", "isolation_ok"}
        ints = {"uid", "gid", "no_new_privileges", "seccomp", "child_exit"}
        versions = {"python_version", "pillow_version"}
        assert set(result) == bools | ints | versions
        assert all(type(result[k]) is bool for k in bools)
        assert all(type(result[k]) is int and -999 <= result[k] <= 65535 for k in ints)
        assert all(re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", result[k]) for k in versions)
        print("C03_TASK14_RUNTIME " + json.dumps(result), flush=True)
clone_lines = [
    line
    for line in Path(sys.argv[1]).read_text(errors="replace").splitlines()
    if line.startswith("C03_TASK14_CLONE_DIAGNOSTIC ")
]
assert len(clone_lines) <= 1
for line in clone_lines:
    clone = json.loads(line.removeprefix("C03_TASK14_CLONE_DIAGNOSTIC "))
    assert set(clone) == {
        "relative_path",
        "lstat_type",
        "error_class",
        "errno",
        "symlink_target_exists",
        "symlink_target_kind",
    }
    relative = clone["relative_path"]
    assert isinstance(relative, str) and 1 <= len(relative) <= 240
    assert not relative.startswith("/")
    assert all(ord(character) >= 32 and ord(character) != 127 for character in relative)
    assert clone["lstat_type"] in {
        "regular", "directory", "symlink", "socket", "fifo", "other",
        "missing", "not-applicable",
    }
    assert isinstance(clone["error_class"], str)
    assert re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,63}|none|unknown", clone["error_class"])
    error_number = clone["errno"]
    assert error_number is None or (
        type(error_number) is int and 1 <= error_number <= 4095
    )
    assert clone["symlink_target_exists"] in {"yes", "no", "not-applicable"}
    assert clone["symlink_target_kind"] in {
        "absolute", "relative", "unavailable", "not-applicable"
    }
    print("FIRST OFFENDING RELATIVE PATH: " + json.dumps(relative), flush=True)
    print("LSTAT TYPE: " + clone["lstat_type"], flush=True)
    print("ERROR CLASS: " + clone["error_class"], flush=True)
    print(
        "ERRNO: " + (str(error_number) if error_number is not None else "unavailable"),
        flush=True,
    )
    print("SYMLINK TARGET EXISTS: " + clone["symlink_target_exists"], flush=True)
    if clone["lstat_type"] == "symlink":
        print("SYMLINK TARGET KIND: " + clone["symlink_target_kind"], flush=True)
mutation_lines = [
    line
    for line in Path(sys.argv[1]).read_text(errors="replace").splitlines()
    if line.startswith("C03_TASK14_C02_MUTATION ")
]
assert len(mutation_lines) <= 32
for line in mutation_lines:
    mutation = json.loads(line.removeprefix("C03_TASK14_C02_MUTATION "))
    assert set(mutation) == {
        "path",
        "kind",
        "expected_type",
        "observed_type",
        "expected_sha256",
        "observed_sha256",
    }
    path = mutation["path"]
    assert isinstance(path, str) and re.fullmatch(r"[A-Za-z0-9._/-]{1,240}", path)
    assert not path.startswith("/") and ".." not in path.split("/") and "//" not in path
    assert mutation["kind"] in {"modified", "missing", "extra", "symlink"}
    assert mutation["expected_type"] in {"file", "directory", "missing", "symlink"}
    assert mutation["observed_type"] in {"file", "directory", "missing", "symlink"}
    for key in ("expected_sha256", "observed_sha256"):
        value = mutation[key]
        assert value is None or (
            isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value)
        )
    print("C03_TASK14_C02_MUTATION " + json.dumps(mutation, sort_keys=True), flush=True)
if not clone_lines:
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
c02_source_snapshot() {
  python - "$1" "$2" <<'PY'
import hashlib
import json
import os
import stat
import sys
from pathlib import Path, PurePosixPath

root = Path(sys.argv[1]).absolute()
out = Path(sys.argv[2])
manifest = json.loads(Path("docker/c03_source_manifest.json").read_text())
entries = manifest["entries"]
sources = {
    entry["path"]: entry
    for entry in entries
    if entry["type"] == "blob" and entry["mode"] in {"100644", "100755"}
}
directories = {
    entry["path"]
    for entry in entries
    if entry["type"] == "tree" and entry["mode"] == "040000"
}
generated_roots = {
    ".git",
    ".venv",
    "node_modules",
    "staticfiles",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "test-results",
    "playwright-report",
}
generated_files = {
    ".env.verify",
    ".env.c02-upgrade",
    ".runtime/upgrade/metadata.json",
}


def observed(path):
    if path.is_symlink():
        return {"observed_type": "symlink", "sha256": None}
    try:
        mode = path.stat().st_mode
    except OSError:
        return {"observed_type": "missing", "sha256": None}
    if stat.S_ISREG(mode):
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        return {"observed_type": "file", "sha256": digest.hexdigest()}
    if stat.S_ISDIR(mode):
        return {"observed_type": "directory", "sha256": None}
    return {"observed_type": "symlink", "sha256": None}


records = {}
for entry in entries:
    expected_type = "file" if entry["type"] == "blob" else "directory"
    records[entry["path"]] = {
        "expected_type": expected_type,
        **observed(root / entry["path"]),
    }

extras = 0


def record_invalid(relative, path):
    global extras
    if relative not in records:
        extras += 1
        if extras > 128:
            raise RuntimeError("C02 source diagnostic exceeded bound")
        records[relative] = {"expected_type": "missing", **observed(path)}


for parent, children, files in os.walk(root, followlinks=False):
    for name in (*children, *files):
        path = Path(parent) / name
        relative = path.relative_to(root).as_posix()
        parts = PurePosixPath(relative).parts
        if parts[0] in generated_roots:
            if relative == parts[0] and path.is_symlink():
                record_invalid(relative, path)
            if name in children:
                children.remove(name)
            continue
        if path.is_symlink():
            record_invalid(relative, path)
            if name in children:
                children.remove(name)
            continue
        if relative == ".runtime/c01":
            if name in children:
                children.remove(name)
            continue
        if relative.startswith("static/dist/") or relative == "static/dist":
            if relative != "static/dist" and (
                relative != "static/dist/app.css"
                or not path.is_file()
                or path.stat().st_mode & 0o111
            ):
                record_invalid(relative, path)
            continue
        if "__pycache__" in parts:
            if path.is_file() and not relative.endswith(".pyc"):
                record_invalid(relative, path)
            continue
        if relative in generated_files:
            if not path.is_file():
                record_invalid(relative, path)
            continue
        if path.is_file() and relative not in sources:
            record_invalid(relative, path)
            continue
        if (
            path.is_dir()
            and relative not in directories
            and relative not in {".runtime", ".runtime/upgrade"}
        ):
            record_invalid(relative, path)

out.write_text(json.dumps(records, sort_keys=True))
out.chmod(0o600)
PY
}
c02_source_compare() {
  c02_source_snapshot "$baseline" "$private/c02-source-after.json"
  python - "$private/c02-source-before.json" "$private/c02-source-after.json" <<'PY'
import json
import sys
from pathlib import Path

before = json.loads(Path(sys.argv[1]).read_text())
after = json.loads(Path(sys.argv[2]).read_text())
missing = {"expected_type": "missing", "observed_type": "missing", "sha256": None}
changes = []
for relative in sorted(set(before) | set(after)):
    old = before.get(relative, missing)
    new = after.get(relative, missing)
    if (old["observed_type"], old["sha256"]) == (
        new["observed_type"],
        new["sha256"],
    ):
        continue
    expected_type = old["observed_type"]
    observed_type = new["observed_type"]
    if observed_type == "symlink":
        kind = "symlink"
    elif observed_type == "missing":
        kind = "missing"
    elif expected_type == "missing":
        kind = "extra"
    else:
        kind = "modified"
    changes.append(
        {
            "path": relative,
            "kind": kind,
            "expected_type": expected_type,
            "observed_type": observed_type,
            "expected_sha256": old["sha256"],
            "observed_sha256": new["sha256"],
        }
    )
assert len(changes) <= 32, "C02 source mutation diagnostic exceeded output bound"
for change in changes:
    print("C03_TASK14_C02_MUTATION " + json.dumps(change, sort_keys=True), flush=True)
PY
}
if [ "${1:-}" = --native-processing-diagnostic ]; then
  # Real-service diagnostic only. The separate unqualified final verifier is
  # still mandatory and retains original C02 plus both complete rehearsals.
  python docker/generate_env.py "$env_file"
  diagnostic() { timeout -k 10s 300s docker compose -p "$project" -f "$root/compose.yaml" --env-file "$env_file" --profile test "$@"; }
  diagnostic_cleanup() {
    diagnostic down --remove-orphans >>"$private/cleanup.log" 2>&1
    test -z "$(docker ps -aq --filter label=com.docker.compose.project="$project")"
    test -z "$(docker network ls -q --filter label=com.docker.compose.project="$project")"
  }
  trap 'exit_status=$?; trap - EXIT; diagnostic_cleanup || exit_status=1; exit "$exit_status"' EXIT
  run_step diagnostic_build diagnostic build checks worker scanner scanner-signatures minio minio-init
  run_step diagnostic_services diagnostic up -d --wait db redis minio scanner
  run_step diagnostic_minio diagnostic run --rm minio-init
  run_step diagnostic_migrate diagnostic run --rm --no-deps checks /opt/venv/bin/python manage.py migrate --noinput
  run_step diagnostic_runtime_direct diagnostic run --rm --no-deps --user "$(id -u):$(id -g)" checks /opt/venv/bin/python docker/c03_upgrade_probe.py runtime unused
  run_step diagnostic_runtime_supervised diagnostic run --rm --no-deps --user "$(id -u):$(id -g)" checks timeout -k 5s 90s /opt/venv/bin/python docker/c03_upgrade_probe.py runtime unused
  run_step diagnostic_worker diagnostic up -d --wait worker
  run_step diagnostic_runtime_worker diagnostic exec -T worker timeout -k 5s 90s /opt/venv/bin/python docker/c03_upgrade_probe.py runtime unused
  run_step diagnostic_native diagnostic run --rm --no-deps --user "$(id -u):$(id -g)" checks timeout -k 5s 240s /opt/venv/bin/python docker/c03_upgrade_probe.py diagnostic unused
  run_step diagnostic_cleanup diagnostic_cleanup
  trap - EXIT
  exit
fi
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
cat > "$private/c02-populate-compose.yml" <<C02_POPULATE_COMPOSE
services:
  checks:
    volumes:
      - type: bind
        source: "$baseline"
        target: /app
        read_only: true
        bind:
          create_host_path: false
C02_POPULATE_COMPOSE
c02() {
  docker compose -p "$project" -f "$baseline/compose.yaml" \
    --env-file "$env_file" --profile test "$@"
}
c02_population() {
  docker compose -p "$project" -f "$baseline/compose.yaml" \
    -f "$private/c02-populate-compose.yml" \
    --env-file "$env_file" --profile test "$@"
}
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
run_step exact_c02_before_populate python docker/c03_baseline.py "$baseline"
run_step c02_source_snapshot_before c02_source_snapshot "$baseline" "$private/c02-source-before.json"
run_step c02_populate c02_population run --rm --no-deps --user "$(id -u):$(id -g)" \
  -v "$root/docker/c03_upgrade_probe.py:/task14/docker/c03_upgrade_probe.py:ro" \
  -v "$root/docker/c03_upgrade_probe_impl.py:/task14/docker/c03_upgrade_probe_impl.py:ro" \
  -v "$private/preservation:/rehearsal" checks /opt/venv/bin/python /task14/docker/c03_upgrade_probe.py prepare /rehearsal/metadata.json
run_step c02_source_mutation_compare c02_source_compare
run_step exact_c02_after_populate python docker/c03_baseline.py "$baseline"
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
  -v "$private/preservation:/rehearsal" checks /opt/venv/bin/python docker/c03_upgrade_probe.py verify /rehearsal/metadata.json
# Deliberate C03 commands only after exact preservation and session checks.
run_step upgrade_private_build c03 build scanner scanner-signatures minio minio-init
run_step upgrade_private_services c03 up -d --wait minio scanner
run_step upgrade_private_init c03 run --rm minio-init
run_step upgrade_scanner_health c03 exec -T scanner clamdscan --config-file=/etc/clamav/clamd.c03.conf --ping=1
probe() { c03 run --rm --no-deps --user "$(id -u):$(id -g)" -v "$private/preservation:/rehearsal" checks timeout -k 5s 240s /opt/venv/bin/python docker/c03_upgrade_probe.py "$@" /rehearsal/metadata.json; }
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
run_step exact_c02_host_preflight python docker/c03_baseline.py "$baseline"
run_step exact_c02_clean_runtime_preflight clean run --rm --no-deps checks uv run --frozen python docker/c03_baseline.py /app/.runtime/c02
cloneability_preflight() {
  cat > "$private/clone-diagnostic.py" <<'PY'
import json
import os
import re
import shutil
import stat
import tempfile
from pathlib import Path

source = Path("/app/.runtime/c02")
with tempfile.TemporaryDirectory(prefix="c03-task14-clone-") as temporary:
    destination = Path(temporary) / "baseline"
    try:
        shutil.copytree(
            source,
            destination,
            ignore=shutil.ignore_patterns(".git"),
        )
    except shutil.Error as aggregate:
        failures = aggregate.args[0]
        if not isinstance(failures, list) or not failures:
            result = {
                "relative_path": "<aggregate-entry-unavailable>",
                "lstat_type": "not-applicable",
                "error_class": "unknown",
                "errno": None,
                "symlink_target_exists": "not-applicable",
                "symlink_target_kind": "not-applicable",
            }
        else:
            src, _dst, message = failures[0]
            path = Path(src)
            try:
                relative = path.relative_to(source).as_posix()
            except ValueError:
                relative = "<outside-c02>"
            if len(relative) > 240:
                relative = "<relative-path-over-bound>"

            try:
                mode = path.lstat().st_mode
            except OSError:
                lstat_type = "missing"
            else:
                if stat.S_ISREG(mode):
                    lstat_type = "regular"
                elif stat.S_ISDIR(mode):
                    lstat_type = "directory"
                elif stat.S_ISLNK(mode):
                    lstat_type = "symlink"
                elif stat.S_ISSOCK(mode):
                    lstat_type = "socket"
                elif stat.S_ISFIFO(mode):
                    lstat_type = "fifo"
                else:
                    lstat_type = "other"

            if lstat_type == "symlink":
                target_exists = "yes" if path.exists() else "no"
                try:
                    target = os.readlink(path)
                except OSError:
                    target_kind = "unavailable"
                else:
                    target_kind = "absolute" if os.path.isabs(target) else "relative"
            else:
                target_exists = "not-applicable"
                target_kind = "not-applicable"

            match = re.search(r"\[Errno ([0-9]+)\]", str(message))
            error_number = int(match.group(1)) if match else None
            error_class = (
                OSError(error_number, "").__class__.__name__
                if error_number is not None
                else "unknown"
            )
            result = {
                "relative_path": relative,
                "lstat_type": lstat_type,
                "error_class": error_class,
                "errno": error_number,
                "symlink_target_exists": target_exists,
                "symlink_target_kind": target_kind,
            }
        print(
            "C03_TASK14_CLONE_DIAGNOSTIC " + json.dumps(result, sort_keys=True),
            flush=True,
        )
        raise SystemExit(1)
    else:
        print(
            "C03_TASK14_CLONE_DIAGNOSTIC "
            + json.dumps(
                {
                    "relative_path": "none",
                    "lstat_type": "not-applicable",
                    "error_class": "none",
                    "errno": None,
                    "symlink_target_exists": "not-applicable",
                    "symlink_target_kind": "not-applicable",
                },
                sort_keys=True,
            ),
            flush=True,
        )
        raise SystemExit(0)
PY
  chmod 644 "$private/clone-diagnostic.py"
  clean run --rm --no-deps \
    -v "$private/clone-diagnostic.py:/task14/clone-diagnostic.py:ro" \
    checks /opt/venv/bin/python /task14/clone-diagnostic.py
}
if [ "$clone_diagnostic_only" -eq 1 ]; then
  run_step cloneability_preflight cloneability_preflight
  exit
fi
run_step isolated_exact_baseline clean run --rm --no-deps checks uv run --frozen pytest tests/unit/c03/test_exact_baseline.py -q --strict-markers
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
clean_c02_browser_diagnostic() {
  diagnostic_script=$private/clean-c02-browser-diagnostic.py
  diagnostic_log=$private/clean-c02-browser-focused.log
  diagnostic_evidence=$evidence/browser-diagnostic.jsonl
  web_id=$(clean ps -q web)
  if [ -n "$web_id" ]; then
    web_state=$(docker inspect --format '{{.State.Status}}' "$web_id" 2>/dev/null || printf 'unavailable')
    web_health=$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}undefined{{end}}' "$web_id" 2>/dev/null || printf 'unavailable')
    web_restarts=$(docker inspect --format '{{.RestartCount}}' "$web_id" 2>/dev/null || printf 'unavailable')
  else
    web_state=missing
    web_health=unavailable
    web_restarts=unavailable
  fi
  python - "$diagnostic_evidence" "$web_state" "$web_health" "$web_restarts" <<'PY'
import json
import re
import sys
from pathlib import Path

out = Path(sys.argv[1])
state, health, restarts = sys.argv[2:]
assert re.fullmatch(r"[a-z-]{1,32}", state)
assert re.fullmatch(r"[a-z-]{1,32}", health)
restart_count = None if restarts == "unavailable" else int(restarts)
assert restart_count is None or 0 <= restart_count <= 1000000
out.write_text(
    json.dumps(
        {
            "event": "clean_web_service",
            "web_state": state,
            "web_health": health,
            "web_restart_count": restart_count,
        },
        sort_keys=True,
    )
    + "\n"
)
PY
  cat > "$diagnostic_script" <<'PY'
import json
import socket
import urllib.error
import urllib.request


def probe(target_class, url):
    try:
        response = urllib.request.urlopen(url, timeout=5)
    except urllib.error.HTTPError as error:
        result = {
            "target_class": target_class,
            "result": "reachable",
            "http_status": int(error.code),
            "error_class": "none",
            "errno": None,
        }
    except Exception as error:
        reason = getattr(error, "reason", error)
        error_number = getattr(reason, "errno", None)
        result = {
            "target_class": target_class,
            "result": "unreachable",
            "http_status": None,
            "error_class": reason.__class__.__name__,
            "errno": error_number if type(error_number) is int else None,
        }
    else:
        result = {
            "target_class": target_class,
            "result": "reachable",
            "http_status": int(response.status),
            "error_class": "none",
            "errno": None,
        }
        response.close()
    print("C03_TASK14_BROWSER_PROBE " + json.dumps(result, sort_keys=True), flush=True)


try:
    socket.getaddrinfo("web", 8000, type=socket.SOCK_STREAM)
except OSError:
    network = "unavailable"
else:
    network = "available"
print(
    "C03_TASK14_BROWSER_NETWORK "
    + json.dumps({"available": network}, sort_keys=True),
    flush=True,
)
probe("loopback-8001", "http://127.0.0.1:8001/fa/auth/login/")
probe("compose-web-8000", "http://web:8000/fa/auth/login/")
PY
  chmod 644 "$diagnostic_script"
  result=0
  clean run --rm --no-deps \
    -v "$diagnostic_script:/task14/clean-c02-browser-diagnostic.py:ro" \
    browser sh -c '/opt/venv/bin/python /task14/clean-c02-browser-diagnostic.py && exec uv run --frozen pytest tests/e2e/test_foundation_smoke.py::test_foundation_smoke -q --strict-markers --tb=long --tracing=off --screenshot=off --video=off' \
    >"$diagnostic_log" 2>&1 || result=$?
  python - "$diagnostic_log" "$diagnostic_evidence" "$result" <<'PY'
import json
import re
import sys
from pathlib import Path

log = Path(sys.argv[1]).read_text(errors="replace")
out = Path(sys.argv[2])
pytest_exit = int(sys.argv[3])
records = []
network = None
for line in log.splitlines():
    if line.startswith("C03_TASK14_BROWSER_NETWORK "):
        assert network is None
        network = json.loads(line.removeprefix("C03_TASK14_BROWSER_NETWORK "))
    if line.startswith("C03_TASK14_BROWSER_PROBE "):
        records.append(json.loads(line.removeprefix("C03_TASK14_BROWSER_PROBE ")))
assert network is not None and set(network) == {"available"}
assert network["available"] in {"available", "unavailable"}
assert len(records) == 2
by_target = {record["target_class"]: record for record in records}
assert set(by_target) == {"loopback-8001", "compose-web-8000"}
with out.open("a") as stream:
    stream.write(
        json.dumps(
            {"event": "browser_network", "available": network["available"]},
            sort_keys=True,
        )
        + "\n"
    )
    for target in ("loopback-8001", "compose-web-8000"):
        record = by_target[target]
        assert set(record) == {
            "target_class", "result", "http_status", "error_class", "errno"
        }
        assert record["result"] in {"reachable", "unreachable"}
        status = record["http_status"]
        assert status is None or type(status) is int and 100 <= status <= 599
        error_class = record["error_class"]
        assert re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,63}|none", error_class)
        error_number = record["errno"]
        assert error_number is None or type(error_number) is int and 1 <= error_number <= 4095
        stream.write(json.dumps(record, sort_keys=True) + "\n")

clean = re.sub(r"\x1b\[[0-9;]*m", "", log)
error_class = "none" if pytest_exit == 0 else "unavailable"
message = "none" if pytest_exit == 0 else "playwright navigation error unavailable"
for line in clean.splitlines():
    match = re.search(
        r"playwright\._impl\._errors\.([A-Za-z][A-Za-z0-9_]{0,63}):\s*(.+)",
        line,
    )
    if not match:
        continue
    error_class = match.group(1)
    raw = match.group(2)
    destination_match = re.search(
        r"https?://(?:127\.0\.0\.1|web):(?:8000|8001)(?:/[A-Za-z0-9._~!$&'()*+,;=:@%/-]*)?",
        raw,
    )
    destination = destination_match.group(0) if destination_match else None
    if "ERR_CONNECTION_REFUSED" in raw:
        message = "Page.goto: net::ERR_CONNECTION_REFUSED"
    elif "ERR_NAME_NOT_RESOLVED" in raw:
        message = "Page.goto: net::ERR_NAME_NOT_RESOLVED"
    elif "ERR_CONNECTION_RESET" in raw:
        message = "Page.goto: net::ERR_CONNECTION_RESET"
    elif "ERR_ABORTED" in raw:
        message = "Page.goto: net::ERR_ABORTED"
    elif "Timeout" in raw or "timeout" in raw:
        message = "Page.goto: timeout"
    else:
        message = "Page.goto: unclassified navigation failure"
    if destination is not None:
        message += " at " + destination
    break
assert re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,63}|none|unavailable", error_class)
assert 1 <= len(message) <= 300 and all(32 <= ord(character) < 127 for character in message)
with out.open("a") as stream:
    stream.write(
        json.dumps(
            {
                "event": "playwright_error",
                "error_class": error_class,
                "message": message,
                "pytest_exit_code": pytest_exit,
            },
            sort_keys=True,
        )
        + "\n"
    )
PY
  case "$result" in
    0|1) return 0 ;;
    *) return "$result" ;;
  esac
}
run_step clean_c02_browser_diagnostic clean_c02_browser_diagnostic
run_step clean_c02_browser clean run --rm --no-deps -e E2E_BASE_URL=http://web:8000 browser uv run --frozen pytest tests/e2e/c02 tests/e2e/test_foundation_smoke.py -q --strict-markers --tracing=off --screenshot=off --video=off
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