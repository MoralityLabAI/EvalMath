#!/usr/bin/env python3
"""Generate a fresh suite, collect measured calls, score only after collection."""
import argparse
import json
import os
from pathlib import Path
import time
from urllib.request import Request, urlopen
from spiral_ln.evaluation_cpf_suite import STAGES, generate, export, digest, arms, score

SYSTEM = ('Evaluate the exact mathematical question under its stated assumptions. '
          'Return only a JSON object with keys label and certificate. '
          'Use entailed if established, counterexample if false in the stated model, '
          'or unresolved if the stated evidence does not establish a claim. '
          'Return the certificate in the precise JSON format requested. No prose.')


def read_jsonl(path):
    return [json.loads(s) for s in Path(path).read_text(encoding='utf-8').splitlines() if s.strip()]


def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False)+'\n', encoding='utf-8')


def write_jsonl(path, rows):
    with Path(path).open('x', encoding='utf-8') as f:
        for row in rows: f.write(json.dumps(row, sort_keys=True, ensure_ascii=False)+'\n')


def prepare(args):
    seed = os.environ.get(args.seed_env)
    if not seed: raise ValueError('set the seed environment variable; keep prospective seeds private until evaluation closes')
    excluded=set()
    for path in getattr(args,'exclude_prompts',[]): excluded.update(r['id'] for r in read_jsonl(path))
    rows=generate(seed,args.per_family,args.split,excluded); prompts,gold=export(rows)
    out=Path(args.out); out.mkdir(parents=True,exist_ok=False)
    write_jsonl(out/'prompts.jsonl',prompts); write_jsonl(out/'gold.jsonl',gold)
    write_json(out/'manifest.json',{'schema':'CPF-suite.1','seed_commitment':digest(seed),'per_family':args.per_family,
        'split':args.split,'excluded_ids_digest':digest(sorted(excluded)),'prompt_digest':digest(prompts),'gold_digest':digest(gold),'roots':len(rows)})


def call(model, prompt, cap, seed, temperature, previous=None):
    messages=[{'role':'system','content':SYSTEM},{'role':'user','content':prompt}]
    if previous is not None:
        messages.extend([{'role':'assistant','content':previous}, {'role':'user','content':
            'Independently check the reasoning, especially the assumptions and certificate. Revise if needed. Return the same JSON format.'}])
    req={'model':model['model'],'messages':messages,'max_tokens':cap,'temperature':temperature,'seed':seed}
    # Per-model server options (e.g. chat_template_kwargs). With answer_reserve set, thinking is
    # capped per request at cap - answer_reserve so the answer fits inside the same completion cap.
    req.update(model.get('request_extra',{}))
    if model.get('answer_reserve') is not None:
        req['reasoning_budget_tokens']=max(0,cap-int(model['answer_reserve']))
    headers={'Content-Type':'application/json'}
    if model.get('key_env'):
        key=os.environ.get(model['key_env']);
        if not key: raise ValueError('model API key environment variable is missing')
        headers['Authorization']='Bearer '+key
    request=Request(model['url'].rstrip('/')+'/chat/completions',data=json.dumps(req).encode(),headers=headers)
    start=time.monotonic()
    with urlopen(request,timeout=model.get('timeout',300)) as resp: raw=json.load(resp)
    secs=time.monotonic()-start
    usage=raw.get('usage') or {}; c=usage.get('completion_tokens'); p=usage.get('prompt_tokens')
    if type(c) is not int or type(p) is not int or not 0<=c<=cap or p<0:
        raise ValueError('server omitted measured token usage or exceeded completion cap')
    choice=raw['choices'][0]; text=choice['message'].get('content') or ''
    return {'text':text,'reasoning':choice['message'].get('reasoning_content'),'completion':c,'prompt':p,
            'seconds':secs,'cap':cap,'seed':seed,'request_id':raw.get('id'),'finish_reason':choice.get('finish_reason'),
            'reported_model':raw.get('model'),'completion_tokens_details':usage.get('completion_tokens_details'),
            'timings':raw.get('timings'),'request_options':{k:v for k,v in req.items() if k not in ('messages',)}}


