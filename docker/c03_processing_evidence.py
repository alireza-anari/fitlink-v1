"""Same verified process ownership/window, additional isolated Task 5 project."""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    os.chdir(ROOT)
    from docker.c03_gate_diagnostics import watch

    result = watch(
        "storage", ["sh", "docker/verify_c03_processing.sh"], acceptance=True
    )
    config_result = ROOT / ".runtime/c03-compose-check.json"
    if config_result.is_file():
        print("C03_COMPOSE_CHECK " + config_result.read_text(), flush=True)
    for path in (ROOT / ".runtime/c03-diagnostics").glob("storage-*.jsonl"):
        for line in path.read_text().splitlines():
            print(
                "C03_PROCESSING_EVIDENCE "
                + json.dumps(json.loads(line), sort_keys=True),
                flush=True,
            )
    return result


if __name__ == "__main__":
    raise SystemExit(main())
