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

import causal_metrics as m
from causal_classify import classify

ROOT = Path.cwd()
BASE = ROOT / ".runtime/causal-evidence"
PRIVATE = ROOT / ".runtime/causal-private"
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
TESTS = [
    "tests/integration/c02/test_account_migrations.py::test_populated_c01_upgrade_preserves_identity_and_sessions",
    "tests/integration/c03/test_c03_migrations.py::test_optional_profiles_not_created",
    "tests/integration/c03/test_c03_migrations.py::test_restriction_has_reasoned_forward_history",
    "tests/integration/c03/test_upgrade_from_c02.py::test_upgrade_replays_all_eleven_capability_cases",
    "tests/integration/c04/test_search_eligibility.py::test_candidate_budget_fails_without_partial_output_and_recovers",
]


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
    m.PROJECT = "fitlink-c04-causal-" + os.environ["GITHUB_RUN_ID"] + "-" + label
    assert re.fullmatch(r"fitlink-c04-causal-[0-9]+-[a-z0-9]+", m.PROJECT)
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
    (m.PRIVATE / "owned").write_text(m.PROJECT)


def cleanup(summary):
    if not (m.PRIVATE / "owned").exists():
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
    code = subprocess.run(
        ["timeout", "-k", "10s", str(seconds) + "s", *args],
        cwd=m.SOURCE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode
    summary["stages"].append(
        {
            "stage": name,
            "start_ns": start,
            "end_ns": time.monotonic_ns(),
            "exit_code": code,
        }
    )
    return code


def readiness():
    raw = m.capture([*m.compose("ps", "--all", "--format", "json")], timeout=3)
    result = {}
    try:
        rows = (
            json.loads(raw)
            if raw and raw.lstrip().startswith("[")
            else [json.loads(x) for x in (raw or "").splitlines()]
        )
        for x in rows:
            service = x.get("Service")
            if service not in {"minio", "minio-init"}:
                continue
            result[service] = {
                "state": x.get("State")
                if x.get("State")
                in {"running", "exited", "created", "restarting", "dead", "paused"}
                else "unknown",
                "health": x.get("Health")
                if x.get("Health") in {"healthy", "unhealthy", "starting"}
                else "unknown",
                "exit_code": x.get("ExitCode")
                if type(x.get("ExitCode")) is int
                else None,
            }
    except (ValueError, TypeError):
        return None
    return result if raw is not None else None


def minio():
    source = ROOT / ".runtime/seven/.runtime/c03"
    verify(ROOT / ".runtime/seven", "seven")
    configure(source, "minio")
    summary = {
        "acceptance": False,
        "stages": [],
        "source_sha": "0a867328a6d8ee8c71ec9bd9eeb8910221d1b270",
        "operations": None,
    }
    try:
        assert (
            shell_stage(
                summary,
                "immutable_identity",
                ["python", "docker/c03_baseline.py", ".runtime/c02"],
                30,
            )
            == 0
        )
        # Verify the whole C03 fixture with the current C04 tree verifier.
        assert (
            shell_stage(
                summary,
                "immutable_c03",
                [
                    "python",
                    str(ROOT / ".runtime/seven/docker/c04_baseline.py"),
                    str(source),
                ],
                30,
            )
            == 0
        )
        events = m.OUT / "operations"
        events.mkdir(mode=0o777)
        events.chmod(0o777)
        # Only PATH delegation and observation mounts differ. Original script,
        # mc binary, env, dependency health and provisioning commands are intact.
        m.OVERRIDE.write_text(
            'services:\n  minio-init:\n    entrypoint: ["sh", "-c", "export PATH=/observe/bin:$$PATH; exec sh /init/minio-init.sh"]\n    volumes:\n      - '
            + str(ROOT / "docker/mc_observe.py")
            + ":/observe/bin/mc:ro\n      - "
            + str(events)
            + ":/observe/events\n"
        )
        for name, args, limit in [
            ("env", ["python", "docker/generate_env.py", str(m.ENV)], 30),
            ("config", m.compose("config", "--quiet"), 30),
            ("build", m.compose("build", "minio", "minio-init"), 900),
            ("services", m.compose("up", "-d", "--wait", "minio"), 180),
        ]:
            assert shell_stage(summary, name, args, limit) == 0
        summary["before_init"] = {
            "mono_ns": time.monotonic_ns(),
            "services": readiness(),
        }
        summary["original_script_sha256"] = hashlib.sha256(
            (source / "docker/minio-init.sh").read_bytes()
        ).hexdigest()
        summary["daemon_probe_exit"] = subprocess.run(
            ["docker", "version", "--format", "{{.Server.Version}}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=10,
        ).returncode
        # Retain stopped init until numeric inspection; remove in owned cleanup.
        summary["init_exit_code"] = shell_stage(
            summary,
            "original_minio_init",
            m.compose("run", "--name", m.PROJECT + "-init", "minio-init"),
            150,
        )
        summary["after_init"] = {
            "mono_ns": time.monotonic_ns(),
            "services": readiness(),
        }
        raw = m.capture(
            [
                "docker",
                "inspect",
                "--format",
                "{{.State.ExitCode}}",
                m.PROJECT + "-init",
            ]
        )
        summary["container_exit_code"] = (
            int(raw.strip()) if raw and re.fullmatch(r"[0-9]+\s*", raw) else None
        )
        path = events / "mc.jsonl"
        if path.exists() and path.stat().st_size <= 65536:
            rows = [json.loads(x) for x in path.read_text().splitlines()]
            allowed = {
                "alias",
                "ready",
                "bucket",
                "anonymous",
                "policy",
                "user",
                "attach",
                "unknown",
            }
            assert len(rows) <= 256
            assert all(
                set(r) <= {"event", "operation", "mono_ns", "exit_code"}
                and r["event"] in {"start", "end"}
                and r["operation"] in allowed
                and type(r["mono_ns"]) is int
                and (r["event"] != "end" or type(r["exit_code"]) is int)
                for r in rows
            )
            summary["operations"] = rows
            summary["readiness_attempts"] = sum(
                r["event"] == "start" and r["operation"] == "alias" for r in rows
            )
        summary["immutable_tree_unchanged"] = (
            shell_stage(
                summary,
                "immutable_after",
                [
                    "python",
                    str(ROOT / ".runtime/seven/docker/c04_baseline.py"),
                    str(source),
                ],
                30,
            )
            == 0
        )
    except Exception:
        summary["diagnostic_error"] = "bounded_stage_or_observer_failure"
    finally:
        cleanup(summary)
        summary["classification"] = classify(summary)
        write(m.OUT / "summary.json", summary)
    return (
        0
        if summary.get("cleanup_complete") and "diagnostic_error" not in summary
        else 1
    )


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
                "CAUSAL_MODE=" + mode,
                "-e",
                "PYTEST_PLUGINS=causal_plugin",
                "-e",
                "PYTHONPATH=/telemetry",
                "-v",
                str(ROOT / "docker/causal_plugin.py")
                + ":/telemetry/causal_plugin.py:ro",
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
            600,
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
                "thread_stopped": not sampler.thread.is_alive(),
                "interval_seconds": 5,
            }
        cleanup(summary)
        try:
            verify(source, key)
            summary["source_unchanged"] = True
        except Exception:
            summary["source_unchanged"] = False
        summary["evidence"] = evidence_check(m.OUT, summary.get("sampler", {}))
        summary["calibration_after"] = calibration()
        write(m.OUT / "summary.json", summary)
    return summary


def evidence_check(folder, sampler):
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
        assert c["unknown_nodes"] == 0 and c["count"] > 0
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
        return {
            "valid": True,
            "cases": c["count"],
            "sequence_sha256": c["sequence_sha256"],
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
    # within two-job budget (the other independent job localizes MinIO).
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
            "observation_controls": "minimal excludes cursor wrapper; order/time effects remain possible, indirect overhead not fully isolated",
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
        ("minio", "seven"),
        ("sixfull", "six"),
        ("sevenfull", "seven"),
        ("sevenminimal", "seven"),
        ("sixminimal", "six"),
    ]:
        folder = PRIVATE / label
        marker = folder / "owned"
        expected = "fitlink-c04-causal-" + os.environ["GITHUB_RUN_ID"] + "-" + label
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
        if label == "minio":
            m.SOURCE = m.SOURCE / ".runtime/c03"
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
    BASE.mkdir(parents=True, exist_ok=False)
    PRIVATE.mkdir(mode=0o700, parents=True, exist_ok=False)
    return (
        minio()
        if sys.argv[1:] == ["minio"]
        else paired()
        if sys.argv[1:] == ["paired"]
        else 2
    )


if __name__ == "__main__":
    try:
        code = main()
    except Exception:
        code = 1
    raise SystemExit(code)
