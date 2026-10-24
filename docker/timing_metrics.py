# ruff: noqa: E501
# Long literals are fixed numeric SQL and the unchanged original worker command.
"""One owned full-topology run; export only numeric/fixed-schema observations."""

import json
import math
import os
import re
import resource
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

SHA = "2b2790cdf9019338ddeb09f9df2fdfb1fa0dd331"
TREE = "f4a49666111ce27d6c12cc6aff89f3430c7ea243"
SERVICES = {
    "db",
    "redis",
    "minio",
    "minio-init",
    "scanner",
    "scanner-signatures",
    "web",
    "worker",
    "beat",
    "checks",
}
ROOT = Path.cwd()
SOURCE = ROOT / ".runtime/source"
OUT = ROOT / ".runtime/topology-evidence"
PRIVATE = ROOT / ".runtime/topology-private"
PROJECT = (
    "fitlink-c04-task07-topology-"
    + os.environ.get("GITHUB_RUN_ID", "0")
    + "-"
    + os.environ.get("GITHUB_RUN_ATTEMPT", "0")
)
ENV = PRIVATE / "service.env"
OVERRIDE = PRIVATE / "compose.yml"


def capture(command, timeout=5):
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=timeout,
            check=False,
        )
        if result.returncode or len(result.stdout) > 262144:
            return None
        return result.stdout.decode("utf-8", errors="strict")
    except (OSError, subprocess.TimeoutExpired, UnicodeError):
        return None


def integer(path):
    try:
        value = Path(path).read_text().strip()
        return int(value) if value != "max" else None
    except (OSError, ValueError):
        return None


def key_numbers(path, keys):
    try:
        lines = Path(path).read_text().splitlines()
        pairs = [line.split() for line in lines]
        return {k: int(v) for k, v in pairs if k in keys}
    except (OSError, ValueError):
        return None


def pressure(path):
    try:
        result = {}
        for line in Path(path).read_text().splitlines():
            kind, *values = line.split()
            if kind not in {"some", "full"}:
                continue
            result[kind] = {
                k: float(v)
                for k, v in (pair.split("=") for pair in values)
                if k in {"avg10", "avg60", "avg300", "total"}
            }
        return result
    except (OSError, ValueError):
        return None


def cgroup(path):
    result = {
        "cpu": key_numbers(
            path / "cpu.stat",
            {
                "usage_usec",
                "user_usec",
                "system_usec",
                "nr_periods",
                "nr_throttled",
                "throttled_usec",
            },
        ),
        "memory_bytes": integer(path / "memory.current"),
        "memory_limit_bytes": integer(path / "memory.max"),
        "memory_events": key_numbers(
            path / "memory.events", {"low", "high", "max", "oom", "oom_kill"}
        ),
        "pressure": {
            k: pressure(path / (k + ".pressure")) for k in ["cpu", "memory", "io"]
        },
    }
    try:
        quota, period = (path / "cpu.max").read_text().split()
        result["cpu_capacity"] = None if quota == "max" else int(quota) / int(period)
        result["cpu_quota_unlimited"] = quota == "max"
    except (OSError, ValueError, ZeroDivisionError):
        result["cpu_capacity"] = None
        result["cpu_quota_unlimited"] = None
    try:
        totals = dict.fromkeys(
            ["rbytes", "wbytes", "rios", "wios", "dbytes", "dios"], 0
        )
        devices = 0
        for line in (path / "io.stat").read_text().splitlines():
            devices += 1
            for pair in line.split()[1:]:
                k, v = pair.split("=")
                if k in totals:
                    totals[k] += int(v)
        result["io"] = {"devices": devices, **totals}
    except (OSError, ValueError):
        result["io"] = None
    return result


