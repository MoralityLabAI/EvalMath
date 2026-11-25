"""CFH-06: finite route identification with charged acquisition, public development."""
from functools import cache
from itertools import combinations
from math import comb, prod
from collections import Counter
from pathlib import Path
import json, sys
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent/'CFH05'))
sys.path.insert(0,str(here.parent/'cfh05_dev'))
from compositional import routes, predict, make_deck
DEPTH=3
CAPS=(0,18,39,68,100,204)
Q=4
ARMS=('eager','lazy','symbolic_lazy','symbolic_only','lazy_recheck','symbolic_recheck','lazy_terminal','symbolic_terminal')

@cache
def known_coeff(g,key):
    """Exact sparse coefficient identities; absent entries are unknown."""
    l,r,c,inv=key;n,edges=g;n-=l+r
    E={(a-l,b-l) for a,b in edges if l<=a<b<n+l}
    if c:E=set(combinations(range(n),2))-E
    m=len(E);ds=[0]*n
    for a,b in E:ds[a]+=1;ds[b]+=1
    z={}
    def put(k,v):
        if k in z:assert z[k]==v
        z[k]=v
    if inv in ('independence','clique'):
        put(0,1);put(1,n);put(2,comb(n,2)-m if inv=='independence' else m)
        put(n,int(m==0 if inv=='independence' else m==comb(n,2)))
    elif inv=='matching':
        put(0,1);put(1,m);put(2,comb(m,2)-sum(comb(d,2) for d in ds))
        for k in range(n//2+1,n+1):put(k,0)
    elif inv=='chromatic':
        tri=sum((a,b) in E and (a,c) in E and (b,c) in E for a,b,c in combinations(range(n),3))
        put(0,0);put(n,1);put(n-1,-m);put(n-2,comb(m,2)-tri)
    elif inv=='domination':
        put(0,0);put(1,sum(d==n-1 for d in ds));put(n,1);put(n-1,n-sum(d==0 for d in ds))
    else:raise ValueError(inv)
    return n,z

def cheap_value(g,r,k,p):
    n,z=known_coeff(g,r[:4]);d,s=r[4:];v=0
    for j in range(k+d,n+1):
        a=(prod(range(j-d+1,j+1))*comb(j-d,k)*pow(s,j-d-k,p))%p
        if a:
            if j not in z:return None
            v=(v+a*z[j])%p
    return v

class Deck:
    def __init__(self,cards):
        self.cards=cards;self.rr=routes(DEPTH);self.n=len(self.rr);self.full=(1<<self.n)-1
        self.keys=tuple(sorted({r[:4] for r in self.rr}));self.k=len(self.keys)
        idx={k:i for i,k in enumerate(self.keys)};self.group=[0]*self.k
        for j,r in enumerate(self.rr):self.group[idx[r[:4]]]|=1<<j
        self.probes=[(h,k,p) for h,g in enumerate(cards) for k in range(g[0]+1) for p in (2,3,5)]
        # Environment-owned truth tables. Exact masks exposed to policy only
        # through the purchased group restriction. Offline logical-cost emulator.
        self.truth=[];self.cheap=[];self.cheap_checks=0;self.cheap_known=0
        gold=[[predict(g,r) for r in self.rr] for g in cards]
        for h,k,p in self.probes:
            t=[0]*p;a=[0]*p
            for j,r in enumerate(self.rr):
                v=gold[h][j][k]%p;t[v]|=1<<j
                z=cheap_value(cards[h],r,k,p);self.cheap_checks+=1
                if z is not None:
                    assert z==v;a[z]|=1<<j;self.cheap_known+=1
            self.truth.append(tuple(t));self.cheap.append(tuple(a))
        self.truth=tuple(self.truth);self.cheap=tuple(self.cheap)
        sig=[tuple(next(v for v,m in enumerate(t) if m>>j&1) for t in self.truth) for j in range(self.n)]
        cnt=Counter(sig);self.ceiling=sum(cnt[s]==1 for s in sig)

    @cache
    def coverage(self,bought):
        cov=[]
        for b in bought:
            s=0
            for j,m in enumerate(self.group):
                if b>>j&1:s|=m
            cov.append(s)
        return tuple(cov)

    def acquire(self,S,bought,left,mode):
        """Buy one card's surviving base groups, largest groups first if capped."""
        opts=[]
        for h,b in enumerate(bought):
            groups=[((S&m).bit_count(),j) for j,m in enumerate(self.group) if not b>>j&1 and S&m]
            if groups:
                groups.sort(key=lambda z:(-z[0],z[1]));take=groups[:left]
                opts.append((sum(v for v,j in take),-len(take),-h,take))
        if not opts:return bought,0,0
        choice=max(opts,key=lambda x:x[2] if mode=='eager' else x[:3])
        count,_,nh,take=choice;h=-nh;b=list(bought)
        for _,j in take:b[h]|=1<<j
        # Whole group cache makes all derived routes on that card available.
        vectors=sum(self.group[j].bit_count() for _,j in take)
        return tuple(b),len(take),vectors

    def known_masks(self,idx,bought,symbolic):
        h,k,p=self.probes[idx];cov=self.coverage(bought)[h]
        return tuple((t&cov)|(a if symbolic else 0) for t,a in zip(self.truth[idx],self.cheap[idx]))

    def choose(self,S,bought,asked,symbolic,last):
        n=S.bit_count();best=None;work=0
        for idx,(h,k,p) in enumerate(self.probes):
            if asked>>idx&1:continue
            masks=self.known_masks(idx,bought,symbolic)
            counts=[(S&m).bit_count() for m in masks];u=n-sum(counts);work+=1
            # Conservative expected elimination under uniform hidden class:
            # unknown hypotheses survive every reply, and each unknown truth
            # could produce the largest known cell.
            gain=n*n-(sum(v*(u+v) for v in counts)+u*(u+max(counts)))
            hits=sum(v==1 for v in counts) if u==0 else 0
            rank=(hits,gain,-u,-idx) if last else (gain,hits,-u,-idx)
            if gain>0 and (best is None or rank>best[0]):best=(rank,idx,masks,gain)
        return best,work

    def run(self,cap,mode):
        symbolic=mode.startswith('symbolic');bought=(0,)*len(self.cards);left=cap;acq=vec=0
        recheck=mode.endswith(('recheck','terminal'));terminal=mode.endswith('terminal')
        if mode=='eager':
            while left:
                b,c,v=self.acquire(self.full,bought,left,mode)
                if not c:break
                bought=b;left-=c;acq+=c;vec+=v
        sums=Counter();records=[]
        def visit(S,T,bought,left,asked,steps,acq,vec,scans,trace,retros):
            assert T and T&S==T and acq<=cap
            n=S.bit_count();remaining=Q-steps
            if n>1 and remaining:
                best,w=self.choose(S,bought,asked,symbolic,remaining==1);scans+=w
                # Lazy policies buy only when known probes have <50% conservative
                # expected elimination. All arms share exact probe scoring.
                while mode not in ('eager','symbolic_only') and left and n>1 and (best is None or best[3]*2<n*n or (terminal and remaining==1 and best[0][0]<n)):
                    b,c,v=self.acquire(S,bought,left,mode)
                    if not c:break
                    bought=b;left-=c;acq+=c;vec+=v
                    if recheck:
                        for idx,answer in trace:
                            masks=self.known_masks(idx,bought,symbolic);known=0
                            for m in masks:known|=m
                            S &= (~known | masks[answer]);retros+=1
                        assert T&S==T
                        n=S.bit_count()
                        if n==1:break
                    best,w=self.choose(S,bought,asked,symbolic,remaining==1);scans+=w
                if n>1 and best is not None:
                    _,idx,masks,gain=best;known=0
                    for m in masks:known|=m
                    unknown=S&~known
                    # Environment alone branches by true response. The policy
                    # never receives T or hidden identity as an input.
                    for v,t in enumerate(self.truth[idx]):
                        child=T&t
                        if child:visit(S&(unknown|masks[v]),child,bought,left,asked|(1<<idx),steps+1,acq,vec,scans,trace+[(idx,v)],retros)
                    return
            for j in range(self.n):
                if T>>j&1:
                    hit=n==1;assert not hit or S==1<<j
                    records.append(dict(hidden=j,hit=hit,remaining=n,base_calls=acq,route_vectors=vec,queries=steps,scans=scans,retros=retros,trace=trace))
        visit(self.full,self.full,bought,left,0,0,acq,vec,0,[],0)
        assert len(records)==self.n and len({r['hidden'] for r in records})==self.n
        for r in records:
            for k in ('hit','remaining','base_calls','route_vectors','queries','scans','retros'):sums[k]+=r[k]
        assert sums['hit']<=self.ceiling
        return dict(sums),records

def main():
    records=[];summary=[];meta=[];traces=[]
    for group,n in (('shift',8),('structured',4)):
        for i in range(n):
            seed=96000+i+(100 if group=='structured' else 0)
            d=Deck(make_deck(group,seed));meta.append(dict(group=group,seed=seed,ceiling=d.ceiling,keys=d.k,cards=d.cards,probes=d.probes,cheap_checks=d.cheap_checks,cheap_known=d.cheap_known))
            for cap in CAPS:
                for mode in ARMS:
                    if mode=='symbolic_only' and cap:continue
                    sums,rr=d.run(cap,mode)
                    records.append(dict(group=group,seed=seed,cap=cap,mode=mode,tasks=d.n,**sums))
                    traces.extend(dict(seed=seed,cap=cap,mode=mode,**r) for r in rr)
            print(group,i,'ceiling',d.ceiling,flush=True,file=sys.stderr)
            d.coverage.cache_clear()
    for cap in CAPS:
        for mode in ARMS:
            rows=[r for r in records if r['cap']==cap and r['mode']==mode]
            if not rows:continue
            count=sum(r['tasks'] for r in rows)
            summary.append(dict(cap=cap,mode=mode,tasks=count,hits=sum(r['hit'] for r in rows),**{'mean_'+k:sum(r[k] for r in rows)/count for k in ('remaining','base_calls','route_vectors','queries','scans','retros')}))
    return dict(evidence='public finite acquisition pilot; logical resources, no causal or latency claim',depth=DEPTH,query_budget=Q,meta=meta,summary=summary,records=records,traces=traces)
if __name__=='__main__':print(json.dumps(main(),indent=2))
