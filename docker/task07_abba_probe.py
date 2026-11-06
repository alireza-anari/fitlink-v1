"""One authorized four-function A-B-B-A diagnostic, without acceptance or raw output."""
from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from task07_abba_plugin import SELECTIONS, SPECS, PINS, ORDER, check_metrics, check_collection, closed, number, integer, reject_malformed
CAP = 56
PASSES = [(source,'fixed','four') for source in ORDER]
LOCKS = ('uv.lock', 'package-lock.json')
ROOT = Path(os.environ.get('GITHUB_WORKSPACE', Path.cwd())).resolve()
STATE = ROOT / '.runtime/abba-private'
OUT = ROOT / '.runtime/abba-evidence'
PROJECT = 'fitlink-c04-abba-four-' + os.environ.get('GITHUB_RUN_ID', 'local')
STAGES = []
FAILURES={None,'deadline','invalid_clock','expired_clock','attempt_not_one','manifest_cap_mismatch',
    'source_identity_mismatch','preparation_deadline','ownership_conflict','uv_version_mismatch',
    'command_failed','service_start_failed','collection_mismatch','actual_collection_cap_mismatch',
    'cross_source_collection_mismatch','source_changed_during_preparation','evidence_schema_failure',
    'pytest_failed_or_incomplete','test_failed_or_observation_incomplete','combined_measurement_deadline_or_incomplete',
    'interrupted','control_failure','not_started','offline_harness_failed','cleanup_failed','preservation_failed','process_reap_failed'}
STAGE_NAMES={
    'uv_version','private_credentials','compose_config','services_start','service_status_private',
    'task6_frozen_sync','task7_frozen_sync','collect_0','collect_1',
    'private_files_cleanup',
    *('pytest_pass_'+str(i) for i in range(1,5)),*('redis_reset_'+str(i) for i in range(1,5)),
    *('inventory_'+k for k in ('containers','networks','volumes')),
    *('cleanup_inventory_'+k for k in ('containers','networks','volumes')),
    *('owned_remove_'+k for k in ('containers','networks','volumes')),
}
OUTCOME_LIMITATIONS=[
    'Two-service topology excludes Foundation background services and full-suite ordering.',
    'Task6 and Task7 schemas intentionally differ; databases are fresh and owned Redis is reset.',
    'All passes use fixed wrappers; observer overhead can depend on source workload.',
    'Historical migration aliases and child/worker SQL and CPU are excluded from default SQL counters.',
]


class Stop(Exception):
    def __init__(self,reason):
        self.reason=reason if reason in FAILURES else 'control_failure'
        super().__init__(self.reason)


def parse_clock(raw,now):
    if type(raw) is not str or re.fullmatch(r'[0-9]+(?:\.[0-9]+)?',raw) is None:
        raise Stop('invalid_clock')
    began=float(raw)
    if not math.isfinite(began) or not math.isfinite(now) or began<=0 or began>now:
        raise Stop('invalid_clock')
    if now-began>=600:raise Stop('expired_clock')
    return began


def strict_json(text):
    def pairs(items):
        result={}
        for key,value in items:
            if key in result:raise Stop('evidence_schema_failure')
            result[key]=value
        return result
    def invalid(value):raise Stop('evidence_schema_failure')
    try:return json.loads(text,object_pairs_hook=pairs,parse_constant=invalid)
    except (ValueError,TypeError):raise Stop('evidence_schema_failure') from None


@reject_malformed
def check_stage(value):
    keys={'stage','exit_code','timed_out','truncated','wall_seconds'}
    optional={'failure_class','infrastructure_categories','service_state'}
    if type(value) is not dict or not keys<=set(value) or not set(value)<=keys|optional:return False
    if type(value['stage']) is not str or value['stage'] not in STAGE_NAMES or not integer(value['exit_code'],-255,255):return False
    if type(value['timed_out']) is not bool or type(value['truncated']) is not bool or not number(value['wall_seconds']):return False
    if 'failure_class' in value and value['failure_class'] not in ('command_unavailable','deadline','command_failed'):return False
    if 'infrastructure_categories' in value:
        categories={'service_unhealthy','daemon_unavailable','port_collision','image_pull_failure','registry_rate_limit','dns_failure','disk_full','connection_refused','permission_denied','unclassified'}
        if type(value['infrastructure_categories']) is not list or not set(value['infrastructure_categories'])<=categories:return False
    if 'service_state' in value and not check_services(value['service_state']):return False
    return True