def host_metrics():
    result = {
        "cpu_count": os.cpu_count(),
        "affinity_count": len(os.sched_getaffinity(0)),
        "pressure": {
            k: pressure("/proc/pressure/" + k) for k in ["cpu", "memory", "io"]
        },
        "cgroup": cgroup(Path("/sys/fs/cgroup")),
    }
    try:
        result["cpu_ticks"] = [
            int(x) for x in Path("/proc/stat").read_text().splitlines()[0].split()[1:9]
        ]
        result["memory_kib"] = {
            k: int(v)
            for k, v in re.findall(
                r"^(MemAvailable|SwapFree|Dirty|Writeback):\s+(\d+)",
                Path("/proc/meminfo").read_text(),
                re.M,
            )
        }
        io = dict.fromkeys(
            [
                "read_ops",
                "read_sectors",
                "read_ms",
                "write_ops",
                "write_sectors",
                "write_ms",
                "inflight",
                "io_ms",
                "weighted_io_ms",
            ],
            0,
        )
        devices = 0
        for line in Path("/proc/diskstats").read_text().splitlines():
            cols = line.split()
            if not re.fullmatch(
                r"(sd[a-z]+|vd[a-z]+|xvd[a-z]+|nvme[0-9]+n[0-9]+)", cols[2]
            ):
                continue
            devices += 1
            for key, index in zip(io, [3, 5, 6, 7, 9, 10, 11, 12, 13], strict=True):
                io[key] += int(cols[index])
        result["disk"] = {"devices": devices, **io} if devices else None
        stat = os.statvfs(SOURCE)
        result["disk_available_bytes"] = stat.f_bavail * stat.f_frsize
    except (OSError, ValueError, IndexError):
        result["partial_unavailable"] = True
    return result


def containers():
    raw = capture(
        [
            "docker",
            "ps",
            "-aq",
            "--filter",
            "label=com.docker.compose.project=" + PROJECT,
        ]
    )
    if raw is None:
        return None, {}
    ids = raw.split()
    if len(ids) > 16 or any(not re.fullmatch("[a-f0-9]{12,64}", x) for x in ids):
        return None, {}
    if not ids:
        return {}, {}
    raw = capture(
        [
            "docker",
            "inspect",
            "--format",
            '{{index .Config.Labels "com.docker.compose.service"}} {{.State.Pid}} {{.State.Running}}',
            *ids,
        ]
    )
    if raw is None:
        return None, {}
    result, known = {}, {}
    for container_id, line in zip(ids, raw.splitlines(), strict=True):
        service, pid, running = line.split()
        if (
            service not in SERVICES
            or not pid.isdigit()
            or running not in {"true", "false"}
        ):
            continue
        metrics = {"running": running == "true", "cgroup": None}
        known[service] = container_id
        if int(pid):
            try:
                entry = next(
                    x[3:]
                    for x in Path("/proc/" + pid + "/cgroup").read_text().splitlines()
                    if x.startswith("0::")
                )
                # Kernel-derived absolute cgroup path is not exported.
                if ".." not in Path(entry).parts:
                    metrics["cgroup"] = cgroup(
                        Path("/sys/fs/cgroup") / entry.lstrip("/")
                    )
            except (OSError, StopIteration):
                pass
        result[service] = metrics
    return result, known


SQL = """SELECT json_build_object(
'active',(SELECT count(*) FROM pg_stat_activity WHERE pid<>pg_backend_pid() AND state='active'),
'lock_wait',(SELECT count(*) FROM pg_stat_activity WHERE pid<>pg_backend_pid() AND state='active' AND wait_event_type='Lock'),
'io_wait',(SELECT count(*) FROM pg_stat_activity WHERE pid<>pg_backend_pid() AND state='active' AND wait_event_type='IO'),
'lwlock_wait',(SELECT count(*) FROM pg_stat_activity WHERE pid<>pg_backend_pid() AND state='active' AND wait_event_type='LWLock'),
'client_wait',(SELECT count(*) FROM pg_stat_activity WHERE pid<>pg_backend_pid() AND state='active' AND wait_event_type='Client'),
'other_wait',(SELECT count(*) FROM pg_stat_activity WHERE pid<>pg_backend_pid() AND state='active' AND wait_event_type IS NOT NULL AND wait_event_type NOT IN ('Lock','IO','LWLock','Client')),
'test_active',(SELECT count(*) FROM pg_stat_activity WHERE pid<>pg_backend_pid() AND datname='test_fitlink' AND state='active'),
'service_active',(SELECT count(*) FROM pg_stat_activity WHERE pid<>pg_backend_pid() AND datname='fitlink' AND state='active'),
'other_active',(SELECT count(*) FROM pg_stat_activity WHERE pid<>pg_backend_pid() AND datname NOT IN ('test_fitlink','fitlink') AND state='active'),
'ungranted_locks',(SELECT count(*) FROM pg_locks WHERE NOT granted),
'io_timing_enabled',(current_setting('track_io_timing')='on'),
'database',(SELECT json_build_object('commits',xact_commit,'rollbacks',xact_rollback,'blocks_read',blks_read,'blocks_hit',blks_hit,'temp_bytes',temp_bytes,'deadlocks',deadlocks,'read_ms',blk_read_time,'write_ms',blk_write_time) FROM pg_stat_database WHERE datname='test_fitlink'),
'io_cluster',(SELECT json_build_object('reads',sum(reads),'writes',sum(writes),'read_ms',sum(read_time),'write_ms',sum(write_time),'fsyncs',sum(fsyncs),'fsync_ms',sum(fsync_time)) FROM pg_stat_io)
)"""


