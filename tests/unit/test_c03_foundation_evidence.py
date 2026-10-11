"""Opt-in Foundation diagnostics preserve the original commands and privacy."""

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit
ROOT = Path(__file__).resolve().parents[2]

# Pinned from authoritative Task 12 HEAD, before any Task 13 script extension.
INHERITED_FOUNDATION_LENGTH = 2793
INHERITED_FOUNDATION_BLOB = "344898c20c0d5ede46fe7d5e653df378c267d9b7"
TASK13_SUFFIX = b"""# C03 TASK 13 APPENDED CONSOLIDATION -- inherited prefix ends above.
if [ -d tests/integration/c03 ]; then
  sh docker/verify_c03_incremental.sh --task13-foundation
fi
"""


def foundation_extension_valid(body):
    prefix = body[:INHERITED_FOUNDATION_LENGTH]
    digest = hashlib.sha1(b"blob " + str(len(prefix)).encode() + b"\0" + prefix)
    return digest.hexdigest() == INHERITED_FOUNDATION_BLOB and body[
        INHERITED_FOUNDATION_LENGTH:
    ] in (b"", TASK13_SUFFIX)


def test_foundation_reporter_loads_after_console_bootstrap(tmp_path):
    env = dict(os.environ)
    env.pop("PYTEST_PLUGINS", None)
    env.pop("C03_TRIAGE_EVIDENCE_FILE", None)
    env["C03_FOUNDATION_TRIAGE"] = "1"
    env["C03_FOUNDATION_EVIDENCE_DIRECTORY"] = str(tmp_path)
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/unit/test_storage.py",
            "--collect-only",
            "-q",
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0
    files = list(tmp_path.glob("foundation-*.jsonl"))
    assert len(files) == 1, "Foundation case evidence absent"
    events = [json.loads(line) for line in files[0].read_text().splitlines()]
    assert any(e.get("event") == "pytest_exit" and e["exitstatus"] == 0 for e in events)
    assert not any(e.get("event") == "diagnostic_cutoff" for e in events)


def test_inherited_rehearsal_commands_remain_unmodified():
    # Reviewed Git blob IDs work with GitHub's depth-one checkout, too.
    expected = {
        "docker/verify_c02.sh": "bebab2374dd3daf2d234cf5c0a94300ce3796b8a",
    }
    for path, blob in expected.items():
        body = (ROOT / path).read_bytes()
        assert (
            hashlib.sha1(b"blob " + str(len(body)).encode() + b"\0" + body).hexdigest()
            == blob
        )
    assert foundation_extension_valid(
        (ROOT / "docker/verify_foundation.sh").read_bytes()
    )


def test_exact_appended_extension_preserves_complete_inherited_blob():
    prefix = (ROOT / "docker/verify_foundation.sh").read_bytes()[
        :INHERITED_FOUNDATION_LENGTH
    ]
    assert foundation_extension_valid(prefix)
    assert foundation_extension_valid(prefix + TASK13_SUFFIX)
    for suffix in (b"exit 0\n", TASK13_SUFFIX + b"true\n", TASK13_SUFFIX * 2):
        assert not foundation_extension_valid(prefix + suffix)
    assert not foundation_extension_valid(TASK13_SUFFIX)


@pytest.mark.parametrize("mutation", ["byte", "remove", "reorder", "shorten", "insert"])
def test_inherited_prefix_mutations_are_rejected(mutation):
    prefix = (ROOT / "docker/verify_foundation.sh").read_bytes()[
        :INHERITED_FOUNDATION_LENGTH
    ]
    command = (
        b"dc run --rm browser uv run --frozen pytest tests/e2e/c02 "
        b"-q -m e2e --strict-markers\n"
    )
    assert command in prefix
    candidates = {
        "byte": b"!" + prefix[1:],
        "remove": prefix.replace(command, b"", 1),
        "reorder": command + prefix.replace(command, b"", 1),
        "shorten": prefix[:-1],
        "insert": prefix[:100] + TASK13_SUFFIX + prefix[100:],
    }
    assert not foundation_extension_valid(candidates[mutation] + TASK13_SUFFIX)


def test_observational_reporter_continues_after_session_snapshot(tmp_path, monkeypatch):
    import importlib.util
    import threading

    spec = importlib.util.spec_from_file_location(
        "foundation_reporter", ROOT / "docker/c03_pytest_triage.py"
    )
    reporter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reporter)
    path = tmp_path / "observation.jsonl"
    observed = {name: threading.Event() for name in ("session_snapshot", "case_cutoff")}
    original_emit = reporter.Journal.emit

    def emit(self, event, **values):
        original_emit(self, event, **values)
        if event in observed:
            observed[event].set()

    monkeypatch.setattr(reporter.Journal, "emit", emit)
    journal = reporter.Journal(path, cutoff=0.05, session_cutoff=0.05, terminate=False)
    assert observed["session_snapshot"].wait(5)
    journal.begin(
        "tests/unit/test_c03_foundation_evidence.py::test_observational_reporter_continues_after_session_snapshot"
    )
    assert observed["case_cutoff"].wait(5)
    journal.finish()
    events = [json.loads(line) for line in path.read_text().splitlines()]
    assert any(e["event"] == "session_snapshot" for e in events)
    assert any(e["event"] == "case_cutoff" for e in events)
    assert not any(e["event"] == "diagnostic_cutoff" for e in events)


def test_wrapper_emits_internal_error_and_preserves_nonzero(
    tmp_path, monkeypatch, capsys
):
    import importlib.util

    import docker.c03_gate_diagnostics as diagnostics

    spec = importlib.util.spec_from_file_location(
        "foundation_wrapper", ROOT / "docker/c03_foundation_evidence.py"
    )
    wrapper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(wrapper)
    folder = tmp_path / "evidence"
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("C03_FOUNDATION_TRIAGE", "0")
    monkeypatch.setattr(wrapper, "ROOT", tmp_path)
    monkeypatch.setattr(wrapper, "FOLDER", folder)

    def observe(phase, command, *, acceptance):
        assert phase == "foundation" and command == ["sh", "docker/verify_c02.sh"]
        assert acceptance is True
        (folder / "test.jsonl").write_text(
            json.dumps({"event": "pytest_internalerror", "exception": "ValueError"})
            + "\n"
        )
        return 3

    monkeypatch.setattr(diagnostics, "watch", observe)
    assert wrapper.main() == 3
    assert '"event": "pytest_internalerror"' in capsys.readouterr().out
