"""Private, bounded fixture-cost instrumentation for Task 7; no payload or SQL capture."""
from __future__ import annotations

import functools
import json
import os
import platform
import pytest
import threading
import time
from contextlib import ExitStack
from pathlib import Path
from typing import Any, Callable

TARGETS = (
    "tests/integration/c04/test_educational_posts.py::test_post_receipt_payload_and_expected_version_are_fenced",
    "tests/integration/c04/test_post_races.py::test_stale_post_edit_cannot_replace_current_revision",
    "tests/integration/c04/test_post_races.py::test_concurrent_same_version_post_edit_has_one_winner",
    "tests/integration/c04/test_educational_posts.py::test_confirmed_post_activates_only_complete_copies_and_edit_withdraws",
)
_ALLOWED_TARGETS = {"identity", "coach", "nutritionist"}
_ALLOWED_DECISIONS = {"approve", "reject"}
_ALLOWED_COMMANDS = {
    "prepare_verification",
    "submit_verification",
    "assign_verification",
    "start_verification_review",
    "decide_verification_target",
}
_OUTPUT = Path(os.environ.get("FITLINK_DIAG_OUTPUT", ".runtime/task07-fixture-cost/metrics.json"))
_EVENTS: list[dict[str, Any]] = []
_PHASES: list[dict[str, Any]] = []
_STATUSES: dict[str, str] = {}
_STACKS: dict[str, ExitStack] = {}
_LOCK = threading.Lock()
_SQL_LOCK = threading.Lock()
_SQL_COUNT = 0
_SQL_SECONDS = 0.0
_SQL_WRAPPER_ENABLED = False
_SQL_WRAPPER_ERRORS = 0
_INSTALLED = False
_SESSION_WALL = 0.0
_SESSION_PROCESS = 0.0
_SESSION_THREAD = 0.0
_COLLECTION: dict[str, Any] = {}
_RESOURCE: dict[str, Any] = {
    "samples": 0,
    "min_mem_available_mib": None,
    "max_load_per_cpu": None,
    "max_memory_psi_some_avg10": None,
    "sampler_thread_cpu_seconds": 0.0,
}
_STOP = threading.Event()
_SAMPLER: threading.Thread | None = None


def _sql_snapshot() -> tuple[int, float]:
    with _SQL_LOCK:
        return _SQL_COUNT, _SQL_SECONDS


def _execute_wrapper(execute, sql, params, many, context):
    global _SQL_COUNT, _SQL_SECONDS
    started = time.perf_counter()
    try:
        return execute(sql, params, many, context)
    finally:
        elapsed = time.perf_counter() - started
        with _SQL_LOCK:
            _SQL_COUNT += 1
            _SQL_SECONDS += elapsed


