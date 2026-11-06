"""Offline control tests only. No application import, original pytest, Docker or git execution."""
import ast
import copy
import hashlib
import json
import os
from pathlib import Path
import shlex
import signal
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import types
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0,str(Path(__file__).parent))
import task07_abba_plugin as p
import task07_abba_probe as c


def metric(source='task6',index=1):
    labels={v for group in p.SPECS.values() for v in group.values()}
    resources={key:0.0 for key in p.RESOURCE_KEYS}
    resources.update(samples=1 if index else 0,sampling_error=False,min_mem_available_mib=15000.0 if index else None)
    phases=[]
    functions=[node.split('[',1)[0] for node in p.expected_ids()]
    if index:
        for occurrence,function in enumerate(functions):
            for phase in ('setup','call','teardown'):
                events={}
                operations={'other_sql':{'count':1,'seconds':.001}}
                if phase=='call' and occurrence==0:
                    events={key:dict(count=1,raised=0,inclusive_seconds=.001,self_excluding_labelled_children_seconds=.001) for key in ('corpus','candidate_query')}
                    operations={key:dict(count=1,seconds=.001) for key in p.BUCKETS}
                if phase=='call' and occurrence in (1,2):
                    events={key:dict(count=1,raised=0,inclusive_seconds=.001,self_excluding_labelled_children_seconds=.001) for key in labels-{'corpus','candidate_query'}}
                phases.append(dict(occurrence=occurrence,function=function,phase=phase,outcome='passed',wall_seconds=.1,
                    process_cpu_seconds=.05,main_thread_cpu_seconds=.04,
                    sql_count=sum(x['count'] for x in operations.values()),sql_seconds=sum(x['seconds'] for x in operations.values()),
                    wrapper_bookkeeping_cpu_seconds_lower_bound=.0001,lifecycle=events,sql_operations=operations))
    return dict(schema_version=1,group='four',source=source,source_sha=p.PINS[source][0],source_tree=p.PINS[source][1],
        pass_index=index,kind='measurement' if index else 'collection',complete=True,exit_code=0,mode='fixed' if index else 'minimal',
        collection=p.collection_record(p.expected_ids(),'four',source),
        collection_timing=dict(wall_seconds=.01,process_cpu_seconds=.005,main_thread_cpu_seconds=.005,failed=False),
        phases=phases,observer_errors=0,truncated=False,
        actual_pytest_python_version='3.13.15',actual_pytest_python_implementation='CPython',actual_pytest_package_version='9.1.1',
        session_wall_seconds=5.,session_process_cpu_seconds=3.,session_main_thread_cpu_seconds=2.9,
        wrapper_bookkeeping_cpu_seconds_lower_bound=.001,alias_installation_wall_seconds=.001,alias_restoration_wall_seconds=.001,
        fixed_callsite_labels=sorted(labels) if index else [],alias_bindings=8 if index else 0,resources=resources,limitations=p.LIMITATIONS)


class FakeCommands:
    """Models commands and files; never executes a subprocess or an application test."""
    def __init__(self,fail=None,corrupt=None,cleanup_fail=None,clock=None,advance=None):
        self.calls=[];self.fail=fail;self.corrupt=corrupt;self.cleanup_fail=cleanup_fail;self.clock=clock
        self.resources=dict(containers=0,networks=0,volumes=0)
        self.advance=advance
    def __call__(self,stage,args,*,cwd,timeout,env=None):
        self.calls.append((stage,list(args),timeout))
        if not p.number(timeout) or timeout<=4:raise c.Stop('deadline')
        if self.advance and stage==self.advance[0]:self.clock[0]+=self.advance[1]
        event=dict(stage=stage,exit_code=0,timed_out=False,truncated=False,wall_seconds=.01)
        data=b''
        if stage==self.fail:
            event['exit_code']=1;event['failure_class']='command_failed'
            return event,b'PRIVATE RAW FAILURE'
        if stage.startswith('owned_remove_') and stage.endswith(self.cleanup_fail or 'NO_MATCH'):
            event['exit_code']=1;event['failure_class']='command_failed';return event,b'PRIVATE CLEANUP'
        if stage=='uv_version':data=b'uv 0.12.19\n'
        elif stage=='private_credentials':
            values=dict(POSTGRES_DB='fitlink',POSTGRES_USER='fitlink',POSTGRES_PASSWORD='PRIVATE',POSTGRES_HOST='127.0.0.1',POSTGRES_PORT='5434',REDIS_HOST_PORT='6381',REDIS_URL='redis://127.0.0.1:6381/0',CELERY_BROKER_URL='redis://127.0.0.1:6381/1',CELERY_RESULT_BACKEND='redis://127.0.0.1:6381/2',CHANNEL_REDIS_URL='redis://127.0.0.1:6381/3')
            (c.STATE/'private.env').write_text(''.join(k+'='+v+'\n' for k,v in values.items()))
        elif stage=='services_start':self.resources=dict(containers=2,networks=1,volumes=2)
        elif stage=='service_status_private':
            data=b'\n'.join(json.dumps(dict(Service=s,State='running',Health='healthy',ExitCode=0)).encode() for s in ('db','redis'))
        elif stage.startswith('inventory_') or stage.startswith('cleanup_inventory_'):
            key=stage.rsplit('_',1)[1];data=b'\n'.join(('owned-'+key+str(i)).encode() for i in range(self.resources[key]))
        elif stage.startswith('owned_remove_'):self.resources[stage.rsplit('_',1)[1]]=0
        elif stage=='private_files_cleanup':
            for path in [*c.STATE.glob('pytest-tmp-*'),c.STATE/'pytest-cache',*c.STATE.glob('collection-*.json'),*c.STATE.glob('pass-*.json')]:
                if path.is_dir():shutil.rmtree(path)
                else:path.unlink(missing_ok=True)
        elif stage.startswith('collect_') or stage.startswith('pytest_pass_'):
            source=env['FITLINK_DIAG_SOURCE'];index=int(env['FITLINK_DIAG_PASS'])
            result=metric(source,index)
            if self.corrupt and index:result=self.corrupt(result)
            Path(env['FITLINK_DIAG_OUTPUT']).write_text(json.dumps(result))
            if self.clock is not None and stage=='pytest_pass_2':
                self.clock[0]+=901;event.update(exit_code=124,timed_out=True,failure_class='deadline')
        return event,data


