#!/usr/local/bin/python
"""Delegate original mc exactly once. Never serialize argv, env or output."""

import json
import subprocess
import sys
import time
from pathlib import Path

REAL = "/usr/local/bin/mc"
LOG = Path("/observe/events/mc.jsonl")


def operation(args):
    for prefix, category in [
        (("alias", "set"), "alias"),
        (("ready",), "ready"),
        (("mb",), "bucket"),
        (("anonymous", "set"), "anonymous"),
        (("admin", "policy", "create"), "policy"),
        (("admin", "user", "add"), "user"),
        (("admin", "policy", "attach"), "attach"),
    ]:
        if tuple(args[: len(prefix)]) == prefix:
            return category
    return "unknown"


def emit(event, category, code=None):
    try:
        if LOG.exists() and LOG.stat().st_size >= 65536:
            return
        with LOG.open("a") as f:
            row = {
                "event": event,
                "operation": category,
                "mono_ns": time.monotonic_ns(),
            }
            if code is not None:
                row["exit_code"] = code
            f.write(json.dumps(row, separators=(",", ":")) + "\n")
    except OSError:
        pass


def run(args):
    category = operation(args)
    emit("start", category)
    try:
        code = subprocess.run([REAL, *args], check=False).returncode
    except OSError:
        code = 127
    emit("end", category, code)
    return code if code >= 0 else 128 - code


if __name__ == "__main__":
    raise SystemExit(run(sys.argv[1:]))
