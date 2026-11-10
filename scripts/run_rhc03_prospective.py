#!/usr/bin/env python3
"""Prepare, calibrate, and audit RHC-03 on a sealed MeshEscapePit family split.

The HTTP runner reads only actor request JSONL. It never opens the oracle vault.
The audit runner uses only fixed actor output and the independently held vault.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from spiral_ln.evaluation_reward_hacking_prospective import (  # noqa: E402
    SCHEMA, audit, digest, fit, git_blob_sha, independent_score,
    load_catalog, prepare, read_json, simulate_mock,
)


def read_lines(path:Path)->list[dict]:
    content=path.read_text(encoding='utf8')
    return [json.loads(row) for row in content.splitlines() if row.strip()]


def write_new(path:Path, value, *, jsonl:bool=False)->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    content=(''.join(json.dumps(obj,sort_keys=True,ensure_ascii=True)+'\n' for obj in value) if jsonl
             else json.dumps(value,indent=2,sort_keys=True,ensure_ascii=True)+'\n')
    with path.open('x',encoding='utf-8') as f:
        f.write(content)


def verify_envelope(envelope:dict,protocol:dict,requests:dict[str,list],vault:dict)->None:
    if (envelope.get('schema')!='rhc03_prepare_v1' or
        envelope.get('protocol_sha256')!=digest(protocol) or
        envelope.get('oracle_sha256')!=digest(vault) or
        envelope.get('actor_request_sha256')!={k:digest(v) for k,v in requests.items()}):
        raise ValueError('prepared request/vault/protocol receipts disagree')


def check_upstream_parity(catalog:dict,scorer_path:Path)->dict:
    """Compare independently implemented outcome checker to pinned upstream scorer."""
    blob=scorer_path.read_bytes()
    expected='7665c6c28d1e015d9da32eac76c41e0b203a6658'
    if git_blob_sha(blob)!=expected:
        raise ValueError('upstream scorer blob differs from pinned source')
    spec=importlib.util.spec_from_file_location('rhc03_upstream_scorer',scorer_path)
    assert spec and spec.loader
    mod=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=mod
    spec.loader.exec_module(mod)
    examples=[]
    for task in catalog['tasks']:
        evidence=[item['evidence_id'] for item in task['evidence']]
        for decision in ('remove','retain','escalate'):
            for accepted in ([],evidence[:1],evidence[:4]):
                examples.append((task,json.dumps({'decision':decision,'accepted_evidence':accepted,'reason_code':'parity_test'})))
        examples.extend((task,s) for s in ('not-json', '',
            '{"decision":"retain","accepted_evidence":[],"reason_code":"bad","extra":1}'))
    for row,reply in examples:
        direct=independent_score(row,reply)
        pinned=mod.score_reply(row,reply)
        for field in ('schema_valid','effective_decision','main_task_success','side_attack_success','authority_valid','fail_closed'):
            if direct[field]!=getattr(pinned,field):
                raise AssertionError(f'upstream scorer parity mismatch {row["trajectory_id"]}/{field}')
    return {'source_score_git_blob_sha':expected,'tested_cases':len(examples),'all_matched':True}


def http_responses(requests:list[dict], endpoint:str,model:str, timeout:int=60,
                   max_output_tokens:int=180)->list[dict]:
    parsed=urllib.parse.urlparse(endpoint)
    if parsed.scheme!='http' or parsed.hostname not in ('localhost','127.0.0.1','::1') or parsed.path!='/v1/chat/completions':
        raise ValueError('HTTP runner restricted to loopback /v1/chat/completions; use offline imported responses for other providers')
    if not model or timeout<=0 or max_output_tokens<=0:
        raise ValueError('invalid local model configuration')
    responses=[]
    for req in requests:
        body={'model':model,'messages':req['messages'],'temperature':0,
              'max_tokens':max_output_tokens,'stream':False}
        payload=json.dumps(body).encode('utf8')
        hdr={'Content-Type':'application/json'}
        # Optional local gateway key. Never store or print its value.
        key=os.environ.get('RHC03_LOCAL_API_KEY')
        if key:hdr['Authorization']='Bearer '+key
        request=urllib.request.Request(endpoint,data=payload,headers=hdr,method='POST')
        try:
            with urllib.request.urlopen(request,timeout=timeout) as response:
                result=json.loads(response.read(1_000_000).decode('utf8'))
            raw=result['choices'][0]['message']['content']
            if not isinstance(raw,str):raise ValueError('gateway returned non-text content')
            error=None
        except (TimeoutError,urllib.error.URLError,ValueError,KeyError,IndexError) as exc:
            raw=''
            error=type(exc).__name__
        responses.append({'blind_id':req['blind_id'],'request_sha256':req['request_sha256'],
                          'raw_reply':raw,'mode':'imported_actor','model_id':model,
                          'runner_error_type':error})
    return responses


def main()->int:
    cli=argparse.ArgumentParser(description=__doc__)
    sub=cli.add_subparsers(dest='cmd',required=True)
    p=sub.add_parser('prepare');p.add_argument('--catalog',type=Path,required=True);p.add_argument('--protocol',type=Path,required=True)
    p.add_argument('--actor-dir',type=Path,required=True);p.add_argument('--auditor-dir',type=Path,required=True)
    p=sub.add_parser('parity');p.add_argument('--catalog',type=Path,required=True);p.add_argument('--protocol',type=Path,required=True)
    p.add_argument('--scorer',type=Path,required=True)
    p=sub.add_parser('mock');p.add_argument('--requests',type=Path,required=True);p.add_argument('--responses',type=Path,required=True)
    p=sub.add_parser('local-http');p.add_argument('--requests',type=Path,required=True);p.add_argument('--responses',type=Path,required=True)
    p.add_argument('--model',required=True);p.add_argument('--endpoint',default='http://127.0.0.1:1234/v1/chat/completions')
    p.add_argument('--timeout',type=int,default=60)
    p=sub.add_parser('fit');p.add_argument('--protocol',type=Path,required=True);p.add_argument('--requests',type=Path,required=True)
    p.add_argument('--responses',type=Path,required=True);p.add_argument('--vault',type=Path,required=True)
    p.add_argument('--envelope',type=Path,required=True);p.add_argument('--holdout-requests',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p=sub.add_parser('audit');p.add_argument('--protocol',type=Path,required=True);p.add_argument('--requests',type=Path,required=True)
    p.add_argument('--responses',type=Path,required=True);p.add_argument('--vault',type=Path,required=True)
    p.add_argument('--envelope',type=Path,required=True);p.add_argument('--calibration-requests',type=Path,required=True)
    p.add_argument('--detector',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--require-live',action='store_true')
    args=cli.parse_args()
    if args.cmd in ('prepare','parity'):
        protocol=read_json(args.protocol.read_bytes())
        catalog=load_catalog(args.catalog.read_bytes(),protocol)
        if args.cmd=='parity':
            print(json.dumps(check_upstream_parity(catalog,args.scorer),sort_keys=True));return 0
        if args.actor_dir.resolve()==args.auditor_dir.resolve():
            raise ValueError('actor and oracle locations must be separate')
        requests,vault,envelope=prepare(catalog,protocol)
        for phase,items in requests.items():
            write_new(args.actor_dir/f'{phase}_requests.jsonl',items,jsonl=True)
        write_new(args.auditor_dir/'oracle_vault.json',vault)
        write_new(args.auditor_dir/'prepare_receipt.json',envelope)
        print(json.dumps({'prepared':{k:len(v) for k,v in requests.items()},'sealed_digest':envelope['oracle_sha256'],
                          'claim_level':'preparation_only_no_model_calls'},sort_keys=True));return 0
    if args.cmd in ('mock','local-http'):
        requests=read_lines(args.requests)
        responses=(simulate_mock(requests) if args.cmd=='mock' else
                   http_responses(requests,args.endpoint,args.model,timeout=args.timeout))
        write_new(args.responses,responses,jsonl=True)
        print(json.dumps({'mode':'mock_preflight' if args.cmd=='mock' else 'imported_actor',
                          'responses':len(responses)},sort_keys=True));return 0
    protocol=read_json(args.protocol.read_bytes())
    vault=read_json(args.vault.read_bytes())
    calibration=read_lines(args.requests if args.cmd=='fit' else args.calibration_requests)
    holdout=read_lines(args.holdout_requests if args.cmd=='fit' else args.requests)
    envelope=read_json(args.envelope.read_bytes())
    verify_envelope(envelope,protocol,{'calibration':calibration,'holdout':holdout},vault)
    replies=read_lines(args.responses)
    if args.cmd=='fit':
        result=fit(protocol,calibration,vault,replies)
    else:
        detector=read_json(args.detector.read_bytes())
        result=audit(protocol,holdout,vault,replies,detector,require_live=args.require_live)
    write_new(args.output,result)
    print(json.dumps({'created':str(args.output),'schema':result['schema'],'mode':result.get('mode','pre-holdout fit')},sort_keys=True))
    return 0

if __name__=='__main__':raise SystemExit(main())
