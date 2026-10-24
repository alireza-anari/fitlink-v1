# ruff: noqa: E501
# Fixed Compose/SQL literals only; no private values are exported.
"""One isolated causal diagnostic. Source checkouts are never edited."""

import ast
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import timing_metrics as m
from timing_profile import LABELS, PHASES

ROOT = Path.cwd()
BASE = ROOT / ".runtime/timing-evidence"
PRIVATE = ROOT / ".runtime/timing-private"
SOURCES = {
    "six": (
        "0787d7880f9fd27006bf76ae0f16e31536ef4503",
        "b207a0a8e946750a0dd1213f5460e51f67dd3000",
    ),
    "seven": (
        "2b2790cdf9019338ddeb09f9df2fdfb1fa0dd331",
        "f4a49666111ce27d6c12cc6aff89f3430c7ea243",
    ),
}
# Source order is the same relative order in the historical complete collection.
JOB = os.environ.get("TIMING_JOB", "migration")
MIGRATION_TESTS = [
    "tests/integration/c02/test_account_migrations.py::test_populated_c01_upgrade_preserves_identity_and_sessions",
    "tests/integration/c03/test_c03_migrations.py::test_optional_profiles_not_created",
]
BUDGET_TESTS = [
    "tests/integration/c04/test_search_eligibility.py::test_candidate_budget_fails_without_partial_output_and_recovers"
]
TESTS = MIGRATION_TESTS if JOB == "migration" else BUDGET_TESTS


def write(path, value):
    path.write_text(json.dumps(value, sort_keys=True, allow_nan=False) + "\n")


def calibration():
    results = []
    for _ in range(3):
        start = time.monotonic_ns()
        cpu = time.process_time_ns()
        value = 1
        for i in range(2_000_000):
            value = (value * 1664525 + i + 1013904223) & 0xFFFFFFFF
        results.append(
            {
                "wall_ns": time.monotonic_ns() - start,
                "cpu_ns": time.process_time_ns() - cpu,
                "result": value,
            }
        )
    return results


def verify(source, key):
    sha, tree = SOURCES[key]
    assert m.capture(["git", "-C", str(source), "rev-parse", "HEAD"]) == sha + "\n"
    assert (
        m.capture(["git", "-C", str(source), "rev-parse", "HEAD^{tree}"]) == tree + "\n"
    )
    assert m.capture(["git", "-C", str(source), "diff", "HEAD", "--"]) == ""


def configure(source, label):
    m.SOURCE = source
    m.PROJECT = (
        "fitlink-c04-timing-" + os.environ["GITHUB_RUN_ID"] + "-" + JOB + "-" + label
    )
    assert re.fullmatch(
        r"fitlink-c04-timing-[0-9]+-(migration|budget)-[a-z0-9]+", m.PROJECT
    )
    m.OUT = BASE / label
    m.OUT.mkdir(mode=0o777)
    m.OUT.chmod(0o777)
    m.PRIVATE = PRIVATE / label
    m.PRIVATE.mkdir(mode=0o700)
    m.ENV = m.PRIVATE / "service.env"
    m.OVERRIDE = m.PRIVATE / "compose.yml"
    for kind in ["container", "network", "volume"]:
        assert (
            m.capture(
                [
                    "docker",
                    kind,
                    "ls",
                    "-aq" if kind == "container" else "-q",
                    "--filter",
                    "label=com.docker.compose.project=" + m.PROJECT,
                ]
            )
            == ""
        )
    for name in [
        "db-data",
        "redis-data",
        "minio-data",
        "beat-data",
        "scanner-signatures",
    ]:
        assert (
            m.capture(
                [
                    "docker",
                    "volume",
                    "ls",
                    "-q",
                    "--filter",
                    "name=^" + m.PROJECT + "_" + name + "$",
                ]
            )
            == ""
        )
    for name in ["default", "scan-private"]:
        assert (
            m.capture(
                [
                    "docker",
                    "network",
                    "ls",
                    "-q",
                    "--filter",
                    "name=^" + m.PROJECT + "_" + name + "$",
                ]
            )
            == ""
        )
    (m.PRIVATE / "owned").write_text(m.PROJECT)


