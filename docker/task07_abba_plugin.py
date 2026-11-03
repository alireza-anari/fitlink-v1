"""A-B-B-A fixed operation observers: original four tests, no private content."""
from __future__ import annotations

import functools
import hashlib
import importlib
import json
import os
import platform
import sys
import threading
import time
from contextlib import ExitStack
from pathlib import Path

try:
    import pytest
except ModuleNotFoundError:  # dependency-free control harness only
    pytest = None

SELECTIONS = {'four': {
    'tests/integration/c04/test_search_query_plans.py::test_real_bounded_fts_trigram_query_plan': 1,
    'tests/integration/c02/test_account_migrations.py::test_populated_c01_upgrade_preserves_identity_and_sessions': 1,
    'tests/integration/c03/test_c03_migrations.py::test_optional_profiles_not_created': 1,
    'tests/integration/c03/test_upgrade_from_c02.py::test_upgrade_replays_all_eleven_capability_cases': 1,
}}
GROUP = 'four'
MODE = os.environ.get('FITLINK_DIAG_MODE', 'fixed')
MAIN_THREAD = threading.get_ident()
EVENTS = {}
WRAPPER_STACK = []
SQL = [0, 0.0]
SQL_CLASSES = {}
BOOKKEEPING_CPU = 0.0
PHASES = []
ITEMS = {}
COLLECTION = {}
COLLECTION_TIMING = {}
START = None
PHASE_START = None
SQL_STACK = None
ALIASES = []
INSTALL_SECONDS = 0.0
RESTORE_SECONDS = 0.0
OBSERVER_ERRORS = 0
STOP = threading.Event()
SAMPLER = None
RESOURCES = {'samples': 0, 'sampler_cpu_seconds': 0.0}
# The labels name only fixed, source-neutral operations. Timers nest and overlap.
SPECS = {'fixed': {label: label for label in (
    'corpus', 'candidate_query', 'migration_executor_init',
    'migration_build_graph', 'migration_execute', 'migration_apply',
    'migration_unapply', 'migration_state_render', 'migration_state_clone'
)}}


def collection_record(ids,group):
    counts={key:0 for key in SELECTIONS[group]};unexpected=0
    for node in ids:
        base=node.split('[',1)[0]
        if base in counts:counts[base]+=1
        else:unexpected+=1
    return {'counts':counts,'total':len(ids),'unexpected_count':unexpected,
        'exact':counts==SELECTIONS[group] and unexpected==0 and len(set(ids))==len(ids),
        'digest':hashlib.sha256('\n'.join(ids).encode()).hexdigest()}


def timed(label,original):
    @functools.wraps(original)
    def wrapped(*args,**kwargs):
        global BOOKKEEPING_CPU
        if threading.get_ident()!=MAIN_THREAD:
            return original(*args,**kwargs)
        tick=time.thread_time()
        entry=[time.perf_counter(),0.0]
        WRAPPER_STACK.append(entry)
        BOOKKEEPING_CPU+=time.thread_time()-tick
        raised=False
        try:
            return original(*args,**kwargs)
        except BaseException:
            raised=True
            raise
        finally:
            tick=time.thread_time()
            elapsed=time.perf_counter()-entry[0]
            WRAPPER_STACK.pop()
            row=EVENTS.setdefault(label,{'count':0,'raised':0,'inclusive_seconds':0.0,'self_excluding_labelled_children_seconds':0.0})
            row['count']+=1;row['raised']+=int(raised)
            row['inclusive_seconds']+=elapsed
            row['self_excluding_labelled_children_seconds']+=max(0.0,elapsed-entry[1])
            if WRAPPER_STACK:WRAPPER_STACK[-1][1]+=elapsed
            BOOKKEEPING_CPU+=time.thread_time()-tick
    return wrapped


def bind_aliases(modules,replacements):
    records=[]
    for module in modules:
        for name,value in list(vars(module).items()):
            # Avoid overloaded equality/hash on unrelated imported objects.
            match=next((new for old,new in replacements.items() if value is old),None)
            if match is not None:
                records.append((module,name,value,match))
                setattr(module,name,match)
    return records


def restore_aliases(records):
    global OBSERVER_ERRORS
    for module,name,original,wrapped in reversed(records):
        if getattr(module,name) is not wrapped:OBSERVER_ERRORS+=1
        setattr(module,name,original)


