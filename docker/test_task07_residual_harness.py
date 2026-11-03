"""Diagnostic controls only; never collected with product tests."""
import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


class HarnessTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec('task07_residual_cost_plugin'),
                             'residual observer must exist before spending hosted budget')
        import task07_residual_cost_plugin as p
        import task07_residual_cost_probe as c
        self.p, self.c = p, c

    def test_manifest_exact_101_and_five_pass_order(self):
        self.assertEqual(self.c.CAP, 101)
        self.assertEqual(self.c.PASSES, [('task6', 'minimal', 'inherited'),
                         ('task7', 'detailed', 'inherited'),
                         ('task7', 'minimal', 'inherited'),
                         ('task6', 'detailed', 'inherited'),
                         ('task7', 'detailed', 'new')])
        self.assertEqual(sum(sum(self.p.SELECTIONS[g].values()) for _, _, g in self.c.PASSES), 101)

    def test_collection_rejects_missing_extra_and_changed_parameters(self):
        expected = self.p.SELECTIONS['inherited']
        ids = [f'{k}[case{n}]' for k, count in expected.items() for n in range(count)]
        record = self.p.collection_record(ids, 'inherited')
        self.assertTrue(record['exact'])
        self.assertFalse(self.p.collection_record(ids[:-1], 'inherited')['exact'])
        self.assertFalse(self.p.collection_record(ids + ['private-record'], 'inherited')['exact'])
        changed = list(ids); changed[-1] += 'changed'
        self.assertNotEqual(record['digest'], self.p.collection_record(changed, 'inherited')['digest'])
        self.assertNotIn('private-record', json.dumps(self.p.collection_record(ids + ['private-record'], 'inherited')))

    def test_sql_delegates_once_returns_and_preserves_exception(self):
        calls = []
        token = object()
        def delegate(*args):
            calls.append(args)
            return token
        self.assertIs(self.p.sql_wrapper(delegate, 'PRIVATE SQL', ['PRIVATE PARAM'], False, {}), token)
        self.assertEqual(len(calls), 1)
        error = ValueError('PRIVATE ERROR')
        def fail(*args):
            calls.append(args)
            raise error
        with self.assertRaises(ValueError) as caught:
            self.p.sql_wrapper(fail, 'SECRET', [], False, {})
        self.assertIs(caught.exception, error)
        self.assertEqual(len(calls), 2)
        self.assertNotIn('PRIVATE', json.dumps(self.p.snapshot()))

    def test_failed_truncated_and_cleanup_failure_cannot_pass(self):
        ids = [f'{k}[{i}]' for k, n in self.p.SELECTIONS['new'].items() for i in range(n)]
        collection = self.p.collection_record(ids, 'new')
        phases = [dict(occurrence=i, phase=phase, outcome='passed') for i in range(5) for phase in ('setup', 'call', 'teardown')]
        good = dict(complete=True, exit_code=0, collection=collection, phases=phases, observer_errors=0, truncated=False, unfinished_children=0)
        self.assertTrue(self.c.valid_metrics(good, collection))
        for key, value in [('complete',False), ('exit_code',1), ('truncated',True), ('observer_errors',1), ('unfinished_children',1)]:
            bad = copy.deepcopy(good); bad[key] = value
            self.assertFalse(self.c.valid_metrics(bad, collection))
        bad = copy.deepcopy(good); bad['phases'].pop()
        self.assertFalse(self.c.valid_metrics(bad, collection))
        bad = copy.deepcopy(good); bad['phases'][0]['outcome']='failed'
        self.assertFalse(self.c.valid_metrics(bad, collection))
        self.assertFalse(self.c.final_valid(True, False, True))
        self.assertFalse(self.c.final_valid(True, True, False))
        self.assertTrue(self.c.final_valid(True, True, True))

    def test_child_observer_preserves_semantics_and_exports_no_arguments(self):
        self.p.install_children()
        try:
            r = subprocess.run([sys.executable, '-c', "import sys; print('PRIVATE OUTPUT'); sys.exit(17)"], capture_output=True, timeout=5)
            self.assertEqual(r.returncode, 17)
            self.assertEqual(r.stdout.strip(), b'PRIVATE OUTPUT')
            with self.assertRaises(subprocess.TimeoutExpired):
                subprocess.run([sys.executable, '-c', 'import time; time.sleep(3)'], capture_output=True, timeout=.01)
            rows = self.p.child_snapshot()
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]['exit_code'], 17)
            self.assertNotIn('PRIVATE', json.dumps(rows))
            self.assertNotIn('sleep', json.dumps(rows))
        finally:
            self.p.restore_children()

    def test_profile_nested_labels_and_exception_do_not_change_behavior(self):
        p = self.p
        p.PROFILE_CODES.clear(); p.LIFECYCLE.clear(); p.PROFILE_STACK.clear()
        token = object()
        def inner():
            return token
        def outer():
            return inner()
        p.PROFILE_CODES[inner.__code__]='credential_evidence'
        p.PROFILE_CODES[outer.__code__]='full_approval'
        self.assertIsNone(sys.getprofile())
        sys.setprofile(p.profile)
        try:
            self.assertIs(outer(), token)
        finally:
            sys.setprofile(None)
        self.assertEqual(p.LIFECYCLE['full_approval']['count'], 1)
        self.assertEqual(p.LIFECYCLE['credential_evidence']['count'], 1)
        self.assertGreaterEqual(p.LIFECYCLE['full_approval']['inclusive_seconds'], p.LIFECYCLE['full_approval']['self_excluding_labelled_children_seconds'])

    def test_private_command_output_is_never_exported(self):
        with tempfile.TemporaryDirectory() as d:
            event, data = self.c.run_command('harness', [sys.executable, '-c', "print('PRIVATE'); raise SystemExit(2)"], cwd=Path(d), timeout=5)
            self.assertIn(b'PRIVATE', data)
            self.assertNotIn('PRIVATE', json.dumps(event))
            self.assertEqual(event['exit_code'], 2)

    def test_cleanup_failure_still_removes_private_credentials(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as d:
            state, out = Path(d)/'private', Path(d)/'evidence'
            state.mkdir(); (state/'owned').touch()
            (state/'private.env').write_text('PRIVATE PASSWORD')
            with patch.object(self.c, 'STATE', state), patch.object(self.c,'OUT',out), patch.object(self.c,'execute',side_effect=RuntimeError('PRIVATE FAILURE')):
                result = self.c.cleanup()
            self.assertFalse(result['verified'])
            self.assertFalse((state/'private.env').exists())
            self.assertNotIn('PRIVATE', (out/'cleanup.json').read_text())

    def test_source_identity_detects_dirty_source_and_lock_changes(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); source = root/'.runtime/test-source'
            source.mkdir(parents=True)
            for name in self.c.LOCKS:
                (source/name).write_text('pinned')
            def git(*args):
                return subprocess.run(['git','-C',str(source),*args],check=True,capture_output=True,text=True).stdout.strip()
            git('init','-q'); git('add','.')
            git('-c','user.name=Diagnostic','-c','user.email=diagnostic@example.invalid','commit','-qm','test source')
            pins = {'test':(git('rev-parse','HEAD'),git('rev-parse','HEAD^{tree}'))}
            with patch.object(self.c,'ROOT',root), patch.object(self.c,'PINS',pins):
                before = self.c.identity('test')
                (source/'uv.lock').write_text('modified')
                with self.assertRaises(self.c.Stop):
                    self.c.identity('test')
                git('add','.'); git('-c','user.name=Diagnostic','-c','user.email=diagnostic@example.invalid','commit','-qm','changed lock')
                with self.assertRaises(self.c.Stop):
                    self.c.identity('test')
            self.assertTrue(before['clean'])

    def test_profile_code_loading_matches_unchanged_source_functions(self):
        import os
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'tests/integration/c03/test_verification_decisions.py'
            path.parent.mkdir(parents=True)
            path.write_text('def approved():\n    return 7\n')
            namespace={}
            exec(compile(path.read_bytes(),str(path),'exec',dont_inherit=True),namespace)
            old=os.getcwd()
            try:
                os.chdir(d)
                with patch.object(self.p,'LABEL_SPECS', {k:v for k,v in self.p.LABEL_SPECS.items() if not k.startswith('django/')}):
                    self.p.load_profile_codes()
            finally:
                os.chdir(old)
            code=namespace['approved'].__code__
            self.assertEqual(self.p.PROFILE_PATHS[code.co_filename][code.co_name],'full_approval')

    def test_cleanup_verdict_is_sticky_after_failure(self):
        self.assertTrue(hasattr(self.c, 'update_cleanup_verdict'))
        data=dict(valid=False, cleanup_verified=False, measurements_complete=True, sources_and_locks_preserved=True)
        self.c.update_cleanup_verdict(data, True)
        self.assertFalse(data['valid'])
        self.assertFalse(data['cleanup_verified'])

    def test_interruption_reaps_command_group_before_propagating(self):
        from unittest.mock import MagicMock, patch
        child=MagicMock(pid=12345)
        child.wait.side_effect=[KeyboardInterrupt(), -9]
        with tempfile.TemporaryDirectory() as d, patch.object(self.c.subprocess,'Popen',return_value=child), patch.object(self.c.os,'killpg') as kill:
            with self.assertRaises(KeyboardInterrupt):
                self.c.run_command('harness', ['private-argument'], cwd=Path(d), timeout=10)
            kill.assert_called_once_with(12345, self.c.signal.SIGKILL)
            self.assertEqual(child.wait.call_count, 2)


if __name__ == '__main__':
    unittest.main()
