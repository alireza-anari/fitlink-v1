"""Run original C03 unchanged; emit only bounded, finite outer diagnostics."""

import errno
import json
import os
import re
import stat
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


MINIO_LOG_LIMIT = 65536


def _minio_record(
    state, classification="unknown_or_insufficient_evidence", evidence=()
):
    return {
        "acceptance": False,
        "log_state": state,
        "classification": classification,
        "evidence": sorted(evidence),
    }


def classify_minio_private_log(data):
    """Pinned mc error prefixes only. Silent alias/readiness failures stay unknown."""
    if len(data) > MINIO_LOG_LIMIT:
        return _minio_record("oversized")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return _minio_record("malformed")
    text = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", text)
    if any(ord(c) < 32 and c not in "\t\n\r" for c in text):
        return _minio_record("malformed")
    lines = text.splitlines()
    if len(lines) > 4096 or any(len(line) > 8192 for line in lines):
        return _minio_record("malformed")
    if not text.strip():
        return _minio_record("empty")
    categories = set()
    evidence = set()
    messages = (
        (
            "Unable to initialize new alias from the provided credentials.",
            "readiness_or_alias_failure",
        ),
        ("Unable to make bucket", "bucket_configuration_failure"),
        ("Unable to set anonymous", "anonymous_access_policy_failure"),
        ("Unable to create new policy", "application_policy_creation_failure"),
        ("Unable to add new user", "application_user_creation_failure"),
        (
            "Unable to make user/group policy association",
            "application_policy_attachment_failure",
        ),
    )
    for line in lines:
        line = line.strip()
        if line.startswith("mc: <ERROR> "):
            message = line.removeprefix("mc: <ERROR> ")
            for prefix, category in messages:
                if message.startswith(prefix) and (
                    len(message) == len(prefix) or message[len(prefix)] in " .`:\t"
                ):
                    categories.add(category)
                    evidence.add(category)
            if message.startswith("Unable to initialize admin connection."):
                evidence.add("admin_connection_error_without_operation")
        if line.startswith("Error response from daemon:"):
            evidence.add("docker_daemon_error")
            if "failed to create task for container" in line:
                categories.add("container_startup_failure")
                evidence.add("container_task_creation_error")
            else:
                categories.add("docker_daemon_failure")
        if line.startswith("dependency failed to start:"):
            categories.add("container_startup_failure")
            evidence.add("container_dependency_start_error")
    classification = (
        next(iter(categories))
        if len(categories) == 1
        else "unknown_or_insufficient_evidence"
    )
    return _minio_record("read", classification, evidence)


def read_minio_private_log(path):
    """Read at most 64KiB, reject links/nonregular files and never return text."""
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except OSError as error:
        state = {errno.ENOENT: "missing", errno.ELOOP: "symlink"}.get(
            error.errno, "unreadable"
        )
        return _minio_record(state)
    result = _minio_record("unreadable")
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode):
            result = _minio_record("not_regular")
        elif info.st_size > MINIO_LOG_LIMIT:
            result = _minio_record("oversized")
        else:
            result = classify_minio_private_log(
                os.read(descriptor, MINIO_LOG_LIMIT + 1)
            )
    except OSError:
        result = _minio_record("unreadable")
    finally:
        try:
            os.close(descriptor)
        except OSError:
            result = _minio_record("unreadable")
    return result


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
    record["logs"]["clean_minio"] = read_minio_private_log(
        baseline / ".runtime/task14-private/clean_minio.log"
    )
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
