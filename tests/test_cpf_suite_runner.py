"""Local HTTP fixture only. No model, remote service, or model benchmark is run."""
import argparse
import importlib.util
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import pytest
from spiral_ln.evaluation_cpf_suite import digest, generate

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('cpf_runner', ROOT/'scripts/run_cpf_suite.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def test_generate_collect_score_resume(tmp_path, monkeypatch):
    seed='mock-http-fixture-v1'; monkeypatch.setenv('CPF_SEED',seed)
    generated=tmp_path/'case'; runner.prepare(argparse.Namespace(seed_env='CPF_SEED',per_family=2,split='test',out=generated))
    roots=generate(seed,2,'test'); gold={r['prompt']:r for r in roots}; requests=[]
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*a): pass
        def do_POST(self):
            body=json.loads(self.rfile.read(int(self.headers['Content-Length']))); requests.append(body)
            g=gold[body['messages'][1]['content']]; cap=body['max_tokens']; refined=len(body['messages'])==4
            # Both low calls share the same deliberately wrong label on false roots.
            answer={'label':'entailed','certificate':None} if cap==32 and not refined and g['label']=='counterexample' else {'label':g['label'],'certificate':g['certificate']}
            payload=json.dumps({'id':f'mock-{len(requests)}','model':body['model'],'usage':{'completion_tokens':min(cap,12),'prompt_tokens':20+int(refined)*10},'choices':[{'message':{'content':json.dumps(answer)},'finish_reason':'stop'}]}).encode()
            self.send_response(200); self.send_header('Content-Length',str(len(payload))); self.end_headers(); self.wfile.write(payload)
    http=ThreadingHTTPServer(('127.0.0.1',0),Handler); thread=threading.Thread(target=http.serve_forever,daemon=True); thread.start()
    try:
        config=tmp_path/'config.json'; calls=tmp_path/'calls.jsonl'; url=f'http://127.0.0.1:{http.server_port}/v1'
        config.write_text(json.dumps({'budget':64,'sampling_seed':'mock','temperature':.3,'models':{m:{'url':url,'model':m} for m in ('B','I')}}))
        args=argparse.Namespace(prompts=str(generated/'prompts.jsonl'),config=str(config),calls=str(calls))
        args.only_model='B'; runner.collect(args); assert len(requests)==48
        args.only_model='I'; runner.collect(args); assert len(requests)==96
        args.only_model=None; runner.collect(args); assert len(requests)==96
        assert sum(len(r['messages'])==4 for r in requests)==24
        assert all(len(r['messages'])==2 for r in requests if len(r['messages'])!=4)
        assert all(r['max_tokens'] in (32,64) for r in requests)
        output=tmp_path/'report.json'; score_args=argparse.Namespace(prompts=args.prompts,gold=str(generated/'gold.jsonl'),generation_manifest=str(generated/'manifest.json'),calls=args.calls,out=str(output))
        runner.analyze(score_args); report=json.loads(output.read_text())
        assert report['roots']==12 and len(report['arms'])==13
        assert report['arms']['B/direct']['counts']['certified_correct']==12
        assert report['arms']['B/refine']['counts']['certified_correct']==12
        assert report['arms']['B/independent']['counts']['false_authorized']==5
        assert report['paired']['B/low|I/low']['joint_false']==5
        # Invalid gold, drift in generation manifest, or run configuration must fail closed.
        gpath=generated/'gold.jsonl'; raw=gpath.read_text(); lines=raw.splitlines(); g=json.loads(lines[0]); g['label']='invalid'; lines[0]=json.dumps(g); gpath.write_text('\n'.join(lines)+'\n')
        with pytest.raises(ValueError,match='generation manifest mismatch'): runner.analyze(score_args)
        gpath.write_text(raw)
        c=json.loads(config.read_text()); c['temperature']=.9; config.write_text(json.dumps(c))
        with pytest.raises(ValueError,match='resume manifest mismatch'): runner.collect(args)
    finally:
        http.shutdown(); http.server_close(); thread.join(timeout=2)