@reject_malformed
def check_services(value):
    if closed(value,{'available','reason'}):
        return value['available'] is False and value['reason'] in ('service_state_unavailable','service_state_malformed')
    if not closed(value,{'available','services'}) or type(value['available']) is not bool or type(value['services']) is not list:return False
    if len(value['services'])>2:return False
    seen=set()
    for row in value['services']:
        if not closed(row,{'service','state','health','exit_code'}):return False
        if row['service'] not in ('db','redis') or row['service'] in seen:return False
        seen.add(row['service'])
        if row['state'] not in ('created','running','exited','restarting','paused','dead','unknown'):return False
        if row['health'] not in ('starting','healthy','unhealthy','','unknown'):return False
        if row['exit_code'] is not None and not integer(row['exit_code'],-255,255):return False
    return value['available']==bool(seen)


@reject_malformed
def check_cleanup(value):
    if not closed(value,{'verified','resources_after','private_files_removed','owned_resources_created','wall_seconds','errors'}):return False
    if any(type(value[k]) is not bool for k in ('verified','private_files_removed','owned_resources_created')):return False
    if not number(value['wall_seconds']) or not closed(value['resources_after'],{'containers','networks','volumes'}):return False
    if not all(v is None or integer(v) for v in value['resources_after'].values()):return False
    if type(value['errors']) is not list or not set(value['errors'])<={'containers','networks','volumes','inventory','private_files','deadline'}:return False
    return not value['verified'] or (value['private_files_removed'] and not value['errors'] and value['wall_seconds']<=120 and all(v==0 for v in value['resources_after'].values()))


def hash_string(value,length=64):
    return type(value) is str and len(value)==length and all(x in '0123456789abcdef' for x in value)


def env_integer(name):
    value=os.environ.get(name,'0')
    return int(value) if re.fullmatch(r'[0-9]{1,12}',value) else 0


@reject_malformed
def check_identities(value):
    if type(value) is not dict or not set(value)<=set(PINS):return False
    for source,row in value.items():
        if not closed(row,{'head','tree','clean','locks'}):return False
        if (row['head'],row['tree'])!=PINS[source] or type(row['clean']) is not bool:return False
        if not closed(row['locks'],LOCKS) or not all(hash_string(v) for v in row['locks'].values()):return False
    return True


@reject_malformed
def check_outcome(value):
    keys={'diagnostic_only','acceptance','count_cap','expected_executions','measurement_state','control_sha','control_tree',
        'run_id','attempt','sources_before','sources_after','sources_and_locks_preserved','collections','passes','stages',
        'measurement_seconds','preparation_seconds','cleanup_verified','measurements_complete','valid','failure_class',
        'host','topology','comparison_order','limitations','protected_branch_modified','local_unpublished_workspace_accessed'}
    if not closed(value,keys):return False
    if value['diagnostic_only'] is not True or value['acceptance'] is not False or value['count_cap']!=56 or value['expected_executions']!=56:return False
    if value['measurement_state'] not in ('not_started','partial','complete'):return False
    for key in ('control_sha','control_tree'):
        if value[key] is not None and not hash_string(value[key],40):return False
    if not integer(value['run_id']) or not integer(value['attempt'],0,100):return False
    if not check_identities(value['sources_before']) or not check_identities(value['sources_after']):return False
    if any(type(value[k]) is not bool for k in ('sources_and_locks_preserved','cleanup_verified','measurements_complete','valid')):return False
    if type(value['collections']) is not dict or not set(value['collections'])<={'task6_four','task7_four'}:return False
    for key,row in value['collections'].items():
        if not check_collection(row,key.split('_')[0],True):return False
    if type(value['passes']) is not list or len(value['passes'])>4:return False
    for index,row in enumerate(value['passes'],1):
        if not closed(row,{'pass','source','observer','selection','count','valid','session_wall_seconds'}):return False
        if not integer(row['pass'],1,4) or row['pass']!=index or row['source']!=ORDER[index-1] or row['observer']!='fixed' or row['selection']!='four' or row['count']!=sum(SELECTIONS['four'].values()):return False
        if type(row['valid']) is not bool or not number(row['session_wall_seconds']):return False
    if type(value['stages']) is not list or len(value['stages'])>128 or not all(check_stage(s) for s in value['stages']):return False
    if value['measurement_seconds'] is not None and not number(value['measurement_seconds']):return False
    if not number(value['preparation_seconds']) or value['failure_class'] is not None and type(value['failure_class']) is not str or value['failure_class'] not in FAILURES:return False
    host=value['host']
    if not closed(host,{'cpu_count','python','uv','memory_total_mib'}):return False
    if host['cpu_count'] is not None and not integer(host['cpu_count'],1,10000):return False
    if type(host['python']) is not str or re.fullmatch(r'3\.[0-9]{1,2}\.[0-9]{1,3}',host['python']) is None:return False
    if host['uv'] not in (None,'0.12.19') or host['memory_total_mib'] is not None and not number(host['memory_total_mib']):return False
    if value['topology']!=['PostgreSQL','Redis'] or value['comparison_order']!='A-B-B-A' or value['limitations']!=OUTCOME_LIMITATIONS:return False
    if value['protected_branch_modified'] is not False or value['local_unpublished_workspace_accessed'] is not False:return False
    if value['sources_and_locks_preserved'] and (set(value['sources_before'])!=set(PINS) or value['sources_before']!=value['sources_after'] or not all(r['clean'] for r in value['sources_after'].values())):return False
    if value['measurements_complete'] and (len(value['passes'])!=4 or not all(p['valid'] for p in value['passes']) or value['measurement_seconds'] is None or value['measurement_seconds']>900):return False
    if value['measurements_complete'] != (value['measurement_state']=='complete'):return False
    if value['measurement_state']=='not_started' and (value['passes'] or value['measurement_seconds'] is not None):return False
    if value['measurement_state']=='partial' and value['measurement_seconds'] is None:return False
    if value['valid']:
        if not final_valid(value['measurements_complete'],value['cleanup_verified'],value['sources_and_locks_preserved']) or value['failure_class'] is not None or value['preparation_seconds']>600 or value['attempt']!=1 or value['measurement_state']!='complete':return False
        if not hash_string(value['control_sha'],40) or not hash_string(value['control_tree'],40) or host['uv']!='0.12.19':return False
        if set(value['collections'])!={'task6_four','task7_four'} or value['collections']['task6_four']['digest']!=value['collections']['task7_four']['digest']:return False
        if any(s['exit_code'] or s['timed_out'] or s['truncated'] for s in value['stages']):return False
    return True


