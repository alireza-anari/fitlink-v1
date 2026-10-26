"""One bounded Task 7 fixture-cost observation with isolated service ownership."""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

EXPECTED_SHA = "2b2790cdf9019338ddeb09f9df2fdfb1fa0dd331"
EXPECTED_TREE = "f4a49666111ce27d6c12cc6aff89f3430c7ea243"
PROJECT = "fitlink-c04-task07-fixture-cost"
LOCKS = ("uv.lock", "package-lock.json")
TESTS = (
    "tests/integration/c04/test_educational_posts.py::test_post_receipt_payload_and_expected_version_are_fenced",
    "tests/integration/c04/test_post_races.py::test_stale_post_edit_cannot_replace_current_revision",
    "tests/integration/c04/test_post_races.py::test_concurrent_same_version_post_edit_has_one_winner",
    "tests/integration/c04/test_educational_posts.py::test_confirmed_post_activates_only_complete_copies_and_edit_withdraws",
)


class DiagnosticStop(Exception):
    def __init__(self, stage: str, classification: str):
        super().__init__(classification)
        self.stage = stage
        self.classification = classification


def safe_classification(data: bytes) -> str:
    text = data[-1_000_000:].decode("utf-8", errors="replace").lower()
    if any(x in text for x in ("temporary failure in name resolution", "could not resolve", "name or service not known")):
        return "dns_resolution"
    if any(x in text for x in ("tls", "ssl", "certificate verify")):
        return "tls_or_certificate"
    if any(x in text for x in ("timed out", "timeout")):
        return "timeout"
    if any(x in text for x in ("no space left", "out of memory", "oomkilled")):
        return "resource_pressure"
    if any(x in text for x in ("connection refused", "could not connect", "connection reset")):
        return "connection_failure"
    if any(x in text for x in ("failed to download", "download failed", "http status")):
        return "dependency_download"
    if any(x in text for x in ("invalid interpolation", "variable is not set", "compose config")):
        return "compose_configuration"
    return "unclassified"


def run_command(name, args, *, cwd, env=None, timeout=30):
    started = time.monotonic()
    code = 127
    data = b""
    timed_out = False
    wrapped = ["timeout", "--signal=TERM", "--kill-after=5s", f"{int(timeout)}s", *args]
    with tempfile.TemporaryFile() as log:
        try:
            child = subprocess.Popen(
                wrapped,
                cwd=str(cwd),
                env=env,
                stdout=log,
                stderr=subprocess.STDOUT,
            )
        except OSError:
            event = {
                "stage": name,
                "exit_code": 127,
                "wall_seconds": round(time.monotonic() - started, 6),
                "timed_out": False,
                "output_limit_exceeded": False,
                "failure_class": "command_unavailable",
            }
            return event, data
        code = child.wait()
        elapsed = time.monotonic() - started
        timed_out = code == 124 and elapsed >= max(1.0, timeout - 1.0)
        size = os.fstat(log.fileno()).st_size
        log.seek(max(0, size - 1_000_000))
        data = log.read(1_000_000)
    event = {
        "stage": name,
        "exit_code": int(code),
        "wall_seconds": round(time.monotonic() - started, 6),
        "timed_out": timed_out,
        "output_limit_exceeded": False,
    }
    if code != 0 or timed_out:
        event["failure_class"] = "timeout" if timed_out else safe_classification(data)
    return event, data

def git_text(source: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(source), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        timeout=10,
        check=True,
    )
    return result.stdout.strip()


def file_hashes(source: Path) -> dict[str, str | None]:
    result: dict[str, str | None] = {}
    for name in LOCKS:
        path = source / name
        result[name] = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    return result


def clean_environment() -> dict[str, str]:
    env = os.environ.copy()
    for key in (
        "GITHUB_TOKEN",
        "ACTIONS_RUNTIME_TOKEN",
        "ACTIONS_ID_TOKEN_REQUEST_TOKEN",
        "NODE_AUTH_TOKEN",
    ):
        env.pop(key, None)
    return env


def resource_ids(project: str, cwd: Path, env: dict[str, str], stages: list[dict]) -> tuple[dict[str, int | None], bool]:
    specs = {
        "containers": ["docker", "ps", "-aq", "--filter", f"label=com.docker.compose.project={project}"],
        "networks": ["docker", "network", "ls", "-q", "--filter", f"label=com.docker.compose.project={project}"],
        "volumes": ["docker", "volume", "ls", "-q", "--filter", f"label=com.docker.compose.project={project}"],
    }
    counts: dict[str, int | None] = {}
    ok = True
    for label, args in specs.items():
        event, output = run_command(f"inventory_{label}", args, cwd=cwd, env=env, timeout=10)
        stages.append(event)
        if event["exit_code"] != 0 or event["timed_out"]:
            counts[label] = None
            ok = False
        else:
            counts[label] = len([line for line in output.decode(errors="replace").splitlines() if line.strip()])
    return counts, ok


