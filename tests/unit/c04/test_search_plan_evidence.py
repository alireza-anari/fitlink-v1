"""Only numeric actual-plan metadata from the specific passing probe may emit."""

from types import SimpleNamespace

import pytest

pytestmark = pytest.mark.unit


def test_plan_evidence_rejects_unknown_private_and_nonfinite_fields():
    from docker.c04_gate import RequiredEvidence

    assert hasattr(RequiredEvidence, "pytest_runtest_logreport"), (
        "Missing finite real-plan evidence"
    )
    metrics = dict(
        rows=30000,
        returned=10,
        index_nodes=2,
        planning_ms=1.0,
        execution_ms=2.0,
        buffer_blocks=100,
    )
    for change in (
        {"query": "PRIVATE-QUERY"},
        {"execution_ms": float("nan")},
        {"rows": True},
    ):
        plugin = RequiredEvidence()
        plugin.pytest_runtest_logreport(
            SimpleNamespace(
                nodeid="tests/integration/c04/test_search_query_plans.py::test_real_bounded_fts_trigram_query_plan",
                when="call",
                outcome="passed",
                user_properties=[("c04_query_plan", {**metrics, **change})],
            )
        )
        assert plugin.invalid_plan and not plugin.query_plans