def publish_outcome(value):
    if not check_outcome(value):raise Stop('evidence_schema_failure')
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'outcome.json').write_text(json.dumps(value,sort_keys=True,allow_nan=False)+'\n')


def not_started_outcome(clean):
    return {'diagnostic_only':True,'acceptance':False,'count_cap':56,'expected_executions':56,'measurement_state':'not_started',
        'control_sha':None,'control_tree':None,'run_id':env_integer('GITHUB_RUN_ID'),'attempt':env_integer('GITHUB_RUN_ATTEMPT'),
        'sources_before':{},'sources_after':{},'sources_and_locks_preserved':False,'collections':{},'passes':[],'stages':[],
        'measurement_seconds':None,'preparation_seconds':0.0,'cleanup_verified':clean['verified'],'measurements_complete':False,'valid':False,
        'failure_class':'offline_harness_failed' if os.environ.get('FITLINK_HARNESS_OUTCOME')=='failure' else 'not_started',
        'host':{'cpu_count':os.cpu_count(),'python':platform.python_version(),'uv':None,'memory_total_mib':None},
        'topology':['PostgreSQL','Redis'],'comparison_order':'A-B-B-A','limitations':OUTCOME_LIMITATIONS,
        'protected_branch_modified':False,'local_unpublished_workspace_accessed':False}


def run_command(stage, args, *, cwd, timeout, env=None):
    began = time.monotonic()
    event = {'stage': stage, 'exit_code': 127, 'timed_out': False, 'truncated': False}
    if not number(timeout) or timeout <= 4:
        raise Stop('deadline')
    deadline=began+timeout
    # Include TERM/KILL grace within the supplied wall-clock ceiling.
    command = ['timeout', '--signal=TERM', '--kill-after=2s', f'{max(1, math.floor(timeout)-3)}s', *args]
    data = b''
    with tempfile.TemporaryFile() as log:
        try:
            process = subprocess.Popen(command, cwd=cwd, env=env, stdout=log,
                                       stderr=subprocess.STDOUT, start_new_session=True)
            try:
                # Keep one second inside the command ceiling for kill/reap.
                code = process.wait(timeout=max(.001,deadline-time.monotonic()-1))
            except subprocess.TimeoutExpired:
                kill_and_reap(process,deadline)
                code = 124
            except BaseException:
                # Cancellation must stop/reap the whole command group before
                # owned-resource cleanup starts; no late pytest or Compose CLI.
                try:kill_and_reap(process,deadline)
                except Stop:pass  # original cancellation identity still propagates
                raise
            size = os.fstat(log.fileno()).st_size
            log.seek(max(0, size - 1_000_000))
            data = log.read(1_000_000)
            event.update(exit_code=code, timed_out=code in (124, 137, -9), truncated=size > 1_000_000)
        except OSError:
            event['failure_class'] = 'command_unavailable'
    event['wall_seconds'] = time.monotonic() - began
    if event['exit_code'] != 0:
        event.setdefault('failure_class','deadline' if event['timed_out'] else 'command_failed')
    return event, data


