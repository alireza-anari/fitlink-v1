"""Dependency-free diagnostic harness, outside the original pytest selection."""
import ast
import importlib.util
import json
import subprocess
import sys
import tempfile
import time
import types
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent))


class Harness(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec('task07_abba_plugin'), 'observer is required')
        import task07_abba_plugin as p
        import task07_abba_probe as c
        self.p,self.c=p,c
        p.EVENTS.clear();p.WRAPPER_STACK.clear()

    def metrics(self,mode='minimal'):
        ids=[f'{k}[{n}]' for k,num in self.p.SELECTIONS['four'].items() for n in range(num)]
        collection=self.p.collection_record(ids,'four')
        functions=[key for key,count in self.p.SELECTIONS['four'].items() for _ in range(count)]
        phases=[dict(occurrence=i,function=functions[i],phase=phase,outcome='passed',wall_seconds=.1,
            process_cpu_seconds=.02,main_thread_cpu_seconds=.01,sql_count=1 if mode=='fixed' else None,
            sql_seconds=.001 if mode=='fixed' else None,wrapper_bookkeeping_cpu_seconds_lower_bound=.0001 if mode=='fixed' else None,
            sql_operations={'other_sql':{'count':1,'seconds':.001}} if mode=='fixed' else {},
            lifecycle={}) for i in range(4) for phase in ('setup','call','teardown')]
        labels=[label for group in self.p.SPECS.values() for label in group.values()]
        if mode=='fixed':
            phases[1]['lifecycle']={label:dict(count=1,raised=0,inclusive_seconds=.001,self_excluding_labelled_children_seconds=.001) for label in labels}
        return collection,dict(complete=True,exit_code=0,collection=collection,observer_errors=0,truncated=False,
            actual_pytest_python_version='3.13.15',mode=mode,alias_bindings=len(labels) if mode=='fixed' else 0,
            resources={'samples':1 if mode=='fixed' else 0},fixed_callsite_labels=labels if mode=='fixed' else [],
            session_wall_seconds=2.,session_process_cpu_seconds=.5,session_main_thread_cpu_seconds=.4,phases=phases)

    def test_exact_two_pass_manifest(self):
        self.assertEqual(self.c.CAP,16)
        self.assertEqual(self.c.PASSES,[('task6','fixed','four'),('task7','fixed','four'),
                                        ('task7','fixed','four'),('task6','fixed','four')])
        self.assertEqual(sorted(self.p.SELECTIONS['four'].values()),[1,1,1,1])
        ids=[f'{k}[{n}]' for k,num in self.p.SELECTIONS['four'].items() for n in range(num)]
        record=self.p.collection_record(ids,'four')
        self.assertTrue(record['exact'])
        self.assertFalse(self.p.collection_record(ids[:-1],'new')['exact'])
        self.assertFalse(self.p.collection_record(ids+['PRIVATE'],'new')['exact'])
        self.assertNotIn('PRIVATE',json.dumps(self.p.collection_record(ids+['PRIVATE'],'new')))

    def test_wrapper_delegates_once_and_preserves_identity(self):
        calls=[];token=object();error=ValueError('PRIVATE')
        def original(*args,**kwargs):
            calls.append((args,kwargs));return token
        wrapped=self.p.timed('approval',original)
        self.assertIs(wrapped('PRIVATE',secret='PRIVATE'),token)
        self.assertEqual(len(calls),1)
        def fail(*args,**kwargs):
            calls.append(None);raise error
        with self.assertRaises(ValueError) as caught:
            self.p.timed('approval',fail)('PRIVATE')
        self.assertIs(caught.exception,error)
        self.assertEqual(len(calls),2)
        self.assertNotIn('PRIVATE',json.dumps(self.p.EVENTS))

    def test_nested_self_time_is_non_overlapping_and_workers_excluded(self):
        import threading
        child=self.p.timed('post_image',lambda:time.sleep(.002))
        parent=self.p.timed('post_publication',lambda:child())
        parent()
        event=self.p.EVENTS['post_publication']
        self.assertEqual(event['count'],1)
        self.assertAlmostEqual(event['inclusive_seconds']-event['self_excluding_labelled_children_seconds'],self.p.EVENTS['post_image']['inclusive_seconds'],places=5)
        worker=threading.Thread(target=parent);worker.start();worker.join()
        self.assertEqual(event['count'],1)
        self.assertFalse(self.p.WRAPPER_STACK)

    def test_alias_patching_and_restore_do_not_double_delegate(self):
        calls=[]
        def original(): calls.append(1);return 3
        one=types.SimpleNamespace(call=original)
        two=types.SimpleNamespace(alias=original)
        records=self.p.bind_aliases([one,two],{original:self.p.timed('approval',original)})
        self.assertEqual(one.call(),3);self.assertEqual(two.alias(),3)
        self.assertEqual(len(calls),2)
        self.assertEqual(self.p.EVENTS['approval']['count'],2)
        self.p.restore_aliases(records)
        self.assertIs(one.call,original);self.assertIs(two.alias,original)

    def test_sql_is_pure_delegation_and_exceptions_survive(self):
        calls=[];token=object();error=RuntimeError('PRIVATE SQL')
        def execute(*args):calls.append(args);return token
        self.assertIs(self.p.sql_wrapper(execute,'PRIVATE SQL',['PRIVATE'],False,{}),token)
        self.assertEqual(len(calls),1)
        def fail(*args):raise error
        with self.assertRaises(RuntimeError) as caught:self.p.sql_wrapper(fail,'PRIVATE',None,False,{})
        self.assertIs(caught.exception,error)
        self.assertNotIn('PRIVATE',json.dumps(self.p.EVENTS))

    def test_fixed_search_statement_classes_have_no_sql_text(self):
        p=self.p
        cases=[
            ('CREATE TEMP TABLE marketplace_publicprofessionalprojection (id int)','fts_temp_create'),
            (' INSERT INTO marketplace_publicprofessionalprojection SELECT 1','fts_insert_30000'),
            ('ANALYZE marketplace_publicprofessionalprojection','fts_analyze'),
            ('EXPLAIN (ANALYZE, BUFFERS) SELECT 1','fts_explain'),
            ('SELECT PRIVATE_PASSWORD FROM secret','other_sql'),
        ]
        for statement, label in cases:
            self.assertEqual(p.sql_bucket(statement),label)
        self.assertNotIn('PRIVATE_PASSWORD',json.dumps(p.SQL_CLASSES))

    def test_startup_classifier_only_exports_allowlisted_categories(self):
        evidence=self.c.startup_classifier(b'PRIVATE secret; dependency failed because port is already allocated')
        self.assertEqual(evidence,['port_collision'])
        self.assertNotIn('PRIVATE',json.dumps(evidence))
        self.assertEqual(self.c.startup_classifier(b'PRIVATE secrets without known category'),['unclassified'])

    def test_failure_incompleteness_and_cleanup_never_pass(self):
        collection,good=self.metrics()
        self.assertTrue(self.c.valid_metrics(good,collection))
        for key,value in [('complete',False),('exit_code',1),('observer_errors',1),('truncated',True)]:
            bad={**good,key:value};self.assertFalse(self.c.valid_metrics(bad,collection))
        self.assertFalse(self.c.valid_metrics({**good,'phases':good['phases'][:-1]},collection))
        data=dict(valid=False,cleanup_verified=False,measurements_complete=True,sources_and_locks_preserved=True)
        self.c.update_cleanup_verdict(data,True)
        self.assertFalse(data['valid'])
        self.assertFalse(self.c.final_valid(True,False,True))

    def test_no_global_profiler_or_trace_or_transactions(self):
        path=Path(self.p.__file__)
        tree=ast.parse(path.read_text())
        forbidden={'setprofile','settrace','atomic','commit','rollback','set_autocommit'}
        self.assertFalse([n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in forbidden])

    def test_command_failure_and_cancellation_remain_private(self):
        with tempfile.TemporaryDirectory() as d:
            event,data=self.c.run_command('harness',[sys.executable,'-c',"print('PRIVATE');raise SystemExit(2)"],cwd=Path(d),timeout=5)
            self.assertEqual(event['exit_code'],2);self.assertNotIn('PRIVATE',json.dumps(event))
            child=MagicMock(pid=12345);child.wait.side_effect=[KeyboardInterrupt(),-9]
            with patch.object(self.c.subprocess,'Popen',return_value=child),patch.object(self.c.os,'killpg') as kill:
                with self.assertRaises(KeyboardInterrupt):self.c.run_command('harness',['PRIVATE'],cwd=Path(d),timeout=5)
                kill.assert_called_once_with(12345,self.c.signal.SIGKILL)

    def test_cleanup_failure_erases_credentials_and_fails(self):
        with tempfile.TemporaryDirectory() as d:
            state=Path(d)/'private';out=Path(d)/'evidence';state.mkdir()
            (state/'owned').touch();(state/'private.env').write_text('PRIVATE')
            with patch.object(self.c,'STATE',state),patch.object(self.c,'OUT',out),patch.object(self.c,'execute',side_effect=RuntimeError('PRIVATE')):
                result=self.c.cleanup()
            self.assertFalse(result['verified']);self.assertFalse((state/'private.env').exists())
            self.assertNotIn('PRIVATE',(out/'cleanup.json').read_text())

    def test_source_and_lock_mutation_are_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'.runtime/task7-source';source.mkdir(parents=True)
            for name in self.c.LOCKS:(source/name).write_text('pinned')
            def git(*args):
                return subprocess.run(['git','-C',str(source),*args],check=True,capture_output=True,text=True).stdout.strip()
            git('init','-q');git('add','.')
            git('-c','user.name=Diagnostic','-c','user.email=diagnostic@example.invalid','commit','-qm','fixture')
            pins={'task7':(git('rev-parse','HEAD'),git('rev-parse','HEAD^{tree}'))}
            with patch.object(self.c,'ROOT',root),patch.object(self.c,'PINS',pins):
                self.assertTrue(self.c.identity('task7')['clean'])
                (source/'uv.lock').write_text('modified')
                with self.assertRaises(self.c.Stop):self.c.identity('task7')

    def test_fixed_observer_cannot_pass_without_callsite_activity(self):
        collection,good=self.metrics('fixed')
        self.assertTrue(self.c.valid_metrics(good,collection,'fixed'))
        for key,value in [('alias_bindings',0),('resources',{'samples':0}),('resources',{'samples':1,'sampling_error':True}),('fixed_callsite_labels',[])]:
            self.assertFalse(self.c.valid_metrics({**good,key:value},collection))
        self.assertFalse(self.c.valid_metrics(good,collection,'minimal'))
        good['phases'][1]['lifecycle']={}
        self.assertFalse(self.c.valid_metrics(good,collection))

    def test_bad_phase_mapping_and_nonfinite_metrics_are_rejected(self):
        import copy
        collection,good=self.metrics()
        for key,value in [('function','PRIVATE'),('wall_seconds',float('nan')),('main_thread_cpu_seconds',float('inf'))]:
            bad=copy.deepcopy(good);bad['phases'][0][key]=value
            self.assertFalse(self.c.valid_metrics(bad,collection))


if __name__=='__main__':unittest.main()
