"""Standalone worker failures expose finite source locations, never private text."""

import json

from docker import c04_media_probe


def test_projection_recovery_witness_requires_exact_fresh_successful_task(monkeypatch):
    from types import SimpleNamespace
    from uuid import uuid4

    witness = getattr(c04_media_probe, "projection_recovery_witness", None)
    assert callable(witness), "Missing unique post-restart projection task witness"

    class WitnessStore:
        def __init__(self):
            self.values = {}

        def exists(self, key):
            return key in self.values

        def set(self, key, value, *, ex):
            assert ex == 180
            self.values[key] = value

    store = WitnessStore()
    monkeypatch.setattr(c04_media_probe, "redis_client", lambda: store)
    identifier = str(uuid4())
    sender = SimpleNamespace(name="apps.marketplace.tasks.reconcile_publications")
    proof = "c04-projection-proof:" + identifier
    done = "c04-projection-done:" + identifier
    witness(
        sender=sender,
        task_id=identifier,
        retval={"processed": 1, "failures": 0},
        state="SUCCESS",
    )
    assert done not in store.values
    store.values[proof] = "1"
    witness(
        sender=sender,
        task_id=identifier,
        retval={"processed": 0, "failures": 1},
        state="SUCCESS",
    )
    assert done not in store.values
    witness(
        sender=SimpleNamespace(name="other.task"),
        task_id=identifier,
        retval={"processed": 1, "failures": 0},
        state="SUCCESS",
    )
    assert done not in store.values
    witness(
        sender=sender,
        task_id=str(uuid4()),
        retval={"processed": 1, "failures": 0},
        state="SUCCESS",
    )
    assert done not in store.values
    witness(
        sender=sender,
        task_id=identifier,
        retval={"processed": 1, "failures": 0},
        state="SUCCESS",
    )
    assert store.values[done] == "1"


def test_probe_failure_metadata_excludes_private_exception_and_phase():
    error = RuntimeError("PRIVATE-SOURCE-SESSION-AND-GPS-SENTINEL")
    value = c04_media_probe.failure_metadata(error, "PRIVATE-PHASE-SENTINEL")
    assert value["phase"] == "unknown"
    assert value["error_class"] == "RuntimeError"
    assert "PRIVATE" not in json.dumps(value)


def test_probe_failure_metadata_reports_bounded_source_frames_only():
    try:
        raise PermissionError("PRIVATE-OBJECT-PATH-SENTINEL")
    except PermissionError as error:
        value = c04_media_probe.failure_metadata(error, "worker-prepare")
    assert value.get("frames"), "Missing finite first-cause source frames"
    for frame in value["frames"]:
        assert set(frame) == {"file", "function", "line"}
        assert frame["file"].startswith(("apps/", "config/", "docker/", "tests/"))
        assert not frame["file"].startswith("/")
        assert type(frame["line"]) is int
    assert "PRIVATE" not in json.dumps(value)


def test_probe_failure_metadata_handles_relocated_compiled_source():
    from pathlib import Path

    relative = Path(__file__).resolve().relative_to(c04_media_probe.ROOT).as_posix()
    filename = "/different-host-checkout/" + relative
    namespace = {"__file__": __file__}
    try:
        exec(
            compile(
                'raise PermissionError("PRIVATE-COMPILED-SENTINEL")', filename, "exec"
            ),
            namespace,
        )
    except PermissionError as error:
        value = c04_media_probe.failure_metadata(error, "worker-prepare")
    assert any(
        frame["file"] == relative and frame["line"] == 1 for frame in value["frames"]
    ), "Missing relocated source frame"
    assert "different-host-checkout" not in json.dumps(value)
    assert "PRIVATE" not in json.dumps(value)


def test_probe_journal_is_private_before_serialization(tmp_path, monkeypatch):
    import os
    import stat

    path = tmp_path / "probe-private.json"
    monkeypatch.setattr(c04_media_probe, "STATE", path)
    original = json.dump

    def checked_dump(value, stream):
        assert stat.S_IMODE(os.fstat(stream.fileno()).st_mode) == 0o600
        return original(value, stream)

    monkeypatch.setattr(c04_media_probe.json, "dump", checked_dump)
    c04_media_probe.save({"copy_uuid": "synthetic-identifier"})
    assert json.loads(path.read_text()) == {"copy_uuid": "synthetic-identifier"}


def test_probe_journal_write_failure_preserves_previous_checkpoint(
    tmp_path, monkeypatch
):
    import pytest

    path = tmp_path / "probe-private.json"
    previous = '{"copy_uuid":"previous-synthetic-identifier"}'
    path.write_text(previous)
    path.chmod(0o600)
    monkeypatch.setattr(c04_media_probe, "STATE", path)

    def failed_dump(value, stream):
        raise RuntimeError("PRIVATE-JOURNAL-SENTINEL")

    monkeypatch.setattr(c04_media_probe.json, "dump", failed_dump)
    with pytest.raises(RuntimeError):
        c04_media_probe.save({"copy_uuid": "replacement-synthetic-identifier"})
    assert path.read_text() == previous


def test_probe_checkpoint_and_partial_writes_are_excluded_from_artifacts():
    from fnmatch import fnmatchcase

    import yaml

    workflow = yaml.safe_load(
        (c04_media_probe.ROOT / ".github/workflows/c04.yml").read_text()
    )
    uploads = [
        step["with"]["path"]
        for step in workflow["jobs"]["c04-public-media"]["steps"]
        if step.get("with", {}).get("name") == "c04-public-media-evidence"
    ]
    assert len(uploads) == 1
    for private in (
        c04_media_probe.STATE,
        c04_media_probe.STATE.with_name(".c04-private-" + "0" * 32 + ".tmp"),
    ):
        relative = private.relative_to(c04_media_probe.ROOT).as_posix()
        assert not any(
            fnmatchcase(relative, pattern)
            for pattern in uploads[0].splitlines()
            if pattern and not pattern.startswith("!")
        ), "Private checkpoint selected for artifact publication"