def kill_and_reap(process,deadline):
    try:os.killpg(process.pid,signal.SIGKILL)
    except ProcessLookupError:pass
    try:process.wait(timeout=max(.001,min(1,deadline-time.monotonic())))
    except subprocess.TimeoutExpired:raise Stop('process_reap_failed') from None


def startup_classifier(data):
    # The raw private process output is held in the parent only. Only enums
    # leave the runner, even when Docker prints credential-bearing arguments.
    message = data.decode('utf-8', errors='replace').lower()
    patterns = (
        ('service_unhealthy', ('unhealthy', 'health check failed')),
        ('daemon_unavailable', ('cannot connect to the docker daemon',)),
        ('port_collision', ('port is already allocated', 'bind: address already in use')),
        ('image_pull_failure', ('pull access denied', 'failed to resolve source metadata')),
        ('registry_rate_limit', ('toomanyrequests', '429 too many requests')),
        ('dns_failure', ('temporary failure in name resolution',)),
        ('disk_full', ('no space left on device',)),
        ('connection_refused', ('connection refused',)),
        ('permission_denied', ('permission denied',)),
    )
    hits = [name for name, markers in patterns if any(marker in message for marker in markers)]
    return hits if hits else ['unclassified']


def safe_service_states(deadline, env):
    try:
        event,data=run_command('service_status_private',compose()+['ps','-a','--format','json'],cwd=ROOT,env=env,timeout=min(10,deadline-time.monotonic()))
        STAGES.append(event)
        if event['exit_code'] or event['timed_out'] or event['truncated']:
            return {'available':False,'reason':'service_state_unavailable'}
        try:
            parsed=strict_json(data.decode())
            items=parsed if type(parsed) is list else [parsed]
        except Stop:
            items=[strict_json(line.decode()) for line in data.splitlines() if line.strip()]
        rows=[]
        for item in items:
            if type(item) is not dict:raise ValueError
            if item.get('Service') not in ('db','redis'):continue
            exit_code=item.get('ExitCode')
            rows.append({'service':item['Service'],
                'state':item.get('State') if item.get('State') in ('created','running','exited','restarting','paused','dead') else 'unknown',
                'health':item.get('Health') if item.get('Health') in ('starting','healthy','unhealthy','') else 'unknown',
                'exit_code':exit_code if integer(exit_code,-255,255) else None})
        value={'available':bool(rows),'services':rows}
        if not check_services(value):raise ValueError
        return value
    except (Stop,ValueError,TypeError,AttributeError):
        return {'available':False,'reason':'service_state_malformed'}


def execute(stage, args, cwd, deadline, env=None, limit=180):
    event, data = run_command(stage, args, cwd=cwd, env=env,
                             timeout=min(limit, deadline-time.monotonic()))
    STAGES.append(event)
    if event['exit_code'] or event['timed_out'] or event['truncated']:
        raise Stop('deadline' if event['timed_out'] else 'command_failed')
    return data


def valid_metrics(value, expected, source, index):
    return check_metrics(value,source,index,True) and value['collection']==expected



def final_valid(measurements, cleanup, preservation):
    return measurements is True and cleanup is True and preservation is True


def update_cleanup_verdict(data, verified):
    data['cleanup_verified'] = data.get('cleanup_verified') is True and verified is True
    data['valid'] = data.get('valid') is True and final_valid(
        data['measurements_complete'], data['cleanup_verified'], data['sources_and_locks_preserved'])
    if not data['cleanup_verified']:data['failure_class']=data['failure_class'] or 'cleanup_failed'


def git(source, *args, deadline=None):
    remaining = 10 if deadline is None else min(10, deadline-time.monotonic())
    if remaining <= 0:
        raise Stop('preparation_deadline')
    return subprocess.run(['git', '-C', str(source), *args], check=True, capture_output=True,
                          text=True, timeout=remaining).stdout.strip()


