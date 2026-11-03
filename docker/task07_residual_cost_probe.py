"""One authorized 101-execution diagnostic. Private output never leaves runner."""
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

from task07_residual_cost_plugin import SELECTIONS

CAP = 101
PASSES = [('task6', 'minimal', 'inherited'), ('task7', 'detailed', 'inherited'),
          ('task7', 'minimal', 'inherited'), ('task6', 'detailed', 'inherited'),
          ('task7', 'detailed', 'new')]
PINS = {
    'task6': ('0787d7880f9fd27006bf76ae0f16e31536ef4503', 'b207a0a8e946750a0dd1213f5460e51f67dd3000'),
    'task7': ('2b2790cdf9019338ddeb09f9df2fdfb1fa0dd331', 'f4a49666111ce27d6c12cc6aff89f3430c7ea243'),
}
LOCKS = ('uv.lock', 'package-lock.json')
ROOT = Path(os.environ.get('GITHUB_WORKSPACE', Path.cwd())).resolve()
STATE = ROOT / '.runtime/residual-private'
OUT = ROOT / '.runtime/residual-evidence'
PROJECT = 'fitlink-c04-residual-' + os.environ.get('GITHUB_RUN_ID', 'local')
STAGES = []


class Stop(Exception):
    pass


def run_command(stage, args, *, cwd, timeout, env=None):
    began = time.monotonic()
    event = {'stage': stage, 'exit_code': 127, 'timed_out': False, 'truncated': False}
    if timeout <= 4:
        raise Stop('deadline')
    # Include TERM/KILL grace within the supplied wall-clock ceiling.
    command = ['timeout', '--signal=TERM', '--kill-after=2s', f'{max(1, math.floor(timeout)-3)}s', *args]
    data = b''
    with tempfile.TemporaryFile() as log:
        try:
            process = subprocess.Popen(command, cwd=cwd, env=env, stdout=log,
                                       stderr=subprocess.STDOUT, start_new_session=True)
            try:
                code = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
                code = 124
            except BaseException:
                # Cancellation must stop/reap the whole command group before
                # owned-resource cleanup starts; no late pytest or Compose CLI.
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait(timeout=3)
                raise
            size = os.fstat(log.fileno()).st_size
            log.seek(max(0, size - 1_000_000))
            data = log.read(1_000_000)
            event.update(exit_code=code, timed_out=code in (124, 137, -9), truncated=size > 1_000_000)
        except OSError:
            event['failure_class'] = 'command_unavailable'
    event['wall_seconds'] = time.monotonic() - began
    if event['exit_code'] != 0:
        event['failure_class'] = 'deadline' if event['timed_out'] else 'command_failed'
    return event, data


def execute(stage, args, cwd, deadline, env=None, limit=180):
    event, data = run_command(stage, args, cwd=cwd, env=env,
                             timeout=min(limit, deadline-time.monotonic()))
    STAGES.append(event)
    if event['exit_code'] or event['timed_out'] or event['truncated']:
        raise Stop(stage + ('_deadline' if event['timed_out'] else '_failed'))
    return data


def valid_metrics(value, expected):
    if not isinstance(value, dict) or not value.get('complete') or value.get('exit_code') != 0:
        return False
    if value.get('truncated') or value.get('observer_errors') != 0 or value.get('unfinished_children') != 0:
        return False
    collection = value.get('collection', {})
    if collection != expected or not collection.get('exact'):
        return False
    phases = value.get('phases', [])
    total = expected['total']
    keys = {(r.get('occurrence'), r.get('phase')) for r in phases}
    want = {(i, p) for i in range(total) for p in ('setup', 'call', 'teardown')}
    return len(phases) == total*3 and keys == want and all(r.get('outcome') == 'passed' for r in phases)


def final_valid(measurements, cleanup, preservation):
    return measurements is True and cleanup is True and preservation is True


