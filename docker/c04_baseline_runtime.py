"""Run original C03 unchanged; emit only bounded, finite outer diagnostics."""

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from docker.c04_baseline import verify_baseline  # noqa: E402


def classify_private_log(text):
    allowed = {
        "E503",
        "E502",
        "E504",
        "E500",
        "E429",
        "E403",
        "E404",
        "ECONNRESET",
        "ETIMEDOUT",
        "EAI_AGAIN",
        "ECONNREFUSED",
        "ENOTFOUND",
        "EINTEGRITY",
        "EUSAGE",
        "ENOENT",
        "EACCES",
        "EPERM",
    }
    codes = {
        code
        for code in re.findall(r"npm (?:error|ERR!) code ([A-Z0-9_]+)", text)
        if code in allowed
    }
    categories = {
        name
        for name, pattern in (
            ("npm_failure", r"npm (?:error|ERR!)"),
            ("dependency_download", r"[Ff]ailed to (?:download|fetch)"),
            ("build_failure", r"failed to (?:build|solve)"),
            ("registry_rate_limit", r"(?:toomanyrequests|pull rate limit)"),
            ("connection_refused", r"[Cc]onnection refused"),
        )
        if re.search(pattern, text)
    }
    return {"npm_codes": sorted(codes), "categories": sorted(categories)}


def run(root):
    baseline = root / ".runtime/c03"
    tree = verify_baseline(baseline)
    result = subprocess.run(["sh", "docker/verify_c03.sh"], cwd=baseline)
    record = {"baseline_tree": tree, "exit_code": result.returncode, "logs": {}}
    # Read only known private stage logs, never upload them or reproduce text.
    for stage in ("exact_original_c02",):
        path = baseline / ".runtime/task14-private" / (stage + ".log")
        if path.is_file() and not path.is_symlink():
            with path.open("rb") as stream:
                stream.seek(max(0, path.stat().st_size - 4_000_000))
                text = stream.read(4_000_000).decode("utf-8", errors="replace")
            record["logs"][stage] = classify_private_log(text)
    folder = root / ".runtime/c04-baseline-evidence"
    folder.mkdir(mode=0o700, parents=True, exist_ok=True)
    path = folder / (uuid4().hex + ".json")
    with path.open("x") as stream:
        os.chmod(path, 0o600)
        json.dump(record, stream, sort_keys=True)
    print("C04_BASELINE_DIAGNOSTIC " + json.dumps(record, sort_keys=True), flush=True)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(run(Path(__file__).resolve().parents[1]))