def identity(name, deadline=None):
    path = ROOT / '.runtime' / (name+'-source')
    sha, tree = PINS[name]
    values = {'head': git(path, 'rev-parse', 'HEAD', deadline=deadline), 'tree': git(path, 'rev-parse', 'HEAD^{tree}', deadline=deadline),
              'clean': git(path, 'status', '--porcelain=v1', '--untracked-files=all', deadline=deadline) == '',
              'locks': {f: hashlib.sha256((path/f).read_bytes()).hexdigest() for f in LOCKS}}
    if values['head'] != sha or values['tree'] != tree or not values['clean']:
        raise Stop('source_identity_mismatch')
    return values


def inventory(deadline):
    counts = {}
    for kind, args in {
        'containers': ['docker', 'ps', '-aq'],
        'networks': ['docker', 'network', 'ls', '-q'],
        'volumes': ['docker', 'volume', 'ls', '-q'],
    }.items():
        data = execute('inventory_'+kind, args+['--filter', 'label=com.docker.compose.project='+PROJECT],
                       ROOT, deadline, limit=10)
        counts[kind] = len(data.split())
    return counts


def private_env():
    env = os.environ.copy()
    for key in list(env):
        if any(x in key for x in ('TOKEN', 'SECRET', 'PASSWORD', 'ACCESS_KEY')):
            env.pop(key)
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    return env


def compose():
    return ['docker', 'compose', '-f', str(ROOT/'.runtime/task7-source/compose.yaml'),
            '--env-file', str(STATE/'private.env'), '-p', PROJECT]


def cleanup():
    """Best effort for every owned category; one shared120s clock, sticky errors."""
    OUT.mkdir(parents=True,exist_ok=True);STATE.mkdir(parents=True,exist_ok=True)
    marker=STATE/'cleanup-start';now=time.monotonic();errors=[]
    try:
        if marker.exists():
            began=float(marker.read_text())
            if not math.isfinite(began) or began<=0 or began>now:raise ValueError
        else:
            began=now;marker.write_text(str(began))
        deadline=began+120
    except (ValueError,OSError):
        began=now;deadline=now;errors.append('deadline')
    owned=(STATE/'owned').exists();counts={k:None for k in ('containers','networks','volumes')}
    commands=(
        ('containers',['docker','ps','-aq'],['docker','rm','-f']),
        ('networks',['docker','network','ls','-q'],['docker','network','rm']),
        ('volumes',['docker','volume','ls','-q'],['docker','volume','rm']),
    )
    for kind,ls,rm in commands:
        if owned:
            try:
                data=execute('cleanup_inventory_'+kind,ls+['--filter','label=com.docker.compose.project='+PROJECT],ROOT,deadline,limit=10)
                ids=data.decode().split()
                if ids:execute('owned_remove_'+kind,rm+ids,ROOT,deadline,limit=20)
            except Exception:errors.append(kind)
    # Verify all categories, even after an earlier removal or query failed.
    for kind,ls,_ in commands:
        try:
            data=execute('inventory_'+kind,ls+['--filter','label=com.docker.compose.project='+PROJECT],ROOT,deadline,limit=10)
            counts[kind]=len(data.split())
        except Exception:errors.append('inventory')
    envpath=STATE/'private.env'
    try:
        envpath.unlink(missing_ok=True)
    except OSError:errors.append('private_files')
    # Keep only ownership/clock markers. Raw private metric files are erased too.
    try:
        paths=[*STATE.glob('pytest-tmp-*'),STATE/'pytest-cache',*STATE.glob('collection-*.json'),*STATE.glob('pass-*.json')]
        if any(path.exists() for path in paths):
            script="from pathlib import Path;import shutil,sys;root=Path(sys.argv[1]);paths=[*root.glob('pytest-tmp-*'),root/'pytest-cache',*root.glob('collection-*.json'),*root.glob('pass-*.json')];[(shutil.rmtree(p) if p.is_dir() and not p.is_symlink() else p.unlink(missing_ok=True)) for p in paths if p.exists() or p.is_symlink()]"
            execute('private_files_cleanup',[sys.executable,'-B','-c',script,str(STATE)],ROOT,deadline,limit=20)
        removed=not envpath.exists() and not any(path.exists() or path.is_symlink() for path in paths)
        if not removed:errors.append('private_files')
    except Exception:
        removed=False;errors.append('private_files')
    elapsed=time.monotonic()-began
    if elapsed>120:errors.append('deadline')
    result={'verified':not errors and removed and all(v==0 for v in counts.values()),
        'resources_after':counts,'private_files_removed':removed,'owned_resources_created':owned,
        'wall_seconds':max(0,elapsed),'errors':sorted(set(errors))}
    if not check_cleanup(result):raise Stop('evidence_schema_failure')
    (OUT/'cleanup.json').write_text(json.dumps(result,sort_keys=True)+'\n')
    return result


