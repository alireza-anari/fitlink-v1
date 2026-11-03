"""Allowlisted aggregate observer. Never records values, SQL, argv or output."""
from __future__ import annotations

import functools
import hashlib
import json
import os
import subprocess
import sys
import threading
import time
import weakref
from contextlib import ExitStack
from pathlib import Path

try:
    import pytest
except ModuleNotFoundError:  # dependency-free diagnostic harness checks only
    pytest = None

SELECTIONS = {
    'inherited': {
        'tests/integration/c03/test_verification_decisions.py::test_expired_withdrawn_or_quarantined_evidence_denies_only_affected_target': 12,
        'tests/integration/c02/test_outbox_worker.py::test_worker_process_crash_rolls_back_effect_then_expired_lease_recovers': 1,
        'tests/integration/c04/test_public_copy_races.py::test_cleanup_replay_preserves_first_erasure_metadata': 4,
        'tests/integration/c04/test_public_projection.py::test_broker_and_beat_down_reads_still_deny': 7,
    },
    'new': {
        'tests/integration/c04/test_post_review_regressions.py::test_assigned_media_denies_stale_derivative_binding': 4,
        'tests/integration/c04/test_public_moderation.py::test_report_quota_and_duplicate_are_account_serialized': 1,
    },
}
GROUP = os.environ.get('FITLINK_DIAG_GROUP', 'inherited')
MODE = os.environ.get('FITLINK_DIAG_MODE', 'minimal')
SQL = [0, 0.0]
OBSERVER = [0.0, 0]
ERRORS = 0
TRUNCATED = False
PROFILE_CODES = {}
PROFILE_PATHS = {}
PROFILE_STACK = []
LIFECYCLE = {}
CHILDREN = weakref.WeakKeyDictionary()
CHILD_ROWS = []
ORIGINAL_CHILDREN = {}
PHASES = []
COLLECTION = {}
ITEMS = {}
ACTIVE = None
STACK = None
START = None
PHASE_START = None
STOP = threading.Event()
SAMPLER = None
RESOURCES = {'samples': 0, 'sampler_cpu_seconds': 0.0}


def collection_record(ids, group):
    expected = SELECTIONS[group]
    counts = {k: 0 for k in expected}
    unexpected = 0
    for node in ids:
        base = node.split('[', 1)[0]
        if base in counts:
            counts[base] += 1
        else:
            unexpected += 1
    return {'counts': counts, 'total': len(ids), 'unexpected_count': unexpected,
            'exact': counts == expected and unexpected == 0 and len(set(ids)) == len(ids),
            'digest': hashlib.sha256('\n'.join(ids).encode()).hexdigest()}


def sql_wrapper(execute, sql, params, many, context):
    started = time.perf_counter()
    try:
        return execute(sql, params, many, context)
    finally:
        SQL[0] += 1
        SQL[1] += time.perf_counter() - started


def snapshot():
    return {'sql_count': SQL[0], 'sql_seconds': SQL[1]}


def profile(frame, event, arg):
    # Frame values and callback arg are never inspected or retained.
    if event not in ('call', 'return'):
        return
    began_cpu = time.thread_time()
    code = frame.f_code
    if code not in PROFILE_CODES:
        PROFILE_CODES[code] = PROFILE_PATHS.get(code.co_filename, {}).get(code.co_name)
    label = PROFILE_CODES[code]
    if label is not None:
        now = time.perf_counter()
        if event == 'call':
            PROFILE_STACK.append([frame, label, now, 0.0])
        elif PROFILE_STACK and PROFILE_STACK[-1][0] is frame:
            _, label, began, children = PROFILE_STACK.pop()
            elapsed = now - began
            row = LIFECYCLE.setdefault(label, {'count': 0, 'inclusive_seconds': 0.0,
                        'self_excluding_labelled_children_seconds': 0.0})
            row['count'] += 1
            row['inclusive_seconds'] += elapsed
            row['self_excluding_labelled_children_seconds'] += max(0, elapsed - children)
            if PROFILE_STACK:
                PROFILE_STACK[-1][3] += elapsed
    OBSERVER[0] += time.thread_time() - began_cpu
    OBSERVER[1] += 1


