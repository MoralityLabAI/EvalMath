import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from external import plan, run, SUPPORTED

class NativePlans(unittest.TestCase):
    def test_prime_v041_uses_current_cli_and_explicit_local_runtime(self):
        r=plan('prime-v041',model='bonsai-27b',base_url='http://127.0.0.1:18127/v1',
               out='out',taskset='gsm8k',limit=5,rollouts=2,harness='null',max_tokens=4096,temperature=0.6)
        self.assertEqual(r['command'][r['command'].index('--sampling.max_tokens')+1],'4096')
        self.assertEqual(r['command'][0],'vf-run')
        self.assertEqual(r['command'][r['command'].index('--env.agent.runtime.type')+1],'subprocess')
        self.assertIn('--dry-run',r['prepare_command'])
        self.assertNotIn('vf-eval',r['command'])
        self.assertFalse(run(r,workdir='.')['executed'])
    def test_prime_plan_requires_an_explicit_harness(self):
        # vf-run 0.4.1 falls back to the bash harness (a shell for the model) when neither the run
        # nor the taskset names one, so the plan never leaves the choice implicit.
        with self.assertRaisesRegex(ValueError,'explicit harness'):
            plan('prime-v041',model='m',base_url='http://127.0.0.1:18127/v1',out='out',taskset='gsm8k')
        r=plan('prime-v041',model='m',base_url='http://127.0.0.1:18127/v1',out='out',taskset='gsm8k',
               harness='null')
        self.assertEqual(r['command'][r['command'].index('--env.agent.harness.id')+1],'null')
        r=plan('prime-v041',model='m',base_url='http://127.0.0.1:18127/v1',out='out',taskset='mcp-sqlite',
               harness='taskset')
        self.assertNotIn('--env.agent.harness.id',r['command'])
        r=plan('prime-v041',model='m',base_url='http://127.0.0.1:18127/v1',out='out',taskset='gsm8k',
               harness='bash')
        self.assertTrue(any('executes model-written code' in n for n in r['notes']))
        n=plan('inkling-niah',model='m',base_url='http://127.0.0.1:18127/v1',out='o',data_dir='d',
               max_tokens=4096,temperature=0.0,concurrency=2)['command']
        self.assertEqual(n[n.index('--data-dir')+1],'d')
        self.assertEqual(n[n.index('--max-output-tokens')+1],'4096')
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
               taskset='gsm8k',runtime='prime',harness='null')
        with self.assertRaisesRegex(ValueError,'--allow-paid'):
            run(r,workdir='.',execute=True)
        r=plan('prime-v041',model='m',base_url='https://example.com/v1',out='out',
               taskset='gsm8k',harness='null')
        with self.assertRaisesRegex(ValueError,'--allow-remote'):
            run(r,workdir='.',execute=True)
        with self.assertRaisesRegex(ValueError,'explicit installed'):
            plan('prime-v041',model='m',base_url='http://localhost:8000/v1',out='out')

if __name__=='__main__':
    unittest.main()
