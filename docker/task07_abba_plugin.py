"""A-B-B-A fixed operation observers: original four tests, no private content."""
from __future__ import annotations

import functools
import hashlib
import importlib
import json
import math
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

PINS = {
    'task6': ('0787d7880f9fd27006bf76ae0f16e31536ef4503','b207a0a8e946750a0dd1213f5460e51f67dd3000'),
    'task7': ('2b2790cdf9019338ddeb09f9df2fdfb1fa0dd331','f4a49666111ce27d6c12cc6aff89f3430c7ea243'),
}
ORDER = ('task6','task7','task7','task6')
CAPABILITY_CASES = (
    'coach_approve_nutritionist_reject','nutritionist_expiry_preserves_coach',
    'coach_revocation_preserves_nutritionist','temporary_role_restriction_is_local',
    'restriction_removal_reuses_valid_approval','restriction_removal_cannot_undo_revocation',
    'add_declared_role_preserves_other_approval','deactivate_role_preserves_other_approval',
    'inflight_requested_role_or_evidence_edit_is_stale','c04_input_excludes_unverified_declarations',
    'concurrent_restriction_revocation_decision_consistent',
)
SELECTIONS = {'four': {
    'tests/integration/c04/test_search_query_plans.py::test_real_bounded_fts_trigram_query_plan': 1,
    'tests/integration/c02/test_account_migrations.py::test_populated_c01_upgrade_preserves_identity_and_sessions': 1,
    'tests/integration/c03/test_c03_migrations.py::test_optional_profiles_not_created': 1,
    'tests/integration/c03/test_upgrade_from_c02.py::test_upgrade_replays_all_eleven_capability_cases': len(CAPABILITY_CASES),
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
RESOURCES = {'samples':0,'sampler_cpu_seconds':0.0,'sampling_error':False,
    'min_mem_available_mib':None,'max_load_per_cpu':0.0,
    **{f'max_{kind}_psi_{scope}_avg10':0.0 for kind in ('cpu','memory','io') for scope in ('some','full')}}
RESOURCE_KEYS=frozenset(RESOURCES)
# The labels name only fixed, source-neutral operations. Timers nest and overlap.
SPECS = {'fixed': {label: label for label in (
    'corpus', 'candidate_query', 'migration_executor_init',
    'migration_build_graph', 'migration_execute', 'migration_apply',
    'migration_unapply', 'migration_state_render', 'migration_state_clone'
)}}
LIMITATIONS = [
    'Main-thread class/fixture timers; primary default Django SQL connection only.',
    'Separate historical migration aliases and worker/child SQL and CPU are not counted.',
    'candidate_query times lazy queryset construction; fts_explain times SQL execution.',
    'Self time excludes labelled descendants only; inclusive timings overlap.',
    'Bookkeeping CPU is a lower bound; ABBA fixed-only comparisons are not natural runtimes.',
]
BUCKETS={'fts_temp_create','fts_insert_30000','fts_analyze','fts_explain','other_sql'}


def reject_malformed(function):
    @functools.wraps(function)
    def checked(*args,**kwargs):
        try:return function(*args,**kwargs)
        except (TypeError,ValueError,OverflowError,KeyError,IndexError):return False
    return checked


def closed(value,keys):
    return type(value) is dict and set(value)==set(keys)


def integer(value,minimum=0,maximum=10**12):
    return type(value) is int and minimum<=value<=maximum


def number(value):
    return type(value) in (float,int) and math.isfinite(value) and 0<=value<=10**12


@reject_malformed
def check_collection(value,source,require_exact=False):
    keys={'group','source','counts','total','unexpected_count','exact','digest'}
    if not closed(value,keys) or source not in PINS:return False
    if value['group']!='four' or value['source']!=source:return False
    if not closed(value['counts'],SELECTIONS['four']):return False
    if not all(integer(x) for x in value['counts'].values()):return False
    if not integer(value['total']) or not integer(value['unexpected_count']):return False
    if sum(value['counts'].values())+value['unexpected_count']!=value['total']:return False
    if type(value['exact']) is not bool:return False
    if type(value['digest']) is not str or len(value['digest'])!=64 or any(x not in '0123456789abcdef' for x in value['digest']):return False
    if require_exact:
        return value==collection_record(expected_ids(),'four',source)
    if value['exact'] and value!=collection_record(expected_ids(),'four',source):return False
    return True


@reject_malformed
def check_metrics(value,source,index,require_complete=False):
    """Closed privacy schema is checked even when exporting failed observations."""
    root={'schema_version','group','source','source_sha','source_tree','pass_index','kind',
        'complete','exit_code','mode','collection','collection_timing','phases','observer_errors','truncated',
        'actual_pytest_python_version','actual_pytest_python_implementation','actual_pytest_package_version',
        'session_wall_seconds','session_process_cpu_seconds','session_main_thread_cpu_seconds',
        'wrapper_bookkeeping_cpu_seconds_lower_bound','alias_installation_wall_seconds','alias_restoration_wall_seconds',
        'fixed_callsite_labels','alias_bindings','resources','limitations'}
    if not closed(value,root) or source not in PINS:return False
    if type(index) is not int or not 0<=index<=len(ORDER):return False
    if index and source!=ORDER[index-1]:return False
    if value['schema_version']!=1 or type(value['schema_version']) is not int:return False
    if value['group']!='four' or value['source']!=source:return False
    if (value['source_sha'],value['source_tree'])!=PINS[source]:return False
    if type(value['pass_index']) is not int or value['pass_index']!=index:return False
    if value['kind']!=('measurement' if index else 'collection'):return False
    if value['mode']!=('fixed' if index else 'minimal'):return False
    if type(value['complete']) is not bool or type(value['truncated']) is not bool:return False
    if not integer(value['exit_code'],0,255) or not integer(value['observer_errors']):return False
    if not check_collection(value['collection'],source,require_complete):return False
    timing=value['collection_timing']
    if not closed(timing,{'wall_seconds','process_cpu_seconds','main_thread_cpu_seconds','failed'}):return False
    if type(timing['failed']) is not bool or not all(number(timing[k]) for k in timing if k!='failed'):return False
    if value['actual_pytest_python_version']!='3.13.15' or value['actual_pytest_python_implementation']!='CPython':return False
    # Frozen source pins fix the dependency version; never accept free text.
    if value['actual_pytest_package_version']!='9.1.1':return False
    scalar=('session_wall_seconds','session_process_cpu_seconds','session_main_thread_cpu_seconds',
        'wrapper_bookkeeping_cpu_seconds_lower_bound','alias_installation_wall_seconds','alias_restoration_wall_seconds')
    if not all(number(value[k]) for k in scalar):return False
    labels={label for group in SPECS.values() for label in group.values()}
    installed=labels-{'corpus'}
    if value['fixed_callsite_labels']!=(sorted(labels) if index else []):return False
    if not integer(value['alias_bindings']) or value['alias_bindings']!=(len(installed) if index else 0):return False
    if value['limitations']!=LIMITATIONS:return False
    resource=value['resources']
    if not closed(resource,RESOURCE_KEYS):return False
    if not integer(resource['samples']) or type(resource['sampling_error']) is not bool:return False
    for key,v in resource.items():
        if key in ('samples','sampling_error'):continue
        if key=='min_mem_available_mib' and v is None:continue
        if not number(v):return False
    phases=value['phases']
    if type(phases) is not list or len(phases)>len(expected_ids())*3:return False
    seen=set();seen_labels=set();by_call={}
    functions=[node.split('[',1)[0] for node in expected_ids()]
    phasekeys={'occurrence','function','phase','outcome','wall_seconds','process_cpu_seconds','main_thread_cpu_seconds',
        'sql_count','sql_seconds','wrapper_bookkeeping_cpu_seconds_lower_bound','lifecycle','sql_operations'}
    for row in phases:
        if not closed(row,phasekeys):return False
        occurrence=row['occurrence'];phase=row['phase']
        if not integer(occurrence,0,len(functions)-1) or phase not in ('setup','call','teardown'):return False
        if row['function']!=functions[occurrence] or (occurrence,phase) in seen:return False
        seen.add((occurrence,phase))
        if row['outcome'] not in ('passed','failed','skipped','unexpected_xfail'):return False
        if not all(number(row[k]) for k in ('wall_seconds','process_cpu_seconds','main_thread_cpu_seconds','sql_seconds','wrapper_bookkeeping_cpu_seconds_lower_bound')):return False
        if not integer(row['sql_count']):return False
        operations=row['sql_operations']
        if type(operations) is not dict or not set(operations)<=BUCKETS:return False
        for op in operations.values():
            if not closed(op,{'count','seconds'}) or not integer(op['count'],1) or not number(op['seconds']):return False
        if sum(op['count'] for op in operations.values())!=row['sql_count']:return False
        if not math.isclose(sum(op['seconds'] for op in operations.values()),row['sql_seconds'],rel_tol=1e-6,abs_tol=1e-7):return False
        events=row['lifecycle']
        if type(events) is not dict or not set(events)<=labels:return False
        for label,event in events.items():
            if not closed(event,{'count','raised','inclusive_seconds','self_excluding_labelled_children_seconds'}):return False
            if not integer(event['count'],1) or not integer(event['raised'],0,event['count']):return False
            if not number(event['inclusive_seconds']) or not number(event['self_excluding_labelled_children_seconds']):return False
            if event['self_excluding_labelled_children_seconds']>event['inclusive_seconds']+1e-8:return False
            seen_labels.add(label)
        if phase=='call':by_call[occurrence]=row
    if not index and phases:return False
    if require_complete:
        if not value['complete'] or value['exit_code'] or value['observer_errors'] or value['truncated'] or timing['failed']:return False
        if index:
            if seen!={(i,k) for i in range(len(functions)) for k in ('setup','call','teardown')}:return False
            if any(row['outcome']!='passed' for row in phases):return False
            if seen_labels!=labels or resource['samples']<1 or resource['sampling_error'] or resource['min_mem_available_mib'] is None:return False
            if not {'corpus','candidate_query'}<=set(by_call[0]['lifecycle']):return False
            if any(by_call[0]['sql_operations'].get(k,{}).get('count')!=1 for k in BUCKETS-{'other_sql'}):return False
            for occurrence in (1,2):
                if not {'migration_executor_init','migration_build_graph','migration_execute'}<=set(by_call[occurrence]['lifecycle']):return False
    return True


class EvidenceError(ValueError):
    """Fixed category only; never carries input or exception text."""


def expected_ids():
    functions=list(SELECTIONS['four'])
    return functions[:3]+[functions[3]+'['+case+']' for case in CAPABILITY_CASES]


def collection_record(ids,group,source):
    if group!='four':raise EvidenceError('group_mismatch')
    if source not in PINS:raise EvidenceError('source_mismatch')
    if not isinstance(ids,list) or any(type(node) is not str for node in ids):raise EvidenceError('collection_shape')
    counts={key:0 for key in SELECTIONS[group]};unexpected=0
    for node in ids:
        base=node.split('[',1)[0]
        if base in counts:counts[base]+=1
        else:unexpected+=1
    return {'group':group,'source':source,'counts':counts,'total':len(ids),'unexpected_count':unexpected,
        'exact':ids==expected_ids(),
        'digest':hashlib.sha256('\n'.join(ids).encode()).hexdigest()}


def timed(label,original):
    @functools.wraps(original)
    def wrapped(*args,**kwargs):
        global BOOKKEEPING_CPU
        if threading.get_ident()!=MAIN_THREAD:
            return original(*args,**kwargs)
        entry=None
        try:
            tick=time.thread_time()
            entry=[time.perf_counter(),0.0]
            WRAPPER_STACK.append(entry)
            BOOKKEEPING_CPU+=time.thread_time()-tick
        except Exception:
            observer_error()
        raised=False
        try:
            return original(*args,**kwargs)
        except BaseException:
            raised=True
            raise
        finally:
            if entry is not None:
                try:
                    tick=time.thread_time()
                    elapsed=time.perf_counter()-entry[0]
                    if WRAPPER_STACK and WRAPPER_STACK[-1] is entry:WRAPPER_STACK.pop()
                    row=EVENTS.setdefault(label,{'count':0,'raised':0,'inclusive_seconds':0.0,'self_excluding_labelled_children_seconds':0.0})
                    row['count']+=1;row['raised']+=int(raised)
                    row['inclusive_seconds']+=elapsed
                    row['self_excluding_labelled_children_seconds']+=max(0.0,elapsed-entry[1])
                    if WRAPPER_STACK:WRAPPER_STACK[-1][1]+=elapsed
                    BOOKKEEPING_CPU+=time.thread_time()-tick
                except Exception:observer_error()
                finally:
                    WRAPPER_STACK[:]=[x for x in WRAPPER_STACK if x is not entry]
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


def observer_error():
    global OBSERVER_ERRORS
    OBSERVER_ERRORS+=1


def restore_aliases(records):
    ok=True
    for module,name,original,wrapped in reversed(records):
        try:
            if getattr(module,name) is not wrapped:observer_error();ok=False
        except Exception:observer_error();ok=False
        try:setattr(module,name,original)
        except Exception:observer_error();ok=False
    return ok


def class_targets():
    # Use class objects for migration instrumentation so separately imported
    # module aliases still dispatch through the exact original class method.
    from django.db.migrations.executor import MigrationExecutor
    from django.db.migrations.loader import MigrationLoader
    from django.db.migrations.state import ProjectState, StateApps
    from apps.marketplace import search
    return (
        (MigrationExecutor, '__init__', 'migration_executor_init'),
        (MigrationLoader, 'build_graph', 'migration_build_graph'),
        (MigrationExecutor, 'migrate', 'migration_execute'),
        (MigrationExecutor, 'apply_migration', 'migration_apply'),
        (MigrationExecutor, 'unapply_migration', 'migration_unapply'),
        (StateApps, '__init__', 'migration_state_render'),
        (ProjectState, 'clone', 'migration_state_clone'),
        (search, 'candidate_query', 'candidate_query'),
    )
def install_aliases():
    targets=class_targets()
    labels={x for group in SPECS.values() for x in group.values()}-{'corpus'}
    if len(targets)!=8 or {x[2] for x in targets}!=labels or len({(id(owner),name) for owner,name,_ in targets})!=8:
        raise RuntimeError('invalid_fixed_callsite')
    planned=[]
    for owner,name,label in targets:
        original = getattr(owner, name)
        if not callable(original):
            raise RuntimeError('invalid_fixed_callsite')
        planned.append((owner,name,original,timed(label,original)))
    records=[]
    try:
        for owner,name,original,wrapped in planned:
            records.append((owner,name,original,wrapped))
            setattr(owner,name,wrapped)
    except BaseException:
        restore_aliases(records)
        raise
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
    try:kind=sql_bucket(sql);began=time.perf_counter()
    except Exception:observer_error();kind='other_sql';began=None
    try:
        return execute(sql, params, many, context)
    finally:
        if began is not None:
            try:
                elapsed=time.perf_counter()-began
                SQL[0]+=1;SQL[1]+=elapsed
                entry=SQL_CLASSES.setdefault(kind,[0,0.0]);entry[0]+=1;entry[1]+=elapsed
            except Exception:observer_error()


def read_resources():
    for line in Path('/proc/meminfo').read_text().splitlines():
        if line.startswith('MemAvailable:'):
            value=int(line.split()[1])/1024
            old=RESOURCES.get('min_mem_available_mib')
            RESOURCES['min_mem_available_mib']=value if old is None else min(old,value)
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
    except (OSError,ValueError,TypeError):RESOURCES['sampling_error']=True
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
    source=os.environ.get('FITLINK_DIAG_SOURCE')
    try:
        index=int(os.environ.get('FITLINK_DIAG_PASS','-1'))
        if os.environ.get('FITLINK_DIAG_GROUP')!=GROUP or source not in PINS or (os.environ.get('FITLINK_DIAG_SOURCE_SHA'),os.environ.get('FITLINK_DIAG_SOURCE_TREE'))!=PINS[source]:raise ValueError
        if session.config.option.collectonly:
            if index!=0 or MODE!='minimal':raise ValueError
        elif not 1<=index<=4 or source!=ORDER[index-1] or MODE!='fixed':raise ValueError
    except (ValueError,TypeError):raise pytest.UsageError('diagnostic_configuration') from None
    COLLECTION=collection_record([i.nodeid for i in session.items],GROUP,source)
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
    try:
        begin_phase(item, 'call')
        yield
    finally:
        try:end_phase(item, 'call')
        except Exception:observer_error()
        finally:
            if prior is not None:item.funcargs['corpus']=prior


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
    if SQL_STACK is not None:
        try:SQL_STACK.close()
        except Exception:observer_error()
    RESTORE_SECONDS=time.perf_counter()-began
    source=os.environ.get('FITLINK_DIAG_SOURCE')
    result={'schema_version':1,'group':GROUP,'source':source,
        'source_sha':os.environ.get('FITLINK_DIAG_SOURCE_SHA'),
        'source_tree':os.environ.get('FITLINK_DIAG_SOURCE_TREE'),
        'pass_index':int(os.environ.get('FITLINK_DIAG_PASS','0')),
        'kind':'collection' if session.config.option.collectonly else 'measurement',
        'complete':True,'exit_code':int(exitstatus),'mode':MODE,'collection':COLLECTION,
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
        'limitations':LIMITATIONS}
    path=Path(os.environ['FITLINK_DIAG_OUTPUT']);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,sort_keys=True)+'\n')