LABEL_SPECS = {
    'tests/integration/c03/test_verification_decisions.py': {
        'approved': 'full_approval', 'review': 'verification_review',
        'decision': 'verification_decision', 'prepared': 'verification_bundle'},
    'tests/integration/c03/verification_helpers.py': {
        'prepared': 'verification_bundle', 'reviewer': 'reviewer_setup',
        'assign': 'verification_assignment', 'command': 'verification_command'},
    'tests/integration/c03/test_professional_setup.py': {
        'owner': 'owner_profile', 'save': 'profile_save'},
    'tests/integration/c03/test_credential_revisions.py': {
        'ready': 'credential_evidence', 'create': 'credential_revision'},
    'tests/integration/c04/publication_helpers.py': {
        'prepare': 'publication_prepare', 'confirm': 'publication_confirm'},
    'tests/integration/c04/search_helpers.py': {'create': 'corpus_create'},
    'tests/integration/c04/post_helpers.py': {'published': 'post_publication'},
    'config/use_cases/marketplace.py': {'refresh_public_projection': 'projection_refresh'},
    'django/core/management/commands/flush.py': {'handle': 'database_flush'},
}


def load_profile_codes():
    # Match exact trusted source paths and fixed function names. Pytest rewrites
    # assertion bytecode, so compiled-original code equality would miss helpers.
    for suffix, names in LABEL_SPECS.items():
        if suffix.startswith('django/'):
            import django
            path = Path(django.__file__).parent.parent / suffix
        else:
            path = Path.cwd() / suffix
        if not path.is_file():
            continue
        PROFILE_PATHS[str(path)] = names


def child_snapshot():
    return [dict(r) for r in CHILD_ROWS]


def install_children():
    if ORIGINAL_CHILDREN:
        return
    for name in ('__init__', 'wait', 'poll'):
        ORIGINAL_CHILDREN[name] = getattr(subprocess.Popen, name)
    original_init = ORIGINAL_CHILDREN['__init__']

    @functools.wraps(original_init)
    def init(child, *args, **kwargs):
        began = time.perf_counter()
        result = original_init(child, *args, **kwargs)
        # Fixed category only. No argv, environment, output or process IDs stored.
        CHILDREN[child] = (began, ACTIVE)
        return result

    def observe(child):
        global TRUNCATED
        if child.returncode is not None and child in CHILDREN:
            began, occurrence = CHILDREN.pop(child)
            if len(CHILD_ROWS) >= 512:
                TRUNCATED = True
            else:
                CHILD_ROWS.append({'category': 'child_process', 'occurrence': occurrence,
                     'duration_seconds': time.perf_counter() - began,
                     'exit_code': int(child.returncode)})

    def method(name):
        original = ORIGINAL_CHILDREN[name]
        @functools.wraps(original)
        def wrapped(child, *args, **kwargs):
            try:
                return original(child, *args, **kwargs)
            finally:
                observe(child)
        return wrapped
    subprocess.Popen.__init__ = init
    subprocess.Popen.wait = method('wait')
    subprocess.Popen.poll = method('poll')


def restore_children():
    for name, original in ORIGINAL_CHILDREN.items():
        setattr(subprocess.Popen, name, original)
    ORIGINAL_CHILDREN.clear()


def read_resources():
    mem = {}
    for line in Path('/proc/meminfo').read_text().splitlines():
        key, value = line.split(':', 1)
        if key in ('MemAvailable', 'MemTotal'):
            mem[key] = int(value.split()[0]) / 1024
    for key, value in mem.items():
        name = 'min_' + key + '_mib'
        RESOURCES[name] = min(RESOURCES.get(name, value), value)
    load = os.getloadavg()[0] / max(1, os.cpu_count() or 1)
    RESOURCES['max_load_per_cpu'] = max(RESOURCES.get('max_load_per_cpu', 0), load)
    for kind in ('cpu', 'memory', 'io'):
        path = Path('/proc/pressure') / kind
        if path.exists():
            for line in path.read_text().splitlines():
                parts = line.split()
                if parts[0] in ('some', 'full'):
                    values = dict(part.split('=') for part in parts[1:])
                    key = f'max_{kind}_psi_{parts[0]}_avg10'
                    RESOURCES[key] = max(RESOURCES.get(key, 0), float(values['avg10']))
    RESOURCES['samples'] += 1


def sample():
    began = time.thread_time()
    try:
        while not STOP.is_set():
            read_resources()
            STOP.wait(1)
    except (OSError, ValueError):
        RESOURCES['sampling_error'] = True
    finally:
        RESOURCES['sampler_cpu_seconds'] = time.thread_time() - began


def pytest_sessionstart(session):
    global START, SAMPLER
    START = (time.perf_counter(), time.process_time(), time.thread_time())
    if not session.config.option.collectonly:
        SAMPLER = threading.Thread(target=sample, daemon=True)
        SAMPLER.start()


