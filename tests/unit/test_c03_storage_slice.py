"""Storage observation cannot report acceptance after partial/failed evidence."""

from copy import deepcopy

import pytest

from docker.c03_storage_slice import verdict

pytestmark = pytest.mark.unit


def evidence():
    names = [
        "tests/integration/c03/test_private_assets.py::" + name
        for name in (
            "test_real_minio_bounded_private_roundtrip_and_anonymous_denial",
            "test_real_minio_owned_quarantine_not_source_delivery",
            "test_real_minio_missing_and_oversized_objects_fail_closed",
            "test_real_minio_http_owned_private_source",
            "test_real_minio_http_rejects_changed_storage_facts",
        )
    ] + ["tests/integration/test_minio_storage.py::test_private_minio_signed_roundtrip"]
    cases = []
    for index in range(91):
        cases.extend(
            [
                {
                    "event": "test_report",
                    "phase": "call",
                    "outcome": "passed",
                    "node": names[index % len(names)],
                },
                {"event": "test_end"},
            ]
        )
    cases.append({"event": "pytest_exit", "exitstatus": 0})
    observations = [
        {
            "event": "diagnostic_finished",
            "reason": "command_exited",
            "observed_returncode": 0,
            "host_cleanup_complete": True,
            "container_cleanup": {"complete": True},
        }
    ]
    return cases, observations


def test_complete_real_test_and_cleanup_evidence_is_required():
    cases, observations = evidence()
    assert verdict(cases, observations)
    assert not verdict([], observations)
    assert not verdict(cases, [])


@pytest.mark.parametrize(
    "broken",
    [
        "case",
        "failed",
        "skipped",
        "exit",
        "cutoff",
        "host",
        "container",
        "deadline",
        "real",
    ],
)
def test_storage_checkpoint_fails_closed(broken):
    cases, observations = deepcopy(evidence())
    if broken == "case":
        cases.pop(0)
    elif broken in {"failed", "skipped"}:
        cases[0]["outcome"] = broken
    elif broken == "exit":
        cases[-1]["exitstatus"] = 1
    elif broken == "cutoff":
        cases.append({"event": "diagnostic_cutoff"})
    elif broken == "host":
        observations[0]["host_cleanup_complete"] = False
    elif broken == "container":
        observations[0]["container_cleanup"]["complete"] = False
    elif broken == "deadline":
        observations[0]["reason"] = "observation_deadline"
    else:
        for event in cases:
            if event.get("event") == "test_report":
                event["node"] = (
                    "tests/integration/c03/test_upload_lifecycle.py::test_finalize_quarantines_not_ready"
                )
    assert not verdict(cases, observations)
