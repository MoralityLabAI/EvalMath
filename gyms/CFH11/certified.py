"""CFH-11: robust lower bounds on paid mathematical information, public development."""
import argparse, gzip, hashlib, json, random, sys
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
import networkx as nx
HERE=Path(__file__).resolve().parent
for p in ('CFH10','cfh10_dev','CFH09','cfh09_dev'):
    sys.path.insert(0,str(HERE.parent/p))
from cost_frontier import Online, Priced, Free, bits, SCALE, PRICES, CAPS, replay
from value_pilot import graph_key, graph_tuple

@lru_cache(maxsize=32768)
def allocate_min(profiles,u):
    dp=[0]+[10**9]*u
    for profile in profiles:
        dp=[min(dp[j]+profile[k-j] for j in range(k+1)) for k in range(u+1)]
    return dp[u]

@lru_cache(maxsize=32768)
def immediate(counts,u):
    return allocate_min(tuple(tuple(int(k+z==1) for z in range(u+1)) for k in counts),u)

class Safe:
    def __init__(self,o,free,mode):
        self.o=o;self.free=free;self.mode=mode;self.bounds={};self.memo={};self.scans=0;self.second_scans=0
    def lower(self,S,B,a,h):
        key=S,B,a,h
        if key in self.bounds:return self.bounds[key]
        o=self.o;cells=o.known(S,B,a);U=S&~sum(cells);u=U.bit_count();counts=tuple(x.bit_count() for x in cells)
        v=immediate(counts,u)
        if h==2 and self.mode!='immediate':
            new=B|o.need(S,a);profiles=[]
            for K,k in zip(cells,counts,strict=True):
                # A query free on K union U after acquisition is free on every
                # actual child. Each missing prediction can spoil one singleton.
                guarantee=0
                if K:
                    for q in range(len(o.probes)):
                        self.second_scans+=1
                        if o.need(K|U,q)&~new:continue
                        ks=[m.bit_count() for m in o.known(K,B,q)]
                        guarantee=max(guarantee,sum(x==1 for x in ks)-(k-sum(ks)))
                profiles.append(tuple(max(int(k+z==1),guarantee-z,0) for z in range(u+1)))
            v=max(v,allocate_min(tuple(profiles),u))
        self.bounds[key]=v;return v
    def plan(self,S,B,left,h,p):
        key=S,B,left,h,p
        if key in self.memo:return self.memo[key]
        n=S.bit_count()
        if n==1:return SCALE,-1
        if not h:return 0,-1
        best=self.free.plan(S,B,h)
        for a in range(len(self.o.probes)):
            need=self.o.need(S,a)&~B;k=need.bit_count()
            if k>left:continue
            self.scans+=1
            if k==0:
                if self.mode!='adaptive' or h!=2:continue
                cells=tuple(m for m in self.o.known(S,B,a) if m)
                assert sum(cells)==S
                if len(cells)<2:continue
                value=sum(self.plan(t,B,left,h-1,p)[0] for t in cells)
            else:value=SCALE*self.lower(S,B,a,h)-p*n*k
            if value>best[0]:best=value,a
        self.memo[key]=best;return best

def evaluate(o,oracle,free,safe,cap,p):
    records=[];decisions=[]
    def walk(S,B,left,h):
        n=S.bit_count();assert B.bit_count()+left==cap
        if n==1 or not h:
            for i in bits(S):records.append(dict(hidden=i,hit=n==1,cost=B.bit_count(),queries=2-h,remaining=n))
            return SCALE if n==1 else 0
        v,a=safe.plan(S,B,left,h,p);f,_=free.plan(S,B,h);opt=oracle.opt(S,B,left,h,p);assert f<=v<=opt
        if a==-1:
            assert v==0
            for i in bits(S):records.append(dict(hidden=i,hit=False,cost=B.bit_count(),queries=2-h,remaining=n))
            decisions.append(dict(n=n,h=h,action=-1,cost=0,certificate=v,free=f,realized=0,regret=opt));return 0
        need=o.need(S,a)&~B;k=need.bit_count();new=B|need;o.purchase(need)
        cells=tuple(m for m in o.known(S,new,a) if m);assert cells==tuple(S&m for m in oracle.truth[a] if S&m) and sum(cells)==S
        q=oracle.q(S,B,new,left-k,cells,h,p)
        if k:
            actual_free=sum(free.plan(t,new,h-1)[0] for t in cells)-p*n*k
            assert f<v<=actual_free<=q
        val=sum(walk(t,new,left-k,h-1) for t in cells)-p*n*k
        assert v<=val<=q
        decisions.append(dict(n=n,h=h,action=a,cost=k,certificate=v,free=f,realized=val,regret=opt-q));return val
    v=walk(o.full,0,cap,2);assert len(records)==o.n and len({r['hidden'] for r in records})==o.n
    assert v==sum(SCALE*r['hit']-p*r['cost'] for r in records)
    assert oracle.opt(o.full,0,cap,2,p)-v==sum(d['regret'] for d in decisions)
    return records,decisions

