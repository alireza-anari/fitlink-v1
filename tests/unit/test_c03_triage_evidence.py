"""Diagnostic evidence excludes values and captures the active Python call."""

import importlib.util
import json
import time
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit
ROOT = Path(__file__).resolve().parents[2]


def reporter():
    path = ROOT / "docker/c03_pytest_triage.py"
    assert path.is_file(), "Bounded pytest node/stack reporter absent"
    spec = importlib.util.spec_from_file_location("triage", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_node_parameters_and_foreign_paths_are_redacted():
    triage = reporter()
    node = (
        "tests/unit/test_healthcheck_entrypoint.py::"
        "test_direct_healthcheck_boots_project_with_redacted_db_failure"
    )
    assert triage.safe_node(node + "[synthetic-private-payload]") == node
    assert triage.safe_node("private/secret.py::test_private") == "<redacted>"


def test_stack_preserves_code_locations_without_local_values():
    triage = reporter()
    synthetic_private_payload = "synthetic-private-payload"
    frames = triage.stacks()
    encoded = json.dumps(frames)
    assert "test_stack_preserves_code_locations_without_local_values" in encoded
    assert synthetic_private_payload not in encoded


def test_fixed_cutoff_records_active_node_stack_and_returns(tmp_path):
    triage = reporter()
    path = tmp_path / "evidence.jsonl"
    journal = triage.Journal(path, cutoff=0.1)
    journal.begin(
        "tests/unit/test_c03_triage_evidence.py::test_fixed_cutoff_records_active_node_stack_and_returns"
    )
    time.sleep(0.2)
    journal.finish()
    events = [json.loads(line) for line in path.read_text().splitlines()]
    cutoff = next(e for e in events if e["event"] == "case_cutoff")
    assert cutoff["active_node"].endswith(
        "test_fixed_cutoff_records_active_node_stack_and_returns"
    )
    assert cutoff["stacks"] and cutoff["case_seconds"] >= 0.1
    assert events[-1]["event"] == "observer_finished"


def test_failure_preserves_http_assertion_and_trace_without_response_body():
    from django.http import HttpResponse

    triage = reporter()
    assert callable(getattr(triage, "failure_data", None)), (
        "Safe exception trace absent"
    )
    response = HttpResponse("synthetic-private-payload", status=404)
    try:
        assert response.status_code == 201, response.content
    except AssertionError:
        info = pytest.ExceptionInfo.from_current()
    data = triage.failure_data(info)
    assert data["exception"] == "AssertionError"
    assert data["expected_http_status"] == 201 and data["actual_http_status"] == 404
    assert data["traceback"][-1]["file"] == "tests/unit/test_c03_triage_evidence.py"
    assert "synthetic-private-payload" not in json.dumps(data)


def test_internal_pytest_error_records_only_class_and_code_locations(monkeypatch):
    triage = reporter()
    assert callable(getattr(triage, "pytest_internalerror", None)), (
        "Internal error evidence absent"
    )
    events = []

    class Journal:
        node = None
        last_node = (
            "tests/unit/test_c03_triage_evidence.py::"
            "test_internal_pytest_error_records_only_class_and_code_locations"
        )

        def emit(self, event, **data):
            events.append({"event": event, **data})

    monkeypatch.setattr(triage, "JOURNAL", Journal())
    try:
        raise ValueError("synthetic-private-payload")
    except ValueError:
        info = pytest.ExceptionInfo.from_current()
    triage.pytest_internalerror(None, info)
    event = events[0]
    assert event["exception"] == "ValueError"
    assert event["active_node"].endswith(
        "test_internal_pytest_error_records_only_class_and_code_locations"
    )
    assert event["traceback"][-1]["file"] == "tests/unit/test_c03_triage_evidence.py"
    assert "synthetic-private-payload" not in json.dumps(event)


def test_missing_source_preserves_original_exception_and_http_status():
    from django.http import HttpResponse

    triage = reporter()
    namespace = {"response": HttpResponse("synthetic-private-payload", status=404)}
    code = compile(
        "assert response.status_code == 201", "/source-unavailable.py", "exec"
    )
    try:
        exec(code, namespace)
    except AssertionError:
        info = pytest.ExceptionInfo.from_current()
    data = triage.failure_data(info)
    assert data["exception"] == "AssertionError"
    assert data["actual_http_status"] == 404
    assert data["traceback"][-1]["file"] == "<external>"
    assert "synthetic-private-payload" not in json.dumps(data)


def test_missing_pytest_source_uses_only_known_repository_assertion(monkeypatch):
    from _pytest._code import Code
    from django.http import HttpResponse

    triage = reporter()
    response = HttpResponse("synthetic-private-payload", status=404)
    try:
        assert response.status_code == 201, response.content
    except AssertionError:
        info = pytest.ExceptionInfo.from_current()
    with monkeypatch.context() as scoped:
        scoped.setattr(Code, "fullsource", property(lambda self: None))
        data = triage.failure_data(info)
    assert data["exception"] == "AssertionError"
    assert data["actual_http_status"] == 404
    assert data["expected_http_status"] == 201
    assert "synthetic-private-payload" not in json.dumps(data)