def update_cleanup_verdict(data, verified):
    data['cleanup_verified'] = data.get('cleanup_verified') is True and verified is True
    data['valid'] = data.get('valid') is True and final_valid(
        data['measurements_complete'], data['cleanup_verified'], data['sources_and_locks_preserved'])


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
    OUT.mkdir(parents=True, exist_ok=True)
    marker = STATE/'cleanup-start'
    if marker.exists():
        began = float(marker.read_text())
    else:
        began = time.monotonic()
        STATE.mkdir(parents=True, exist_ok=True)
        marker.write_text(str(began))
    deadline = began+120
    owned = (STATE/'owned').exists()
    verified = False
    removed = False
    try:
        if owned:
            # Label-scoped removal remains usable after private credentials are erased.
            for kind, ls, rm in (
                ('containers', ['docker','ps','-aq'], ['docker','rm','-f']),
                ('networks', ['docker','network','ls','-q'], ['docker','network','rm']),
                ('volumes', ['docker','volume','ls','-q'], ['docker','volume','rm']),
            ):
                ids = execute('cleanup_inventory_'+kind,
                    ls+['--filter','label=com.docker.compose.project='+PROJECT],
                    ROOT, deadline, limit=10).decode().split()
                if ids:
                    execute('owned_remove_'+kind, rm+ids, ROOT, deadline, limit=20)
            counts = inventory(deadline)
            verified = all(n == 0 for n in counts.values())
        else:
            counts = inventory(deadline)
            verified = all(n == 0 for n in counts.values())
    except Exception:
        counts = None
    finally:
        try:
            envpath = STATE/'private.env'
            if envpath.exists():
                envpath.unlink()
            for path in STATE.glob('pytest-tmp-*'):
                shutil.rmtree(path)
            removed = not envpath.exists() and not list(STATE.glob('pytest-tmp-*'))
        except OSError:
            removed = False
    result = {'verified': verified and removed, 'resources_after': counts,
              'private_files_removed': removed, 'owned_resources_created': owned,
              'wall_seconds': time.monotonic()-began}
    (OUT/'cleanup.json').write_text(json.dumps(result, sort_keys=True)+'\n')
    return result


