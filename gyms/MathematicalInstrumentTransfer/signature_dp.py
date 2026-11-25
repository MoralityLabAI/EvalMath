"""MIT-05: exact compression by joint instrument signature and equal prior weight."""
from collections import Counter
from functools import lru_cache
from fractions import Fraction
from random import Random
from pathlib import Path
import json,time,statistics,hashlib
from relational import Env,make
from higher_order import PAT,marginals,optimum

class SignatureDP:
    def __init__(self,spec):
        w,masks,self.costs,self.b=spec
        groups=Counter((sum(((m>>i)&1)<<j for j,m in enumerate(masks)),wi) for i,wi in enumerate(w))
        self.types=tuple(sorted(groups)); self.counts=tuple(groups[t] for t in self.types);self.n=len(w)
        self.start=(self.counts,(1<<len(masks))-1,self.b)
        self.value=lru_cache(None)(self._value)
    def _value(self,counts,a,b):
        if b<=0 or not any(counts):return 0
        mass=sum(w*n for (_,w),n in zip(self.types,counts))
        top=sum(sorted((w for (_,w),n in zip(self.types,counts) for _ in range(n)),reverse=True)[:b]);best=top
        if best==mass:return mass
        for i,((sig,w),n) in enumerate(zip(self.types,counts)):
            if n:best=max(best,w+self.value(counts[:i]+(n-1,)+counts[i+1:],a,b-1))
        for j,c in enumerate(self.costs):
            if a>>j&1 and c<b:
                parts=tuple(tuple(n if (sig>>j&1)==bit else 0 for (sig,_),n in zip(self.types,counts)) for bit in (0,1))
                if all(any(p) for p in parts):best=max(best,sum(self.value(p,a^(1<<j),b-c) for p in parts))
        return best

def expand(counts,budget):
    sig=[p for p,c in zip(PAT,counts) for _ in range(c)]
    return (1,)*len(sig),tuple(sum(p[j]<<i for i,p in enumerate(sig)) for j in range(3)),(1,1,1),budget

def repeated(seed):
    r=Random(seed);n=20;k=4; patterns=[r.randrange(1<<k) for _ in range(6)];s=[r.choice(patterns) for _ in range(n)];w=tuple(r.choice((1,1,2)) for _ in range(n))
    return w,tuple(sum(((p>>j)&1)<<i for i,p in enumerate(s)) for j in range(k)),(1,)*k,5

def main():
    wit=json.loads(Path(__file__).with_name('higher_order_result.json').read_text());rows=[];specs=[('witness_a',expand(wit['counts_a'],5)),('witness_b',expand(wit['counts_b'],5))]+[('random',make(40000+i,'large')) for i in range(8)]+[('repeated',repeated(41000+i)) for i in range(12)]
    for idx,(family,spec) in enumerate(specs):
        t=time.perf_counter_ns();e=Env(spec);v=e.value(*e.start);et=time.perf_counter_ns()-t;states=e.value.cache_info().currsize
        d=e.rollout(lambda e,st,acts:max(acts,key=lambda a:e.qdepth(st,a,2)));d3=e.rollout(lambda e,st,acts:max(acts,key=lambda a:e.qdepth(st,a,3)))
        t=time.perf_counter_ns();g=SignatureDP(spec);gv=g.value(*g.start);gt=time.perf_counter_ns()-t;assert v==gv
        if family.startswith('witness'):assert v==wit['optimum_'+family[-1]]
        rows.append(dict(family=family,root=idx,worlds=len(spec[0]),classes=len(g.types),mass=sum(spec[0]),optimum=v,depth2=d,depth3=d3,expanded_states=states,compressed_states=g.value.cache_info().currsize,expanded_ms=et/1e6,compressed_ms=gt/1e6));print(rows[-1],flush=True)
    result=dict(schema='mit05-exact-dev-v1',roots=len(rows),all_equal=True,rows=rows,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    Path(__file__).with_name('signature_result.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
