"""Observe the existing real-service gate; require actual test/cleanup success."""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def verdict(cases, observations):
    reports = [e for e in cases if e.get("event") == "test_report"]
    calls = [e for e in reports if e.get("phase") == "call"]
    names = {e.get("node") for e in calls if e.get("outcome") == "passed"}
    finished = [e for e in observations if e.get("event") == "diagnostic_finished"]
    required = {
        "tests/integration/c03/test_private_assets.py::"
        "test_real_minio_bounded_private_roundtrip_and_anonymous_denial",
        "tests/integration/c03/test_private_assets.py::"
        "test_real_minio_owned_quarantine_not_source_delivery",
        "tests/integration/c03/test_private_assets.py::"
        "test_real_minio_missing_and_oversized_objects_fail_closed",
        "tests/integration/c03/test_private_assets.py::"
        "test_real_minio_http_owned_private_source",
        "tests/integration/c03/test_private_assets.py::"
        "test_real_minio_http_rejects_changed_storage_facts",
        "tests/integration/test_minio_storage.py::test_private_minio_signed_roundtrip",
    }
    return (
        len(calls) == 91
        and len([e for e in cases if e.get("event") == "test_end"]) == 91
        and required <= names
        and all(e.get("outcome") == "passed" for e in reports)
        and any(
            e.get("event") == "pytest_exit" and e.get("exitstatus") == 0 for e in cases
        )
        and not any(e.get("event") == "diagnostic_cutoff" for e in cases)
        and len(finished) == 1
        and finished[0].get("reason") == "command_exited"
        and finished[0].get("observed_returncode") == 0
        and finished[0].get("host_cleanup_complete") is True
        and finished[0].get("container_cleanup", {}).get("complete") is True
    )


def main():
    os.chdir(ROOT)
    folder = ROOT / ".runtime/c03-triage"
    if folder.exists():
        return 1
    folder.mkdir(parents=True)
    # Only redacted JSONL goes here; the non-root container must write this
    # fresh runner bind mount. Credentials stay in separate ignored env files.
    folder.chmod(0o777)
    os.environ["COMPOSE_FILE"] = "compose.yaml:docker/compose.c03-storage-evidence.yml"
    os.environ["C03_DIAGNOSTIC_SECONDS"] = "600"
    from docker.c03_gate_diagnostics import watch

    try:
        watch("storage", ["sh", "docker/verify_c03_storage.sh"])
    finally:
        cases = []
        for path in sorted(folder.glob("*.jsonl")):
            for line in path.read_text().splitlines():
                event = json.loads(line)
                cases.append(event)
                print("C03_TRIAGE " + json.dumps(event, sort_keys=True), flush=True)
    observations = [
        json.loads(line)
        for path in (ROOT / ".runtime/c03-diagnostics").glob("storage-*.jsonl")
        for line in path.read_text().splitlines()
    ]
    valid = verdict(cases, observations)
    counts = {
        outcome: sum(
            e.get("event") == "test_report"
            and e.get("phase") == "call"
            and e.get("outcome") == outcome
            for e in cases
        )
        for outcome in ("passed", "failed", "skipped")
    }
    print(
        "C03_SLICE_B "
        + json.dumps({**counts, "complete": valid, "task4_complete": False}),
        flush=True,
    )
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
