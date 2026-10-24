"""Focused development ONLY: real private MinIO, finite output, owned cleanup."""

import json
import os
import re
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

COUNTS = {"passed", "failed", "error", "skipped", "xfailed", "xpassed", "deselected"}
PROJECT = "fitlink-c04-task07-focused-storage"
SELECTION = (
    "tests/unit/c04",
    "tests/integration/c04/test_educational_posts.py",
    "tests/integration/c04/test_post_media.py",
    "tests/integration/c04/test_public_moderation.py",
    "tests/integration/c04/test_post_races.py",
    "tests/integration/c04/test_post_review_regressions.py",
    "tests/integration/c04/test_public_copies.py",
    "tests/integration/c04/test_public_copy_races.py",
    "tests/integration/c03/test_upload_lifecycle.py",
    "tests/integration/c03/test_private_assets.py",
)


def sanitized_results(text):
    output = []
    for line in text.splitlines():
        prefix, _, encoded = line.partition(" ")
        if prefix not in {"C04_REQUIRED_COUNTS", "C04_FAILURE"} or len(encoded) > 65536:
            continue
        try:
            value = json.loads(encoded)
            if not isinstance(value, dict):
                continue
            if prefix == "C04_REQUIRED_COUNTS":
                counts = value.get("counts")
                if (
                    not isinstance(counts, dict)
                    or set(counts) != COUNTS
                    or any(
                        type(v) is not int or not 0 <= v <= 100000
                        for v in counts.values()
                    )
                    or type(value.get("exit_code")) is not int
                    or not 0 <= value["exit_code"] <= 255
                ):
                    continue
                safe = {"counts": counts, "exit_code": value["exit_code"]}
            else:
                node = value.get("node")
                exception = value.get("exception")
                if (
                    not isinstance(node, str)
                    or len(node) > 1024
                    or not re.fullmatch(
                        r"tests/(?:unit|integration)/[A-Za-z0-9_./]+\.py::[A-Za-z0-9_:]+",
                        node,
                    )
                    or not isinstance(exception, str)
                    or not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]{0,63}", exception)
                    or value.get("phase") not in {"setup", "call", "teardown"}
                ):
                    continue
                safe = {"node": node, "exception": exception, "phase": value["phase"]}
                frames = []
                for item in value.get("traceback", [])[:64]:
                    if not isinstance(item, dict):
                        continue
                    file = item.get("file", "")
                    function = item.get("function", "")
                    number = item.get("line")
                    if not isinstance(file, str) or not re.fullmatch(
                        r"(?:apps|config|tests|docker)/[A-Za-z0-9_./]+\.py", file
                    ):
                        continue
                    if (
                        not isinstance(function, str)
                        or not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]{0,63}", function)
                        or type(number) is not int
                        or not 1 <= number <= 1000000
                    ):
                        continue
                    frames.append({"file": file, "function": function, "line": number})
                safe["traceback"] = frames[-12:]
            output.append(prefix + " " + json.dumps(safe, sort_keys=True))
        except (ValueError, TypeError, KeyError):
            continue
    return "\n".join(output) + ("\n" if output else "")


def run_private(args, timeout, *, env=None):
    begin = time.monotonic()
    with tempfile.TemporaryFile() as raw:
        child = subprocess.Popen(
            args, stdout=raw, stderr=subprocess.STDOUT, env=env, start_new_session=True
        )
        bound = False
        while child.poll() is None:
            if (
                time.monotonic() - begin > timeout
                or os.fstat(raw.fileno()).st_size > 32 * 1024 * 1024
            ):
                bound = True
                os.killpg(child.pid, signal.SIGTERM)
                try:
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
                break
            time.sleep(0.2)
        code = child.wait(timeout=10)
        raw.seek(0)
        data = raw.read(32 * 1024 * 1024 + 1)
    return (
        code,
        data,
        {
            "exit_code": code,
            "seconds": round(time.monotonic() - begin, 6),
            "bound": bound,
        },
    )


def main():
    from dotenv import dotenv_values

    output = Path(".runtime/task07-focused")
    output.mkdir(parents=True, exist_ok=True)
    journal = []
    owns = False
    cleanup = None
    code = 1

    def stage(name, args, timeout, env=None):
        result, data, event = run_private(args, timeout, env=env)
        journal.append({"stage": name, **event})
        if result or event["bound"]:
            raise RuntimeError("bounded_stage_failed")
        return data

    def dc(*args):
        return [
            "docker",
            "compose",
            "-p",
            PROJECT,
            "--env-file",
            ".env.task07-focused",
            "--profile",
            "test",
            *args,
        ]

    try:
        for kind, args in [
            (
                "container_inventory",
                [
                    "docker",
                    "ps",
                    "-aq",
                    "--filter",
                    "label=com.docker.compose.project=" + PROJECT,
                ],
            ),
            (
                "volume_inventory",
                [
                    "docker",
                    "volume",
                    "ls",
                    "-q",
                    "--filter",
                    "label=com.docker.compose.project=" + PROJECT,
                ],
            ),
        ]:
            if stage(kind, args, 10).strip():
                raise RuntimeError("ownership_conflict")
        owns = True
        stage(
            "private_environment",
            [sys.executable, "docker/generate_env.py", ".env.task07-focused"],
            15,
        )
        stage("minio_build", dc("build", "minio", "minio-init"), 300)
        stage("minio_readiness", dc("up", "-d", "--wait", "minio"), 120)
        stage("minio_security_initialization", dc("run", "--rm", "minio-init"), 120)
        values = dotenv_values(".env.task07-focused")
        env = dict(os.environ)
        env.pop("GITHUB_TOKEN", None)
        env.update(
            {
                "S3_ENDPOINT_URL": "http://127.0.0.1:9000",
                "S3_BUCKET_NAME": "fitlink-private",
                "S3_REGION": "us-east-1",
                "S3_ACCESS_KEY_ID": values["MINIO_APP_ACCESS_KEY"],
                "S3_SECRET_ACCESS_KEY": values["MINIO_APP_SECRET_KEY"],
            }
        )
        code, raw, event = run_private(
            [
                sys.executable,
                "docker/c04_gate.py",
                *SELECTION,
                "-q",
                "--strict-markers",
                "--tb=no",
                "--show-capture=no",
            ],
            600,
            env=env,
        )
        journal.append({"stage": "focused_tests", **event})
        safe = sanitized_results(raw.decode(errors="replace"))
        if (
            len(safe) > 4 * 1024 * 1024
            or "C04_REQUIRED_COUNTS " not in safe
            or event["bound"]
        ):
            safe = (
                "C04_FOCUSED_OUTCOME "
                + json.dumps({"counts_available": False, "exit_code": code})
                + "\n"
            )
            code = 1
        (output / "results.txt").write_text(safe)
    except Exception:
        code = 1
    finally:
        if owns:
            status, _, cleanup = run_private(dc("down", "--remove-orphans"), 45)
            journal.append({"stage": "owned_cleanup", **cleanup})
            if status or cleanup["bound"]:
                code = 1
        result = {
            "diagnostic_only": True,
            "acceptance": False,
            "exit_code": code,
            "owned_cleanup": cleanup,
            "stages": journal,
        }
        (output / "infrastructure.json").write_text(
            json.dumps(result, sort_keys=True) + "\n"
        )
        print(
            "C04_FOCUSED_INFRASTRUCTURE " + json.dumps(result, sort_keys=True),
            flush=True,
        )
    return code if code >= 0 else 128 - code


if __name__ == "__main__":
    raise SystemExit(main())
