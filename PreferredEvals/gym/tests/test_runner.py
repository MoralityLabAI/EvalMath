"""End-to-end local OpenAI-compatible mock, positional bias and task-label isolation."""
import json
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from runner import (check_endpoint, completion_call, load_jsonl, prompt_for,
                    run_tasks, score_run, validate_tasks)
from compare import compare


class MockModel(BaseHTTPRequestHandler):
    calls=[]
    def do_POST(self):
        raw=self.rfile.read(int(self.headers.get('Content-Length','0')))
        request=json.loads(raw)
        MockModel.calls.append(request)
        body=json.dumps({'choices':[{'message':{'content':'A'},'finish_reason':'stop'}],
                         'usage':{'prompt_tokens':140,'completion_tokens':1,'total_tokens':141}}).encode()
        self.send_response(200)
        self.send_header('Content-Length',str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def log_message(self,*args):
        pass


class PromptGymTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),MockModel)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()
        cls.endpoint=f'http://127.0.0.1:{cls.server.server_port}/v1'
        cls.tasks=ROOT/'examples/dev_pair_tasks.jsonl'
        cls.labels=ROOT/'examples/dev_pair_labels.jsonl'
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_local_mock_rollouts_scoring_and_swap(self):
        with TemporaryDirectory() as td:
            folder=Path(td)
            MockModel.calls=[]
            r=run_tasks(dataset=self.tasks,out_dir=folder/'candidate',benchmark='demo-research-taste',
                        model='mock-27b',base_url=self.endpoint,orders='both')
            self.assertEqual(r['total_receipt_rows'],4)
            self.assertEqual(r['n_independent_roots_declared'],2)
            s=score_run(run_dir=folder/'candidate',labels_path=self.labels,out_path=folder/'candidate-scores.json')
            self.assertEqual(s['n_scored'],4)
            self.assertEqual(s['n_correct'],2)
            self.assertEqual(s['macro_root_accuracy'],0.5)
            self.assertEqual(len(MockModel.calls),4)
            self.assertFalse(any('demo-proposal-001' in json.dumps(x) for x in MockModel.calls))
            self.assertTrue(all(x['model']=='mock-27b' for x in MockModel.calls))
            self.assertEqual(run_tasks(dataset=self.tasks,out_dir=folder/'candidate',benchmark='demo-research-taste',
                      model='mock-27b',base_url=self.endpoint,orders='both',resume=True)['new_rollout_rows'],0)
            with self.assertRaisesRegex(ValueError,'config or dataset changed'):
                run_tasks(dataset=self.tasks,out_dir=folder/'candidate',benchmark='demo-research-taste',
                          model='changed-model',base_url=self.endpoint,orders='both',resume=True)
            with self.assertRaises(FileExistsError):
                run_tasks(dataset=self.tasks,out_dir=folder/'candidate',benchmark='demo-research-taste',
                          model='mock-27b',base_url=self.endpoint,orders='both')

    def test_model_pair_exports_clustered_fsi(self):
        with TemporaryDirectory() as td:
            tmp=Path(td)
            for target in ('left','right'):
                run_tasks(dataset=self.tasks,out_dir=tmp/target,benchmark='demo-research-taste',
                          model=target,base_url=self.endpoint,orders='both')
                score_run(run_dir=tmp/target,labels_path=self.labels,out_path=tmp/f'{target}.json')
            result=compare(tmp/'left',tmp/'right',tmp/'left.json',tmp/'right.json')
            self.assertEqual(result['total_assigned_rollouts'],4)
            self.assertEqual(result['n_roots_paired_scored'],2)
            self.assertEqual(len(result['fsi_01_manifest']['cases']),4)
            self.assertFalse(result['fsi_01_manifest']['sealed_readout'])
            self.assertEqual(len({x['cluster_id'] for x in result['fsi_01_manifest']['cases']}),2)

    def test_no_gold_in_tasks_bad_endpoint_or_bad_task(self):
        with self.assertRaisesRegex(ValueError,'--allow-remote'):
            check_endpoint('https://example.net/v1',False)
        raw=load_jsonl(self.tasks)
        self.assertEqual(validate_tasks(raw,'demo-research-taste'),2)
        raw[0]['answer']='A'
        with self.assertRaisesRegex(ValueError,'separate references'):
            validate_tasks(raw,'demo-research-taste')
        with self.assertRaisesRegex(ValueError,'benchmark_id'):
            validate_tasks(load_jsonl(self.tasks),'hle')

    def test_ten_choices_text_normalization_and_request_extra(self):
        with TemporaryDirectory() as td:
            temp=Path(td)
            tasks=temp/'tasks.jsonl'
            labels=temp/'labels.jsonl'
            rows=[{'schema':'preferred-evals/prompt-task-v1','benchmark_id':'b','task_id':'mc10','root_id':'r1',
                   'kind':'choice','question':'Pick one','choices':[f'option {i}' for i in range(10)]},
                  {'schema':'preferred-evals/prompt-task-v1','benchmark_id':'b','task_id':'txt','root_id':'r2',
                   'kind':'exact_text','question':'Say A'}]
            tasks.write_text('\n'.join(json.dumps(x) for x in rows)+'\n')
            labels.write_text('{"task_id":"mc10","answer":"A"}\n{"task_id":"txt","answer":"a"}\n')
            MockModel.calls=[]
            run_tasks(dataset=tasks,out_dir=temp/'run',benchmark='b',model='m',base_url=self.endpoint,
                      request_extra={'chat_template_kwargs':{'enable_thinking':False}})
            self.assertTrue(all(c['chat_template_kwargs']=={'enable_thinking':False} for c in MockModel.calls))
            self.assertIn('J. option 9',prompt_for(rows[0],'normal')[0])
            cfg=json.loads((temp/'run'/'run.json').read_text())
            self.assertEqual(cfg['request_extra'],{'chat_template_kwargs':{'enable_thinking':False}})
            s=score_run(run_dir=temp/'run',labels_path=labels,out_path=temp/'s.json')
            self.assertEqual(s['n_correct'],2)
            with self.assertRaisesRegex(ValueError,'request_extra'):
                run_tasks(dataset=tasks,out_dir=temp/'run2',benchmark='b',model='m',base_url=self.endpoint,
                          request_extra={'max_tokens':5})
        from runner import canonical_text
        self.assertEqual(canonical_text(' "Paris." '),'paris')
        self.assertEqual(canonical_text('`42`'),'42')
        self.assertEqual(canonical_text('Wait...'),'wait...')

    def test_reject_partial_label_file(self):
        with TemporaryDirectory() as td:
            temp=Path(td)
            run_tasks(dataset=self.tasks,out_dir=temp/'run',benchmark='demo-research-taste',model='mock',base_url=self.endpoint)
            partial=temp/'partial.jsonl'
            partial.write_text('{"task_id":"demo-proposal-001","answer":"A"}\n')
            with self.assertRaisesRegex(ValueError,'reference file task IDs'):
                score_run(run_dir=temp/'run',labels_path=partial,out_path=temp/'scores.json')


if __name__=='__main__':
    unittest.main()
