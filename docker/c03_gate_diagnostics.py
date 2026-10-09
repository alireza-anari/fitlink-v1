"""Secret-free observations of C03 gate progress; no replacement service PASS."""

import ast
import ctypes
import json
import math
import os
import re
import signal
import subprocess
import sys
import tempfile
import threading
import time
from collections import deque
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from docker.c03_storage_errors import ERROR_TYPES, error_category

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_FILES = {
    str(path.relative_to(ROOT))
    for path in (ROOT / "docker").iterdir()
    if path.suffix in {".py", ".sh"}
} | {"/probe.py"}
TEST_FILES = {
    str(path.relative_to(ROOT)): {
        node.name
        for node in ast.walk(ast.parse(path.read_text()))
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    for path in (ROOT / "tests").rglob("test_*.py")
}
TEST_PATHS = set(TEST_FILES)
for test_file in TEST_FILES:
    TEST_PATHS.update(
        str(parent) for parent in Path(test_file).parents if str(parent) != "."
    )

PROJECTS = {
    "fitlink-c03-private-storage",
    "fitlink-c02-immutable-c01",
    "fitlink-c02-exact-upgrade",
    "fitlink-foundation-verify",
}
PHASES = {"postgresql", "storage", "foundation"}
QUERY_FAILURES = deque(maxlen=8)
WINDOWS = {"postgresql": 240, "storage": 600, "foundation": 900}
OWNED_PROJECTS = {
    "postgresql": set(),
    "storage": {"fitlink-c03-private-storage"},
    "foundation": PROJECTS - {"fitlink-c03-private-storage"},
}
WORDS = {
    "uv",
    "run",
    "python",
    "python3",
    "python3.13",
    "sh",
    "bash",
    "docker",
    "compose",
    "docker-compose",
    "inspect",
    "top",
    "ps",
    "stop",
    "rm",
    "build",
    "up",
    "down",
    "exec",
    "checks",
    "browser",
    "web",
    "worker",
    "beat",
    "db",
    "redis",
    "minio",
    "minio-init",
    "pytest",
    "timeout",
    "mypy",
    "ruff",
    "npm",
    "go",
    "manage.py",
    "sqlmigrate",
    "migrate",
    "makemigrations",
    "assets",
    "athletes",
    "professionals",
    "governance",
    "accounts",
    "prepare",
    "verify",
    "psql",
    "redis-cli",
    "sleep",
    "pip",
}


def safe_command(argv):
    result = []
    for arg in argv[:24]:
        base = arg.rsplit("/", 1)[-1]
        if arg in WORDS or (not result and base in WORDS):
            result.append(base)
        elif arg in TEST_PATHS:
            result.append(arg)
        elif arg in SCRIPT_FILES:
            result.append(arg)
        elif re.fullmatch(r"(?:[0-9]+s|--?[A-Za-z-]+)", arg):
            result.append(arg)
        elif "sqlmigrate" in result and re.fullmatch(r"[0-9]{4}", arg):
            result.append(arg)
        else:
            result.append("<redacted>")
    return result


def process_rows(marker, proc=Path("/proc"), owner_pid=None):
    rows = []
    if not proc.is_dir():
        return None
    candidates = {}
    owned = set()
    for index, path in enumerate(proc.iterdir()):
        if index >= 4096:
            return None
        if not path.name.isdecimal():
            continue
        try:
            stat = path.joinpath("stat").read_text().rsplit(")", 1)[1].split()
            pid = int(path.name)
            candidates[pid] = (path, stat)
            with path.joinpath("environ").open("rb") as environment:
                if marker in environment.read(65536).split(b"\0"):
                    owned.add(pid)
        except (OSError, IndexError, ValueError):
            continue
    # Subreaper ancestry owns detached/adopted children even if they drop env.
    if owner_pid is not None:
        parents = {owner_pid}
        for _ in range(64):
            descendants = {
                pid for pid, (_, stat) in candidates.items() if int(stat[1]) in parents
            }
            if descendants <= parents:
                break
            parents |= descendants
        owned |= parents - {owner_pid}
    for pid in sorted(owned):
        path, stat = candidates[pid]
        try:
            argv = (
                path.joinpath("cmdline")
                .read_bytes()
                .decode(errors="replace")
                .split("\0")
            )
            try:
                stdin = os.readlink(path / "fd/0")
            except OSError:
                stdin = "unavailable"
            rows.append(
                {
                    "pid": pid,
                    "ppid": int(stat[1]),
                    "pgid": int(stat[2]),
                    "sid": int(stat[3]),
                    "state": stat[0],
                    "start_ticks": int(stat[19]),
                    "command": safe_command([a for a in argv if a]),
                    "stdin": "pipe"
                    if stdin.startswith("pipe:")
                    else "socket"
                    if stdin.startswith("socket:")
                    else "null"
                    if stdin == "/dev/null"
                    else "tty"
                    if stdin.startswith("/dev/pts/")
                    else "unavailable"
                    if stdin == "unavailable"
                    else "file",
                    "wait": path.joinpath("wchan").read_text().strip()[:40],
                }
            )
        except (OSError, IndexError, ValueError):
            continue
    return rows


def query(argv, seconds=2):
    """A bounded metadata command cannot hold a communicate() output pipe open."""
    with tempfile.TemporaryFile() as output, tempfile.TemporaryFile() as errors:
        try:
            child = subprocess.Popen(
                argv,
                stdin=subprocess.DEVNULL,
                stdout=output,
                stderr=errors,
                start_new_session=True,
            )
        except OSError:
            return None
        try:
            child.wait(timeout=seconds)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait(timeout=1)
            except (OSError, subprocess.TimeoutExpired):
                pass
            return None
        if child.returncode:
            errors.seek(0)
            error_text = errors.read(8192).decode(errors="replace")
            category = "metadata_command_failure"
            if argv[:2] == ["docker", "inspect"] and (
                'map has no entry for key "Health"' in error_text
                or "map has no entry for key Health" in error_text
            ):
                category = "inspect_missing_health_field"
            QUERY_FAILURES.append(
                {
                    "command": safe_command(argv),
                    "returncode": child.returncode,
                    "category": category,
                }
            )
            return None
        output.seek(0)
        data = output.read(65537)
        return data.decode(errors="replace") if len(data) <= 65536 else None


def containers():
    value = query(["docker", "ps", "-aq"])
    if value is None:
        return None
    ids = [s for s in value.splitlines() if re.fullmatch("[0-9a-f]{12,64}", s)]
    if not ids:
        return []
    if len(ids) > 64:
        return None
    # Never inspect Config.Env, health output, commands, object keys or mounts.
    fmt = (
        '{{$health := index .State "Health"}}'
        '{"id":{{json .Id}},"status":{{json .State.Status}},'
        '"pid":{{.State.Pid}},"health":{{if $health}}'
        '{{json (index $health "Status")}}{{else}}"none"{{end}},'
        '"project":{{json (index .Config.Labels "com.docker.compose.project")}},'
        '"service":{{json (index .Config.Labels "com.docker.compose.service")}},'
        '"image":{{json .Config.Image}}}'
    )
    value = query(["docker", "inspect", "--format", fmt, *ids])
    if value is None:
        return None
    rows = []
    for line in value.splitlines():
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if row["project"] not in PROJECTS:
            row["project"] = "<other>"
        if row["service"] not in WORDS:
            row["service"] = "<other>"
        image = row.pop("image")
        row["kind"] = "postgres" if "postgres@sha256:" in image else row["service"]
        rows.append(row)
    return rows


def services(rows):
    observations = []
    deadline = time.monotonic() + 10
    for row in (rows or [])[:8]:
        if time.monotonic() > deadline:
            break
        if row["status"] != "running":
            continue
        if row["kind"] == "postgres" or row["service"] == "db":
            sql = (
                "SELECT pid,state,wait_event_type,wait_event,"
                "EXTRACT(EPOCH FROM clock_timestamp()-query_start)::bigint,"
                "pg_blocking_pids(pid) FROM pg_stat_activity "
                "WHERE datname IN ('fitlink','test_fitlink') "
                "AND pid<>pg_backend_pid() ORDER BY pid LIMIT 32"
            )
            value = query(
                [
                    "docker",
                    "exec",
                    row["id"],
                    "psql",
                    "-U",
                    "fitlink",
                    "-d",
                    "fitlink",
                    "-At",
                    "-c",
                    sql,
                ]
            )
            observations.append(
                {
                    "kind": "postgres_activity",
                    "rows": value.splitlines() if value is not None else None,
                }
            )
        elif row["service"] == "minio":
            code = (
                "import urllib.request; "
                "r=urllib.request.urlopen('http://127.0.0.1:9000/minio/health/ready',"
                "timeout=1); print(r.status)"
            )
            value = query(["docker", "exec", row["id"], "python", "-c", code])
            observations.append(
                {
                    "kind": "minio_readiness",
                    "status": 200 if value and value.strip() == "200" else None,
                }
            )
    return observations


def container_processes(rows):
    """Expose the actual container child without its environment/private args."""
    observations = []
    deadline = time.monotonic() + 10
    for row in (rows or [])[:8]:
        if time.monotonic() > deadline:
            break
        if row["status"] != "running" or row["project"] not in PROJECTS:
            continue
        value = query(
            ["docker", "top", row["id"], "-eo", "pid,ppid,pgid,sid,stat,args"]
        )
        processes = None
        if value is not None:
            processes = []
            for line in value.splitlines()[1:65]:
                parts = line.split(None, 5)
                if len(parts) != 6 or not all(p.isdecimal() for p in parts[:4]):
                    continue
                processes.append(
                    {
                        "pid": int(parts[0]),
                        "ppid": int(parts[1]),
                        "pgid": int(parts[2]),
                        "sid": int(parts[3]),
                        "state": parts[4][:5],
                        "command": safe_command(parts[5].split()),
                    }
                )
        observations.append({"container": row["id"], "processes": processes})
    return observations


def stop_owned_containers(phase, baseline):
    """Fresh-runner, exact-label cleanup; never remove volumes or other projects."""
    projects = OWNED_PROJECTS[phase]
    if not projects:
        return {"owned_ids": [], "complete": True}
    rows = containers()
    if rows is None or baseline is None:
        return {"owned_ids": [], "complete": False}
    ids = [
        r["id"] for r in rows if r["project"] in projects and r["id"] not in baseline
    ]
    if ids:
        query(["docker", "stop", "--time", "1", *ids], seconds=5)
        query(["docker", "rm", "-f", *ids], seconds=5)
    remaining = containers()
    return {
        "owned_ids": ids,
        "complete": remaining is not None
        and not any(
            r["project"] in projects and r["id"] not in baseline for r in remaining
        ),
    }


def terminate_owned(child, marker):
    def send(sig):
        rows = process_rows(marker, owner_pid=os.getpid()) or []
        if child.poll() is None or any(
            r["pgid"] == child.pid and r["sid"] == child.pid for r in rows
        ):
            try:
                os.killpg(child.pid, sig)
            except ProcessLookupError:
                pass
        for row in rows:
            try:
                # Do not signal a recycled PID.
                stat = (
                    Path(f"/proc/{row['pid']}/stat")
                    .read_text()
                    .rsplit(")", 1)[1]
                    .split()
                )
                if int(stat[19]) == row["start_ticks"]:
                    os.kill(row["pid"], sig)
            except (OSError, IndexError, ValueError):
                continue

    send(signal.SIGTERM)
    try:
        child.wait(timeout=1)
    except subprocess.TimeoutExpired:
        pass
    send(signal.SIGKILL)
    try:
        child.wait(timeout=2)
    except subprocess.TimeoutExpired:
        return False
    # Repeat for children adopted during termination; bounded, no blocking reap.
    for _ in range(3):
        send(signal.SIGKILL)
        for _ in range(64):
            try:
                if os.waitpid(-1, os.WNOHANG)[0] == 0:
                    break
            except ChildProcessError:
                break
        if process_rows(marker, owner_pid=os.getpid()) == []:
            break
        time.sleep(0.05)
    remaining = process_rows(marker, owner_pid=os.getpid())
    return remaining == [] if remaining is not None else None


def progress_lines(text):
    """Only finite code/progress names; never relay raw child stdout/stderr."""
    for match in re.finditer(
        r"(?m)^C03_STORAGE_PHASE (migrate|probe|pytest) "
        r"(?:(start|success)|(failure) ([0-9]{1,3}))$",
        text,
    ):
        progress = {
            "kind": "storage_phase",
            "name": match[1],
            "state": match[2] or match[3],
        }
        if match[3]:
            code = int(match[4])
            if not 1 <= code <= 255:
                continue
            progress["returncode"] = code
        yield progress
    categories = "|".join(sorted(ERROR_TYPES))
    for match in re.finditer(
        rf"(?m)^(?:C03_STORAGE_ERROR ({categories})$|"
        r"(?:E\s+)?(?:(?:django\.db\.utils|psycopg(?:\.errors)?|"
        r"botocore\.exceptions|redis\.exceptions)\.)?"
        rf"({categories}):[^\n]*$)",
        text,
    ):
        yield {"kind": "storage_error", "error_type": match[1] or match[2]}
    for match in re.finditer(
        r"(?m)^(tests/(?:unit|integration|e2e)(?:/[a-z0-9_]+)*\.py)::"
        r"((?:Test[A-Za-z0-9_]+::)?test_[a-zA-Z0-9_]+)",
        text,
    ):
        if match[2].rsplit("::", 1)[-1] in TEST_FILES.get(match[1], set()):
            yield {"kind": "pytest_case", "file": match[1], "case": match[2]}
    for match in re.finditer(
        r'File "[^"\n]*(tests/(?:unit|integration|e2e)(?:/[a-z0-9_]+)*\.py)", '
        r"line ([0-9]+) in ([A-Za-z0-9_]+)",
        text,
    ):
        if match[3] in TEST_FILES.get(match[1], set()):
            yield {
                "kind": "test_stack_frame",
                "file": match[1],
                "line": int(match[2]),
                "function": match[3],
            }
    for match in re.finditer(r"Applying ([a-z_]+\.[0-9]{4}_[a-z0-9_]+)", text):
        yield {"kind": "migration", "name": match[1]}
    for name in (
        "readiness",
        "additive SQL and migration drift",
        "installed schema contracts",
    ):
        if "C03 cumulative gate: " + name in text:
            yield {"kind": "cumulative_phase", "name": name}


def acceptance_status(code, reason, host_complete, containers_complete):
    if (
        type(code) is int
        and code == 0
        and reason == "command_exited"
        and host_complete is True
        and containers_complete is True
    ):
        return 0
    return code if type(code) is int and code > 0 else 1


def enable_subreaper():
    try:
        return ctypes.CDLL(None).prctl(36, 1, 0, 0, 0) == 0
    except (AttributeError, OSError):
        return False


def watch(phase, command, *, acceptance=False):
    if phase not in PHASES or not command:
        raise ValueError("Invalid diagnostic boundary")
    marker = ("C03_DIAGNOSTIC_OWNER=" + uuid4().hex).encode()
    try:
        seconds = float(os.environ.get("C03_DIAGNOSTIC_SECONDS", WINDOWS[phase]))
    except ValueError:
        raise ValueError("Invalid bounded diagnostic observation window") from None
    if not math.isfinite(seconds) or not 0.1 <= seconds <= WINDOWS[phase]:
        raise ValueError("Invalid bounded diagnostic observation window")
    folder = Path(".runtime/c03-diagnostics")
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / (phase + "-" + uuid4().hex + ".jsonl")
    with path.open("x") as output:
        emission_lock = threading.Lock()

        def emit(event, **values):
            data = {
                "phase": phase,
                "event": event,
                "elapsed_seconds": round(time.monotonic() - started, 1),
                **values,
            }
            line = json.dumps(data, sort_keys=True)
            with emission_lock:
                output.write(line + "\n")
                output.flush()
                print("C03_DIAGNOSTIC " + line, flush=True)

        started = time.monotonic()
        baseline_rows = containers()
        baseline = (
            {r["id"] for r in baseline_rows} if baseline_rows is not None else None
        )
        if OWNED_PROJECTS[phase] and (
            baseline_rows is None
            or any(r["project"] in OWNED_PROJECTS[phase] for r in baseline_rows)
        ):
            emit(
                "diagnostic_finished",
                reason="fresh_runner_ownership_unavailable",
                expected_diagnostic_failure=not acceptance,
            )
            return 1
        subreaper = enable_subreaper()
        if not subreaper:
            emit(
                "diagnostic_finished",
                reason="host_process_ownership_unavailable",
                expected_diagnostic_failure=not acceptance,
            )
            return 1
        child = subprocess.Popen(
            command,
            start_new_session=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=0,
            env={
                **os.environ,
                "C03_DIAGNOSTIC_OWNER": marker.decode().split("=", 1)[1],
            },
        )
        emit(
            "started",
            root_pid=child.pid,
            command=safe_command(command),
            stdin_tty=sys.stdin.isatty(),
            observation_seconds=seconds,
            expected_diagnostic_failure=not acceptance,
            subreaper=subreaper,
        )

        progress_state = {"last": None}

        def read_progress():
            tail = ""

            def record(text):
                for progress in progress_lines(text):
                    progress_state["last"] = progress
                    if progress["kind"] in {"storage_phase", "storage_error"}:
                        emit(progress["kind"], progress=progress)

            while True:
                try:
                    chunk = os.read(child.stdout.fileno(), 4096)
                except (OSError, ValueError):
                    break
                if not chunk:
                    record(tail)
                    break
                tail += chunk.decode(errors="replace")
                while "\n" in tail:
                    line, tail = tail.split("\n", 1)
                    record(line)
                tail = tail[-8192:]

        reader = threading.Thread(target=read_progress, daemon=True)
        reader.start()

        def snapshot(event):
            rows = containers()
            emit(
                event,
                processes=process_rows(marker, owner_pid=os.getpid()),
                containers=rows,
                container_processes=container_processes(rows),
                services=services(rows),
                last_safe_progress=progress_state["last"],
                metadata_failures=list(QUERY_FAILURES),
                disk_available_bytes=os.statvfs(".").f_bavail
                * os.statvfs(".").f_frsize,
            )

        # These windows leave >60s for bounded final snapshot/cleanup/artifact
        # even in the shortest (15 minute) hosted job after its inherited setup.
        final_at = started + seconds
        next_snapshot = started
        last_progress = None
        reason = "observation_deadline"
        code = None

        def cancelled(signum, frame):
            raise InterruptedError

        previous = {
            sig: signal.signal(sig, cancelled)
            for sig in (signal.SIGTERM, signal.SIGINT)
        }
        try:
            while time.monotonic() < final_at:
                progress = progress_state["last"]
                if progress is not None and progress != last_progress:
                    emit("safe_progress", progress=progress)
                    last_progress = progress
                code = child.poll()
                if code is not None:
                    reason = "command_exited"
                    reader.join(timeout=1)
                    emit("command_exited", returncode=code)
                    break
                if time.monotonic() >= next_snapshot:
                    snapshot("snapshot")
                    next_snapshot = time.monotonic() + 20
                time.sleep(0.05)
            snapshot("final_snapshot")
        except InterruptedError:
            reason = "diagnostic_cancelled"
        except Exception as error:
            # Type only: exception text may contain private command arguments.
            reason = "diagnostic_error"
            emit("diagnostic_error", error_type=error_category(error))
        finally:
            for sig in previous:
                signal.signal(sig, signal.SIG_IGN)
            host_complete = terminate_owned(child, marker)
            cleanup = stop_owned_containers(phase, baseline)
            child.stdout.close()
            reader.join(timeout=1)
            emit(
                "diagnostic_finished",
                reason=reason,
                observed_returncode=code,
                host_cleanup_complete=host_complete,
                container_cleanup=cleanup,
                expected_diagnostic_failure=not acceptance,
                last_safe_progress=progress_state["last"],
            )
            for sig, handler in previous.items():
                signal.signal(sig, handler)
        if acceptance:
            return acceptance_status(code, reason, host_complete, cleanup["complete"])
        # Even command success is only an observation, never diagnostic PASS.
        return code if code is not None and code > 0 else 1


if __name__ == "__main__":
    acceptance = sys.argv[1] == "--acceptance"
    args = sys.argv[2:] if acceptance else sys.argv[1:]
    sys.exit(watch(args[0], args[1:], acceptance=acceptance))
