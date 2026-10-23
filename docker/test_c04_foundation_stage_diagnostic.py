import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('diag', Path(__file__).with_name('c04_foundation_stage_diagnostic.py'))
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)

class ObserverTests(unittest.TestCase):
    def test_exact_prefix_and_reject_changed_boundary(self):
        boundary = b'# Independent zero-state C02 DB and every existing Foundation/browser/restart gate.\nsh docker/verify_foundation.sh\n'
        self.assertEqual(d.prefix_bytes(b'original\n' + boundary), b'original\n')
        with self.assertRaises(AssertionError):
            d.prefix_bytes(b'changed')

    def test_stage_finite_and_secret_arguments_redacted(self):
        for name in d.NAMES:
            self.assertNotIn('private-sentinel', d.label(name, ['private-sentinel'], Path('/tmp')))
        self.assertEqual(d.label('sh', ['/tmp/foundation-prefix.sh'], Path('/tmp')), 'c01_c02_prefix')
        for operation in ['config', 'build', 'up', 'down']:
            self.assertEqual(d.label('docker', ['compose', '-p', 'fitlink-c02-immutable-c01', operation], Path('/tmp')), 'immutable_c01.compose_' + operation)

    def test_child_exit_and_stream_bytes(self):
        with tempfile.TemporaryDirectory() as folder, tempfile.TemporaryFile() as private:
            config = {'events': str(Path(folder)/'events'), 'origin': time.monotonic(), 'executables': {'python': sys.executable}}
            saved = os.dup(1), os.dup(2)
            try:
                os.dup2(private.fileno(), 1); os.dup2(private.fileno(), 2)
                code = d.delegate('python', ['-c', "import sys;print('private-sentinel');sys.exit(23)"], config)
            finally:
                os.dup2(saved[0], 1); os.dup2(saved[1], 2)
                os.close(saved[0]); os.close(saved[1])
            self.assertEqual(code, 23)
            private.seek(0)
            self.assertEqual(private.read(), b'private-sentinel\n')
            text = Path(config['events']).read_text()
            self.assertNotIn('private-sentinel', text)
            rows = [json.loads(x) for x in text.splitlines()]
            self.assertEqual([x['event'] for x in rows], ['start','end'])
            self.assertEqual(rows[-1]['exit_code'],23)
            self.assertGreaterEqual(rows[-1]['seconds'], rows[0]['seconds'])

    def probe(self, replies):
        with tempfile.TemporaryDirectory() as folder:
            config = {'events': str(Path(folder)/'events'), 'origin': time.monotonic(), 'executables': {'docker':'unused'}}
            def fake(args, stdout, **kw):
                code, data = replies.pop(0)
                stdout.write(data)
                return subprocess.CompletedProcess(args, code)
            with patch.object(d.subprocess, 'run', fake):
                d.readiness(['compose','-p','fitlink-c02-immutable-c01','up'], config, 'immutable_c01.compose_up')
            return json.loads(Path(config['events']).read_text())

    def test_healthy_readiness(self):
        row = self.probe([(0,b'version'),(0,b'private-container-id'),(0,b'"running"|"healthy"|0|0|"db"')])
        self.assertEqual(row['services'][0]['health'], 'healthy')
        self.assertNotIn('private-container-id',json.dumps(row))

    def test_unhealthy_is_observation_not_root_cause(self):
        row = self.probe([(0,b''),(0,b'id'),(0,b'"running"|"unhealthy"|5|0|"db"')])
        self.assertEqual(row['classification'],'unhealthy_observed')

    def test_failed_query_unknown_not_zero_or_daemon_claim(self):
        row = self.probe([(1,b''),(1,b'')])
        self.assertEqual(row['classification'],'unknown')
        self.assertEqual(row['daemon_query_exit_code'],1)
        self.assertFalse(row['inventory_bounded'])

    def test_malformed_private_output_not_exported(self):
        row = self.probe([(0,b''),(0,b'id'),(0,b'private-sentinel')])
        self.assertEqual(row['services'][0]['parse_state'],'malformed')
        self.assertNotIn('private-sentinel',json.dumps(row))

    def test_missing_cleanup_not_pass(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(d.cleanup_summary(Path(folder)),[])

    def test_metadata_bound(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'events'
            path.write_bytes(b'0'*d.LIMIT)
            d.append_event({'events':str(path)}, {'event':'start'})
            self.assertEqual(path.stat().st_size,d.LIMIT)

    def test_probe_error_preserves_child_exit(self):
        with tempfile.TemporaryDirectory() as folder, tempfile.TemporaryFile() as private:
            executable = Path(folder)/'fake-docker'
            executable.write_text('#!/bin/sh\nexit 31\n')
            executable.chmod(0o700)
            config = {'events': str(Path(folder)/'events'), 'origin': time.monotonic(), 'executables': {'docker': str(executable)}}
            with patch.object(d, 'readiness', side_effect=OSError('private-sentinel')):
                code = d.delegate('docker', ['compose','-p','fitlink-c02-immutable-c01','up'], config)
            self.assertEqual(code,31)
            text = Path(config['events']).read_text()
            self.assertNotIn('private-sentinel',text)
            self.assertEqual(json.loads(text.splitlines()[-1])['classification'],'probe_error')

if __name__ == '__main__':
    unittest.main()
