"""Bounded diagnostic prefix; never a replacement acceptance manifest."""

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def prefix(source):
    marker = (
        "# Deliberate C03 commands only after exact preservation and session checks."
    )
    if source.count(marker) != 1:
        raise ValueError("Unknown verifier boundary")
    before = source.split(marker)[0]
    command = "docker/c03_upgrade_probe.py verify /rehearsal/metadata.json"
    if before.count(command) != 1:
        raise ValueError("Unknown preservation command")
    # Same verifier, snapshot, database and assertions, inside one named test.
    return before.replace(
        command, "docker/c04_preservation_probe.py /rehearsal/metadata.json"
    )


def main():
    from docker.c03_gate_diagnostics import watch

    folder = Path(".runtime/task07-preservation")
    folder.mkdir(mode=0o700, exist_ok=False)
    source = Path("docker/verify_c03.sh").read_text()
    script = folder / "prefix.sh"
    script.write_text(prefix(source))
    code = watch("foundation", ["sh", str(script)], acceptance=True)
    rows = []
    evidence = Path(".runtime/c03-task14-evidence/upgrade.jsonl")
    if evidence.exists():
        for line in evidence.read_text().splitlines():
            value = json.loads(line)
            if (
                set(value) != {"stage", "exit_code"}
                or not re.fullmatch(r"[a-z0-9_]{1,100}", value["stage"])
                or type(value["exit_code"]) is not int
            ):
                raise ValueError("Invalid finite evidence")
            rows.append(value)
    log = Path(".runtime/task14-private/populated_preservation.log")
    predicate = "unavailable"
    if log.exists():
        with log.open("rb") as stream:
            stream.seek(0, 2)
            stream.seek(max(0, stream.tell() - 65536))
            text = stream.read(65536).decode(errors="replace")
        for label in ("exact_content_types", "verified", "unknown"):
            if "C03_TASK14 preservation_" + label in text.splitlines():
                predicate = label
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ValueError("Invalid source identity")
    result = {
        "diagnostic_only": True,
        "acceptance": False,
        "source_sha": sha,
        "verifier_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "exit_code": code,
        "predicate": predicate,
        "stages": rows,
        "equivalence_limit": (
            "Original prefix through preservation only; "
            "later backend/browser/fault gates not executed."
        ),
    }
    (folder / "outcome.json").write_text(json.dumps(result, sort_keys=True) + "\n")
    print("C04_PRESERVATION " + json.dumps(result, sort_keys=True), flush=True)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
