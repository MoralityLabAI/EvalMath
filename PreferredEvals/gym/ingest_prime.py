"""Summarize actual Prime Verifiers 0.4.1 Episode JSONL without changing its judge.

The latest vf-run emits Episode records containing .task and .traces. Older
v1 records can have the same broad top-level structure with different call
fields. Requires an explicit task-to-root mapping; doesn't infer independence.
A trace with dropped/reward-null/failed scoring never enters the reward mean.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


def _identity(task, root_map):
    data=task.get('data') or {}
    if not isinstance(data,dict):
        raise ValueError('task.data expected object')
    aliases=[task.get('key'),data.get('id'),data.get('name'),task.get('hash')]
    matched={root_map[key] for key in aliases if isinstance(key,str) and key in root_map}
    if len(matched)!=1:
        raise ValueError('task identity must match exactly one independent-root mapping')
    identity=next((k for k in aliases if isinstance(k,str) and k in root_map),None)
    return identity, matched.pop()


def ingest(rows, roots):
    if not isinstance(roots,dict) or not roots:
        raise ValueError('explicit nonempty root map required')
    if any(not isinstance(k,str) or not isinstance(v,str) or not k.strip() or not v.strip()
           for k,v in roots.items()):
        raise ValueError('root map keys and values must be nonempty strings')
    records=[]
    unique=set()
    statuses=Counter()
    by_root=defaultdict(list)
    for episode_idx, episode in enumerate(rows):
        if not isinstance(episode,dict) or not isinstance(episode.get('task'),dict):
            raise ValueError('episode requires task object')
        task=episode['task']
        identity, root=_identity(task,roots)
        eid=episode.get('id') or f'row-{episode_idx}'
        if eid in unique:
            raise ValueError('duplicate episode id')
        unique.add(eid)
        traces=episode.get('traces') or []
        if not isinstance(traces,list):
            raise ValueError('episode.traces must be a list')
        if not traces:
            records.append({'episode_id':eid,'task_id':identity,'root_id':root,
                            'status':'no_trace','error_count':len(episode.get('errors') or []),
                            'score':None,'trace_id':None})
            statuses['no_trace']+=1
            continue
        for i, tr in enumerate(traces):
            if not isinstance(tr,dict):
                raise ValueError('invalid episode trace')
            tr_task=tr.get('task')
            if isinstance(tr_task,dict):
                aliases=[tr_task.get('key'),(tr_task.get('data') or {}).get('id'),
                         (tr_task.get('data') or {}).get('name')]
                if any(k in roots and roots[k]!=root for k in aliases if isinstance(k,str)):
                    raise ValueError('trace.task maps to a different independent root')
            is_dropped=bool(tr.get('dropped'))
            success=bool(episode.get('ok',False)) and bool(tr.get('ok',False))
            rewards=tr.get('rewards') or {}
            if not isinstance(rewards,dict):
                raise ValueError('trace.rewards must be a mapping')
            score=0.0
            valid=False
            for key,v in rewards.items():
                if v is None:
                    continue
                if not isinstance(v,dict) or not isinstance(v.get('score'),(float,int)):
                    raise ValueError(f'invalid reward {key}')
                score+=float(v['score'])*float(v.get('weight',1.0))
                valid=True
            if is_dropped:
                status='dropped'
            elif not success:
                status='infrastructure_or_agent_error'
            elif not valid:
                status='unscored'
            else:
                status='scored'
            if status!='scored':
                score=None
            calls=tr.get('calls')
            if calls is None:
                calls=tr.get('model_calls') or []
            if not isinstance(calls,list):
                raise ValueError('model calls must be list')
            r={'episode_id':eid,'task_id':identity,'root_id':root,
               'trace_id':tr.get('id') or f'trace-{i}', 'status':status,
               'score':score,'dropped_reason':tr.get('dropped'),
               'stop_condition':tr.get('stop_condition'),
               'error_count':len(tr.get('errors') or [])+len(episode.get('errors') or []),
               'model_calls':len(calls),
               'input_tokens':tr.get('num_input_tokens'),
               'output_tokens':tr.get('num_output_tokens'),
               'task_hash':task.get('hash'),
               'run_id':(episode.get('run') or {}).get('id')}
            records.append(r)
            statuses[status]+=1
            if status=='scored':
                by_root[root].append(score)
    macro=[sum(v)/len(v) for v in by_root.values() if v]
    return {'schema':'preferred-evals/prime-episode-summary-v041',
            'n_episodes':len(unique),'n_trace_records':len(records),
            'n_scored_roots':len(macro),'mean_root_reward':sum(macro)/len(macro) if macro else None,
            'status_counts':dict(sorted(statuses.items())),
            'evidence_class':'scored native Prime episodes; independent root identity is author-attested',
            'limits':'Preserve upstream native traces for audit; this lightweight importer does not replace Prime judgments.',
            'records':records}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--traces',type=Path,required=True)
    p.add_argument('--root-map',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    rows=[json.loads(x) for x in args.traces.read_text(encoding='utf-8').splitlines() if x.strip()]
    d=ingest(rows,json.loads(args.root_map.read_text(encoding='utf-8')))
    d['native_trace_sha256']=hashlib.sha256(args.traces.read_bytes()).hexdigest()
    d['root_map_sha256']=hashlib.sha256(args.root_map.read_bytes()).hexdigest()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({k:d[k] for k in ('n_episodes','n_trace_records','n_scored_roots','mean_root_reward','status_counts')},sort_keys=True))


if __name__=='__main__':
    main()
