"""Secret-free observations of C03 gate progress; no replacement service PASS."""

import json
import os
import re
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from uuid import uuid4

PROJECTS = {
    "fitlink-c03-private-storage",
    "fitlink-c02-immutable-c01",
    "fitlink-c02-exact-upgrade",
    "fitlink-foundation-verify",
}
PHASES = {"postgresql", "storage", "foundation"}
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
        elif re.fullmatch(
            r"tests/(?:unit|integration|e2e)(?:/[a-z0-9_]+)*(?:\.py)?", arg
        ):
            result.append(arg)
        elif re.fullmatch(
            r"docker/(?:verify_[a-z0-9_]+\.sh|c0[123]_[a-z0-9_]+\.py)", arg
        ):
            result.append(arg)
        elif re.fullmatch(r"(?:[0-9]+s|--?[A-Za-z-]+)", arg):
            result.append(arg)
        elif "sqlmigrate" in result and re.fullmatch(r"[0-9]{4}", arg):
            result.append(arg)
        else:
            result.append("<redacted>")
    return result


def process_rows(marker, proc=Path("/proc")):
    rows = []
    if not proc.is_dir():
        return None
    for path in proc.iterdir():
        if not path.name.isdecimal():
            continue
        try:
            if marker not in path.joinpath("environ").read_bytes().split(b"\0"):
                continue
            stat = path.joinpath("stat").read_text().rsplit(")", 1)[1].split()
            argv = (
                path.joinpath("cmdline")
                .read_bytes()
                .decode(errors="replace")
                .split("\0")
            )
            stdin = os.readlink(path / "fd/0")
            rows.append(
                {
                    "pid": int(path.name),
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
                    else "file",
                    "wait": path.joinpath("wchan").read_text().strip()[:40],
                }
            )
        except (OSError, IndexError, ValueError):
            continue
    return rows


def query(argv, seconds=2):
    """A bounded metadata command cannot hold a communicate() output pipe open."""
    with tempfile.TemporaryFile() as output:
        try:
            child = subprocess.Popen(
                argv,
                stdin=subprocess.DEVNULL,
                stdout=output,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        except OSError:
            return None
        try:
            child.wait(timeout=seconds)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGKILL)
            child.wait(timeout=1)
            return None
        if child.returncode:
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
    # Never inspect Config.Env, health output, commands, object keys or mounts.
    fmt = (
        '{"id":{{json .Id}},"status":{{json .State.Status}},'
        '"pid":{{.State.Pid}},"health":{{if .State.Health}}'
        '{{json .State.Health.Status}}{{else}}"none"{{end}},'
        '"project":{{json (index .Config.Labels "com.docker.compose.project")}},'
        '"service":{{json (index .Config.Labels "com.docker.compose.service")}},'
        '"image":{{json .Config.Image}}}'
    )
    value = query(["docker", "inspect", "--format", fmt, *ids[:16]])
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


def watch(phase, command):
    if phase not in PHASES or not command:
        raise ValueError("Invalid diagnostic boundary")
    marker = ("C03_DIAGNOSTIC_OWNER=" + uuid4().hex).encode()
    folder = Path(".runtime/c03-diagnostics")
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / (phase + "-" + uuid4().hex + ".jsonl")
    with path.open("x") as output:

        def emit(event, **values):
            data = {
                "phase": phase,
                "event": event,
                "elapsed_seconds": round(time.monotonic() - started, 1),
                **values,
            }
            line = json.dumps(data, sort_keys=True)
            output.write(line + "\n")
            output.flush()
            print("C03_DIAGNOSTIC " + line, flush=True)

        started = time.monotonic()
        child = subprocess.Popen(
            command,
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
        )
        while True:
            rows = containers()
            emit(
                "snapshot",
                processes=process_rows(marker),
                containers=rows,
                container_processes=container_processes(rows),
                services=services(rows),
                disk_available_bytes=os.statvfs(".").f_bavail
                * os.statvfs(".").f_frsize,
            )
            try:
                code = child.wait(timeout=20)
                break
            except subprocess.TimeoutExpired:
                continue
        emit(
            "command_exited", returncode=code, remaining_processes=process_rows(marker)
        )
        return code if code >= 0 else 128 - code


if __name__ == "__main__":
    sys.exit(watch(sys.argv[1], sys.argv[2:]))