def install_aliases():
    # Use class objects for migration instrumentation so separately imported
    # module aliases still dispatch through the exact original class method.
    from django.db.migrations.executor import MigrationExecutor
    from django.db.migrations.loader import MigrationLoader
    from django.db.migrations.state import ProjectState, StateApps
    from apps.marketplace import search
    records = []
    targets = (
        (MigrationExecutor, '__init__', 'migration_executor_init'),
        (MigrationLoader, 'build_graph', 'migration_build_graph'),
        (MigrationExecutor, 'migrate', 'migration_execute'),
        (MigrationExecutor, 'apply_migration', 'migration_apply'),
        (MigrationExecutor, 'unapply_migration', 'migration_unapply'),
        (StateApps, '__init__', 'migration_state_render'),
        (ProjectState, 'clone', 'migration_state_clone'),
        (search, 'candidate_query', 'candidate_query'),
    )
    for owner, name, label in targets:
        original = getattr(owner, name)
        if not callable(original):
            raise RuntimeError('invalid_fixed_callsite')
        wrapped = timed(label, original)
        setattr(owner, name, wrapped)
        records.append((owner, name, original, wrapped))
    return records


def sql_bucket(statement):
    # No SQL, parameters or identifiers are written to any output.
    prefix = statement.lstrip().upper() if type(statement) is str else ''
    if prefix.startswith('CREATE TEMP TABLE MARKETPLACE_PUBLICPROFESSIONALPROJECTION'):
        return 'fts_temp_create'
    if prefix.startswith('INSERT INTO MARKETPLACE_PUBLICPROFESSIONALPROJECTION'):
        return 'fts_insert_30000'
    if prefix.startswith('ANALYZE MARKETPLACE_PUBLICPROFESSIONALPROJECTION'):
        return 'fts_analyze'
    if prefix.startswith('EXPLAIN '):
        return 'fts_explain'
    return 'other_sql'


def sql_wrapper(execute, sql, params, many, context):
    kind = sql_bucket(sql)
    began = time.perf_counter()
    try:
        return execute(sql, params, many, context)
    finally:
        elapsed = time.perf_counter() - began
        SQL[0] += 1
        SQL[1] += elapsed
        entry = SQL_CLASSES.setdefault(kind, [0, 0.0])
        entry[0] += 1
        entry[1] += elapsed


def read_resources():
    for line in Path('/proc/meminfo').read_text().splitlines():
        if line.startswith('MemAvailable:'):
            value=int(line.split()[1])/1024
            RESOURCES['min_mem_available_mib']=min(RESOURCES.get('min_mem_available_mib',value),value)
    load=os.getloadavg()[0]/max(1,os.cpu_count() or 1)
    RESOURCES['max_load_per_cpu']=max(RESOURCES.get('max_load_per_cpu',0),load)
    for kind in ('cpu','memory','io'):
        path=Path('/proc/pressure')/kind
        if path.exists():
            for line in path.read_text().splitlines():
                parts=line.split()
                if parts[0] in ('some','full'):
                    values=dict(part.split('=') for part in parts[1:])
                    key=f'max_{kind}_psi_{parts[0]}_avg10'
                    RESOURCES[key]=max(RESOURCES.get(key,0),float(values['avg10']))
    RESOURCES['samples']+=1


def sample():
    tick=time.thread_time()
    try:
        while not STOP.is_set():
            read_resources();STOP.wait(1)
    except (OSError,ValueError):RESOURCES['sampling_error']=True
    finally:RESOURCES['sampler_cpu_seconds']=time.thread_time()-tick


def hook(fn):
    return pytest.hookimpl(hookwrapper=True,tryfirst=True)(fn) if pytest else fn


def pytest_sessionstart(session):
    global START
    START=(time.perf_counter(),time.process_time(),time.thread_time())


@hook
def pytest_collection(session):
    tick=(time.perf_counter(),time.process_time(),time.thread_time())
    outcome=yield
    COLLECTION_TIMING.update(wall_seconds=time.perf_counter()-tick[0],process_cpu_seconds=time.process_time()-tick[1],main_thread_cpu_seconds=time.thread_time()-tick[2],failed=bool(outcome.excinfo))


def pytest_collection_finish(session):
    global COLLECTION,ALIASES,SAMPLER,INSTALL_SECONDS
    COLLECTION=collection_record([i.nodeid for i in session.items],GROUP)
    for i,item in enumerate(session.items):ITEMS[item.nodeid]=i
    expected=os.environ.get('FITLINK_DIAG_EXPECT_DIGEST')
    if not COLLECTION['exact'] or expected and expected!=COLLECTION['digest']:
        raise pytest.UsageError('authorized_manifest_mismatch')
    if MODE=='fixed' and not session.config.option.collectonly:
        began=time.perf_counter()
        ALIASES=install_aliases()
        INSTALL_SECONDS=time.perf_counter()-began
        SAMPLER=threading.Thread(target=sample,daemon=True);SAMPLER.start()


def begin_phase(item,phase):
    global PHASE_START,SQL_STACK
    if phase=='setup' and MODE=='fixed':
        from django.db import connections
        SQL_STACK=ExitStack()
        SQL_STACK.enter_context(connections['default'].execute_wrapper(sql_wrapper))
    PHASE_START=(time.perf_counter(),time.process_time(),time.thread_time(),SQL[0],SQL[1],BOOKKEEPING_CPU,{k:tuple(v) for k,v in SQL_CLASSES.items()})


