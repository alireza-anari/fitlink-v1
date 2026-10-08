"""One narrowly selected diagnostic execution; not an acceptance gate."""

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
EVIDENCE = ROOT / ".runtime/c03-triage"
NODES = {
    "postgresql": [
        "tests/integration/c03/test_upload_lifecycle.py::test_finalize_quarantines_not_ready"
    ],
}


def pytest_run(phase, attempt):
    import pytest

    os.environ["C03_TRIAGE_EVIDENCE_FILE"] = str(EVIDENCE / f"{phase}-{attempt}.jsonl")
    return int(
        pytest.main(
            [
                "-p",
                "docker.c03_pytest_triage",
                *NODES[phase],
                "-x",
                "-vv",
                "--tb=long",
                "--strict-markers",
                "-o",
                "faulthandler_timeout=30",
            ]
        )
    )


def boot(phase):
    # A clear failure needs no retry. Only this real-PostgreSQL node executes.
    return subprocess.run(
        [
            "uv",
            "run",
            "--frozen",
            "python",
            "docker/c03_triage_runner.py",
            "pytest",
            phase,
            "first",
        ],
        check=False,
    ).returncode


def main():
    action, phase = sys.argv[1:3]
    if phase not in NODES:
        return 1
    if action == "pytest":
        return pytest_run(phase, sys.argv[3])
    if action == "boot":
        return boot(phase)
    if action != "observe" or EVIDENCE.exists():
        return 1
    EVIDENCE.mkdir(parents=True)
    from docker.c03_gate_diagnostics import watch

    os.environ["C03_DIAGNOSTIC_SECONDS"] = "180"
    try:
        watch(phase, ["python", "docker/c03_triage_runner.py", "boot", phase])
    finally:
        for path in sorted(EVIDENCE.glob("*.jsonl")):
            for line in path.read_text().splitlines():
                data = json.loads(line)
                print("C03_TRIAGE " + json.dumps(data, sort_keys=True), flush=True)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
