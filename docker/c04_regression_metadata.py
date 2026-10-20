"""Read one pinned failed-run artifact; emit finite diagnostics, never acceptance."""

import ast
import hashlib
import io
import json
import math
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = "alireza-anari/fitlink-v1"
ARTIFACT = 12281581780
RUN = 39451304085
SHA = "48eb911a9cd499649b39c0b4bab73d9b4fe6cba8"
DIGEST = "b12ff7e5d3b6fb8a90477b5853b60b400acb759ce9ca8ea1b99846e6f258f597"
MAX_ARCHIVE = 16 * 1024 * 1024
MAX_MEMBER = 8 * 1024 * 1024
MAX_TOTAL = 32 * 1024 * 1024


def number(value):
    if type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 86400:
        return round(value, 3)
    return None


def safe_node(value, known):
    if not isinstance(value, str):
        return None
    parts = value.split("[", 1)[0].split("::")
    if len(parts) >= 2 and all(p in known.get(parts[0], set()) for p in parts[1:]):
        return "::".join(parts)
    return None


def inspect_archive(data, known, stages):
    if len(data) > MAX_ARCHIVE:
        raise ValueError("Archive bound")
    result = {"acceptance": False, "journals": [], "failed_stages": []}
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        files = archive.infolist()
        if len(files) > 16 or sum(f.file_size for f in files) > MAX_TOTAL:
            raise ValueError("Member bound")
        for entry in files:
            is_journal = re.fullmatch(
                r"c03-foundation-evidence/foundation-[0-9a-f]{32}\.jsonl",
                entry.filename,
            )
            is_stages = entry.filename == "c03-task14-evidence/upgrade.jsonl"
            if not (is_journal or is_stages) or entry.file_size > MAX_MEMBER:
                raise ValueError("Member denied")
            rows = archive.read(entry).decode("utf-8").splitlines()
            if len(rows) > 50000:
                raise ValueError("Event bound")
            summary = {
                "completed": 0,
                "last_node": None,
                "active_node": None,
                "phase": None,
                "elapsed_seconds": None,
                "exit_code": None,
                "call_counts": {"passed": 0, "failed": 0, "skipped": 0},
                "nonpassing_reports": 0,
                "slowest": [],
            }
            for line in rows:
                row = json.loads(line)
                if not isinstance(row, dict):
                    raise ValueError("Event denied")
                if is_stages:
                    stage, code = row.get("stage"), row.get("exit_code")
                    if stage in stages and type(code) is int and 0 < code < 256:
                        result["failed_stages"].append(
                            {"stage": stage, "exit_code": code}
                        )
                    continue
                event = row.get("event")
                node = safe_node(row.get("node"), known)
                elapsed = number(row.get("elapsed_seconds"))
                if elapsed is not None:
                    summary["elapsed_seconds"] = elapsed
                if event == "test_start":
                    summary["last_node"] = node
                    summary["active_node"] = node
                if event == "test_report":
                    phase, outcome = row.get("phase"), row.get("outcome")
                    if phase in ("setup", "call", "teardown"):
                        summary["phase"] = phase
                    if phase == "call" and outcome in summary["call_counts"]:
                        summary["call_counts"][outcome] += 1
                    if outcome in ("failed", "skipped"):
                        summary["nonpassing_reports"] += 1
                if event == "test_end":
                    summary["completed"] += 1
                    summary["active_node"] = None
                    seconds = number(row.get("case_seconds"))
                    if node is not None and seconds is not None:
                        summary["slowest"].append({"node": node, "seconds": seconds})
                        summary["slowest"].sort(
                            key=lambda item: item["seconds"], reverse=True
                        )
                        del summary["slowest"][8:]
                if event == "pytest_exit":
                    code = row.get("exitstatus")
                    if type(code) is int and 0 <= code < 256:
                        summary["exit_code"] = code
            if is_journal:
                result["journals"].append(summary)
    return result


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def hosted_archive():
    token = os.environ["GITHUB_TOKEN"]
    endpoint = f"https://api.github.com/repos/{REPO}/actions/artifacts/{ARTIFACT}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    opener = urllib.request.build_opener(NoRedirect)
    with opener.open(
        urllib.request.Request(endpoint, headers=headers), timeout=20
    ) as r:
        metadata = json.loads(r.read(65537))
    if (
        metadata.get("id") != ARTIFACT
        or metadata.get("digest") != "sha256:" + DIGEST
        or metadata.get("expired") is not False
        or metadata.get("workflow_run", {}).get("id") != RUN
        or metadata.get("workflow_run", {}).get("head_sha") != SHA
    ):
        raise ValueError("Artifact provenance")
    try:
        response = opener.open(
            urllib.request.Request(endpoint + "/zip", headers=headers), timeout=20
        )
    except urllib.error.HTTPError as error:
        if error.code != 302:
            raise
        target = error.headers["Location"]
        parsed = urllib.parse.urlsplit(target)
        host = parsed.hostname or ""
        if parsed.scheme != "https" or not host.endswith(
            (".blob.core.windows.net", ".githubusercontent.com", ".amazonaws.com")
        ):
            raise ValueError("Artifact redirect") from None
        # The GitHub token is never forwarded to a storage provider.
        response = urllib.request.urlopen(target, timeout=20)
    with response:
        data = response.read(MAX_ARCHIVE + 1)
    if len(data) > MAX_ARCHIVE or hashlib.sha256(data).hexdigest() != DIGEST:
        raise ValueError("Artifact digest")
    return data


def main():
    known = {}
    for path in (ROOT / "tests").rglob("test_*.py"):
        known[path.relative_to(ROOT).as_posix()] = {
            node.name
            for node in ast.walk(ast.parse(path.read_text()))
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        }
    source = (ROOT / "docker/verify_c03.sh").read_text()
    stages = set(
        re.findall(r"(?:run_step|original_c02_step)\s+([a-z][a-z0-9_]*)", source)
    )
    result = inspect_archive(hosted_archive(), known, stages)
    result.update(artifact_id=ARTIFACT, run_id=RUN, head_sha=SHA, digest_verified=True)
    print("C04_PREVIOUS_REGRESSION_DIAGNOSTIC " + json.dumps(result), flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        allowed = {
            "HTTPError",
            "URLError",
            "TimeoutError",
            "ValueError",
            "BadZipFile",
            "KeyError",
            "JSONDecodeError",
            "OSError",
        }
        name = type(error).__name__
        print(
            "C04_PREVIOUS_REGRESSION_DIAGNOSTIC "
            + json.dumps(
                {
                    "acceptance": False,
                    "error_class": name if name in allowed else "unknown",
                }
            ),
            flush=True,
        )
        sys.exit(1)