def numeric_tree(value):
    if value is None or type(value) is bool:
        return True
    if type(value) in {int, float}:
        return math.isfinite(value) and value >= 0
    return isinstance(value, dict) and all(numeric_tree(v) for v in value.values())


def database(container):
    raw = capture(
        [
            "docker",
            "exec",
            "-e",
            "PGOPTIONS=-c statement_timeout=1000 -c lock_timeout=500",
            "-e",
            "PGCONNECT_TIMEOUT=2",
            container,
            "psql",
            "-X",
            "-U",
            "fitlink",
            "-d",
            "fitlink",
            "-At",
            "-c",
            SQL,
        ]
    )
    try:
        result = json.loads(raw) if raw else None
        expected = {
            "active",
            "test_active",
            "service_active",
            "other_active",
            "lock_wait",
            "io_wait",
            "lwlock_wait",
            "client_wait",
            "other_wait",
            "ungranted_locks",
            "io_timing_enabled",
            "database",
            "io_cluster",
        }
        if (
            not isinstance(result, dict)
            or set(result) != expected
            or not numeric_tree(result)
        ):
            return None
        nested = {
            "database": {
                "commits",
                "rollbacks",
                "blocks_read",
                "blocks_hit",
                "temp_bytes",
                "deadlocks",
                "read_ms",
                "write_ms",
            },
            "io_cluster": {
                "reads",
                "writes",
                "read_ms",
                "write_ms",
                "fsyncs",
                "fsync_ms",
            },
        }
        for key, expected_keys in nested.items():
            if result[key] is not None and (
                not isinstance(result[key], dict) or set(result[key]) != expected_keys
            ):
                return None
        if type(result["io_timing_enabled"]) is not bool:
            return None
        if any(
            type(result[k]) is not int
            for k in expected - {"database", "io_cluster", "io_timing_enabled"}
        ):
            return None
        for key in nested:
            if result[key] is not None and any(
                v is not None and type(v) not in {int, float}
                for v in result[key].values()
            ):
                return None
        return result
    except (ValueError, TypeError):
        return None


class Sampler:
    def __init__(self):
        self.stop = threading.Event()
        self.samples = self.elapsed_ns = self.errors = 0
        self.cpu_start = time.process_time_ns()
        self.clock_sync = None
        self.clock_attempts = 0
        self.thread = threading.Thread(target=self.run, daemon=True)

    def probe_clock(self, observed, known):
        if self.clock_sync and self.clock_sync["common_origin_verified"]:
            return
        if (
            self.clock_attempts >= 3
            or not observed
            or not observed.get("checks", {}).get("running")
            or "checks" not in known
        ):
            return
        self.clock_attempts += 1
        before = time.monotonic_ns()
        raw = capture(
            [
                "docker",
                "exec",
                known["checks"],
                "python",
                "-c",
                "import time; print(time.monotonic_ns())",
            ]
        )
        after = time.monotonic_ns()
        value = int(raw) if raw and raw.strip().isdigit() else None
        self.clock_sync = {
            "host_before_ns": before,
            "host_after_ns": after,
            "container_ns": value,
            "common_origin_verified": value is not None and before <= value <= after,
            "attempts": self.clock_attempts,
        }

    def run(self):
        try:
            self._run()
        except Exception:
            # Thread bootstrap/open/flush errors never print arbitrary traces.
            self.errors += 1

    def _run(self):
        with (OUT / "host.jsonl").open("x", buffering=1) as output:
            while not self.stop.is_set() and self.samples < 200:
                start = time.monotonic_ns()
                try:
                    observed, known = containers()
                    db = database(known["db"]) if "db" in known else None
                    self.probe_clock(observed, known)
                    host = host_metrics()
                    end = time.monotonic_ns()
                    row = {
                        "mono_start_ns": start,
                        "mono_end_ns": end,
                        "host": host,
                        "containers": observed,
                        "postgres": db,
                    }
                    line = json.dumps(row, allow_nan=False, sort_keys=True)
                    if len(line) > 65536:
                        self.errors += 1
                        break
                    output.write(line + "\n")
                except Exception:
                    self.errors += 1
                self.samples += 1
                self.elapsed_ns += time.monotonic_ns() - start
                self.stop.wait(max(0, 5 - (time.monotonic_ns() - start) / 1e9))


