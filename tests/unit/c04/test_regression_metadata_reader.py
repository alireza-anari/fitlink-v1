"""Pinned diagnostic artifacts never authorize a task or expose private text."""

import io
import json
import zipfile

import pytest

from docker import c04_regression_metadata as reader

pytestmark = pytest.mark.unit
NODE = "tests/unit/test_storage.py::test_default_storage"
MEMBER = "c03-foundation-evidence/foundation-" + "a" * 32 + ".jsonl"


def archive(members):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as output:
        for name, value in members.items():
            output.writestr(name, value)
    return stream.getvalue()


def test_reader_reports_real_progress_and_failure_without_private_values():
    rows = [
        {"event": "test_start", "node": NODE + "[PRIVATE_TOKEN]"},
        {"event": "test_report", "phase": "call", "outcome": "passed"},
        {"event": "test_end", "node": NODE, "case_seconds": 12.5},
        {"event": "test_start", "node": NODE + "[PRIVATE_NAME]"},
        {
            "event": "test_report",
            "phase": "setup",
            "outcome": "passed",
            "private_value": "PRIVATE_PHONE",
        },
    ]
    data = archive(
        {
            MEMBER: "\n".join(json.dumps(row) for row in rows),
            "c03-task14-evidence/upgrade.jsonl": json.dumps(
                {"stage": "complete_backend", "exit_code": 124}
            ),
        }
    )
    result = reader.inspect_archive(
        data,
        {"tests/unit/test_storage.py": {"test_default_storage"}},
        {"complete_backend"},
    )
    assert result["acceptance"] is False
    assert result["failed_stages"] == [{"stage": "complete_backend", "exit_code": 124}]
    summary = result["journals"][0]
    assert summary["completed"] == 1
    assert summary["active_node"] == NODE
    assert summary["phase"] == "setup"
    assert summary["exit_code"] is None
    assert summary["call_counts"] == {"passed": 1, "failed": 0, "skipped": 0}
    assert "PRIVATE_" not in json.dumps(result)


def test_reader_denies_unexpected_archive_members():
    with pytest.raises(ValueError, match="Member denied"):
        reader.inspect_archive(
            archive({"private/customer.txt": "PRIVATE_VALUE"}), {}, set()
        )


def test_reader_bounds_uncompressed_members_before_parsing(monkeypatch):
    monkeypatch.setattr(reader, "MAX_MEMBER", 1)
    with pytest.raises(ValueError, match="Member denied"):
        reader.inspect_archive(archive({MEMBER: "{}"}), {}, set())