class Harness(unittest.TestCase):
    def setUp(self):
        p.EVENTS.clear();p.WRAPPER_STACK.clear();p.SQL[:]=[0,0.0];p.SQL_CLASSES.clear();p.OBSERVER_ERRORS=0

    def test_manifest_has_four_functions_fourteen_cases_and_56_executions(self):
        self.assertEqual(c.CAP,56)
        self.assertEqual(c.PASSES,[('task6','fixed','four'),('task7','fixed','four'),('task7','fixed','four'),('task6','fixed','four')])
        self.assertEqual(list(p.SELECTIONS['four'].values()),[1,1,1,11])
        self.assertEqual(len(set(p.expected_ids())),14)
        self.assertEqual(sum(sum(p.SELECTIONS[g].values()) for _,_,g in c.PASSES),56)

    def test_manifest_matches_both_pinned_source_ast_without_import_or_execution(self):
        for source in ('task6','task7'):
            roots=[Path(__file__).resolve().parents[1]/'.runtime'/(source+'-source'),Path(__file__).resolve().parents[2]/'source-evidence'/source]
            root=next((x for x in roots if (x/'docker/c03_upgrade_probe_impl.py').is_file()),None)
            self.assertIsNotNone(root,'Pinned source AST evidence must be available for offline manifest proof')
            tree=ast.parse((root/'docker/c03_upgrade_probe_impl.py').read_text())
            node=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CAPABILITY_CASES' for t in n.targets))
            self.assertEqual(ast.literal_eval(node.value),p.CAPABILITY_CASES)
            counts=[]
            for selection in p.SELECTIONS['four']:
                path,name=selection.split('::');tree=ast.parse((root/path).read_text())
                fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
                decorators=[d for d in fn.decorator_list if isinstance(d,ast.Call) and isinstance(d.func,ast.Attribute) and d.func.attr=='parametrize']
                if decorators:
                    self.assertEqual(len(decorators),1);self.assertEqual(decorators[0].args[1].id,'CAPABILITY_CASES');counts.append(len(p.CAPABILITY_CASES))
                else:counts.append(1)
            self.assertEqual(counts,[1,1,1,11])

    def test_collection_accepts_only_exact_node_ids_group_source_and_order(self):
        ids=p.expected_ids()
        for source in p.PINS:
            good=p.collection_record(ids,'four',source);self.assertTrue(p.check_collection(good,source,True))
            for bad in [ids[:-1],ids+['PRIVATE'],[ids[0]]+ids[:-1],list(reversed(ids)),ids[:-1]+[ids[-1]+'altered']]:
                record=p.collection_record(bad,'four',source)
                self.assertFalse(record['exact']);self.assertFalse(p.check_collection(record,source,True))
                self.assertNotIn('PRIVATE',json.dumps(record))
            changed={**good,'digest':'0'*64};self.assertFalse(p.check_collection(changed,source,True))
        for group,source in [('new','task6'),('four','PRIVATE')]:
            with self.assertRaises(p.EvidenceError):p.collection_record(ids,group,source)

    def test_workflow_clock_writes_one_real_newline_and_round_trips(self):
        workflow=Path(__file__).resolve().parents[1]/'.github/workflows/c04-task07-abba-four.yml'
        line=next(l for l in workflow.read_text().splitlines() if 'FITLINK_PREPARATION_START=' in l)
        command=shlex.split(line.split('run: ',1)[1]);self.assertEqual(command[:2],['python','-c'])
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'env'
            subprocess.run([sys.executable,'-B','-c',command[2]],env={**os.environ,'GITHUB_ENV':str(path)},check=True,capture_output=True,timeout=5)
            data=path.read_bytes();self.assertTrue(data.endswith(b'\n'));self.assertEqual(data.count(b'\n'),1);self.assertNotIn(b'\\n',data)
            raw=data.decode().splitlines()[0].split('=',1)[1];self.assertLessEqual(c.parse_clock(raw,time.monotonic()),time.monotonic())

    def test_invalid_clocks_are_rejected(self):
        for raw in [None,'','NaN','inf','-1','0','100.01','90\\n','90\n','1e2','PRIVATE']:
            with self.subTest(raw=raw):
                with self.assertRaises(c.Stop):c.parse_clock(raw,100)
        with self.assertRaises(c.Stop):c.parse_clock('1',601)
        self.assertEqual(c.parse_clock('90',100),90)

    def test_precontroller_step_bounds_and_outer_watchdogs_reserve_cleanup(self):
        text=(Path(__file__).resolve().parents[1]/'.github/workflows/c04-task07-abba-four.yml').read_text()
        prefix=text.split('      - name: One bounded')[0]
        import re
        self.assertLessEqual(sum(map(int,re.findall(r'timeout-minutes: ([0-9]+)',prefix.split('steps:')[1])))*60,420)
        self.assertIn('timeout -k 125s 1500s',text);self.assertIn('timeout-minutes: 42',text)
        self.assertLess(420+1500+125+140+180,42*60)

    def test_wrappers_delegate_once_return_identity_and_exception_identity(self):
        calls=[];token=object();error=ValueError('PRIVATE')
        def original(*args,**kwargs):calls.append((args,kwargs));return token
        self.assertIs(p.timed('corpus',original)('PRIVATE',key='PRIVATE'),token);self.assertEqual(len(calls),1)
        def fail(*args):calls.append(None);raise error
        with self.assertRaises(ValueError) as caught:p.timed('corpus',fail)('PRIVATE')
        self.assertIs(caught.exception,error);self.assertEqual(len(calls),2);self.assertNotIn('PRIVATE',json.dumps(p.EVENTS))
        with patch.object(p.time,'thread_time',side_effect=ValueError('PRIVATE OBSERVER')):
            self.assertIs(p.timed('corpus',original)(),token)
        self.assertFalse(p.WRAPPER_STACK);self.assertGreater(p.OBSERVER_ERRORS,0)

    def test_wrapper_nested_self_time_and_worker_exclusion(self):
        child=p.timed('candidate_query',lambda:time.sleep(.001));outer=p.timed('corpus',child);outer()
        self.assertAlmostEqual(p.EVENTS['corpus']['inclusive_seconds']-p.EVENTS['corpus']['self_excluding_labelled_children_seconds'],p.EVENTS['candidate_query']['inclusive_seconds'],places=6)
        worker=threading.Thread(target=outer);worker.start();worker.join();self.assertEqual(p.EVENTS['corpus']['count'],1)

    def targets(self,fail=False):
        labels=sorted({x for d in p.SPECS.values() for x in d.values()}-{'corpus'})
        class Owner:
            def __setattr__(self,name,value):
                if fail and name=='op3' and hasattr(self,'op3') and value is not originals['op3']:raise RuntimeError('PRIVATE INSTALL FAILURE')
                object.__setattr__(self,name,value)
        owner=Owner();originals={}
        for index,label in enumerate(labels):
            def fn(*args,**kwargs):return args
            originals['op'+str(index)]=fn;setattr(owner,'op'+str(index),fn)
        return owner,originals,[(owner,'op'+str(index),label) for index,label in enumerate(labels)]

    def test_partial_installation_rolls_back_every_attempted_change(self):
        owner,originals,targets=self.targets(True)
        with patch.object(p,'class_targets',return_value=targets):
            with self.assertRaises(RuntimeError):p.install_aliases()
        for name,original in originals.items():self.assertIs(getattr(owner,name),original)

    def test_successful_installation_and_restoration(self):
        owner,originals,targets=self.targets()
        with patch.object(p,'class_targets',return_value=targets):records=p.install_aliases()
        self.assertEqual(len(records),8)
        for name,original in originals.items():self.assertIsNot(getattr(owner,name),original)
        self.assertTrue(p.restore_aliases(records))
        for name,original in originals.items():self.assertIs(getattr(owner,name),original)

    def test_fixture_restored_after_execution_and_observer_failure(self):
        original=lambda:object();item=types.SimpleNamespace(funcargs={'corpus':original})
        error=RuntimeError('PRIVATE APPLICATION ERROR')
        with patch.object(p,'MODE','fixed'),patch.object(p,'begin_phase'),patch.object(p,'end_phase',side_effect=ValueError('PRIVATE OBSERVER ERROR')):
            generator=p.pytest_runtest_call(item);next(generator);self.assertIsNot(item.funcargs['corpus'],original)
            with self.assertRaises(RuntimeError) as caught:generator.throw(error)
            self.assertIs(caught.exception,error)
        self.assertIs(item.funcargs['corpus'],original)

    def test_sql_delegation_classification_and_no_private_retention(self):
        calls=[];token=object();error=ValueError('PRIVATE SQL')
        def execute(*args):calls.append(args);return token
        for statement,label in [('CREATE TEMP TABLE marketplace_publicprofessionalprojection (x int)','fts_temp_create'),('INSERT INTO marketplace_publicprofessionalprojection SELECT 1','fts_insert_30000'),('ANALYZE marketplace_publicprofessionalprojection','fts_analyze'),('EXPLAIN SELECT 1','fts_explain'),('SELECT PRIVATE FROM secret','other_sql')]:
            self.assertEqual(p.sql_bucket(statement),label);self.assertIs(p.sql_wrapper(execute,statement,['PRIVATE'],False,{}),token)
        self.assertEqual(len(calls),5)
        def fail(*args):raise error
        with self.assertRaises(ValueError) as caught:p.sql_wrapper(fail,'PRIVATE SQL',None,False,{})
        self.assertIs(caught.exception,error);self.assertNotIn('PRIVATE',json.dumps(p.SQL_CLASSES))
        with patch.object(p,'sql_bucket',side_effect=RuntimeError('PRIVATE CLASSIFIER')):
            self.assertIs(p.sql_wrapper(execute,'PRIVATE',None,False,{}),token)

    def test_closed_metric_schema_and_all_pass_source_mappings(self):
        for index,source in enumerate(p.ORDER,1):
            value=metric(source,index);expected=p.collection_record(p.expected_ids(),'four',source)
            self.assertTrue(c.valid_metrics(value,expected,source,index))
            self.assertFalse(p.check_metrics(value,'task7' if source=='task6' else 'task6',index,True))
        self.assertTrue(p.check_metrics(metric('task6',0),'task6',0,True))

    def test_metric_failure_negative_counterexamples(self):
        good=metric()
        changes=[('source_sha','0'*40),('pass_index',2),('group','new'),('observer_errors',1),('exit_code',1),('complete',False),('truncated',True),('alias_bindings',0),('actual_pytest_python_version','3.12.3')]
        for key,value in changes:
            bad=copy.deepcopy(good);bad[key]=value;self.assertFalse(p.check_metrics(bad,'task6',1,True),key)
        for key,value in [('wall_seconds',float('nan')),('sql_count',-1),('sql_count',True),('sql_seconds',999),('function','PRIVATE'),('occurrence',99),('phase','PRIVATE')]:
            bad=copy.deepcopy(good);bad['phases'][1][key]=value;self.assertFalse(p.check_metrics(bad,'task6',1,True),key)
        for mutation in [lambda x:x['phases'].pop(),lambda x:x['phases'].append(copy.deepcopy(x['phases'][0])),lambda x:x['phases'][4]['lifecycle'].clear(),lambda x:x['resources'].update(sampling_error=True),lambda x:x['phases'][1]['sql_operations']['fts_explain'].update(count=2)]:
            bad=copy.deepcopy(good);mutation(bad);self.assertFalse(p.check_metrics(bad,'task6',1,True))

    def test_sensitive_field_injection_at_every_export_depth(self):
        good=metric()
        for location in [lambda x:x,lambda x:x['resources'],lambda x:x['collection'],lambda x:x['collection']['counts'],lambda x:x['phases'][1],lambda x:x['phases'][1]['lifecycle']['corpus'],lambda x:x['phases'][1]['sql_operations']['fts_explain']]:
            bad=copy.deepcopy(good);location(bad)['private_payload']='PRIVATE';self.assertFalse(p.check_metrics(bad,'task6',1,False))
        self.assertNotIn('PRIVATE',json.dumps(good))
        for text in ['{"x":1,"x":2}','{"wall":NaN}','{"wall":Infinity}']:
            with self.assertRaises(c.Stop):c.strict_json(text)

    def simulation(self,fail=None,corrupt=None,cleanup_fail=None,raw_clock='90',deadline=False,preexisting=False,advance=None):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);state=root/'private';out=root/'evidence';clock=[100.]
            commands=FakeCommands(fail,corrupt,cleanup_fail,clock if deadline or advance else None,advance)
            if preexisting:commands.resources['containers']=1
            def identity(source,deadline=None):return dict(head=p.PINS[source][0],tree=p.PINS[source][1],clean=True,locks={name:'a'*64 for name in c.LOCKS})
            env=dict(GITHUB_RUN_ID='123456',GITHUB_RUN_ATTEMPT='1',GITHUB_SHA='d'*40,FITLINK_PREPARATION_START=raw_clock)
            with patch.object(c,'ROOT',root),patch.object(c,'STATE',state),patch.object(c,'OUT',out),patch.object(c,'run_command',side_effect=commands),patch.object(c,'identity',side_effect=identity),patch.object(c,'git',return_value='c'*40),patch.object(c.time,'monotonic',side_effect=lambda:clock[0]),patch.dict(os.environ,env),patch.object(c.subprocess,'run',side_effect=AssertionError('Unexpected external process in controller simulation')):
                code=c.main();outcome=json.loads((out/'outcome.json').read_text());cleanup=json.loads((out/'cleanup.json').read_text())
                self.assertTrue(c.check_outcome(outcome));self.assertTrue(c.check_cleanup(cleanup))
                self.assertFalse((state/'private.env').exists())
                self.assertNotIn('PRIVATE',''.join(path.read_text() for path in out.glob('*.json')))
                safe_bytes={path.name:path.read_text() for path in out.iterdir()}
                return code,outcome,cleanup,commands.calls,safe_bytes

    def test_mocked_successful_ABBA_controller(self):
        code,outcome,cleanup,calls,files=self.simulation()
        self.assertEqual(code,0);self.assertTrue(outcome['valid']);self.assertTrue(cleanup['verified'])
        self.assertEqual([row['source'] for row in outcome['passes']],list(p.ORDER))
        self.assertEqual(sum(row['count'] for row in outcome['passes']),56)
        self.assertEqual(len([x for x in calls if x[0].startswith('pytest_pass_')]),4)
        self.assertEqual(len([x for x in calls if x[0].startswith('collect_')]),2)
        self.assertTrue(all(timeout<=240 for stage,args,timeout in calls if stage.startswith('pytest_')))
        self.assertTrue({'pass-1.json','pass-2.json','pass-3.json','pass-4.json'}<=set(files))

    def test_mocked_failed_preparation_does_not_start_pytest(self):
        code,outcome,cleanup,calls,_=self.simulation(fail='task6_frozen_sync')
        self.assertEqual(code,1);self.assertFalse(outcome['valid']);self.assertEqual(outcome['measurement_state'],'not_started')
        self.assertFalse(any(stage.startswith('pytest_pass_') for stage,_,_ in calls));self.assertTrue(cleanup['verified'])

    def test_invalid_clock_produces_explicit_failed_evidence(self):
        code,outcome,cleanup,calls,_=self.simulation(raw_clock='90\\n')
        self.assertEqual(code,1);self.assertEqual(outcome['failure_class'],'invalid_clock')
        self.assertFalse(any(stage in ('services_start','private_credentials') for stage,_,_ in calls))

    def test_mocked_failed_second_pass_keeps_first_pass_and_stops(self):
        code,outcome,cleanup,calls,files=self.simulation(fail='pytest_pass_2')
        self.assertEqual(code,1);self.assertFalse(outcome['valid']);self.assertEqual(len(outcome['passes']),1)
        self.assertIn('pass-1.json',files);self.assertNotIn('pass-3.json',files)
        self.assertFalse(any(stage=='pytest_pass_3' for stage,_,_ in calls));self.assertTrue(cleanup['verified'])

    def test_private_metric_is_never_exported(self):
        def corrupt(value):value['private_payload']='PRIVATE';return value
        code,outcome,_,_,files=self.simulation(corrupt=corrupt)
        self.assertEqual(code,1);self.assertEqual(outcome['failure_class'],'evidence_schema_failure');self.assertNotIn('pass-1.json',files)

    def test_partial_cleanup_failure_attempts_other_categories_and_stays_failed(self):
        code,outcome,cleanup,calls,_=self.simulation(cleanup_fail='containers')
        self.assertEqual(code,1);self.assertFalse(cleanup['verified']);self.assertFalse(outcome['valid'])
        self.assertTrue(any(stage=='owned_remove_networks' for stage,_,_ in calls));self.assertTrue(any(stage=='owned_remove_volumes' for stage,_,_ in calls))
        self.assertIn('containers',cleanup['errors'])
        copy_outcome=copy.deepcopy(outcome);c.update_cleanup_verdict(copy_outcome,True);self.assertFalse(copy_outcome['valid'])

    def test_measurement_deadline_stops_before_third_pass(self):
        code,outcome,cleanup,calls,_=self.simulation(deadline=True)
        self.assertEqual(code,1);self.assertEqual(outcome['failure_class'],'deadline')
        self.assertFalse(any(stage=='pytest_pass_3' for stage,_,_ in calls));self.assertTrue(cleanup['verified'])

    def test_outcome_and_cleanup_closed_schemas_reject_sensitive_fields(self):
        _,value,clean,_,_=self.simulation()
        for target in [lambda x:x,lambda x:x['host'],lambda x:x['sources_before']['task6'],lambda x:x['sources_before']['task6']['locks'],lambda x:x['passes'][0],lambda x:x['stages'][0]]:
            bad=copy.deepcopy(value);target(bad)['private_payload']='PRIVATE';self.assertFalse(c.check_outcome(bad))
        self.assertFalse(c.check_cleanup({**clean,'private_payload':'PRIVATE'}))

    def test_not_started_outcome_cannot_become_success_from_cleanup(self):
        clean=dict(verified=True,resources_after=dict(containers=0,networks=0,volumes=0),private_files_removed=True,owned_resources_created=False,wall_seconds=.1,errors=[])
        with patch.dict(os.environ,{'FITLINK_HARNESS_OUTCOME':'failure'}):value=c.not_started_outcome(clean)
        self.assertTrue(c.check_outcome(value));self.assertEqual(value['failure_class'],'offline_harness_failed')
        c.update_cleanup_verdict(value,True);self.assertFalse(value['valid'])

    def test_cancellation_kills_and_reaps_process_group(self):
        child=MagicMock(pid=12345);error=KeyboardInterrupt();child.wait.side_effect=[error,-9]
        with tempfile.TemporaryDirectory() as directory,patch.object(c.subprocess,'Popen',return_value=child),patch.object(c.os,'killpg') as kill:
            with self.assertRaises(KeyboardInterrupt) as caught:c.run_command('uv_version',['PRIVATE'],cwd=Path(directory),timeout=5)
            self.assertIs(caught.exception,error);kill.assert_called_once_with(12345,signal.SIGKILL);self.assertEqual(child.wait.call_count,2)

    def test_real_offline_command_failure_and_timeout_are_sanitized(self):
        with tempfile.TemporaryDirectory() as directory:
            event,data=c.run_command('uv_version',[sys.executable,'-B','-c',"print('PRIVATE');raise SystemExit(2)"],cwd=Path(directory),timeout=5)
            self.assertEqual(event['exit_code'],2);self.assertNotIn('PRIVATE',json.dumps(event))
            event,_=c.run_command('uv_version',[sys.executable,'-B','-c','import time;time.sleep(10)'],cwd=Path(directory),timeout=4.5)
            self.assertTrue(event['timed_out']);self.assertLess(event['wall_seconds'],4.5)

    def test_no_global_profiler_transaction_or_remote_mutation_commands(self):
        tree=ast.parse(Path(p.__file__).read_text());forbidden={'setprofile','settrace','atomic','commit','rollback','set_autocommit'}
        self.assertFalse([node for node in ast.walk(tree) if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr in forbidden])
        text=Path(c.__file__).read_text();self.assertNotIn('git commit',text);self.assertNotIn('git push',text)
        self.assertEqual(p.sql_bucket('SELECT PRIVATE FROM secret'),'other_sql')

    def test_ownership_conflict_never_removes_preexisting_resources(self):
        code,value,clean,calls,_=self.simulation(preexisting=True)
        self.assertEqual(code,1);self.assertEqual(value['failure_class'],'ownership_conflict')
        self.assertFalse(clean['owned_resources_created']);self.assertEqual(clean['resources_after']['containers'],1)
        self.assertFalse(any(stage.startswith('owned_remove_') or stage=='services_start' for stage,_,_ in calls))

    def test_preparation_deadline_stops_before_services_or_collection(self):
        code,value,_,calls,_=self.simulation(advance=('task6_frozen_sync',601))
        self.assertEqual(code,1);self.assertEqual(value['failure_class'],'deadline')
        self.assertFalse(any(stage.startswith('collect_') or stage=='services_start' for stage,_,_ in calls))

    def test_source_identity_rejects_wrong_sha_dirty_state_and_changed_locks(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);source=root/'.runtime/task6-source';source.mkdir(parents=True)
            for name in c.LOCKS:(source/name).write_text('frozen')
            def git(path,*args,**kwargs):
                if args==('rev-parse','HEAD'):return p.PINS['task6'][0]
                if args==('rev-parse','HEAD^{tree}'):return p.PINS['task6'][1]
                return ''
            with patch.object(c,'ROOT',root),patch.object(c,'git',side_effect=git):
                before=c.identity('task6');(source/'uv.lock').write_text('changed');after=c.identity('task6')
                self.assertNotEqual(before['locks'],after['locks'])
            with patch.object(c,'ROOT',root),patch.object(c,'git',return_value='0'*40):
                with self.assertRaises(c.Stop):c.identity('task6')
            def dirty(path,*args,**kwargs):return ' M uv.lock' if args[0]=='status' else git(path,*args,**kwargs)
            with patch.object(c,'ROOT',root),patch.object(c,'git',side_effect=dirty):
                with self.assertRaises(c.Stop):c.identity('task6')

    def test_class_method_descriptor_and_return_semantics(self):
        calls=[];token=object();error=ValueError('PRIVATE')
        class Model:
            def __init__(self,marker):calls.append(('init',marker))
            def operation(self,marker):calls.append(('operation',marker));return token
            def failed(self):raise error
        original_init=Model.__init__;original_op=Model.operation;original_failed=Model.failed
        Model.__init__=p.timed('migration_executor_init',original_init)
        Model.operation=p.timed('migration_execute',original_op);Model.failed=p.timed('migration_apply',original_failed)
        try:
            marker=object();obj=Model(marker);self.assertIs(obj.operation(marker),token)
            self.assertEqual(calls,[('init',marker),('operation',marker)])
            with self.assertRaises(ValueError) as caught:obj.failed()
            self.assertIs(caught.exception,error)
        finally:Model.__init__=original_init;Model.operation=original_op;Model.failed=original_failed

    def test_parent_wait_timeout_is_reaped_with_bounded_wait(self):
        child=MagicMock(pid=12345);child.wait.side_effect=[subprocess.TimeoutExpired('PRIVATE',5),-9]
        with tempfile.TemporaryDirectory() as directory,patch.object(c.subprocess,'Popen',return_value=child),patch.object(c.os,'killpg') as kill:
            event,_=c.run_command('uv_version',['PRIVATE'],cwd=Path(directory),timeout=5)
            self.assertTrue(event['timed_out']);kill.assert_called_once_with(12345,signal.SIGKILL)
            self.assertLessEqual(child.wait.call_args.kwargs['timeout'],1)

    def test_clock_failure_still_erases_preexisting_private_credentials(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);state=root/'private';out=root/'evidence';state.mkdir();(state/'private.env').write_text('PRIVATE')
            commands=FakeCommands()
            with patch.object(c,'ROOT',root),patch.object(c,'STATE',state),patch.object(c,'OUT',out),patch.object(c,'run_command',side_effect=commands),patch.object(c,'git',return_value='c'*40),patch.object(c,'identity',side_effect=c.Stop('source_identity_mismatch')),patch.dict(os.environ,{'FITLINK_PREPARATION_START':'NaN','GITHUB_SHA':'d'*40,'GITHUB_RUN_ATTEMPT':'1'}):
                self.assertEqual(c.main(),1)
            self.assertFalse((state/'private.env').exists());self.assertEqual(json.loads((out/'outcome.json').read_text())['failure_class'],'invalid_clock')

    def test_malformed_shapes_fail_closed_without_exceptions(self):
        examples=[None,True,False,1,'PRIVATE',[],[{}],{'private_payload':'PRIVATE'}]
        for value in examples:
            self.assertFalse(p.check_metrics(value,'task6',1));self.assertFalse(c.check_outcome(value));self.assertFalse(c.check_cleanup(value));self.assertFalse(c.check_services(value));self.assertFalse(c.check_stage(value))
        value=metric();value['resources']['samples']=True;self.assertFalse(p.check_metrics(value,'task6',1,True))

    def test_private_service_fields_are_sanitized_and_bad_health_is_not_accepted(self):
        event=dict(stage='service_status_private',exit_code=0,timed_out=False,truncated=False,wall_seconds=.01)
        raw=json.dumps([dict(Service='db',State='running',Health='healthy',ExitCode=0,PRIVATE_PASSWORD='PRIVATE'),dict(Service='redis',State='running',Health='healthy',ExitCode=0,Command='PRIVATE')]).encode()
        with patch.object(c,'run_command',return_value=(event,raw)):
            result=c.safe_service_states(time.monotonic()+20,{})
        self.assertTrue(c.check_services(result));self.assertNotIn('PRIVATE',json.dumps(result));self.assertEqual(len(result['services']),2)
        with patch.object(c,'run_command',return_value=(event,b'PRIVATE invalid JSON')):
            result=c.safe_service_states(time.monotonic()+20,{})
        self.assertFalse(result['available']);self.assertNotIn('PRIVATE',json.dumps(result))

    def test_private_files_deleted_even_when_inventory_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            state=Path(directory)/'private';out=Path(directory)/'out';state.mkdir();(state/'private.env').write_text('PRIVATE')
            with patch.object(c,'STATE',state),patch.object(c,'OUT',out),patch.object(c,'execute',side_effect=c.Stop('command_failed')):
                result=c.cleanup()
            self.assertFalse(result['verified']);self.assertFalse((state/'private.env').exists());self.assertIn('inventory',result['errors'])

    def test_expired_cleanup_clock_does_not_reset_budget(self):
        with tempfile.TemporaryDirectory() as directory:
            state=Path(directory)/'private';out=Path(directory)/'out';state.mkdir();(state/'cleanup-start').write_text(str(time.monotonic()-121));(state/'private.env').write_text('PRIVATE')
            with patch.object(c,'STATE',state),patch.object(c,'OUT',out):
                with patch.object(c.subprocess,'Popen',side_effect=AssertionError('No command may start after cleanup deadline')):
                    result=c.cleanup()
            self.assertFalse(result['verified']);self.assertIn('deadline',result['errors']);self.assertFalse((state/'private.env').exists())

    def test_deleted_instrumented_attribute_is_still_restored(self):
        owner,originals,targets=self.targets()
        with patch.object(p,'class_targets',return_value=targets):records=p.install_aliases()
        delattr(owner,'op0');p.restore_aliases(records)
        for name,original in originals.items():self.assertIs(getattr(owner,name),original)

    def test_artifact_manifest_rejects_unknown_json_and_uses_exact_upload_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            out=Path(directory)/'evidence';out.mkdir()
            clean=dict(verified=True,resources_after=dict(containers=0,networks=0,volumes=0),private_files_removed=True,owned_resources_created=False,wall_seconds=.1,errors=[])
            with patch.object(c,'OUT',out):
                (out/'cleanup.json').write_text(json.dumps(clean));c.publish_outcome(c.not_started_outcome(clean))
                (out/'private-raw.json').write_text('{"private_payload":"PRIVATE"}')
                self.assertFalse(c.write_manifest())
                self.assertNotIn('private-raw.json',(out/'SHA256SUMS.txt').read_text())
                result=json.loads((out/'outcome.json').read_text());self.assertEqual(result['failure_class'],'evidence_schema_failure');self.assertFalse(result['valid'])
        workflow=(Path(__file__).resolve().parents[1]/'.github/workflows/c04-task07-abba-four.yml').read_text()
        self.assertNotIn('*.json',workflow)