def evidence_consistent(outcome, clean, metrics):
    """Reconcile independent artifacts, allowing an unreported failed last pass."""
    if outcome is None or clean is None:return False
    if outcome['cleanup_verified'] and not clean['verified']:return False
    if outcome['measurement_state']=='not_started':return not metrics
    rows=outcome['passes']
    for row in rows:
        index=row['pass'];data=metrics.get(index)
        if data is None:return False
        expected=outcome['collections'].get(row['source']+'_four')
        complete=valid_metrics(data,expected,row['source'],index)
        if row['valid']!=complete or row['session_wall_seconds']!=data['session_wall_seconds']:return False
        if row['count']!=data['collection']['total']:return False
    if outcome['measurements_complete']:
        return set(metrics)=={1,2,3,4} and all(row['valid'] for row in rows)
    # invoke() may export a safe failed/partial observation before appending its
    # summary. Later passes cannot have started after that failure.
    return set(metrics)<=set(range(1,min(4,len(rows)+1)+1))


def write_manifest():
    """Validate presence, schemas and agreement before sealing named exports."""
    allowed={'cleanup.json','outcome.json',*('pass-'+str(i)+'.json' for i in range(1,5))}
    bad=False;clean=None;outcome=None;metrics={}
    for path in OUT.glob('*.json'):
        if path.name not in allowed:
            bad=True
            continue  # never hash/upload an unexpected file name or its contents
        try:
            if path.is_symlink():raise Stop('evidence_schema_failure')
            data=strict_json(path.read_text())
            if path.name=='cleanup.json':
                valid=check_cleanup(data)
                if valid:clean=data
            elif path.name=='outcome.json':
                valid=check_outcome(data)
                if valid:outcome=data
            else:
                index=int(path.stem.split('-')[1]);valid=check_metrics(data,ORDER[index-1],index,False)
                if valid:metrics[index]=data
            if not valid:raise Stop('evidence_schema_failure')
        except Exception:
            bad=True;path.unlink(missing_ok=True)  # invalid data stays out of export
    if not evidence_consistent(outcome,clean,metrics):bad=True
    if bad:
        data=outcome
        if data is None:
            clean=clean or {'verified':False,'resources_after':{'containers':None,'networks':None,'volumes':None},'private_files_removed':False,'owned_resources_created':False,'wall_seconds':0.0,'errors':['private_files']}
            data=not_started_outcome(clean)
        data['valid']=False
        if data['failure_class'] in (None,'not_started'):data['failure_class']='evidence_schema_failure'
        publish_outcome(data)
    lines=[]
    for name in sorted(allowed):
        path=OUT/name
        if path.is_file():lines.append(hashlib.sha256(path.read_bytes()).hexdigest()+'  '+name)
    (OUT/'SHA256SUMS.txt').write_text('\n'.join(lines)+'\n')
    return not bad


