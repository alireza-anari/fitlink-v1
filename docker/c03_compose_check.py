"""Retain finite Compose validation evidence without environment/config output."""

import json
import subprocess
import sys
from pathlib import Path


def category(text):
    if "network_mode" in text and "networks" in text:
        return "network_mode_conflict"
    if "unknown tag" in text or "!reset" in text:
        return "unsupported_reset_tag"
    if "undefined" in text:
        return "undefined_resource"
    return "other_config_error"


def main():
    result = subprocess.run(
        [
            "docker",
            "compose",
            "-p",
            sys.argv[1],
            "--env-file",
            sys.argv[2],
            "--profile",
            "test",
            "config",
            "--quiet",
        ],
        capture_output=True,
        text=True,
        timeout=20,
    )
    Path(".runtime").mkdir(exist_ok=True)
    Path(".runtime/c03-compose-check.json").write_text(
        json.dumps(
            {
                "returncode": result.returncode,
                "category": category(result.stderr) if result.returncode else "valid",
            }
        )
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
