"""Standalone worker failures expose finite source locations, never private text."""

import json

from docker import c04_media_probe


def test_probe_failure_metadata_excludes_private_exception_and_phase():
    error = RuntimeError("PRIVATE-SOURCE-SESSION-AND-GPS-SENTINEL")
    value = c04_media_probe.failure_metadata(error, "PRIVATE-PHASE-SENTINEL")
    assert value["phase"] == "unknown"
    assert value["error_class"] == "RuntimeError"
    assert "PRIVATE" not in json.dumps(value)
