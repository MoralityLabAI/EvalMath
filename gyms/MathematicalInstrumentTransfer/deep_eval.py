"""MIT-05B: fresh open depth stress after discovery of a two-step failure."""
from pathlib import Path
import json,time,statistics
import numpy as np
from deep_stress import spec_for
from signature_dp import SignatureDP
from relational import Env,select

P=Path(__file__).parent
r=json.loads((P/'relational_result.json').read_text());models={k:tuple(np.array(p) for p in v) for k,v in r['models'].items() if k.startswith('rel_')}
rows=[]
for seed in range(52040,52064):
    spec=spec_for(seed);g=SignatureDP(spec);t=time.perf_counter_ns();opt=g.value(*g.start);row={'seed':seed,'mass':sum(spec[0]),'oracle':opt,'oracle_ms':(time.perf_counter_ns()-t)/1e6}
    pol={'depth2':lambda e,st,acts:max(acts,key=lambda a:e.qdepth(st,a,2)),'depth3':lambda e,st,acts:max(acts,key=lambda a:e.qdepth(st,a,3))}
    for k,v in models.items():pol[k]=lambda e,st,acts,p=v:select(e,st,acts,'rel',p)
    for k,v in pol.items():
        e=Env(spec);t=time.perf_counter_ns();row[k]=e.rollout(v);row[k+'_ms']=(time.perf_counter_ns()-t)/1e6;assert row[k]<=opt
    rows.append(row)
keys=('oracle','depth2','depth3',*models);out={'roots':len(rows),'results':{k:sum(x[k]/x['mass'] for x in rows)/len(rows) for k in keys},'optimal_roots':{k:sum(x[k]==x['oracle'] for x in rows) for k in keys},'median_ms':{k:statistics.median(x[k+'_ms'] for x in rows) for k in keys},'rows':rows}
(P/'deep_eval_result.json').write_text(json.dumps(out,indent=2)+'\n');print({k:v for k,v in out.items() if k!='rows'})
