"""Native Verifiers 0.4.1 Episode import, dropped and unscored result handling."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ingest_prime import ingest


def episode(eid,ok=True,dropped=None,reward=1.0):
    return {'id':eid,'task':{'type':'GSMSimple','key':'q1','hash':'fake-hash',
                            'data':{'id':'task-1','name':'question-one'}},
            'ok':ok,'errors':[],'run':{'id':'run-1'},'traces':[
            {'id':eid+'-trace','task':{'key':'q1','data':{'id':'task-1'}},
             'ok':ok,'dropped':dropped,'errors':[],
             'rewards':{'task_correct':{'score':reward,'weight':0.8},
                        'format':{'score':1,'weight':0.2}},
             'metrics':{'task_success':1},'calls':[{},{}],
             'num_input_tokens':120,'num_output_tokens':8}]}


class PrimeImporterTests(unittest.TestCase):
    def test_episode_schema_dropped_and_error_traces(self):
        r=ingest([episode('e1'),episode('e2',dropped='timeout'),episode('e3',ok=False)],
                 {'q1':'source-root-a','task-1':'source-root-a'})
        self.assertEqual(r['n_episodes'],3)
        self.assertEqual(r['n_scored_roots'],1)
        self.assertAlmostEqual(r['mean_root_reward'],1)
        self.assertEqual(r['status_counts'],{'dropped':1,'infrastructure_or_agent_error':1,'scored':1})
        self.assertEqual(r['records'][0]['model_calls'],2)
        self.assertIsNone(r['records'][1]['score'])
        self.assertIsNone(r['records'][2]['score'])
    def test_unattributed_roots_conflicting_ids_or_duplicate_episodes(self):
        with self.assertRaisesRegex(ValueError,'root map'):
            ingest([episode('e1')],{})
        with self.assertRaisesRegex(ValueError,'exactly one'):
            ingest([episode('e1')],{'some-other-task':'other'})
        with self.assertRaisesRegex(ValueError,'exactly one'):
            ingest([episode('e1')],{'q1':'a','task-1':'b'})
        with self.assertRaisesRegex(ValueError,'duplicate episode'):
            ingest([episode('e1'),episode('e1')],{'q1':'a'})
    def test_none_reward_and_empty_trace(self):
        e=episode('e2');e['traces'][0]['rewards']={'x':None}
        blank=episode('e1');blank['traces']=[]
        r=ingest([e,blank],{'q1':'r'})
        self.assertEqual(r['status_counts'],{'no_trace':1,'unscored':1})
        self.assertEqual(r['n_scored_roots'],0)


if __name__=='__main__':
    unittest.main()