def _detail_safe(detail: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(detail, dict):
        return {}
    safe: dict[str, Any] = {}
    for key, value in detail.items():
        if key in {"target", "decision", "command", "category", "role"}:
            if isinstance(value, str) and len(value) <= 40:
                safe[key] = value
        elif key in {"target_count", "role_count", "field_count"}:
            if type(value) is int and 0 <= value <= 20:
                safe[key] = value
        elif key == "coach_only" and type(value) is bool:
            safe[key] = value
    return safe


def _record_timing(
    label: str,
    started_wall: float,
    started_process: float,
    started_thread: float,
    sql_before: tuple[int, float],
    detail: dict[str, Any] | None,
    raised: bool,
) -> None:
    sql_after = _sql_snapshot()
    event = {
        "label": label,
        "wall_seconds": round(max(0.0, time.perf_counter() - started_wall), 6),
        "process_cpu_seconds": round(max(0.0, time.process_time() - started_process), 6),
        "thread_cpu_seconds": round(max(0.0, time.thread_time() - started_thread), 6),
        "sql_count_primary_thread": max(0, sql_after[0] - sql_before[0]),
        "sql_execute_seconds_primary_thread": round(max(0.0, sql_after[1] - sql_before[1]), 6),
        "raised": raised,
        **_detail_safe(detail),
    }
    with _LOCK:
        if len(_EVENTS) < 2000:
            _EVENTS.append(event)


def _timed_wrapper(label: str, original: Callable, detail_fn=None):
    if getattr(original, "_fitlink_diag_wrapped", False):
        return original

    @functools.wraps(original)
    def wrapped(*args, **kwargs):
        started_wall = time.perf_counter()
        started_process = time.process_time()
        started_thread = time.thread_time()
        sql_before = _sql_snapshot()
        raised = False
        try:
            return original(*args, **kwargs)
        except BaseException:
            raised = True
            raise
        finally:
            detail = None
            if detail_fn is not None:
                try:
                    detail = detail_fn(args, kwargs)
                except Exception:
                    detail = None
            _record_timing(
                label, started_wall, started_process, started_thread, sql_before, detail, raised
            )

    setattr(wrapped, "_fitlink_diag_wrapped", True)
    return wrapped


def _command_detail(args, kwargs):
    name = args[0] if args else kwargs.get("name")
    return {"command": name if name in _ALLOWED_COMMANDS else "other"}


def _target_detail(args, kwargs):
    target = args[1] if len(args) > 1 else kwargs.get("kind")
    decision = args[2] if len(args) > 2 else kwargs.get("value", "approve")
    return {
        "target": target if target in _ALLOWED_TARGETS else "other",
        "decision": decision if decision in _ALLOWED_DECISIONS else "other",
    }


def _category_detail(args, kwargs):
    category = args[1] if len(args) > 1 else kwargs.get("category", "identity")
    return {"category": category if category in {"identity", "qualification"} else "other"}


def _credential_detail(args, kwargs):
    category = kwargs.get("category", args[1] if len(args) > 1 else "identity")
    role = kwargs.get("role")
    return {
        "category": category if category in {"identity", "qualification"} else "other",
        "role": role if role in _ALLOWED_TARGETS else "other",
    }


def _review_detail(args, kwargs):
    targets = args[1] if len(args) > 1 else kwargs.get("targets", ("identity", "coach", "nutritionist"))
    try:
        count = len(targets)
    except TypeError:
        count = 0
    return {"target_count": count}


def _publication_detail(args, kwargs):
    roles = kwargs.get("roles", ("coach",))
    fields = kwargs.get("fields", ("display_name", "biography"))
    return {
        "role_count": len(roles) if isinstance(roles, (tuple, list)) else 0,
        "field_count": len(fields) if isinstance(fields, (tuple, list)) else 0,
    }


def _corpus_detail(args, kwargs):
    roles = kwargs.get("roles", ("coach",))
    return {
        "coach_only": kwargs.get("coach_only", False) is True,
        "role_count": len(roles) if isinstance(roles, (tuple, list)) else 0,
    }


def _install_wrappers() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    import importlib

    search = importlib.import_module("tests.integration.c04.search_helpers")
    decisions = importlib.import_module("tests.integration.c03.test_verification_decisions")
    verification = importlib.import_module("tests.integration.c03.verification_helpers")

    verification.ready = _timed_wrapper("credential_evidence_asset_construction", verification.ready, _category_detail)
    verification.create = _timed_wrapper("credential_revision_construction", verification.create, _credential_detail)
    verification.command = _timed_wrapper("verification_command", verification.command, _command_detail)

    decisions.prepared = _timed_wrapper("account_profile_evidence_bundle", decisions.prepared)
    decisions.reviewer = _timed_wrapper("reviewer_and_step_up_setup", decisions.reviewer)
    decisions.assign = _timed_wrapper("review_assignment", decisions.assign)
    decisions.command = _timed_wrapper("verification_command", decisions.command, _command_detail)
    decisions.review = _timed_wrapper("review_bundle_and_submission", decisions.review, _review_detail)
    decisions.decision = _timed_wrapper("target_approval_decision", decisions.decision, _target_detail)

    original_approved = search.approved

    @functools.wraps(original_approved)
    def approved_with_setup_detail(*args, **kwargs):
        original_owner = verification.owner
        original_save = verification.save
        verification.owner = _timed_wrapper("account_profile_construction", original_owner)
        verification.save = _timed_wrapper("profile_step_save", original_save)
        try:
            started_wall = time.perf_counter()
            started_process = time.process_time()
            started_thread = time.thread_time()
            sql_before = _sql_snapshot()
            raised = False
            try:
                return original_approved(*args, **kwargs)
            except BaseException:
                raised = True
                raise
            finally:
                _record_timing(
                    "full_approval_lifecycle",
                    started_wall,
                    started_process,
                    started_thread,
                    sql_before,
                    None,
                    raised,
                )
        finally:
            verification.owner = original_owner
            verification.save = original_save

    setattr(approved_with_setup_detail, "_fitlink_diag_wrapped", True)
    search.approved = approved_with_setup_detail
    search.configure = _timed_wrapper("publication_configuration", search.configure)
    search.prepare = _timed_wrapper("publication_draft_preparation", search.prepare, _publication_detail)
    search.confirm = _timed_wrapper("publication_confirmation", search.confirm)

    original_api = search.api

    @functools.wraps(original_api)
    def api_with_projection_timing(*args, **kwargs):
        module = original_api(*args, **kwargs)
        refresh = getattr(module, "refresh_public_projection", None)
        if callable(refresh):
            setattr(
                module,
                "refresh_public_projection",
                _timed_wrapper("public_projection_refresh", refresh),
            )
        return module

    search.api = api_with_projection_timing
    _INSTALLED = True


def _read_resources() -> None:
    try:
        meminfo = Path("/proc/meminfo").read_text()
        available_kib = None
        for line in meminfo.splitlines():
            if line.startswith("MemAvailable:"):
                available_kib = int(line.split()[1])
                break
        load = os.getloadavg()[0] / max(1, os.cpu_count() or 1)
        psi = None
        pressure = Path("/proc/pressure/memory")
        if pressure.exists():
            for line in pressure.read_text().splitlines():
                if line.startswith("some "):
                    for token in line.split():
                        if token.startswith("avg10="):
                            psi = float(token.split("=", 1)[1])
                            break
        with _LOCK:
            _RESOURCE["samples"] += 1
            if available_kib is not None:
                mib = round(available_kib / 1024, 3)
                old = _RESOURCE["min_mem_available_mib"]
                _RESOURCE["min_mem_available_mib"] = mib if old is None else min(old, mib)
            old_load = _RESOURCE["max_load_per_cpu"]
            _RESOURCE["max_load_per_cpu"] = load if old_load is None else max(old_load, load)
            if psi is not None:
                old_psi = _RESOURCE["max_memory_psi_some_avg10"]
                _RESOURCE["max_memory_psi_some_avg10"] = psi if old_psi is None else max(old_psi, psi)
    except (OSError, ValueError, IndexError):
        return


def _sample_resources() -> None:
    started = time.thread_time()
    try:
        while not _STOP.is_set():
            _read_resources()
            _STOP.wait(1.0)
        _read_resources()
    finally:
        with _LOCK:
            _RESOURCE["sampler_thread_cpu_seconds"] = round(max(0.0, time.thread_time() - started), 6)


def pytest_sessionstart(session):
    global _SESSION_WALL, _SESSION_PROCESS, _SESSION_THREAD, _SAMPLER
    _SESSION_WALL = time.perf_counter()
    _SESSION_PROCESS = time.process_time()
    _SESSION_THREAD = time.thread_time()
    _STOP.clear()
    _SAMPLER = threading.Thread(target=_sample_resources, name="fitlink-diag-sampler", daemon=True)
    _SAMPLER.start()


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_collection(session):
    wall = time.perf_counter()
    process = time.process_time()
    thread = time.thread_time()
    outcome = yield
    _COLLECTION.update(
        {
            "wall_seconds": round(max(0.0, time.perf_counter() - wall), 6),
            "process_cpu_seconds": round(max(0.0, time.process_time() - process), 6),
            "thread_cpu_seconds": round(max(0.0, time.thread_time() - thread), 6),
            "outcome_failed": bool(outcome.excinfo),
        }
    )


def _start_phase(item, phase):
    key = (item.nodeid, phase)
    starts = getattr(item, "_fitlink_diag_starts", {})
    starts[key] = (time.perf_counter(), time.process_time(), time.thread_time(), _sql_snapshot())
    setattr(item, "_fitlink_diag_starts", starts)


def _end_phase(item, phase):
    starts = getattr(item, "_fitlink_diag_starts", {})
    start = starts.pop((item.nodeid, phase), None)
    if start is None:
        return
    wall, process, thread, sql_before = start
    sql_after = _sql_snapshot()
    row = {
        "test": item.nodeid,
        "phase": phase,
        "wall_seconds": round(max(0.0, time.perf_counter() - wall), 6),
        "process_cpu_seconds": round(max(0.0, time.process_time() - process), 6),
        "thread_cpu_seconds": round(max(0.0, time.thread_time() - thread), 6),
        "sql_count_primary_thread": max(0, sql_after[0] - sql_before[0]),
        "sql_execute_seconds_primary_thread": round(max(0.0, sql_after[1] - sql_before[1]), 6),
    }
    with _LOCK:
        _PHASES.append(row)


def _begin_test(item):
    global _SQL_WRAPPER_ENABLED, _SQL_WRAPPER_ERRORS
    stack = ExitStack()
    _STACKS[item.nodeid] = stack
    try:
        from django.db import connections

        stack.enter_context(connections["default"].execute_wrapper(_execute_wrapper))
        _SQL_WRAPPER_ENABLED = True
    except Exception:
        _SQL_WRAPPER_ERRORS += 1
        stack.close()


def _close_test(item):
    stack = _STACKS.pop(item.nodeid, None)
    if stack is not None:
        try:
            stack.close()
        except Exception:
            pass


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_setup(item):
    selected = item.nodeid in TARGETS
    if selected:
        _begin_test(item)
        _start_phase(item, "setup")
    outcome = yield
    if selected:
        _end_phase(item, "setup")


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_call(item):
    selected = item.nodeid in TARGETS
    if selected:
        _start_phase(item, "call")
    outcome = yield
    if selected:
        _end_phase(item, "call")


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_teardown(item, nextitem):
    selected = item.nodeid in TARGETS
    if selected:
        _start_phase(item, "teardown")
    outcome = yield
    if selected:
        _end_phase(item, "teardown")
        _close_test(item)


@pytest.hookimpl(hookwrapper=True)
def pytest_fixture_setup(fixturedef, request):
    outcome = yield
    if fixturedef.argname != "corpus":
        return
    try:
        value = outcome.get_result()
    except Exception:
        return
    if not callable(value):
        return
    _install_wrappers()
    outcome.force_result(_timed_wrapper("corpus_create", value, _corpus_detail))


def pytest_runtest_logreport(report):
    if report.nodeid not in TARGETS:
        return
    if report.failed:
        _STATUSES[report.nodeid] = "failed"
    elif report.when == "call":
        if report.skipped:
            _STATUSES[report.nodeid] = "xfailed" if hasattr(report, "wasxfail") else "skipped"
        elif report.passed:
            _STATUSES[report.nodeid] = "xpassed" if hasattr(report, "wasxfail") else "passed"
    elif report.skipped and report.nodeid not in _STATUSES:
        _STATUSES[report.nodeid] = "skipped"


def pytest_sessionfinish(session, exitstatus):
    _STOP.set()
    if _SAMPLER is not None:
        _SAMPLER.join(timeout=3)
    with _LOCK:
        resources = dict(_RESOURCE)
        phases = list(_PHASES)
        events = list(_EVENTS)
    counts = {key: 0 for key in ("passed", "failed", "skipped", "xfailed", "xpassed", "not_observed")}
    for target in TARGETS:
        status = _STATUSES.get(target, "not_observed")
        counts[status if status in counts else "not_observed"] += 1
    result = {
        "schema_version": 1,
        "diagnostic_only": True,
        "acceptance": False,
        "source_sha": os.environ.get("FITLINK_DIAG_SOURCE_SHA"),
        "source_tree": os.environ.get("FITLINK_DIAG_SOURCE_TREE"),
        "control_sha": os.environ.get("FITLINK_DIAG_CONTROL_SHA"),
        "lockfile_sha256_before_sync": json.loads(os.environ.get("FITLINK_DIAG_LOCK_HASHES", "{}")),
        "python_version": platform.python_version(),
        "cpu_count": os.cpu_count(),
        "pytest_exit_status": int(exitstatus),
        "test_selection": list(TARGETS),
        "test_statuses": [{"test": test, "status": _STATUSES.get(test, "not_observed")} for test in TARGETS],
        "test_status_counts": counts,
        "session": {
            "wall_seconds": round(max(0.0, time.perf_counter() - _SESSION_WALL), 6),
            "process_cpu_seconds": round(max(0.0, time.process_time() - _SESSION_PROCESS), 6),
            "main_thread_cpu_seconds": round(max(0.0, time.thread_time() - _SESSION_THREAD), 6),
            "collection": dict(_COLLECTION),
        },
        "phases": phases,
        "fixture_lifecycle_events": events,
        "sql_instrumentation": {
            "enabled_for_default_connection": _SQL_WRAPPER_ENABLED,
            "setup_errors": _SQL_WRAPPER_ERRORS,
            "scope": "main test thread default Django connection only; worker-thread connections are excluded",
            "sql_text_or_parameters_recorded": False,
        },
        "resource_observation": resources,
        "observer_overhead": {
            "sampler_thread_cpu_seconds": resources.get("sampler_thread_cpu_seconds", 0.0),
            "sample_count": resources.get("samples", 0),
            "pytest_hook_and_wrapper_cpu_not_independently_isolated": True,
            "timings_are_nested_and_must_not_be_summed": True,
        },
    }
    _OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    _OUTPUT.write_text(json.dumps(result, sort_keys=True) + "\n", encoding="utf-8")
