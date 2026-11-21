import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from external import plan, run, SUPPORTED

class NativePlans(unittest.TestCase):
    def test_prime_v041_uses_current_cli_and_explicit_local_runtime(self):
        r=plan('prime-v041',model='bonsai-27b',base_url='http://127.0.0.1:18127/v1',
               out='out',taskset='gsm8k',limit=5,rollouts=2)
        self.assertEqual(r['command'][0],'vf-run')
        self.assertEqual(r['command'][r['command'].index('--env.agent.runtime.type')+1],'subprocess')
        self.assertIn('--dry-run',r['prepare_command'])
        self.assertNotIn('vf-eval',r['command'])
        self.assertFalse(run(r,workdir='.')['executed'])
    def test_inkling_known_exact_modules(self):
        r=plan('inkling-deepswe',model='qwen-4b',base_url='http://127.0.0.1:8095/v1',
               out='swe',limit=2,rollouts=2)
        self.assertIn('inkling_verify.benchmarks.deepswe',r['command'])
        self.assertIn('--samples-per-problem',r['command'])
        self.assertIn('prepare',r['prepare_command'])
        with self.assertRaisesRegex(ValueError,'download'):
            run(r,workdir='.',execute=True,do_prepare=True)
        self.assertIn('inkling-hle',SUPPORTED)
    def test_cost_and_endpoint_safety(self):
        r=plan('prime-v041',model='m',base_url='https://example.com/v1',out='out',
               taskset='gsm8k',runtime='prime')
        with self.assertRaisesRegex(ValueError,'--allow-paid'):
            run(r,workdir='.',execute=True)
        r=plan('prime-v041',model='m',base_url='https://example.com/v1',out='out',
               taskset='gsm8k')
        with self.assertRaisesRegex(ValueError,'--allow-remote'):
            run(r,workdir='.',execute=True)
        with self.assertRaisesRegex(ValueError,'explicit installed'):
            plan('prime-v041',model='m',base_url='http://localhost:8000/v1',out='out')

if __name__=='__main__':
    unittest.main()
