"""Actual timeout/Compose ownership evidence in an isolated stateless fixture."""

import json
import os
import re
import signal
import subprocess
import sys
import tempfile
from pathlib import Path
from uuid import uuid4

from c03_gate_diagnostics import query


def main():
    name = "c03-timeout-probe-" + uuid4().hex[:12]
    root = Path(__file__).resolve().parents[1]
    image = re.search(
        r"FROM (library/python@sha256:[0-9a-f]{64})", (root / "Dockerfile").read_text()
    )[1]
    if query(["docker", "image", "inspect", "--format", "{{.Id}}", image]) is None:
        pull = subprocess.run(["docker", "pull", image], timeout=120)
        if pull.returncode:
            return 1
    with tempfile.TemporaryDirectory() as folder:
        compose = Path(folder) / "compose.yaml"
        code = (
            "import signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); "
            "print('probe_started',flush=True); time.sleep(30)"
        )
        compose.write_text(
            json.dumps(
                {
                    "services": {
                        "probe": {
                            "image": image,
                            "network_mode": "none",
                            "read_only": True,
                            "user": "1000:1000",
                            "command": ["python", "-u", "-c", code],
                        }
                    }
                }
            )
        )
        command = [
            "timeout",
            "-k",
            "0.2s",
            "2s",
            "docker",
            "compose",
            "-p",
            name,
            "-f",
            str(compose),
            "run",
            "--rm",
            "--no-deps",
            "--name",
            name,
            "probe",
        ]
        with tempfile.TemporaryFile() as output:
            child = subprocess.Popen(
                command,
                stdin=subprocess.DEVNULL,
                stdout=output,
                stderr=output,
                start_new_session=True,
            )
            try:
                child.wait(timeout=10)
                running = query(
                    ["docker", "inspect", "--format", "{{.State.Running}}", name]
                )
                output.seek(0)
                started = b"probe_started" in output.read(65536)
                record = {
                    "probe": "existing_gnu_timeout_compose_run",
                    "cli_returncode": child.returncode,
                    "container_started": started,
                    "container_alive_after_timeout": running is not None
                    and running.strip() == "true",
                }
                print("C03_TIMEOUT_PROBE " + json.dumps(record), flush=True)
            finally:
                if child.poll() is None:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait(timeout=2)
                # This new stateless fixture alone is owned; no volumes or user data.
                query(["docker", "rm", "-f", name], seconds=3)
                query(["docker", "network", "rm", name + "_default"], seconds=3)
        supervised_name = "c03-supervised-probe-" + uuid4().hex[:12]
        project = "fitlink-c03-private-storage"
        escaped_path = Path(folder) / "escaped.json"
        escaped_code = (
            "import json,os,signal,time;from pathlib import Path;"
            "signal.signal(signal.SIGTERM,signal.SIG_IGN);"
            f"Path({str(escaped_path)!r}).write_text(json.dumps({{"
            "'pid':os.getpid(),'ticks':Path('/proc/self/stat').read_text()"
            ".rsplit(')',1)[1].split()[19]}));time.sleep(30)"
        )
        compose_command = [
            "docker",
            "compose",
            "-p",
            project,
            "-f",
            str(compose),
            "run",
            "--rm",
            "--no-deps",
            "--name",
            supervised_name,
            "probe",
        ]
        launcher = (
            "import os,subprocess,sys;"
            f"subprocess.Popen([sys.executable,'-c',{escaped_code!r}],"
            "start_new_session=True,env={k:v for k,v in os.environ.items()"
            "if k!='C03_DIAGNOSTIC_OWNER'});"
            f"raise SystemExit(subprocess.call({compose_command!r}))"
        )

        def escaped_alive():
            if not escaped_path.exists():
                return None
            record = json.loads(escaped_path.read_text())
            try:
                stat = (
                    Path(f"/proc/{record['pid']}/stat")
                    .read_text()
                    .rsplit(")", 1)[1]
                    .split()
                )
                return stat[19] == record["ticks"]
            except FileNotFoundError:
                return False

        with tempfile.TemporaryFile() as output:
            child = subprocess.Popen(
                [
                    sys.executable,
                    str(root / "docker/c03_gate_diagnostics.py"),
                    "storage",
                    sys.executable,
                    "-c",
                    launcher,
                ],
                env={**os.environ, "C03_DIAGNOSTIC_SECONDS": "3"},
                stdin=subprocess.DEVNULL,
                stdout=output,
                stderr=output,
                start_new_session=True,
            )
            try:
                child.wait(timeout=60)
                removed = (
                    query(["docker", "inspect", "--format", "{{.Id}}", supervised_name])
                    is None
                )
                events = []
                for path in (root / ".runtime/c03-diagnostics").glob("storage-*.jsonl"):
                    events.extend(
                        json.loads(line) for line in path.read_text().splitlines()
                    )
                seen_running = any(
                    r["project"] == project and r["status"] == "running"
                    for e in events
                    for r in (e.get("containers") or [])
                )
                finished = [e for e in events if e["event"] == "diagnostic_finished"]
                verified = bool(
                    child.returncode != 0
                    and removed
                    and seen_running
                    and escaped_alive() is False
                    and finished
                    and finished[-1]["reason"] == "observation_deadline"
                    and finished[-1]["host_cleanup_complete"] is True
                    and finished[-1]["container_cleanup"]["complete"] is True
                )
                print(
                    "C03_TIMEOUT_PROBE "
                    + json.dumps(
                        {
                            "probe": "bounded_supervisor_compose_run",
                            "diagnostic_returncode": child.returncode,
                            "owned_container_started": seen_running,
                            "owned_container_removed": removed,
                            "detached_host_child_terminated": escaped_alive() is False,
                            "supervisor_contract_satisfied": verified,
                        }
                    ),
                    flush=True,
                )
            finally:
                if child.poll() is None:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait(timeout=2)
                query(["docker", "rm", "-f", supervised_name], seconds=3)
                if escaped_alive():
                    os.kill(json.loads(escaped_path.read_text())["pid"], signal.SIGKILL)
        # This owning RED job is intentionally never an application gate PASS.
        return 1


if __name__ == "__main__":
    sys.exit(main())