class EvidenceIntegrity(unittest.TestCase):
    """Real finalization of synthetic evidence; no service or application calls."""
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.out=Path(self.directory.name)
        self.output_patch=patch.object(c,'OUT',self.out)
        self.output_patch.start();self.addCleanup(self.output_patch.stop)
        self.clean=dict(verified=True,resources_after=dict(containers=0,networks=0,volumes=0),
            private_files_removed=True,owned_resources_created=True,wall_seconds=.1,errors=[])
        identities={name:dict(head=p.PINS[name][0],tree=p.PINS[name][1],clean=True,
            locks={lock:'a'*64 for lock in c.LOCKS}) for name in p.PINS}
        self.outcome=c.not_started_outcome(self.clean)
        self.outcome.update(control_sha='c'*40,control_tree='d'*40,attempt=1,
            sources_before=identities,sources_after=copy.deepcopy(identities),sources_and_locks_preserved=True,
            collections={name+'_four':metric(name,0)['collection'] for name in p.PINS},
            measurement_state='complete',measurement_seconds=20.,measurements_complete=True,valid=True,failure_class=None)
        self.outcome['host']['uv']='0.12.19'
        self.metrics={i:metric(source,i) for i,source in enumerate(p.ORDER,1)}
        self.outcome['passes']=[{'pass':i,'source':source,'observer':'fixed','selection':'four','count':14,
            'valid':True,'session_wall_seconds':5.} for i,source in enumerate(p.ORDER,1)]
        self.save()

    def save(self):
        (self.out/'cleanup.json').write_text(json.dumps(self.clean))
        (self.out/'outcome.json').write_text(json.dumps(self.outcome))
        for i,value in self.metrics.items():(self.out/f'pass-{i}.json').write_text(json.dumps(value))

    def sealed_failure(self):
        self.assertFalse(c.write_manifest())
        value=json.loads((self.out/'outcome.json').read_text())
        self.assertTrue(c.check_outcome(value));self.assertFalse(value['valid'])
        self.assertIsNotNone(value['failure_class'])
        self.assertTrue((self.out/'SHA256SUMS.txt').is_file())
        return value

    def test_missing_pass_two_invalidates_success(self):
        (self.out/'pass-2.json').unlink();self.sealed_failure()

    def test_missing_cleanup_invalidates_success(self):
        (self.out/'cleanup.json').unlink();self.sealed_failure()

    def test_failing_pass_one_invalidates_success_and_is_preserved(self):
        self.metrics[1].update(complete=False,exit_code=1);self.save()
        self.assertTrue(p.check_metrics(self.metrics[1],'task6',1,False))
        self.sealed_failure();self.assertEqual(json.loads((self.out/'pass-1.json').read_text()),self.metrics[1])

    def test_every_missing_mandatory_artifact_fails_closed(self):
        for name in ('outcome.json','cleanup.json',*(f'pass-{i}.json' for i in range(1,5))):
            with self.subTest(name=name):
                self.save();(self.out/name).unlink();self.sealed_failure()

    def test_empty_directory_emits_explicit_failed_outcome(self):
        for path in self.out.iterdir():path.unlink()
        self.sealed_failure()

    def test_pass_summary_wall_time_must_match_artifact(self):
        self.outcome['passes'][0]['session_wall_seconds']=6.;self.save();self.sealed_failure()

    def test_pass_summary_verdict_must_match_artifact_even_on_failure(self):
        self.outcome.update(valid=False,failure_class='cleanup_failed')
        self.metrics[1].update(complete=False,exit_code=1);self.save();self.sealed_failure()

    def test_cleanup_claim_must_match_cleanup_artifact(self):
        self.clean.update(verified=False,errors=['containers']);self.save();self.sealed_failure()

    def test_failed_phase_cannot_support_success(self):
        self.metrics[1]['phases'][0]['outcome']='failed';self.save();self.sealed_failure()

    def test_incomplete_observation_cannot_support_success(self):
        for key,value in (('complete',False),('observer_errors',1),('truncated',True)):
            with self.subTest(key=key):
                self.metrics[1]=metric();self.metrics[1][key]=value;self.save();self.sealed_failure()

    def test_malformed_artifact_excluded_from_manifest(self):
        for text in ('{','{"complete":true,"complete":false}', '{"secret":NaN}'):
            self.save();(self.out/'pass-1.json').write_text(text);self.sealed_failure()
            self.assertFalse((self.out/'pass-1.json').exists())
            self.assertNotIn('pass-1.json',(self.out/'SHA256SUMS.txt').read_text())

    def test_complete_bundle_seals_all_six_artifacts_with_exact_hashes(self):
        self.assertTrue(c.write_manifest());self.assertTrue(json.loads((self.out/'outcome.json').read_text())['valid'])
        lines=(self.out/'SHA256SUMS.txt').read_text().splitlines();self.assertEqual(len(lines),6)
        for line in lines:
            digest,name=line.split('  ');self.assertEqual(digest,hashlib.sha256((self.out/name).read_bytes()).hexdigest())

    def test_failed_second_pass_preserves_partial_evidence_and_failure(self):
        self.outcome.update(valid=False,failure_class='pytest_failed_or_incomplete',measurements_complete=False,
            measurement_state='partial',passes=self.outcome['passes'][:1])
        self.metrics={1:self.metrics[1],2:self.metrics[2]};self.metrics[2].update(complete=False,exit_code=1)
        for i in (3,4):(self.out/f'pass-{i}.json').unlink()
        self.save();self.assertTrue(c.write_manifest())
        result=json.loads((self.out/'outcome.json').read_text())
        self.assertEqual(result,self.outcome);self.assertFalse(result['valid'])
        self.assertEqual(json.loads((self.out/'pass-2.json').read_text()),self.metrics[2])

    def test_not_started_needs_no_pass_files_and_stays_failed(self):
        for i in range(1,5):(self.out/f'pass-{i}.json').unlink()
        self.outcome=c.not_started_outcome(self.clean);self.metrics={};self.save()
        self.assertTrue(c.write_manifest());self.assertEqual(json.loads((self.out/'outcome.json').read_text()),self.outcome)

    def test_original_failure_reason_survives_integrity_failure(self):
        self.outcome.update(valid=False,failure_class='cleanup_failed');self.save()
        (self.out/'pass-2.json').unlink()
        self.assertEqual(self.sealed_failure()['failure_class'],'cleanup_failed')

    def test_not_started_cannot_claim_measurements_or_passes(self):
        for change in ({'measurement_state':'not_started'}, {'measurement_state':'partial'}):
            value=copy.deepcopy(self.outcome);value.update(change)
            self.assertFalse(c.check_outcome(value))

    def test_mocked_complete_four_pass_diagnostic_still_succeeds(self):
        # Linux host metadata is a fixture only for this wholly mocked controller.
        original=Path.read_text
        def read(path,*args,**kwargs):
            return 'MemTotal: 20480000 kB\n' if path==Path('/proc/meminfo') else original(path,*args,**kwargs)
        with patch.object(Path,'read_text',read):
            code,outcome,clean,calls,files=Harness().simulation()
        self.assertEqual(code,0);self.assertTrue(outcome['valid']);self.assertTrue(clean['verified'])
        self.assertEqual([row['source'] for row in outcome['passes']],list(p.ORDER))
        self.assertEqual(sum(row['count'] for row in outcome['passes']),56)
        self.assertEqual(len([stage for stage,_,_ in calls if stage.startswith('pytest_pass_')]),4)
        self.assertEqual(len([name for name in files if name.startswith('pass-')]),4)

    def test_tampered_source_digest_manifest_and_phase_mapping_fail_closed(self):
        mutations=[lambda value:value.update(source_sha='0'*40),
            lambda value:value['collection'].update(digest='0'*64),
            lambda value:value['collection'].update(total=13),
            lambda value:value['phases'].pop(),
            lambda value:value['phases'][0].update(occurrence=13)]
        for mutate in mutations:
            with self.subTest(mutation=mutations.index(mutate)):
                self.metrics[1]=metric();mutate(self.metrics[1]);self.save();self.sealed_failure()

    def test_reordered_outcome_passes_cannot_be_successful(self):
        self.outcome['passes'].reverse();self.save();self.sealed_failure()

    def test_cleanup_failure_with_complete_measurements_stays_failed(self):
        self.clean.update(verified=False,errors=['containers'])
        self.outcome.update(valid=False,cleanup_verified=False,failure_class='cleanup_failed')
        self.save();self.assertTrue(c.write_manifest())
        self.assertEqual(json.loads((self.out/'outcome.json').read_text()),self.outcome)

    def test_controller_returns_failure_when_finalization_loses_pass_two(self):
        original_read=Path.read_text;original_seal=c.write_manifest
        def read(path,*args,**kwargs):
            return 'MemTotal: 20480000 kB\n' if path==Path('/proc/meminfo') else original_read(path,*args,**kwargs)
        def seal():
            (c.OUT/'pass-2.json').unlink()
            return original_seal()
        with patch.object(Path,'read_text',read),patch.object(c,'write_manifest',side_effect=seal):
            code,outcome,clean,calls,files=Harness().simulation()
        self.assertEqual(code,1);self.assertFalse(outcome['valid'])
        self.assertEqual(outcome['failure_class'],'evidence_schema_failure')
        self.assertNotIn('pass-2.json',files)


if __name__=='__main__':unittest.main()
