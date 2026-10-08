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
                return (
                    1 if not started or record["container_alive_after_timeout"] else 0
                )
            finally:
                if child.poll() is None:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait(timeout=2)
                # This new stateless fixture alone is owned; no volumes or user data.
                query(["docker", "rm", "-f", name], seconds=3)
                query(["docker", "network", "rm", name + "_default"], seconds=3)


if __name__ == "__main__":
    sys.exit(main())