def main() -> int:
    workspace = Path(os.environ.get("GITHUB_WORKSPACE", Path.cwd())).resolve()
    source = (workspace / ".runtime/task7-source").resolve()
    output = workspace / ".runtime/task07-fixture-cost"
    output.mkdir(parents=True, exist_ok=True)
    metrics_path = output / "metrics.json"
    outcome_path = output / "outcome.json"
    private_env = output / "private.env"
    stages: list[dict] = []
    before_locks: dict[str, str | None] = {}
    after_locks: dict[str, str | None] = {}
    source_before: dict[str, object] = {}
    source_after: dict[str, object] = {}
    env_values: dict[str, str] = {}
    compose_base: list[str] | None = None
    may_own_resources = False
    preflight_inventory_empty = False
    cleanup: dict[str, object] = {"status": "not_started", "verified": False}
    private_env_removed = True
    pytest_exit_code: int | None = None
    test_status_counts: dict[str, int] | None = None
    metrics_sha256: str | None = None
    failure_stage: str | None = None
    failure_class: str | None = None
    final_exit = 1
    base_env = clean_environment()

    try:
        current_stage = "diagnostic_syntax_check"
        syntax_command = [
            sys.executable,
            "-c",
            "import ast,pathlib,sys; [ast.parse(pathlib.Path(p).read_text(encoding='utf-8')) for p in sys.argv[1:]]",
            str(workspace / "docker/task07_fixture_cost_probe.py"),
            str(workspace / "docker/task07_fixture_cost_plugin.py"),
        ]
        event, _ = run_command("diagnostic_syntax_check", syntax_command, cwd=workspace, env=base_env, timeout=15)
        stages.append(event)
        if event["exit_code"] != 0 or event["timed_out"]:
            raise DiagnosticStop(current_stage, "diagnostic_python_syntax_invalid")

        source_before = {
            "head": git_text(source, "rev-parse", "HEAD"),
            "tree": git_text(source, "rev-parse", "HEAD^{tree}"),
            "clean": git_text(source, "status", "--porcelain=v1", "--untracked-files=all") == "",
        }
        before_locks = file_hashes(source)
        if source_before["head"] != EXPECTED_SHA or source_before["tree"] != EXPECTED_TREE or not source_before["clean"]:
            raise DiagnosticStop("source_identity", "source_identity_mismatch")

        current_stage = "lock_check"
        event, _ = run_command("lock_check", ["uv", "lock", "--check"], cwd=source, env=base_env, timeout=60)
        stages.append(event)
        if event["exit_code"] != 0 or event["timed_out"]:
            raise DiagnosticStop(current_stage, event.get("failure_class", "lock_check_failed"))

        current_stage = "frozen_dependency_sync"
        event, _ = run_command(
            "frozen_dependency_sync",
            ["uv", "sync", "--frozen", "--group", "dev", "--python", "3.13.15", "--no-progress"],
            cwd=source,
            env=base_env,
            timeout=600,
        )
        stages.append(event)
        if event["exit_code"] != 0 or event["timed_out"] or event["output_limit_exceeded"]:
            raise DiagnosticStop(current_stage, event.get("failure_class", "dependency_sync_failed"))

        current_stage = "private_environment_generation"
        event, _ = run_command(
            "private_environment_generation",
            [sys.executable, str(source / "docker/generate_env.py"), str(private_env)],
            cwd=source,
            env=base_env,
            timeout=15,
        )
        stages.append(event)
        if event["exit_code"] != 0 or event["timed_out"] or not private_env.is_file():
            raise DiagnosticStop(current_stage, event.get("failure_class", "private_environment_failed"))
        env_values = {}
        for line in private_env.read_text(encoding="utf-8").splitlines():
            key, sep, value = line.partition("=")
            if sep:
                env_values[key] = value

        current_stage = "preexisting_resource_inventory"
        before_resources, inventory_ok = resource_ids(PROJECT, source, base_env, stages)
        if not inventory_ok:
            raise DiagnosticStop(current_stage, "docker_inventory_unavailable")
        preflight_inventory_empty = all(value == 0 for value in before_resources.values())
        if not preflight_inventory_empty:
            raise DiagnosticStop(current_stage, "ownership_conflict")

        compose_base = [
            "docker", "compose", "-f", str(source / "compose.yaml"),
            "-p", PROJECT, "--env-file", str(private_env),
        ]
        current_stage = "compose_config"
        event, _ = run_command("compose_config", compose_base + ["config", "--quiet"], cwd=source, env=base_env, timeout=30)
        stages.append(event)
        if event["exit_code"] != 0 or event["timed_out"]:
            raise DiagnosticStop(current_stage, event.get("failure_class", "compose_config_failed"))

        current_stage = "service_startup"
        may_own_resources = True
        event, _ = run_command("service_startup", compose_base + ["up", "-d", "--wait", "db", "redis"], cwd=source, env=base_env, timeout=180)
        stages.append(event)
        if event["exit_code"] != 0 or event["timed_out"]:
            raise DiagnosticStop(current_stage, event.get("failure_class", "service_startup_failed"))

        current_stage = "service_health_verification"
        event, output_bytes = run_command("service_health_verification", compose_base + ["ps", "--format", "json"], cwd=source, env=base_env, timeout=15)
        stages.append(event)
        if event["exit_code"] != 0 or event["timed_out"]:
            raise DiagnosticStop(current_stage, event.get("failure_class", "service_health_query_failed"))
        text = output_bytes.decode("utf-8", errors="replace").strip()
        try:
            parsed = json.loads(text)
            services = parsed if isinstance(parsed, list) else [parsed]
        except json.JSONDecodeError:
            services = []
            for line in text.splitlines():
                try:
                    value = json.loads(line)
                    if isinstance(value, dict):
                        services.append(value)
                except json.JSONDecodeError:
                    services = []
                    break
        health = sorted(
            [
                {
                    "service": item.get("Service"),
                    "state": item.get("State"),
                    "health": item.get("Health"),
                }
                for item in services
                if isinstance(item, dict) and item.get("Service") in {"db", "redis"}
            ],
            key=lambda x: str(x["service"]),
        )
        service_health_ok = (
            {item["service"] for item in health} == {"db", "redis"}
            and all(item.get("state") == "running" and item.get("health") == "healthy" for item in health)
        )
        stages.append({"stage": "service_health_verdict", "services": health, "healthy": service_health_ok})
        if not service_health_ok:
            raise DiagnosticStop(current_stage, "required_service_unhealthy")

        current_stage = "pytest_four_test_subset"
        pytest_env = clean_environment()
        needed = (
            "POSTGRES_PASSWORD",
            "POSTGRES_DB",
            "POSTGRES_USER",
            "REDIS_URL",
            "CELERY_BROKER_URL",
            "CELERY_RESULT_BACKEND",
            "CHANNEL_REDIS_URL",
        )
        for key in needed:
            if key in env_values:
                pytest_env[key] = env_values[key]
        pytest_env.update(
            {
                "POSTGRES_HOST": "127.0.0.1",
                "POSTGRES_PORT": env_values.get("POSTGRES_PORT", "5434"),
                "POSTGRES_DB": "fitlink",
                "POSTGRES_USER": "fitlink",
                "POSTGRES_PASSWORD": env_values["POSTGRES_PASSWORD"],
                "OTP_RATE_REDIS_URL": "redis://127.0.0.1:" + env_values.get("REDIS_HOST_PORT", "6381") + "/4",
                "DJANGO_SETTINGS_MODULE": "config.settings.test",
                "FITLINK_DIAG_OUTPUT": str(metrics_path),
                "FITLINK_DIAG_SOURCE_SHA": EXPECTED_SHA,
                "FITLINK_DIAG_SOURCE_TREE": EXPECTED_TREE,
                "FITLINK_DIAG_CONTROL_SHA": os.environ.get("FITLINK_DIAG_CONTROL_SHA", ""),
                "FITLINK_DIAG_LOCK_HASHES": json.dumps(before_locks, sort_keys=True),
            }
        )
        control_docker = str(workspace / "docker")
        source_path = str(source)
        old_pythonpath = pytest_env.get("PYTHONPATH", "")
        pytest_env["PYTHONPATH"] = os.pathsep.join(
            item for item in (source_path, control_docker, old_pythonpath) if item
        )
        command = [
            "uv", "run", "--frozen", "--no-sync", "pytest",
            "-q", "--strict-markers", "--tb=no", "--show-capture=no",
            "-p", "task07_fixture_cost_plugin",
            *TESTS,
        ]
        event, _ = run_command("pytest_four_test_subset", command, cwd=source, env=pytest_env, timeout=300)
        stages.append(event)
        pytest_exit_code = event["exit_code"]
        if metrics_path.is_file():
            try:
                metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
                test_status_counts = metrics.get("test_status_counts")
                metrics_sha256 = hashlib.sha256(metrics_path.read_bytes()).hexdigest()
                statuses = metrics.get("test_statuses", [])
                exact_selection = [row.get("test") for row in statuses] == list(TESTS)
                all_passed = (
                    exact_selection
                    and len(statuses) == 4
                    and all(row.get("status") == "passed" for row in statuses)
                    and metrics.get("pytest_exit_status") == 0
                )
            except (OSError, ValueError, TypeError):
                all_passed = False
        else:
            all_passed = False
        if event["timed_out"]:
            raise DiagnosticStop(current_stage, "test_subset_timeout")
        if pytest_exit_code != 0 or not all_passed:
            raise DiagnosticStop(current_stage, "test_subset_incomplete_or_failed")
        final_exit = 0

    except DiagnosticStop as exc:
        failure_stage = exc.stage
        failure_class = exc.classification
        final_exit = 1
    except Exception as exc:
        failure_stage = locals().get("current_stage", "harness")
        failure_class = "harness_exception_" + re.sub(r"[^A-Za-z0-9_]", "", type(exc).__name__)[:60]
        final_exit = 1
    finally:
        if may_own_resources and compose_base is not None and private_env.is_file():
            down_event, _ = run_command(
                "owned_cleanup_down",
                compose_base + ["down", "--remove-orphans", "--volumes"],
                cwd=source,
                env=base_env,
                timeout=60,
            )
            stages.append(down_event)
            after_resources, inventory_ok = resource_ids(PROJECT, source, base_env, stages)
            empty = inventory_ok and all(value == 0 for value in after_resources.values())
            cleanup = {
                "status": "completed" if down_event["exit_code"] == 0 and not down_event["timed_out"] and empty else "failed",
                "down_exit_code": down_event["exit_code"],
                "resources_after": after_resources,
                "verified": bool(down_event["exit_code"] == 0 and not down_event["timed_out"] and empty),
            }
            if not cleanup["verified"]:
                final_exit = 1
                failure_stage = failure_stage or "owned_cleanup"
                failure_class = failure_class or "owned_cleanup_unverified"
        else:
            cleanup = {
                "status": "not_created" if preflight_inventory_empty else "not_started",
                "verified": bool(preflight_inventory_empty and not may_own_resources),
                "resources_after": None,
            }
        try:
            if private_env.exists():
                private_env.unlink()
            private_env_removed = not private_env.exists()
        except OSError:
            private_env_removed = False
            final_exit = 1
            failure_stage = failure_stage or "private_environment_removal"
            failure_class = failure_class or "private_environment_removal_failed"

        try:
            source_after = {
                "head": git_text(source, "rev-parse", "HEAD"),
                "tree": git_text(source, "rev-parse", "HEAD^{tree}"),
                "clean": git_text(source, "status", "--porcelain=v1", "--untracked-files=all") == "",
            }
            after_locks = file_hashes(source)
        except Exception:
            source_after = {"head": None, "tree": None, "clean": False}
            after_locks = {}
        locks_unchanged = bool(before_locks) and before_locks == after_locks
        source_preserved = (
            source_after.get("head") == EXPECTED_SHA
            and source_after.get("tree") == EXPECTED_TREE
            and source_after.get("clean") is True
        )
        if not locks_unchanged or not source_preserved or not private_env_removed:
            final_exit = 1
            failure_stage = failure_stage or "preservation_verification"
            failure_class = failure_class or "preservation_check_failed"
        if metrics_path.is_file():
            try:
                metrics_sha256 = hashlib.sha256(metrics_path.read_bytes()).hexdigest()
            except OSError:
                pass
        outcome = {
            "schema_version": 1,
            "diagnostic_only": True,
            "acceptance": False,
            "execution_source_sha": EXPECTED_SHA,
            "execution_source_tree": EXPECTED_TREE,
            "diagnostic_control_sha": os.environ.get("FITLINK_DIAG_CONTROL_SHA"),
            "expected_tests": list(TESTS),
            "dependency_lock_sha256_before": before_locks,
            "dependency_lock_sha256_after": after_locks,
            "dependency_lockfiles_unchanged": locks_unchanged,
            "source_before": source_before,
            "source_after": source_after,
            "source_preserved": source_preserved,
            "stages": stages,
            "pytest_exit_code": pytest_exit_code,
            "test_status_counts": test_status_counts,
            "metrics_present": metrics_path.is_file(),
            "metrics_sha256": metrics_sha256,
            "owned_cleanup": cleanup,
            "private_environment_removed": private_env_removed,
            "failure_stage": failure_stage,
            "failure_class": failure_class,
            "local_unpublished_workspace_accessed": False,
        }
        outcome_path.write_text(json.dumps(outcome, sort_keys=True) + "\n", encoding="utf-8")
    return final_exit


if __name__ == "__main__":
    raise SystemExit(main())
