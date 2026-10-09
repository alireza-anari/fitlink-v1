"""Observe the unchanged Foundation gate with opt-in redacted pytest reports."""

import importlib
import json
import os
import sys
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
FOLDER = ROOT / ".runtime/c03-foundation-evidence"


def configure(config):
    if os.environ.get("C03_FOUNDATION_TRIAGE") != "1":
        return
    if config.pluginmanager.hasplugin("docker.c03_pytest_triage"):
        return
    folder = Path(os.environ.get("C03_FOUNDATION_EVIDENCE_DIRECTORY", str(FOLDER)))
    folder.mkdir(parents=True, exist_ok=True)
    os.environ["C03_TRIAGE_EVIDENCE_FILE"] = str(
        folder / f"foundation-{uuid4().hex}.jsonl"
    )
    config.pluginmanager.register(
        importlib.import_module("docker.c03_pytest_triage"), "docker.c03_pytest_triage"
    )


def main():
    os.chdir(ROOT)
    if FOLDER.exists():
        return 1
    FOLDER.mkdir(parents=True)
    FOLDER.chmod(0o777)
    os.environ["C03_FOUNDATION_TRIAGE"] = "1"
    from docker.c03_gate_diagnostics import watch

    try:
        return watch("foundation", ["sh", "docker/verify_c02.sh"], acceptance=True)
    finally:
        counts = {"passed": 0, "failed": 0, "skipped": 0}
        for path in sorted(FOLDER.glob("*.jsonl")):
            for line in path.read_text().splitlines():
                event = json.loads(line)
                if event.get("event") == "test_report" and event.get("phase") == "call":
                    outcome = event.get("outcome")
                    if outcome in counts:
                        counts[outcome] += 1
                if event.get("event") in {
                    "pytest_exit",
                    "case_cutoff",
                    "session_snapshot",
                    "pytest_internalerror",
                } or (
                    event.get("event") == "test_report"
                    and event.get("outcome") != "passed"
                ):
                    print(
                        "C03_FOUNDATION " + json.dumps(event, sort_keys=True),
                        flush=True,
                    )
        print("C03_FOUNDATION_COUNTS " + json.dumps(counts, sort_keys=True), flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