def write_manifest():
    lines = []
    for path in sorted(OUT.glob('*.json')):
        lines.append(hashlib.sha256(path.read_bytes()).hexdigest()+'  '+path.name)
    (OUT/'SHA256SUMS.txt').write_text('\n'.join(lines)+'\n')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    STATE.mkdir(parents=True, exist_ok=True)
    STATE.chmod(0o700)
    began = float(os.environ.get('FITLINK_PREPARATION_START', time.monotonic()))
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
    def interrupted(signum, frame):
        raise Stop('interrupted')
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGINT, interrupted)
    try:
        if os.environ.get('GITHUB_RUN_ATTEMPT') != '1':
            raise Stop('attempt_not_one')
        if sum(sum(SELECTIONS[g].values()) for _, _, g in PASSES) != CAP:
            raise Stop('manifest_cap_mismatch')
        before = {n: identity(n, prep_deadline) for n in PINS}
        if before['task6']['locks'] != before['task7']['locks']:
            raise Stop('cross_source_lock_mismatch')
        counts = inventory(prep_deadline)
        if any(counts.values()):
            raise Stop('ownership_conflict')
        execute('private_credentials', [sys.executable, str(ROOT/'.runtime/task7-source/docker/generate_env.py'),
                    str(STATE/'private.env')], ROOT, prep_deadline, env=env, limit=15)
        values = dict(line.split('=', 1) for line in (STATE/'private.env').read_text().splitlines())
        # uv environments remain per-source. Both resolve from identical frozen locks.
        for name in PINS:
            source = ROOT/'.runtime'/(name+'-source')
            execute(name+'_frozen_sync', ['uv', 'sync', '--frozen', '--group', 'dev', '--python', '3.13.15', '--no-progress'],
                    source, prep_deadline, env=env, limit=550)
        execute('compose_config', compose()+['config', '--quiet'], ROOT, prep_deadline, env=env, limit=20)
        (STATE/'owned').touch()
        execute('services_start', compose()+['up', '-d', '--wait', 'db', 'redis'], ROOT,
                prep_deadline, env=env, limit=120)
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
                FITLINK_DIAG_MODE=mode, FITLINK_DIAG_GROUP=group, FITLINK_DIAG_OUTPUT=str(path))
            if digest:
                call_env['FITLINK_DIAG_EXPECT_DIGEST']=digest
            command = ['uv', 'run', '--frozen', '--no-sync', 'pytest', '-q', '--strict-markers',
                '--tb=no', '--show-capture=no', '-o', 'cache_dir='+str(STATE/'pytest-cache'),
                '--basetemp='+str(STATE/('pytest-tmp-'+str(index))), '-p', 'task07_residual_cost_plugin']
            if collect:
                command.append('--collect-only')
            command.extend(SELECTIONS[group])
            execute(('collect_' if collect else 'pytest_pass_')+str(index), command, source, deadline, env=call_env)
            data = json.loads(path.read_text())
            if collect:
                if not data['collection']['exact'] or data['exit_code']:
                    raise Stop('collection_mismatch')
                return data['collection']
            return data

        # Collect all source/selection combinations before executing any test.
        for i, (name, group) in enumerate([('task6','inherited'),('task7','inherited'),('task7','new')]):
            collections[name+'_'+group] = invoke(name,'minimal',group,i,prep_deadline,collect=True)
        if collections['task6_inherited'] != collections['task7_inherited']:
            raise Stop('inherited_parameterization_differs')
        if sum(collections[n+'_'+g]['total'] for n, _, g in PASSES) != CAP:
            raise Stop('actual_collection_cap_mismatch')
        for name in PINS:
            if identity(name, prep_deadline) != before[name]:
                raise Stop('source_changed_during_preparation')
        if time.monotonic() >= prep_deadline:
            raise Stop('preparation_deadline')
        measurement_start = time.monotonic()
        deadline = measurement_start+600
        for index, (name, mode, group) in enumerate(PASSES, 1):
            expected = collections[name+'_'+group]
            execute('redis_reset_'+str(index), compose()+['exec','-T','redis','redis-cli','FLUSHALL'],
                    ROOT, deadline, env=env, limit=10)
            data = invoke(name,mode,group,index,deadline,digest=expected['digest'])
            # Export only structured metrics built from the fixed observer schema.
            (OUT/('pass-'+str(index)+'.json')).write_text(json.dumps(data,sort_keys=True)+'\n')
            valid = valid_metrics(data, expected)
            passes.append({'pass':index, 'source':name, 'observer':mode, 'selection':group,
                'count':data['collection']['total'], 'valid':valid,
                'session_wall_seconds':data['session_wall_seconds']})
            if not valid:
                raise Stop('test_failed_or_observation_incomplete')
        measurements = len(passes) == 5
    except Stop as exc:
        # Stop messages are fixed control labels only, never underlying exception messages.
        failure = str(exc)
    except BaseException:
        failure = 'harness_exception'
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
        result = {'diagnostic_only':True, 'acceptance':False, 'count_cap':CAP, 'expected_executions':101,
            'control_sha':os.environ.get('GITHUB_SHA'), 'control_tree':git(ROOT,'rev-parse','HEAD^{tree}'),
            'run_id':int(os.environ.get('GITHUB_RUN_ID','0')), 'attempt':int(os.environ.get('GITHUB_RUN_ATTEMPT','0')),
            'sources_before':before, 'sources_after':after, 'sources_and_locks_preserved':preserved,
            'collections':collections, 'passes':passes, 'stages':STAGES, 'measurement_seconds':measurement_seconds,
            'preparation_seconds':(measurement_start or time.monotonic())-began,
            'cleanup_verified':cleaned['verified'], 'measurements_complete':measurements,
            'valid':final_valid(measurements,cleaned['verified'],preserved), 'failure_class':failure,
            'host':{'cpu_count':os.cpu_count(),'python':platform.python_version(),
                    'uv':'0.12.19', 'memory_total_mib':next((int(l.split()[1])/1024 for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemTotal:')),None)},
            'topology':['PostgreSQL','Redis'],
            'limitations':['Two-service topology excludes Foundation worker, Beat, scanner and MinIO background load',
                 'Separate fresh pytest databases; owned Redis reset before each pass',
                 'Source/observer comparisons retain order and host variation confounding'],
            'protected_branch_modified':False, 'local_unpublished_workspace_accessed':False}
        (OUT/'outcome.json').write_text(json.dumps(result,sort_keys=True)+'\n')
        write_manifest()
    return 0 if result['valid'] else 1


if __name__ == '__main__':
    if len(sys.argv)>1 and sys.argv[1]=='cleanup':
        clean = cleanup()
        path = OUT/'outcome.json'
        if path.exists():
            data=json.loads(path.read_text())
            update_cleanup_verdict(data, clean['verified'])
            path.write_text(json.dumps(data,sort_keys=True)+'\n')
        write_manifest()
        raise SystemExit(0 if clean['verified'] else 1)
    raise SystemExit(main())