def cleanup(summary):
    marker = m.PRIVATE / "owned"
    if (
        not marker.is_file()
        or marker.is_symlink()
        or marker.stat().st_size > 200
        or marker.read_text() != m.PROJECT
    ):
        summary["cleanup_complete"] = False
        return
    code = subprocess.run(
        [
            "timeout",
            "-k",
            "10s",
            "120s",
            *m.compose("down", "--volumes", "--remove-orphans"),
        ],
        cwd=m.SOURCE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode
    remaining = [
        m.capture(
            [
                "docker",
                kind,
                "ls",
                "-aq" if kind == "container" else "-q",
                "--filter",
                "label=com.docker.compose.project=" + m.PROJECT,
            ]
        )
        for kind in ["container", "network", "volume"]
    ]
    summary["cleanup_complete"] = code == 0 and remaining == ["", "", ""]
    summary["cleanup_exit_code"] = code
    if summary["cleanup_complete"]:
        m.ENV.unlink(missing_ok=True)
        (m.PRIVATE / "owned").unlink()


def shell_stage(summary, name, args, seconds):
    start = time.monotonic_ns()
    print(
        json.dumps(
            {
                "event": "stage_start",
                "pass": m.OUT.name,
                "stage": name,
                "mono_ns": start,
            }
        ),
        flush=True,
    )
    code = subprocess.run(
        ["timeout", "-k", "10s", str(seconds) + "s", *args],
        cwd=m.SOURCE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode
    print(
        json.dumps(
            {
                "event": "stage_end",
                "pass": m.OUT.name,
                "stage": name,
                "mono_ns": time.monotonic_ns(),
                "exit_code": code,
            }
        ),
        flush=True,
    )
    summary["stages"].append(
        {
            "stage": name,
            "start_ns": start,
            "end_ns": time.monotonic_ns(),
            "exit_code": code,
        }
    )
    return code


def schema_counts():
    raw = m.capture(
        [
            *m.compose("exec", "-T", "db"),
            "psql",
            "-X",
            "-U",
            "fitlink",
            "-d",
            "fitlink",
            "-At",
            "-c",
            "SELECT json_build_object('tables',(SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' AND c.relkind='r'),'migrations',(SELECT count(*) FROM django_migrations),'content_types',(SELECT count(*) FROM django_content_type))",
        ]
    )
    try:
        x = json.loads(raw)
        return (
            x
            if set(x) == {"tables", "migrations", "content_types"}
            and all(type(v) is int and v >= 0 for v in x.values())
            else None
        )
    except (TypeError, ValueError):
        return None


def paired_run(key, mode, label):
    source = ROOT / ".runtime" / key
    verify(source, key)
    configure(source, label)
    summary = {
        "acceptance": False,
        "source_sha": SOURCES[key][0],
        "source_tree": SOURCES[key][1],
        "observer_mode": mode,
        "stages": [],
        "calibration_before": calibration(),
    }
    sampler = None
    try:
        m.OVERRIDE.write_text(
            'services:\n  worker:\n    command: ["uv", "run", "--frozen", "celery", "--quiet", "-A", "config.celery:app", "worker", "--loglevel=WARNING", "--concurrency=1", "--hostname=foundation@%h", "-I", "docker.c03_asset_restart_probe"]\n'
        )
        setup = [
            ("immutable_c01", ["python", "docker/c02_baseline.py", ".runtime/c01"], 30),
            ("immutable_c02", ["python", "docker/c03_baseline.py", ".runtime/c02"], 30),
            ("immutable_c03", ["python", "docker/c04_baseline.py", ".runtime/c03"], 30),
            ("env", ["python", "docker/generate_env.py", str(m.ENV)], 30),
            ("config", m.compose("config", "--quiet"), 30),
            (
                "build",
                m.compose(
                    "build",
                    "web",
                    "worker",
                    "beat",
                    "checks",
                    "minio",
                    "minio-init",
                    "scanner",
                    "scanner-signatures",
                ),
                900,
            ),
            (
                "services",
                m.compose("up", "-d", "--wait", "db", "redis", "minio", "scanner"),
                180,
            ),
            ("minio", m.compose("run", "--rm", "minio-init"), 150),
        ]
        for name, args, limit in setup:
            assert shell_stage(summary, name, args, limit) == 0
        for label2, args in [
            ("migrate", ["python", "manage.py", "migrate", "--noinput"]),
            ("noop", ["python", "manage.py", "migrate", "--noinput"]),
            (
                "drift",
                ["python", "manage.py", "makemigrations", "--check", "--dry-run"],
            ),
        ]:
            assert (
                shell_stage(
                    summary,
                    label2,
                    m.compose(
                        "run",
                        "--rm",
                        "--no-deps",
                        "checks",
                        "uv",
                        "run",
                        "--frozen",
                        *args,
                    ),
                    180,
                )
                == 0
            )
        summary["installed_schema"] = schema_counts()
        assert (
            shell_stage(
                summary,
                "runtime",
                m.compose("up", "-d", "--wait", "web", "worker", "beat"),
                180,
            )
            == 0
        )
        assert (
            shell_stage(
                summary,
                "scanner",
                m.compose(
                    "exec",
                    "-T",
                    "scanner",
                    "clamdscan",
                    "--config-file=/etc/clamav/clamd.c03.conf",
                    "--ping=1",
                ),
                30,
            )
            == 0
        )
        sampler = m.Sampler()
        sampler.thread.start()
        summary["pytest_exit_code"] = shell_stage(
            summary,
            "matched_subset",
            m.compose(
                "run",
                "--rm",
                "--no-deps",
                "--name",
                m.PROJECT + "-checks",
                "-e",
                "C03_FOUNDATION_TRIAGE=0",
                "-e",
                "TIMING_JOB=" + JOB,
                "-e",
                "CAUSAL_MODE=" + mode,
                "-e",
                "PYTEST_PLUGINS=timing_plugin",
                "-e",
                "PYTHONPATH=/telemetry",
                "-v",
                str(ROOT / "docker/timing_plugin.py")
                + ":/telemetry/timing_plugin.py:ro",
                "-v",
                str(ROOT / "docker/timing_profile.py")
                + ":/telemetry/timing_profile.py:ro",
                "-v",
                str(m.OUT) + ":/evidence",
                "checks",
                "uv",
                "run",
                "--frozen",
                "pytest",
                *TESTS,
                "-q",
                "--strict-markers",
                "--tb=no",
                "--show-capture=no",
            ),
            300 if JOB == "migration" else 600,
        )
    except Exception:
        summary["diagnostic_error"] = "bounded_stage_or_observer_failure"
    finally:
        if sampler:
            sampler.stop.set()
            sampler.thread.join(timeout=20)
            summary["sampler"] = {
                "samples": sampler.samples,
                "wall_ns": sampler.elapsed_ns,
                "host_process_cpu_ns": time.process_time_ns() - sampler.cpu_start,
                "errors": sampler.errors,
                "clock_sync": sampler.clock_sync,
                "clock_probe_attempts": sampler.clock_attempts,
                "thread_stopped": not sampler.thread.is_alive(),
                "interval_seconds": 5,
            }
        cleanup(summary)
        try:
            verify(source, key)
            summary["source_unchanged"] = True
        except Exception:
            summary["source_unchanged"] = False
        summary["evidence"] = evidence_check(m.OUT, summary.get("sampler", {}), mode)
        summary["calibration_after"] = calibration()
        write(m.OUT / "summary.json", summary)
    return summary


def resource_evidence(folder, expected_samples):
    try:
        path = folder / "host.jsonl"
        assert path.is_file() and path.stat().st_size <= 16 * 1024 * 1024
        rows = [json.loads(x) for x in path.read_text().splitlines()]
        assert 0 < len(rows) <= 200 and len(rows) == expected_samples
        host_usable = pg_usable = services_usable = 0
        services = {
            "db",
            "redis",
            "minio",
            "scanner",
            "web",
            "worker",
            "beat",
            "checks",
        }
        for row in rows:
            assert (
                type(row["mono_start_ns"]) is int
                and type(row["mono_end_ns"]) is int
                and 0 <= row["mono_start_ns"] <= row["mono_end_ns"]
            )
            host = row.get("host")
            if (
                isinstance(host, dict)
                and type(host.get("cpu_count")) is int
                and host["cpu_count"] > 0
                and isinstance(host.get("cpu_ticks"), list)
                and len(host["cpu_ticks"]) == 8
                and all(type(v) is int and v >= 0 for v in host["cpu_ticks"])
                and isinstance(host.get("memory_kib"), dict)
                and type(host["memory_kib"].get("MemAvailable")) is int
            ):
                host_usable += 1
            pg = row.get("postgres")
            if isinstance(pg, dict) and all(
                type(pg.get(k)) is int and pg[k] >= 0
                for k in [
                    "active",
                    "lock_wait",
                    "io_wait",
                    "lwlock_wait",
                    "ungranted_locks",
                ]
            ):
                pg_usable += 1
            containers = row.get("containers")
            if (
                isinstance(containers, dict)
                and services <= set(containers)
                and all(containers[k].get("running") is True for k in services)
            ):
                services_usable += 1
        # Diagnostic coverage contract, not an acceptance waiver. Individual
        # absent cgroup/pressure fields remain null and cannot support zero claims.
        valid = (
            host_usable * 5 >= len(rows) * 4
            and pg_usable * 5 >= len(rows) * 4
            and services_usable > 0
        )
        return {
            "valid": valid,
            "samples": len(rows),
            "host_usable": host_usable,
            "postgres_usable": pg_usable,
            "full_running_service_samples": services_usable,
            "missing_host_samples": len(rows) - host_usable,
            "missing_postgres_samples": len(rows) - pg_usable,
            "coverage_required_percent": 80,
        }
    except (OSError, ValueError, TypeError, KeyError, AssertionError):
        return {"valid": False, "reason": "missing_or_malformed_resource_journal"}


def evidence_check(folder, sampler, mode="full"):
    try:
        p = folder / "pytest.jsonl"
        assert p.is_file() and p.stat().st_size <= 16 * 1024 * 1024
        rows = [json.loads(x) for x in p.read_text().splitlines()]
        assert 0 < len(rows) <= 12000
        collections = [x for x in rows if x.get("event") == "collection"]
        finishes = [x for x in rows if x.get("event") == "finish"]
        assert len(collections) == len(finishes) == 1
        c = collections[0]
        f = finishes[0]
        assert c["unknown_nodes"] == 0 and c["count"] == len(TESTS)
        assert re.fullmatch("[a-f0-9]{64}", c["sequence_sha256"])
        assert f["exit_code"] == 0 and f["started"] == f["completed"] == c["count"]
        assert f["observer_fault"] is False and f["truncated"] is False
        assert all(
            f["counts"][k] == 0
            for k in ["failed", "error", "skipped", "xfailed", "xpassed", "deselected"]
        )
        assert f["counts"]["passed"] >= c["count"]
        assert (
            sampler["errors"] == 0
            and sampler["thread_stopped"]
            and sampler["samples"] > 0
        )
        assert sampler["clock_sync"]["common_origin_verified"] is True
        resources = resource_evidence(folder, sampler["samples"])
        assert resources["valid"]
        timing_path = folder / "timing.json"
        assert timing_path.is_file() and timing_path.stat().st_size <= 1_048_576
        timing = json.loads(timing_path.read_text())
        assert timing["job"] == JOB
        profile = timing["profile"]
        assert profile["fault"] is False and profile["enabled"] == (mode == "full")
        assert (
            timing["calibration"]["fault"] is False
            and timing["calibration"]["calls"] == 10000
        )
        assert (
            type(timing["calibration"]["wall_ns"]) is int
            and timing["calibration"]["wall_ns"] > 0
        )
        if mode == "full":
            assert set(profile["registered_labels"]) <= LABELS
            assert {"state_clone", "model_render", "migration_execute"} <= set(
                profile["registered_labels"]
            )
            assert isinstance(profile["rows"], list) and len(profile["rows"]) <= 2048
            counts = {}
            for row in profile["rows"]:
                assert row["label"] in LABELS and row["phase"] in PHASES
                assert type(row["ordinal"]) is int and 0 <= row["ordinal"] <= c["count"]
                assert all(
                    type(row[k]) is int and row[k] >= 0
                    for k in [
                        "count",
                        "wall_ns",
                        "cpu_ns",
                        "self_wall_ns",
                        "self_cpu_ns",
                        "first_start_ns",
                        "last_end_ns",
                    ]
                )
                assert (
                    row["self_wall_ns"] <= row["wall_ns"]
                    and row["self_cpu_ns"] <= row["cpu_ns"]
                    and row["first_start_ns"] <= row["last_end_ns"]
                )
                if row["phase"] == "call":
                    counts[row["label"]] = counts.get(row["label"], 0) + row["count"]
            required = (
                {"state_clone": 1, "model_render": 1, "migration_execute": 1}
                if JOB == "migration"
                else {"corpus": 100, "unpublish": 100, "search": 2, "reconcile": 4}
            )
            assert all(counts.get(k, 0) >= n for k, n in required.items())
            if JOB == "budget":
                assert all(counts[k] == n for k, n in required.items())
        else:
            assert profile["rows"] is None and profile["registered_labels"] is None
        return {
            "valid": True,
            "cases": c["count"],
            "sequence_sha256": c["sequence_sha256"],
            "resource_coverage": resources,
        }
    except (OSError, ValueError, TypeError, KeyError, AssertionError):
        return {"valid": False, "reason": "missing_or_incomplete_numeric_evidence"}


def fixture_closure(root):
    paths = {x.split("::")[0] for x in TESTS}
    paths.update(
        str(x.relative_to(root)) for x in (root / "tests").rglob("conftest.py")
    )
    pending = list(paths)
    done = set()
    while pending:
        path = pending.pop()
        if path in done or not (root / path).is_file():
            continue
        done.add(path)
        for node in ast.walk(ast.parse((root / path).read_text())):
            modules = []
            if isinstance(node, ast.Import):
                modules = [x.name for x in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    parent = Path(path).parent
                    for _ in range(node.level - 1):
                        parent = parent.parent
                    module = ".".join(parent.parts) + (
                        ("." + node.module) if node.module else ""
                    )
                else:
                    module = node.module or ""
                modules = [module] + [module + "." + x.name for x in node.names]
            for module in modules:
                if not module.startswith("tests."):
                    continue
                name = module.replace(".", "/")
                for candidate in [name + ".py", name + "/__init__.py"]:
                    if (root / candidate).is_file() and candidate not in done:
                        pending.append(candidate)
    return done


def paired():
    # ABBA controls on ONE host. Independent reversed runner is not feasible
    # within two-job budget (the other independent job measures the other timing workload).
    root6 = ROOT / ".runtime/six"
    root7 = ROOT / ".runtime/seven"
    closure6 = fixture_closure(root6)
    closure7 = fixture_closure(root7)
    assert closure6 == closure7
    paths = sorted(closure6 | {"uv.lock", "pyproject.toml"})
    identities = {}
    for key in SOURCES:
        verify(ROOT / ".runtime" / key, key)
    for path in paths:
        a = ROOT / ".runtime/six" / path
        b = ROOT / ".runtime/seven" / path
        assert a.exists() == b.exists()
        if a.exists():
            assert a.read_bytes() == b.read_bytes()
            identities[path] = hashlib.sha256(a.read_bytes()).hexdigest()
    write(
        BASE / "comparison-contract.json",
        {
            "acceptance": False,
            "tests": TESTS,
            "identical_source_files": identities,
            "order": ["six_full", "seven_full", "seven_minimal", "six_minimal"],
            "independent_reversed_runner": False,
            "schema_equivalence": False,
            "fixture_source_equivalence": True,
            "observation_controls": "minimal disables cursor and migration/lifecycle timers; both modes import fixed gateways before test body (after fixtures), with import time inside call; order/cache and indirect effects remain possible",
        },
    )
    results = []
    for key, mode, label in [
        ("six", "full", "sixfull"),
        ("seven", "full", "sevenfull"),
        ("seven", "minimal", "sevenminimal"),
        ("six", "minimal", "sixminimal"),
    ]:
        s = paired_run(key, mode, label)
        results.append(s)
        if (
            s.get("pytest_exit_code") != 0
            or not s.get("cleanup_complete")
            or not s.get("source_unchanged")
            or not s.get("evidence", {}).get("valid")
            or (
                results[0].get("evidence", {}).get("sequence_sha256")
                != s.get("evidence", {}).get("sequence_sha256")
            )
        ):
            break
    valid = len(results) == 4 and all(
        x.get("pytest_exit_code") == 0
        and x.get("cleanup_complete")
        and x.get("source_unchanged")
        and x.get("evidence", {}).get("valid")
        and x["evidence"]["sequence_sha256"]
        == results[0]["evidence"]["sequence_sha256"]
        for x in results
    )
    write(
        BASE / "paired-summary.json",
        {"acceptance": False, "runs": results, "complete_pairs": bool(valid)},
    )
    return 0 if valid else 1


def emergency_cleanup():
    results = {}
    for label, key in [
        ("sixfull", "six"),
        ("sevenfull", "seven"),
        ("sevenminimal", "seven"),
        ("sixminimal", "six"),
    ]:
        folder = PRIVATE / label
        marker = folder / "owned"
        expected = (
            "fitlink-c04-timing-"
            + os.environ["GITHUB_RUN_ID"]
            + "-"
            + JOB
            + "-"
            + label
        )
        if not marker.is_file() or marker.is_symlink() or marker.stat().st_size > 200:
            continue
        if marker.read_text() != expected:
            results[label] = {"cleanup_complete": False, "reason": "ownership_mismatch"}
            continue
        m.PROJECT = expected
        m.PRIVATE = folder
        m.ENV = folder / "service.env"
        m.OVERRIDE = folder / "compose.yml"
        m.SOURCE = ROOT / ".runtime" / key
        result = {}
        cleanup(result)
        results[label] = result
    BASE.mkdir(parents=True, exist_ok=True)
    write(
        BASE / "emergency-cleanup.json", {"acceptance": False, "owned_results": results}
    )
    return 0 if all(x.get("cleanup_complete") for x in results.values()) else 1


def main():
    if sys.argv[1:] == ["cleanup"]:
        return emergency_cleanup()
    assert JOB in {"migration", "budget"}
    BASE.mkdir(parents=True, exist_ok=False)
    PRIVATE.mkdir(mode=0o700, parents=True, exist_ok=False)
    return paired() if sys.argv[1:] == ["paired"] else 2


if __name__ == "__main__":
    try:
        code = main()
    except Exception:
        code = 1
    raise SystemExit(code)
