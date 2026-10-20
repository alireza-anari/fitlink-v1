"""Standalone worker failures expose finite source locations, never private text."""

import json

from docker import c04_media_probe


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
