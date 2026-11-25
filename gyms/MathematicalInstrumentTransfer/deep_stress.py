"""Find an open development counterexample to receding two-action search."""
import json,time
from pathlib import Path
from random import Random
from relational import Env
from signature_dp import SignatureDP

def spec_for(seed):
    r=Random(seed);n=28; k=6; patterns=r.sample(range(1<<k),8)
    sig=[r.choice(patterns) for _ in range(n)]
    w=(1,)*n
    return w,tuple(sum(((p>>j)&1)<<i for i,p in enumerate(sig)) for j in range(k)),(1,)*k,6

def main():
    rows=[]
    for seed in range(52000,52040):
        spec=spec_for(seed);e=Env(spec);g=SignatureDP(spec)
        opt=g.value(*g.start);d=e.rollout(lambda e,st,acts:max(acts,key=lambda a:e.qdepth(st,a,2)));assert d<=opt
        rows.append(dict(seed=seed,optimum=opt,depth2=d))
        if d<opt:
            d3=e.rollout(lambda e,st,acts:max(acts,key=lambda a:e.qdepth(st,a,3)));assert d3<=opt
            r=dict(spec=spec,seed=seed,optimum=opt,depth2=d,depth3=d3,worlds=len(spec[0]),screened=len(rows),rows=rows);break
    else:r=dict(screened=len(rows),rows=rows,witness=None)
    Path(__file__).with_name('deep_stress_result.json').write_text(json.dumps(r,indent=2)+'\n');print(r,flush=True)
if __name__=='__main__':main()