def pytest_collection_finish(session):
    global COLLECTION, ERRORS
    COLLECTION = collection_record([i.nodeid for i in session.items], GROUP)
    for n, item in enumerate(session.items):
        ITEMS[item.nodeid] = n
    if not COLLECTION['exact']:
        raise pytest.UsageError('Authorized diagnostic collection mismatch')
    digest = os.environ.get('FITLINK_DIAG_EXPECT_DIGEST')
    if digest and COLLECTION['digest'] != digest:
        raise pytest.UsageError('Authorized diagnostic parameter digest mismatch')
    if MODE == 'detailed' and not session.config.option.collectonly:
        load_profile_codes()


def hook(fn):
    return pytest.hookimpl(hookwrapper=True, tryfirst=True)(fn) if pytest else fn


def begin_phase(item, phase):
    global ACTIVE, STACK, PHASE_START, ERRORS
    ACTIVE = ITEMS[item.nodeid]
    if phase == 'setup' and MODE == 'detailed':
        from django.db import connections
        STACK = ExitStack()
        STACK.enter_context(connections['default'].execute_wrapper(sql_wrapper))
        install_children()
        if sys.getprofile() is not None:
            ERRORS += 1
        else:
            sys.setprofile(profile)
    PHASE_START = (time.perf_counter(), time.process_time(), time.thread_time(), SQL[0], SQL[1], OBSERVER[0])


def end_phase(item, phase):
    global STACK, ACTIVE
    wall, process, thread, count, sql, observer = PHASE_START
    PHASES.append({'occurrence': ITEMS[item.nodeid],
        'function': item.nodeid.split('[', 1)[0], 'phase': phase,
        'wall_seconds': time.perf_counter() - wall,
        'process_cpu_seconds': time.process_time() - process,
        'main_thread_cpu_seconds': time.thread_time() - thread,
        'sql_count': SQL[0] - count if MODE == 'detailed' else None,
        'sql_seconds': SQL[1] - sql if MODE == 'detailed' else None,
        'profile_callback_cpu_seconds': OBSERVER[0] - observer if MODE == 'detailed' else None,
        'lifecycle': {k: dict(v) for k, v in LIFECYCLE.items()} if MODE == 'detailed' else {}})
    LIFECYCLE.clear()
    if phase == 'teardown':
        if MODE == 'detailed':
            sys.setprofile(None)
            restore_children()
            STACK.close()
            STACK = None
        ACTIVE = None


@hook
def pytest_runtest_setup(item):
    begin_phase(item, 'setup')
    yield
    end_phase(item, 'setup')


@hook
def pytest_runtest_call(item):
    begin_phase(item, 'call')
    yield
    end_phase(item, 'call')


@hook
def pytest_runtest_teardown(item, nextitem):
    begin_phase(item, 'teardown')
    yield
    end_phase(item, 'teardown')


def pytest_runtest_logreport(report):
    for row in reversed(PHASES):
        if row['occurrence'] == ITEMS.get(report.nodeid) and row['phase'] == report.when:
            row['outcome'] = report.outcome if not hasattr(report, 'wasxfail') else 'unexpected_xfail'
            return


def pytest_sessionfinish(session, exitstatus):
    STOP.set()
    if SAMPLER:
        SAMPLER.join(3)
    if MODE == 'detailed':
        sys.setprofile(None)
        restore_children()
    result = {'complete': True, 'exit_code': int(exitstatus), 'mode': MODE,
        'collection': COLLECTION, 'phases': PHASES, 'children': child_snapshot(),
        'unfinished_children': len(CHILDREN), 'observer_errors': ERRORS,
        'truncated': TRUNCATED, 'resources': RESOURCES,
        'session_wall_seconds': time.perf_counter() - START[0],
        'session_process_cpu_seconds': time.process_time() - START[1],
        'session_main_thread_cpu_seconds': time.thread_time() - START[2],
        'profile_callback_cpu_seconds_lower_bound': OBSERVER[0],
        'profile_callback_count': OBSERVER[1],
        'limitations': ['SQL: primary thread/default Django connection only',
            'child duration is parent-observed; SQL in children excluded',
            'self timing excludes only other labelled descendants',
            'profiler CPU excludes interpreter dispatch overhead',
            'minimal mode omits SQL, lifecycle and child instrumentation']}
    path = Path(os.environ['FITLINK_DIAG_OUTPUT'])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, sort_keys=True) + '\n')