def new_decks(used):
    rng=random.Random(2026112511)
    for i in range(8):
        cards=[]
        for j in range(3):
            for _ in range(3000):
                n=rng.randrange(8,10);seed=rng.randrange(2**31)
                if j==0:g=nx.gnp_random_graph(n,rng.uniform(.2,.85),seed=seed)
                elif j==1:g=nx.from_prufer_sequence([rng.randrange(n) for _ in range(n-2)])
                else:g=nx.random_geometric_graph(n,rng.uniform(.25,.7),seed=seed)
                labels=list(range(n));rng.shuffle(labels);g=graph_tuple(nx.relabel_nodes(g,dict(enumerate(labels))));key=graph_key(g)
                if key not in used:used.add(key);cards.append(g);break
            else:raise RuntimeError('generator exhausted')
        yield i,tuple(cards)

def load(path):
    p=Path(path);raw=p.read_bytes();return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)

def audit_small():
    from itertools import product
    count=0
    for p in (2,3,5):
        for counts in product(range(3),repeat=p):
            for u in range(5):
                actual=min(sum(counts[j]+a.count(j)==1 for j in range(p)) for a in product(range(p),repeat=u))
                assert actual==immediate(counts,u);count+=1
    return count

def main():
    pa=argparse.ArgumentParser();pa.add_argument('--prior',nargs='+',required=True);pa.add_argument('--out',required=True);a=pa.parse_args()
    used=set()
    for path in a.prior:
        r=load(path);decks=r.get('decks',r.get('eval_decks',[]))
        if 'manifest' in r:decks=[{'cards':z[2]} for z in r['manifest']]
        for d in decks:
            for n,e in d['cards']:used.add(graph_key((n,tuple(map(tuple,e)))))
    prior=len(used);ds=list(new_decks(used));records=[];decisions=[];meta=[]
    for i,cards in ds:
        o=Online(cards,2);oracle=Priced(o);free=Free(o)
        arms={name:Safe(o,free,name) for name in ('immediate','pair','adaptive')}
        for cap in CAPS:
            for p in PRICES:
                for arm in ('exact','free_exact','priced_greedy',*arms):
                    if arm in arms:rr,dd=evaluate(o,oracle,free,arms[arm],cap,p)
                    else:rr,dd=replay(o,oracle,free,cap,p,arm)
                    records.extend(dict(deck=i,cap=cap,price=p,arm=arm,**r) for r in rr)
                    decisions.extend(dict(deck=i,cap=cap,price=p,arm=arm,**r) for r in dd)
        meta.append(dict(deck=i,oracle_scans=oracle.scans,free_scans=free.work,distinct_base_computations=o.misses,symbolic_checks=o.symbolic_checks,arms={a:dict(scans=s.scans,second_scans=s.second_scans,bounds=len(s.bounds)) for a,s in arms.items()}))
        oracle.options.cache_clear();oracle.opt.cache_clear();free.plan.cache_clear()
        print('deck',i,'records',len(records),flush=True,file=sys.stderr)
    groups=defaultdict(list)
    for r in records:groups[r['cap'],r['price'],r['arm']].append(r)
    summary=[]
    for (cap,p,arm),rr in sorted(groups.items()):
        n=len(rr);hits=sum(r['hit'] for r in rr);cost=sum(r['cost'] for r in rr)
        summary.append(dict(cap=cap,price=p,arm=arm,n=n,hits=hits,cost=cost,mean_cost=cost/n,utility_ticks=SCALE*hits-p*cost,mean_utility=(SCALE*hits-p*cost)/(SCALE*n)))
    out=dict(evidence='public finite development, robust lower-bound policy',scale=SCALE,prior_graph_hashes=prior,manifest=ds,small_allocation_checks=audit_small(),meta=meta,summary=summary,records=records,decisions=decisions,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    Path(a.out).write_text(json.dumps(out,separators=(',',':')))
if __name__=='__main__':main()