def end_phase(item,phase):
    global SQL_STACK,OBSERVER_ERRORS
    wall,process,thread,count,sql,cpu,old_classes=PHASE_START
    PHASES.append({'occurrence':ITEMS[item.nodeid],'function':item.nodeid.split('[',1)[0],
        'phase':phase,'wall_seconds':time.perf_counter()-wall,
        'process_cpu_seconds':time.process_time()-process,'main_thread_cpu_seconds':time.thread_time()-thread,
        'sql_count':SQL[0]-count if MODE=='fixed' else None,
        'sql_seconds':SQL[1]-sql if MODE=='fixed' else None,
        'wrapper_bookkeeping_cpu_seconds_lower_bound':BOOKKEEPING_CPU-cpu if MODE=='fixed' else None,
        'lifecycle':{key:dict(value) for key,value in EVENTS.items()} if MODE=='fixed' else {},
        'sql_operations': {key: {'count': value[0] - old_classes.get(key, (0,0))[0],
                                 'seconds': value[1] - old_classes.get(key, (0,0))[1]}
                           for key,value in SQL_CLASSES.items()
                           if value[0] > old_classes.get(key, (0,0))[0]} if MODE=='fixed' else {}})
    EVENTS.clear()
    if WRAPPER_STACK:OBSERVER_ERRORS+=1
    if phase=='teardown' and SQL_STACK is not None:
        SQL_STACK.close();SQL_STACK=None


@hook
def pytest_runtest_setup(item):
    begin_phase(item,'setup');yield;end_phase(item,'setup')


@hook
def pytest_runtest_call(item):
    # The search case obtains the corpus fixture through item.funcargs.
    # A temporary exactly-once wrapper observes its actual fixture call.
    prior = item.funcargs.get('corpus')
    if MODE == 'fixed' and callable(prior):
        item.funcargs['corpus'] = timed('corpus', prior)
    begin_phase(item, 'call')
    try:
        yield
    finally:
        end_phase(item, 'call')
        if prior is not None:
            item.funcargs['corpus'] = prior


@hook
def pytest_runtest_teardown(item,nextitem):
    begin_phase(item,'teardown');yield;end_phase(item,'teardown')


def pytest_runtest_logreport(report):
    for row in reversed(PHASES):
        if row['occurrence']==ITEMS.get(report.nodeid) and row['phase']==report.when:
            row['outcome']=report.outcome if not hasattr(report,'wasxfail') else 'unexpected_xfail'
            return


def pytest_sessionfinish(session,exitstatus):
    global RESTORE_SECONDS,OBSERVER_ERRORS
    STOP.set()
    if SAMPLER:
        SAMPLER.join(3)
        if SAMPLER.is_alive():OBSERVER_ERRORS+=1
    began=time.perf_counter()
    restore_aliases(ALIASES)
    RESTORE_SECONDS=time.perf_counter()-began
    result={'complete':True,'exit_code':int(exitstatus),'mode':MODE,'collection':COLLECTION,
        'collection_timing':COLLECTION_TIMING,'phases':PHASES,'observer_errors':OBSERVER_ERRORS,
        'truncated':False,
        'actual_pytest_python_version':platform.python_version(),
        'actual_pytest_python_implementation':platform.python_implementation(),
        'actual_pytest_package_version':pytest.__version__,
        'session_wall_seconds':time.perf_counter()-START[0],
        'session_process_cpu_seconds':time.process_time()-START[1],
        'session_main_thread_cpu_seconds':time.thread_time()-START[2],
        'wrapper_bookkeeping_cpu_seconds_lower_bound':BOOKKEEPING_CPU,
        'alias_installation_wall_seconds':INSTALL_SECONDS,'alias_restoration_wall_seconds':RESTORE_SECONDS,
        'fixed_callsite_labels':sorted(label for functions in SPECS.values() for label in functions.values()) if MODE=='fixed' else [],
        'alias_bindings':len(ALIASES),'resources':RESOURCES,
        'limitations':['primary-thread migration and search wrappers and default Django SQL only',
            'worker-thread and child-process CPU/SQL/lifecycles are unobserved',
            'self excludes only labelled descendants; inclusive timers overlap',
            'wrapper CPU is bookkeeping lower bound, excluding dispatch and SQL-wrapper overhead',
            'fixed mode adds default-connection SQL wrapper, class wrappers and a one-second resource sampler',
            'SQL timing excludes separately created migration database aliases and child workers',
            'minimal mode has phase/session hooks only; hook cost not separately isolated']}
    path=Path(os.environ['FITLINK_DIAG_OUTPUT']);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,sort_keys=True)+'\n')