def compose(*args):
    return [
        "docker",
        "compose",
        "-p",
        PROJECT,
        "-f",
        str(SOURCE / "compose.yaml"),
        "-f",
        str(OVERRIDE),
        "--env-file",
        str(ENV),
        "--profile",
        "test",
        *args,
    ]


def stage(summary, name, args, seconds=180):
    started = time.monotonic_ns()
    result = subprocess.run(
        ["timeout", "-k", "10s", str(seconds) + "s", *args],
        cwd=SOURCE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    summary["stages"].append(
        {
            "stage": name,
            "exit_code": result.returncode,
            "elapsed_seconds": round((time.monotonic_ns() - started) / 1e9, 6),
        }
    )
    print(json.dumps({"acceptance": False, **summary["stages"][-1]}), flush=True)
    if result.returncode:
        raise RuntimeError("stage_failed")


def window_events(events, boundary):
    return [
        event
        for event in events
        if type(event.get("mono_ns")) is int and 0 <= event["mono_ns"] <= boundary
    ]


def main():
    summary = {
        "acceptance": False,
        "source_sha": SHA,
        "source_tree": TREE,
        "stages": [],
        "backend": None,
        "cleanup_complete": False,
        "source_unchanged": False,
    }
    owned = False
    sampler = None
    OUT.mkdir(parents=True, exist_ok=False)
    OUT.chmod(0o777)
    PRIVATE.mkdir(mode=0o700, parents=True, exist_ok=False)
    try:
        assert re.fullmatch(r"fitlink-c04-task07-topology-[0-9]+-[0-9]+", PROJECT)
        assert capture(["git", "-C", str(SOURCE), "rev-parse", "HEAD"]).strip() == SHA
        assert (
            capture(["git", "-C", str(SOURCE), "rev-parse", "HEAD^{tree}"]).strip()
            == TREE
        )
        assert capture(["git", "-C", str(SOURCE), "diff", "HEAD", "--"]) == ""
        summary["source_clean_before"] = True
        for kind in ["ps", "network", "volume"]:
            command = (
                ["docker", kind, "-aq"]
                if kind == "ps"
                else ["docker", kind, "ls", "-q"]
            )
            assert (
                capture(
                    [
                        *command,
                        "--filter",
                        "label=com.docker.compose.project=" + PROJECT,
                    ]
                )
                == ""
            )
        for volume in [
            "db-data",
            "redis-data",
            "minio-data",
            "beat-data",
            "scanner-signatures",
        ]:
            assert (
                capture(
                    [
                        "docker",
                        "volume",
                        "ls",
                        "-q",
                        "--filter",
                        "name=^" + PROJECT + "_" + volume + "$",
                    ]
                )
                == ""
            )
        assert not ENV.exists()
        (PRIVATE / "ownership.lock").write_text(SHA)
        owned = True
        OVERRIDE.write_text(
            'services:\n  worker:\n    command: ["uv", "run", "--frozen", "celery", "--quiet", "-A", "config.celery:app", "worker", "--loglevel=WARNING", "--concurrency=1", "--hostname=foundation@%h", "-I", "docker.c03_asset_restart_probe"]\n'
        )
        stage(summary, "generate_env", ["python", "docker/generate_env.py", str(ENV)])
        stage(
            summary,
            "immutable_c03",
            ["python", "docker/c04_baseline.py", ".runtime/c03"],
        )
        stage(
            summary,
            "immutable_c02",
            ["python", "docker/c03_baseline.py", ".runtime/c02"],
        )
        stage(
            summary,
            "immutable_c01",
            ["python", "docker/c02_baseline.py", ".runtime/c01"],
        )
        stage(summary, "config", compose("config", "--quiet"))
        stage(
            summary,
            "build",
            compose(
                "build",
                "web",
                "worker",
                "beat",
                "checks",
                "browser",
                "minio",
                "minio-init",
                "scanner",
                "scanner-signatures",
            ),
            900,
        )
        stage(
            summary,
            "services",
            compose("up", "-d", "--wait", "db", "redis", "minio", "scanner"),
            900,
        )
        stage(summary, "minio", compose("run", "--rm", "minio-init"), 900)
        for label, command in [
            ("migrate", ["python", "manage.py", "migrate", "--noinput"]),
            (
                "independent_clean",
                ["python", "docker/c03_upgrade_probe.py", "clean", "unused"],
            ),
            ("noop", ["python", "manage.py", "migrate", "--noinput"]),
            (
                "drift",
                ["python", "manage.py", "makemigrations", "--check", "--dry-run"],
            ),
        ]:
            stage(
                summary,
                label,
                compose(
                    "run",
                    "--rm",
                    "--no-deps",
                    "checks",
                    "uv",
                    "run",
                    "--frozen",
                    *command,
                ),
            )
        stage(
            summary,
            "runtime",
            compose("up", "-d", "--wait", "web", "worker", "beat"),
            900,
        )
        stage(
            summary,
            "scanner",
            compose(
                "exec",
                "-T",
                "scanner",
                "clamdscan",
                "--config-file=/etc/clamav/clamd.c03.conf",
                "--ping=1",
            ),
        )
        stage(
            summary,
            "isolated_exact_baseline",
            compose(
                "run",
                "--rm",
                "--no-deps",
                "checks",
                "uv",
                "run",
                "--frozen",
                "pytest",
                "tests/unit/c03/test_exact_baseline.py",
                "-q",
                "--strict-markers",
            ),
        )
        # Existing C03 observer remains opt-in exactly as in c03-final. Its raw
        # journal (which may contain stack frames) is never uploaded here.
        (SOURCE / ".runtime/c03-foundation-evidence").mkdir(mode=0o777, exist_ok=True)
        (SOURCE / ".runtime/c03-foundation-evidence").chmod(0o777)
        os.environ["C03_FOUNDATION_TRIAGE"] = "1"
        sampler = Sampler()
        sampler.thread.start()
        started = time.monotonic_ns()
        child_cpu = resource.getrusage(resource.RUSAGE_CHILDREN)
        result = subprocess.run(
            [
                "timeout",
                "-k",
                "10s",
                "900s",
                *compose(
                    "run",
                    "--rm",
                    "--no-deps",
                    "--name",
                    PROJECT + "-checks",
                    "-e",
                    "PYTEST_PLUGINS=c04_topology_plugin",
                    "-e",
                    "PYTHONPATH=/telemetry",
                    "-v",
                    str(ROOT / "docker/c04_topology_plugin.py")
                    + ":/telemetry/c04_topology_plugin.py:ro",
                    "-v",
                    str(OUT) + ":/evidence",
                    "checks",
                    "uv",
                    "run",
                    "--frozen",
                    "pytest",
                    "tests/unit",
                    "tests/integration",
                    "-q",
                    "--strict-markers",
                    "--tb=no",
                    "--show-capture=no",
                ),
            ],
            cwd=SOURCE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        ended = time.monotonic_ns()
        after_cpu = resource.getrusage(resource.RUSAGE_CHILDREN)
        summary["backend"] = {
            "exit_code": result.returncode,
            "mono_start_ns": started,
            "mono_end_ns": ended,
            "deadline_ns": started + 900_000_000_000,
            "window_end_ns": min(ended, started + 900_000_000_000),
            "elapsed_seconds": round((ended - started) / 1e9, 6),
            "host_child_cpu_seconds": after_cpu.ru_utime
            + after_cpu.ru_stime
            - child_cpu.ru_utime
            - child_cpu.ru_stime,
        }
    except Exception:
        summary["diagnostic_error"] = "bounded_stage_or_observer_failure"
    finally:
        if sampler:
            sampler.stop.set()
        # Immediately stop only the acquired project's checks on timeout.
        if (
            owned
            and summary["backend"]
            and summary["backend"]["exit_code"] in {124, 137}
        ):
            name = PROJECT + "-checks"
            label = capture(
                [
                    "docker",
                    "inspect",
                    "--format",
                    '{{index .Config.Labels "com.docker.compose.project"}}',
                    name,
                ]
            )
            if label is not None and label.strip() == PROJECT:
                subprocess.run(
                    ["timeout", "-k", "5s", "30s", "docker", "rm", "-f", name],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
        if owned:
            cleanup = subprocess.run(
                [
                    "timeout",
                    "-k",
                    "10s",
                    "120s",
                    *compose("down", "--volumes", "--remove-orphans"),
                ],
                cwd=SOURCE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            remaining = [
                capture(
                    [
                        "docker",
                        kind,
                        "ls",
                        "-aq" if kind == "container" else "-q",
                        "--filter",
                        "label=com.docker.compose.project=" + PROJECT,
                    ]
                )
                for kind in ["container", "network", "volume"]
            ]
            summary["cleanup_complete"] = cleanup.returncode == 0 and remaining == [
                "",
                "",
                "",
            ]
            if summary["cleanup_complete"]:
                ENV.unlink(missing_ok=True)
                (PRIVATE / "ownership.lock").unlink(missing_ok=True)
        if sampler:
            sampler.thread.join(timeout=20)
            summary["sampler"] = {
                "samples": sampler.samples,
                "sample_wall_ns": sampler.elapsed_ns,
                "host_process_cpu_ns": time.process_time_ns() - sampler.cpu_start,
                "errors": sampler.errors,
                "clock_sync": sampler.clock_sync,
                "interval_seconds": 5,
                "sampling_can_miss_short_waits": True,
                "thread_stopped": not sampler.thread.is_alive(),
            }
        summary["source_unchanged"] = (
            capture(["git", "-C", str(SOURCE), "diff", "HEAD", "--"]) == ""
            and capture(["git", "-C", str(SOURCE), "rev-parse", "HEAD"]) == SHA + "\n"
            and capture(["git", "-C", str(SOURCE), "rev-parse", "HEAD^{tree}"])
            == TREE + "\n"
        )
        # On timeout sessionfinish may not run; phase rows remain flushed.
        events = []
        if (OUT / "pytest.jsonl").exists():
            data = (OUT / "pytest.jsonl").read_bytes()
            if len(data) <= 16 * 1024 * 1024:
                for line in data.splitlines():
                    try:
                        events.append(json.loads(line))
                    except ValueError:
                        summary["partial_last_record"] = True
        boundary = (summary["backend"] or {}).get("window_end_ns", 0)
        summary["post_window_records"] = sum(
            e.get("mono_ns", boundary + 1) > boundary for e in events
        )
        events = window_events(events, boundary)
        summary["terminal"] = {
            "session_finish": next(
                (x for x in reversed(events) if x.get("event") == "finish"), None
            ),
            "cases_started": sum(x.get("event") == "start" for x in events),
            "cases_completed": sum(
                x.get("event") == "phase" and x.get("phase") == "teardown"
                for x in events
            ),
            "call_outcomes": {
                k: sum(
                    x.get("event") == "phase"
                    and x.get("phase") == "call"
                    and x.get("outcome") == k
                    for x in events
                )
                for k in ["passed", "failed", "skipped", "other"]
            },
        }
        (OUT / "summary.json").write_text(
            json.dumps(summary, sort_keys=True, allow_nan=False) + "\n"
        )
        print(
            json.dumps(
                {
                    "acceptance": False,
                    "backend_exit": (summary["backend"] or {}).get("exit_code"),
                    "cleanup_complete": summary["cleanup_complete"],
                    "completed": summary["terminal"]["cases_completed"],
                }
            )
        )
    return (
        0
        if summary["backend"]
        and summary["cleanup_complete"]
        and summary["source_unchanged"]
        else 1
    )


def interrupted(signum, frame):
    raise RuntimeError("interrupted")


def emergency_cleanup():
    if not (PRIVATE / "ownership.lock").exists() or not ENV.exists():
        return 0
    if (PRIVATE / "ownership.lock").read_text() != SHA:
        return 1
    result = subprocess.run(
        [
            "timeout",
            "-k",
            "10s",
            "120s",
            *compose("down", "--volumes", "--remove-orphans"),
        ],
        cwd=SOURCE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(
        json.dumps({"acceptance": False, "emergency_cleanup_exit": result.returncode})
    )
    return result.returncode


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGINT, interrupted)
    try:
        result = emergency_cleanup() if sys.argv[1:] == ["--cleanup-only"] else main()
    except BaseException:
        print('{"acceptance":false,"diagnostic_error":"host_control_failure"}')
        result = 1
    raise SystemExit(result)
