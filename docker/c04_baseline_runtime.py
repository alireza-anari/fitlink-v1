"""Run original C03 unchanged; emit only bounded, finite outer diagnostics."""

import json
import os
import re
import subprocess
import sys
from collections import deque
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


def classify_browser_private_log(text, known_files):
    """Only fixed enums and known repository source locations may leave the host."""
    error_classes = sorted(
        name
        for name in ("AssertionError", "Error", "TargetClosedError", "TimeoutError")
        if re.search(r"\b" + name + r"\b", text)
    )
    operations = sorted(
        name
        for name in (
            "Locator.click",
            "Locator.fill",
            "Locator.press",
            "Locator.wait_for",
            "Page.goto",
            "Page.reload",
            "Page.wait_for_load_state",
            "Page.wait_for_url",
            "expect(locator)",
        )
        if name in text
    )
    allowed_net_codes = {
        "ERR_ABORTED",
        "ERR_CONNECTION_REFUSED",
        "ERR_CONNECTION_RESET",
        "ERR_FAILED",
        "ERR_HTTP_RESPONSE_CODE_FAILURE",
        "ERR_INTERNET_DISCONNECTED",
        "ERR_NAME_NOT_RESOLVED",
        "ERR_NETWORK_CHANGED",
        "ERR_TIMED_OUT",
    }
    net_codes = sorted(
        set(re.findall(r"net::(ERR_[A-Z0-9_]+)", text)) & allowed_net_codes
    )
    locations = deque(maxlen=12)
    pattern = r"((?:apps|config|tests)/[A-Za-z0-9_./-]+\.py):([0-9]{1,6})\b"
    for match in re.finditer(pattern, text):
        filename, line = match.groups()
        if filename in known_files and 0 < int(line) <= 100000:
            locations.append({"file": filename, "line": int(line)})
    return {
        "error_classes": error_classes,
        "locations": list(locations),
        "net_codes": net_codes,
        "operations": operations,
    }


def classify_prerequisite_private_log(text, known_files):
    """Finite prerequisite stages/errors only; marker presence is not a verdict."""
    result = classify_private_log(text)
    categories = set(result["categories"])
    for marker, name in (
        ("dependency failed to start", "service_start_failed"),
        ("is unhealthy", "service_unhealthy"),
        ("Error response from daemon:", "docker_daemon_error"),
        ("Cannot connect to the Docker daemon", "docker_unavailable"),
        ("failed to resolve source metadata", "image_metadata_failed"),
        ("pull access denied", "image_access_denied"),
        ("429 Too Many Requests", "rate_limited"),
        ("TLS handshake timeout", "tls_timeout"),
        ("context deadline exceeded", "provider_deadline"),
        ("connection reset by peer", "connection_reset"),
        ("no space left on device", "disk_full"),
        ("Temporary failure in name resolution", "dns_failure"),
        ("port is already allocated", "port_collision"),
        ("Choose a new isolated verification project", "existing_project_retained"),
        ("Exact upgrade requires new isolated volumes", "existing_project_retained"),
    ):
        if marker in text:
            categories.add(name)
    phases = [
        (text.rfind(marker), name)
        for marker, name in (
            ("load metadata for ", "image_metadata"),
            ("transferring context:", "build_context"),
            ("RUN uv sync", "dependency_sync"),
            ("RUN npm ci", "dependency_npm"),
            ("exporting to image", "image_export"),
            ("Running migrations:", "migrations"),
            ("collected ", "test_collection"),
        )
        if marker in text
    ]
    failure = classify_browser_private_log(text, known_files)
    classes = set(failure["error_classes"])
    for name in (
        "OperationalError",
        "IntegrityError",
        "ConnectionError",
        "PermissionError",
        "FileNotFoundError",
        "ValueError",
        "RuntimeError",
        "HTTPError",
    ):
        if re.search(r"\b" + name + r"\b", text):
            classes.add(name)
    failure["error_classes"] = sorted(classes)
    return {
        "npm_codes": result["npm_codes"],
        "categories": sorted(categories),
        "last_phase": max(phases)[1] if phases else "unknown",
        "failure_metadata": failure,
    }


def run(root):
    baseline = root / ".runtime/c03"
    tree = verify_baseline(baseline)
    result = subprocess.run(["sh", "docker/verify_c03.sh"], cwd=baseline)
    record = {"baseline_tree": tree, "exit_code": result.returncode, "logs": {}}
    known_files = {
        path.relative_to(baseline).as_posix()
        for name in ("apps", "config", "tests")
        for path in (baseline / name).rglob("*.py")
        if path.is_file() and not path.is_symlink()
    }
    # Read only known private stage logs, never upload them or reproduce text.
    for stage in ("exact_original_c02",):
        path = baseline / ".runtime/task14-private" / (stage + ".log")
        if path.is_file() and not path.is_symlink():
            with path.open("rb") as stream:
                stream.seek(max(0, path.stat().st_size - 4_000_000))
                text = stream.read(4_000_000).decode("utf-8", errors="replace")
            record["logs"][stage] = classify_prerequisite_private_log(text, known_files)
    for stage in (
        "upgraded_c02_browser",
        "clean_owner_browser",
        "clean_staff_browser",
        "clean_c02_browser",
    ):
        path = baseline / ".runtime/task14-private" / (stage + ".log")
        if path.is_file() and not path.is_symlink():
            try:
                with path.open("rb") as stream:
                    stream.seek(max(0, path.stat().st_size - 4_000_000))
                    text = stream.read(4_000_000).decode("utf-8", errors="replace")
            except OSError:
                record["logs"][stage] = {"browser_metadata_unavailable": True}
            else:
                record["logs"][stage] = {
                    "browser": classify_browser_private_log(text, known_files)
                }
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
