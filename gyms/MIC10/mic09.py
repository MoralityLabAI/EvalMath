"""MIC-09: exact propagation and component reduction in certified search."""
from run import Engine, root, bits, FAMILIES
from core import Root, valid, exact_table
from random import Random
from time import perf_counter
from pathlib import Path
import hashlib, json, math
CAP=512
SIZES=(32,64,128)
SEEDS=range(4000,4003)
ARMS={'base':(False,False),'prop':(True,False),'factor':(False,True),'both':(True,True)}

def instance(f,seed,n,planted):
    if not planted:return root(f,seed,n)
    r=Random(seed+1009*n+10007*FAMILIES.index(f));order=list(range(n));r.shuffle(order)
    w=[0]*n;edges=[];sup=[]
    for k in range(0,n,8):
        ids=order[k:k+8];d=root(f,seed+103*k,len(ids))
        for i,x in enumerate(ids):w[x]=d.w[i]
        edges.extend(tuple(sorted((ids[i],ids[j]))) for i,j in d.edges)
        sup.extend((ids[i],sum(1<<ids[j] for j in bits(a))) for i,a in d.sup)
    return Root(tuple(w),tuple(sorted(edges)),tuple(sorted(sup)))

class Solver(Engine):
    def __init__(self,d,prop,factor,gate=None,observer=None):
        super().__init__(d);self.prop=prop;self.factor=factor
        self.gate=gate;self.observer=observer;self.gate_calls=0;self.gate_skips=0
        self.norm_calls=0;self.forced_scans=0;self.forced_added=0
        self.component_scans=0;self.components_solved=0;self.enum_masks=0
        self.enum_clause_checks=0;self.cache_hits=0;self.cache={}
    def propagate(self,s,req):
        while True:
            s=self.close(s)
            if req&~s:return None
            if not self.prop:return s,req
            excluded=0
            for i in bits(req):excluded|=self.adj[i]
            if excluded&req:return None
            if excluded&s:s&=~excluded;continue
            old=req
            for i,a in self.d.sup:
                if req>>i&1:
                    self.forced_scans+=1;left=s&a
                    if not left:return None
                    if left&(left-1)==0:req|=left
            self.forced_added+=(req&~old).bit_count()
            if old==req:return s,req
    def components(self,s):
        adj=[a&s for a in self.adj]
        for i,a in self.d.sup:
            self.component_scans+=1
            if not s>>i&1:continue
            for j in bits(a&s):adj[i]|=1<<j;adj[j]|=1<<i
        left=s;out=[]
        while left:
            todo=left&-left;c=0
            while todo:
                v=todo&-todo;todo^=v
                if v&c:continue
                c|=v;todo|=adj[v.bit_length()-1]&left&~c
            out.append(c);left&=~c
        return out
    def component_opt(self,c,req):
        key=c,req&c
        if key in self.cache:self.cache_hits+=1;return self.cache[key]
        best=None;bestval=-1;s=c
        while True:
            if not key[1]&~s:
                self.enum_masks+=1;ok=True
                for i in bits(s):
                    self.enum_clause_checks+=1
                    if self.adj[i]&s:ok=False;break
                if ok:
                    for i,a in self.d.sup:
                        if s>>i&1:
                            self.enum_clause_checks+=1
                            if not s&a:ok=False;break
                if ok:
                    v=self.value(s)
                    if v>bestval:best,bestval=s,v
            if not s:break
            s=(s-1)&c
        self.cache[key]=best;return best
    def normalize(self,s,req):
        self.norm_calls+=1;r=self.propagate(s,req)
        if r is None or not self.factor:return r
        s,req=r
        if self.gate is not None:
            self.gate_calls+=1
            if not self.gate(self,s,req):self.gate_skips+=1;return s,req
        parts=self.components(s)
        if self.observer is not None:self.observer(self,s,req,parts)
        if len(parts)<2:return s,req
        for c in parts:
            if c&~req==0:continue
            if not any(self.adj[i]&c for i in bits(c)):best=c
            elif c.bit_count()<=8:best=self.component_opt(c,req)
            else:continue
            if best is None:return None
            s=(s&~c)|best;req|=best;self.components_solved+=1
        return s,req

def solve(d,mode,cap=CAP,seconds=None,gate=None,observer=None):
    t=perf_counter();deadline=t+seconds if seconds is not None else math.inf
    e=Solver(d,*ARMS[mode],gate=gate,observer=observer);s=e.close(e.full);best=e.initializer(s);bestval=e.value(best)
    init=e.calls;init_value=bestval;assert valid(d,best)
    front=[(-e.upper(s),s,0)];seen={(s,0)};steps=0
    while front:
        if e.norm_calls+2>cap or perf_counter()>=deadline:break
        neg,s,req=front.pop()
        if -neg<=bestval:continue
        edge=e.edge(s,e.degrees(s))
        if edge is None:
            if e.value(s)>bestval:best,bestval=s,e.value(s)
            continue
        i=edge[0];assert not req>>i&1;steps+=1;children=[]
        for active,forced in ((s&~(1<<i),req),(s&~e.adj[i],req|1<<i)):
            norm=e.normalize(active,forced)
            if norm is None:continue
            q,r=norm
            if (q,r) in seen:continue
            seen.add((q,r));v=e.value(q)
            if not any(e.degrees(q).values()):
                assert valid(d,q)
                if v>bestval:best,bestval=q,v
                continue
            b=e.upper(q)
            if b>bestval:children.append((-b,q,r))
        front.extend(sorted(children,reverse=True))
    hi=max([bestval]+[-u for u,_,_ in front]);assert valid(d,best)
    return dict(value=bestval,mask=hex(best),upper=hi,certified=hi==bestval,
                init_value=init_value,init_calls=init,normalizations=e.norm_calls,
                raw_closure_calls=e.calls-init,support_checks=e.support_checks,
                bound_calls=e.bound_calls,forced_scans=e.forced_scans,forced_added=e.forced_added,
                component_scans=e.component_scans,components_solved=e.components_solved,
                enum_masks=e.enum_masks,enum_clause_checks=e.enum_clause_checks,cache_hits=e.cache_hits,
                gate_calls=e.gate_calls,gate_skips=e.gate_skips,expansions=steps,ms=(perf_counter()-t)*1000)

def run():
    t=perf_counter();rows=[]
    for planted in (False,True):
        for n in SIZES:
            for f in FAMILIES:
                for s in SEEDS:
                    d=instance(f,s,n,planted);arms={k:solve(d,k) for k in ARMS}
                    lo=max(a['value'] for a in arms.values());hi=min(a['upper'] for a in arms.values());assert lo<=hi
                    assert all(valid(d,int(a['mask'],16)) and a['normalizations']<=CAP for a in arms.values())
                    rows.append(dict(planted=planted,n=n,family=f,seed=s,arms=arms,pooled_lower=lo,pooled_upper=hi))
            print('done',planted,n,flush=True,file=__import__('sys').stderr)
    return dict(schema='MIC-09/public-structural/v1',cap=CAP,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),rows=rows,elapsed_s=perf_counter()-t)
if __name__=='__main__':print(json.dumps(run(),sort_keys=True,indent=2))