def main():
    STAGES.clear()
    OUT.mkdir(parents=True, exist_ok=True)
    STATE.mkdir(parents=True, exist_ok=True)
    STATE.chmod(0o700)
    began = time.monotonic()
    prep_deadline = began+600
    measurements = False
    preserved = False
    before = {}
    after = {}
    passes = []
    collections = {}
    failure = None
    env = private_env()
    measurement_start = None
    actual_uv=None
    def interrupted(signum, frame):
        raise Stop('interrupted')
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGINT, interrupted)
    try:
        began = parse_clock(os.environ.get('FITLINK_PREPARATION_START'),time.monotonic())
        prep_deadline=began+600
        if os.environ.get('GITHUB_RUN_ATTEMPT') != '1':
            raise Stop('attempt_not_one')
        if sum(sum(SELECTIONS[g].values()) for _, _, g in PASSES) != CAP:
            raise Stop('manifest_cap_mismatch')
        before = {n: identity(n, prep_deadline) for n in PINS}
        uv_output=execute('uv_version',['uv','--version'],ROOT,prep_deadline,env=env,limit=10)
        if not re.match(rb'uv 0\.12\.19(?:\s|$)',uv_output):
            raise Stop('uv_version_mismatch')
        actual_uv='0.12.19'
        counts = inventory(prep_deadline)
        if any(counts.values()):
            raise Stop('ownership_conflict')
        execute('private_credentials', [sys.executable, str(ROOT/'.runtime/task7-source/docker/generate_env.py'),
                    str(STATE/'private.env')], ROOT, prep_deadline, env=env, limit=15)
        values = dict(line.split('=', 1) for line in (STATE/'private.env').read_text().splitlines())
        # One unchanged runtime environment, installed from its frozen lock.
        for name in PINS:
            source = ROOT/'.runtime'/(name+'-source')
            execute(name+'_frozen_sync', ['uv', 'sync', '--frozen', '--group', 'dev', '--python', '3.13.15', '--no-progress'],
                    source, prep_deadline, env=env, limit=550)
        execute('compose_config', compose()+['config', '--quiet'], ROOT, prep_deadline, env=env, limit=20)
        (STATE/'owned').touch()
        startup, private_output = run_command('services_start',
            compose()+['up', '-d', '--wait', 'db', 'redis'], cwd=ROOT,
            env=env, timeout=min(120,prep_deadline-time.monotonic()))
        STAGES.append(startup)
        if startup['exit_code'] or startup['timed_out'] or startup['truncated']:
            startup['infrastructure_categories'] = startup_classifier(private_output)
            startup['service_state'] = safe_service_states(prep_deadline, env)
            raise Stop('service_start_failed')
        startup['service_state'] = safe_service_states(prep_deadline, env)
        health=startup['service_state']
        if not health.get('available') or {r['service'] for r in health.get('services',[])}!={'db','redis'} or any(r['state']!='running' or r['health']!='healthy' for r in health.get('services',[])):
            raise Stop('service_start_failed')
        pytest_env = dict(env)
        for key in ('POSTGRES_DB','POSTGRES_USER','POSTGRES_PASSWORD','POSTGRES_HOST', 'POSTGRES_PORT',
                    'REDIS_URL','CELERY_BROKER_URL','CELERY_RESULT_BACKEND','CHANNEL_REDIS_URL'):
            pytest_env[key] = values[key]
        pytest_env.update(DJANGO_SETTINGS_MODULE='config.settings.test',
            OTP_RATE_REDIS_URL='redis://127.0.0.1:'+values['REDIS_HOST_PORT']+'/4')
        plugin_dir = str(ROOT/'docker')

        def invoke(name, mode, group, index, deadline, collect=False, digest=None):
            source = ROOT/'.runtime'/(name+'-source')
            path = STATE/(f'collection-{index}.json' if collect else f'pass-{index}.json')
            call_env = dict(pytest_env)
            call_env.update(PYTHONPATH=str(source)+os.pathsep+plugin_dir,
                FITLINK_DIAG_MODE=mode, FITLINK_DIAG_GROUP=group, FITLINK_DIAG_OUTPUT=str(path),
                FITLINK_DIAG_SOURCE=name,FITLINK_DIAG_SOURCE_SHA=PINS[name][0],FITLINK_DIAG_SOURCE_TREE=PINS[name][1],
                FITLINK_DIAG_PASS=str(0 if collect else index))
            if digest:
                call_env['FITLINK_DIAG_EXPECT_DIGEST']=digest
            command = ['uv', 'run', '--frozen', '--no-sync', 'pytest', '-q', '--strict-markers',
                '--tb=no', '--show-capture=no', '-o', 'cache_dir='+str(STATE/'pytest-cache'),
                '--basetemp='+str(STATE/('pytest-tmp-'+str(index))), '-p', 'task07_abba_plugin']
            if collect:
                command.append('--collect-only')
            command.extend(SELECTIONS[group])
            stage=('collect_' if collect else 'pytest_pass_')+str(index)
            event,_=run_command(stage,command,cwd=source,env=call_env,timeout=min(240,deadline-time.monotonic()))
            STAGES.append(event)
            data=strict_json(path.read_text()) if path.is_file() else None
            if data is not None and not check_metrics(data,name,0 if collect else index,False):
                raise Stop('evidence_schema_failure')
            if not collect and data is not None:
                (OUT/('pass-'+str(index)+'.json')).write_text(json.dumps(data,sort_keys=True)+'\n')
            if event['exit_code'] or event['timed_out'] or event['truncated'] or data is None:
                raise Stop('deadline' if event['timed_out'] else 'pytest_failed_or_incomplete')
            if collect:
                if not check_metrics(data,name,0,True):
                    raise Stop('collection_mismatch')
                return data['collection']
            return data

        # Collect all source/selection combinations before executing any test.
        for i, (name, group) in enumerate([('task6','four'),('task7','four')]):
            collections[name+'_'+group] = invoke(name,'minimal',group,i,prep_deadline,collect=True)
        if sum(collections[n+'_'+g]['total'] for n, _, g in PASSES) != CAP:
            raise Stop('actual_collection_cap_mismatch')
        if collections['task6_four']['digest'] != collections['task7_four']['digest'] or collections['task6_four']['counts'] != collections['task7_four']['counts']:
            raise Stop('cross_source_collection_mismatch')
        for name in PINS:
            if identity(name, prep_deadline) != before[name]:
                raise Stop('source_changed_during_preparation')
        if time.monotonic() >= prep_deadline:
            raise Stop('preparation_deadline')
        measurement_start = time.monotonic()
        deadline = measurement_start+900
        for index, (name, mode, group) in enumerate(PASSES, 1):
            expected = collections[name+'_'+group]
            execute('redis_reset_'+str(index), compose()+['exec','-T','redis','redis-cli','FLUSHALL'],
                    ROOT, deadline, env=env, limit=10)
            data = invoke(name,mode,group,index,deadline,digest=expected['digest'])
            # Export only structured metrics built from the fixed observer schema.
            (OUT/('pass-'+str(index)+'.json')).write_text(json.dumps(data,sort_keys=True)+'\n')
            valid = valid_metrics(data, expected, name, index)
            passes.append({'pass':index, 'source':name, 'observer':mode, 'selection':group,
                'count':data['collection']['total'], 'valid':valid,
                'session_wall_seconds':data['session_wall_seconds']})
            if not valid:
                raise Stop('test_failed_or_observation_incomplete')
        measurements = len(passes) == 4 and time.monotonic() <= deadline
        if not measurements:
            failure='combined_measurement_deadline_or_incomplete'
    except Stop as exc:
        # Stop messages are fixed control labels only, never underlying exception messages.
        failure = exc.reason
    except BaseException:
        failure = 'control_failure'
    finally:
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        measurement_seconds = time.monotonic()-measurement_start if measurement_start else None
        cleaned = cleanup()
        try:
            after = {name:identity(name) for name in PINS}
            preserved = bool(before) and before == after
        except Exception:
            preserved = False
        if not cleaned['verified']:failure=failure or 'cleanup_failed'
        if not preserved:failure=failure or 'preservation_failed'
        try:control_tree=git(ROOT,'rev-parse','HEAD^{tree}')
        except Exception:control_tree=None;failure=failure or 'control_failure'
        control_sha=os.environ.get('GITHUB_SHA')
        if not hash_string(control_sha,40):control_sha=None;failure=failure or 'control_failure'
        result = {'diagnostic_only':True, 'acceptance':False, 'count_cap':CAP, 'expected_executions':56,
            'measurement_state':'complete' if measurements else ('partial' if measurement_start is not None else 'not_started'),
            'control_sha':control_sha, 'control_tree':control_tree,
            'run_id':env_integer('GITHUB_RUN_ID'), 'attempt':env_integer('GITHUB_RUN_ATTEMPT'),
            'sources_before':before, 'sources_after':after, 'sources_and_locks_preserved':preserved,
            'collections':collections, 'passes':passes, 'stages':STAGES, 'measurement_seconds':measurement_seconds,
            'preparation_seconds':(measurement_start or time.monotonic())-began,
            'cleanup_verified':cleaned['verified'], 'measurements_complete':measurements,
            'valid':failure is None and final_valid(measurements,cleaned['verified'],preserved), 'failure_class':failure,
            'host':{'cpu_count':os.cpu_count(),'python':platform.python_version(),
                    'uv':actual_uv, 'memory_total_mib':next((int(l.split()[1])/1024 for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemTotal:')),None)},
            'topology':['PostgreSQL','Redis'], 'comparison_order':'A-B-B-A',
            'limitations':OUTCOME_LIMITATIONS,
            'protected_branch_modified':False, 'local_unpublished_workspace_accessed':False}
        try:publish_outcome(result)
        except Stop:
            result=not_started_outcome(cleaned);result['failure_class']='evidence_schema_failure';publish_outcome(result)
        if not write_manifest():result['valid']=False
    return 0 if result['valid'] else 1


if __name__ == '__main__':
    if len(sys.argv)>1 and sys.argv[1]=='cleanup':
        clean = cleanup()
        path = OUT/'outcome.json'
        if path.exists():
            data=strict_json(path.read_text())
            update_cleanup_verdict(data, clean['verified'])
            publish_outcome(data)
        else:
            publish_outcome(not_started_outcome(clean))
        sealed=write_manifest()
        raise SystemExit(0 if clean['verified'] and sealed else 1)
    raise SystemExit(main())