def collect(args):
    prompts=read_jsonl(args.prompts); config=json.loads(Path(args.config).read_text()); models=config['models']; budget=config['budget']
    if len(models) not in (1,2) or type(budget) is not int or budget<2 or budget%2: raise ValueError('need 1-2 models and a positive even cap')
    names=list(models)
    selected=getattr(args,'only_model',None)
    if selected is not None and selected not in models: raise ValueError('unknown selected model')
    if any('api_key' in m or 'key' in m for m in models.values()): raise ValueError('use key_env, never store a key in config')
    if len({p['id'] for p in prompts})!=len(prompts): raise ValueError('duplicate prompt IDs')
    if any(set(p)!= {'id','prompt'} for p in prompts): raise ValueError('prompt-only export required')
    # Freeze config and prompt list before any calls, and reject resume drift.
    manifest={'schema':'CPF-run.1','prompt_digest':digest(prompts),'config':config,'system':SYSTEM,'protocol':'four-shared-stages.1'}
    out=Path(args.calls); meta=out.with_suffix(out.suffix+'.manifest.json')
    if meta.exists():
        if json.loads(meta.read_text())!=manifest: raise ValueError('resume manifest mismatch')
    elif out.exists(): raise ValueError('call ledger without manifest')
    else: write_json(meta,manifest)
    keys={}
    if out.exists():
        for row in read_jsonl(out):
            k=(row['id'],row['model'],row['stage'])
            if k in keys: raise ValueError('duplicate calls')
            keys[k]=row
    expected={(p['id'],m,s) for p in prompts for m in names for s in STAGES}
    if not set(keys)<=expected: raise ValueError('unexpected calls in resume ledger')
    with out.open('a',encoding='utf-8') as ledger:
        for i,p in enumerate(prompts):
            order=[selected] if selected else (names if i%2==0 else names[::-1])
            for m in order:
                for stage in STAGES:
                    k=(p['id'],m,stage)
                    if k in keys: continue
                    cap=budget if stage=='direct' else budget//2
                    seed=int(digest([config['sampling_seed'],p['id'],m,stage])[:8],16)&0x7fffffff
                    prev=keys[p['id'],m,'low1']['text'] if stage=='refine2' else None
                    # Each request has a fresh message list; only refinement receives earlier output.
                    result=call(models[m],p['prompt'],cap,seed,config['temperature'],prev)
                    row={'id':p['id'],'model':m,'stage':stage,**result}
                    ledger.write(json.dumps(row,ensure_ascii=False)+'\n'); ledger.flush(); os.fsync(ledger.fileno())
                    keys[k]=row
    print(f'{len(keys)} measured calls complete')


def analyze(args):
    gold=read_jsonl(args.gold); ledger=read_jsonl(args.calls); meta=json.loads(Path(args.calls+'.manifest.json').read_text())
    models=list(meta['config']['models']); budget=meta['config']['budget']; by={}
    for row in ledger:
        k=(row['model'],row['stage']); records=by.setdefault(row['id'],{})
        if k in records: raise ValueError('duplicate calls')
        if k[0] not in models or k[1] not in STAGES: raise ValueError('unknown call arm')
        cap=budget if k[1]=='direct' else budget//2
        if row['cap']!=cap or type(row['completion']) is not int or not 0<=row['completion']<=cap: raise ValueError('invalid measured cap')
        records[k]=row
    if any(set(r)!={(m,s) for m in models for s in STAGES} for r in by.values()): raise ValueError('incomplete call panel')
    prompts=read_jsonl(args.prompts)
    generation=json.loads(Path(args.generation_manifest).read_text())
    if digest(gold)!=generation['gold_digest'] or digest(prompts)!=generation['prompt_digest']:
        raise ValueError('generation manifest mismatch')
    if digest(prompts)!=meta['prompt_digest']: raise ValueError('prompt mismatch')
    if set(by)!={p['id'] for p in prompts}: raise ValueError('incomplete root panel')
    report=score(gold,{i:arms(c,models) for i,c in by.items()}); report['run_manifest']=meta
    write_json(args.out,report)


def main():
    p=argparse.ArgumentParser(description=__doc__); sub=p.add_subparsers(dest='mode',required=True)
    q=sub.add_parser('generate'); q.add_argument('--seed-env',default='CPF_SEED'); q.add_argument('--per-family',type=int,default=40); q.add_argument('--split',choices=['train','dev','test'],default='test'); q.add_argument('--exclude-prompts',action='append',default=[]); q.add_argument('--out',required=True); q.set_defaults(func=prepare)
    q=sub.add_parser('collect'); q.add_argument('--prompts',required=True); q.add_argument('--config',required=True); q.add_argument('--calls',required=True); q.add_argument('--only-model'); q.set_defaults(func=collect)
    q=sub.add_parser('score'); q.add_argument('--prompts',required=True); q.add_argument('--gold',required=True); q.add_argument('--generation-manifest',required=True); q.add_argument('--calls',required=True); q.add_argument('--out',required=True); q.set_defaults(func=analyze)
    args=p.parse_args(); args.func(args)


if __name__=='__main__': main()
