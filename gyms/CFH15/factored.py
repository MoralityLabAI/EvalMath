"""CFH-15B: exploratory factored symbolic setup and guarded acquisition."""
import argparse,json
from collections import defaultdict
from fractions import Fraction
from itertools import combinations,product
from math import comb,prod
from pathlib import Path
from pilot import Live,RR,KEYS,FULL,CAPS,Deck,bits,Meter,Exhausted,manifest,evaluate

ARMS=('lazy_scan','lazy_index','factored_scan','factored_index','factored_guard','factored_free')

class Factored(Live):
    def __init__(self,cards,m,index):
        self.index=index;self.groups=[];self.owner=[];self.refs={};self.ids={};self.probes=[]
        for h,(n,es) in enumerate(cards):
            transforms={}
            for key in KEYS:
                m.tick('setup');l,r,c,inv=key;k=n-l-r;tkey=l,r,c
                if tkey not in transforms:
                    E=set()
                    for a,b in es:
                        m.tick('setup')
                        if l<=a<b<n-r:E.add((a-l,b-l))
                    if c:
                        out=set()
                        for a,b in combinations(range(k),2):
                            m.tick('setup')
                            if (a,b) not in E:out.add((a,b))
                        E=out
                    deg=[0]*k
                    for a,b in sorted(E):m.tick('setup');deg[a]+=1;deg[b]+=1
                    t=0
                    for a,b,d in combinations(range(k),3):m.tick('setup');t+=(a,b) in E and (a,d) in E and (b,d) in E
                    pairs=univ=isolated=0
                    for d in deg:m.tick('setup');pairs+=comb(d,2);univ+=d==k-1;isolated+=d==0
                    transforms[tkey]=((k,tuple(sorted(E))),len(E),t,pairs,univ,isolated)
                base,e,t,pairs,univ,isolated=transforms[tkey]
                if inv in ('independence','clique'):
                    z={0:1,1:k,2:comb(k,2)-e if inv=='independence' else e,k:int(e==0 if inv=='independence' else e==comb(k,2))}
                elif inv=='matching':z={0:1,1:e,2:comb(e,2)-pairs,**{j:0 for j in range(k//2+1,k+1)}}
                elif inv=='chromatic':z={0:0,k:1,k-1:-e,k-2:comb(e,2)-t}
                else:z={0:0,1:univ,k:1,k-1:k-isolated}
                m.tick('setup',len(z));cell={};i=len(self.groups)
                for j in range(k+1):
                    m.tick('setup')
                    if j in z:continue
                    a=len(self.owner);self.owner.append(i);self.ids[h,key,j]=a;cell[a]=j
                self.groups.append((base,inv,cell));self.refs[h,key]=(k,z)
            for k,p in product(range(n+1),(2,3,5)):
                m.tick('setup');self.probes.append((h,k,p))
        m.tick('setup',len(self.probes));self.order=sorted(range(len(self.probes)),key=lambda a:(self.probes[a][1],self.probes[a][0],self.probes[a][2]))

    def compile_shared(self,a,m,cache):
        h,k,p=self.probes[a];cheap=[0]*p;expr=[];groups={}
        for i,r in enumerate(RR):
            m.tick('selection_compile');n,z=self.refs[h,r[:4]];d,s=r[4:];key=('weight',n,k,p,d,s)
            if key not in cache:
                weights=[]
                for j in range(k+d,n+1):
                    m.tick('selection_compile');w=prod(range(j-d+1,j+1))*comb(j-d,k)*pow(s,j-d-k,p)%p
                    if w:weights.append((j,w))
                cache[key]=tuple(weights)
            off=need=0;terms=[]
            for j,w in cache[key]:
                m.tick('selection_compile')
                if j in z:off=(off+w*z[j])%p
                else:
                    c=self.ids[h,r[:4],j];terms.append((c,w));need|=1<<c
            if not need:cheap[off]|=1<<i
            elif self.index:groups[need]=groups.get(need,0)|(1<<i)
            expr.append((off,need,tuple(terms)))
        m.tick('selection_compile');return tuple(cheap),tuple(expr),tuple(groups.items())


def choose(l,S,B,values,cache,h,m,free):
    n=S.bit_count();best=inc=None;scanned=0;cap=m.cap;m.cap=m.used+m.left*(2 if h==2 else 3)//(3 if h==2 else 4)
    try:
        for a in l.order:
            m.tick('selection')
            if a not in cache:cache[a]=l.compile_shared(a,m,cache)
            masks,need=l.state(S,B,values,cache[a],m,'selection');cs=[x.bit_count() for x in masks];u=n-sum(cs);scanned+=1
            if not need and max(cs)==n or need and free:continue
            gain=n*n-sum(v*(u+v) for v in cs)-u*(u+max(cs))
            primary=Fraction(gain,n*n) if h==2 else Fraction(min(len(cs)*4,4*sum(v==1 for v in cs)+u),4*n)
            score=primary*20/(20+need.bit_count())
            if score<=0:continue
            rank=(score,Fraction(gain,n*n),-need.bit_count(),-a)
            if best is None or rank>best[0]:best=rank,a,need
            if not need and (inc is None or rank>inc[0]):inc=rank,a,need
    except Exhausted:pass
    finally:m.cap=cap
    return best,inc,scanned


def play(cards,oracle,cap,arm):
    if arm.startswith('lazy'):return evaluate(cards,oracle,cap,arm)
    m=Meter(cap);rows=[];dec=[]
    def emit(S,m,h,reason):
        assert 0<=m.used<=m.cap and sum(m.ledger.values())==m.used
        for i in bits(S):rows.append(dict(hidden=i,hit=S.bit_count()==1,remaining=S.bit_count(),queries=2-h,used=m.used,ledger=dict(m.ledger),reason=reason))
    try:l=Factored(cards,m,arm!='factored_scan')
    except Exhausted:emit(FULL,m,2,'setup_exhausted');return rows,dec
    assert l.probes==list(oracle.probes) and len(l.owner)==len(oracle.values)
    def walk(S,B,values,h,m,cache):
        if S.bit_count()==1 or not h or not m.left:emit(S,m,h,'terminal');return
        best,inc,scanned=choose(l,S,B,values,cache,h,m,arm=='factored_free')
        if best is None:emit(S,m,h,'no_query');return
        choices=[best]
        if arm=='factored_guard' and best[2] and inc is not None:choices.append(inc)
        for i,(_,a,need) in enumerate(choices):
            before=m.used;old=values.copy();oldcap=m.cap
            # Charge failed work; reserve a quarter of remaining fuel for free fallback.
            if len(choices)==2 and i==0:m.cap=m.used+3*m.left//4
            try:
                new=l.acquire(need,values,m);m.tick('restriction',max(1,len(new)));newB=sum(1<<j for j in new)
                masks,missing=l.state(S,newB,new,cache[a],m,'restriction');assert not missing
                m.tick('restriction');children=tuple(t for t in masks if t)
            except Exhausted:
                assert values==old;dec.append(dict(n=S.bit_count(),h=h,probe=a,scanned=scanned,used=m.used,transaction_fuel=m.used-before,committed=False,fallback=i+1<len(choices)))
                continue
            finally:m.cap=oldcap
            assert values==old and all(new[j]==oracle.values[j] for j in new)
            assert children==oracle.actual(S,a) and sum(children)==S
            dec.append(dict(n=S.bit_count(),h=h,probe=a,scanned=scanned,used=m.used,transaction_fuel=m.used-before,committed=True,acquired=(newB&~B).bit_count(),fallback=bool(i)))
            for child in children:walk(child,newB,new,h-1,m.fork(),cache.copy())
            return
        emit(S,m,h,'transaction_exhausted')
    walk(FULL,0,{},2,m,{})
    assert len(rows)==len(RR) and len({r['hidden'] for r in rows})==len(RR)
    return rows,dec


def main():
    p=argparse.ArgumentParser();p.add_argument('--prior',nargs='+',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    old,ds=manifest(a.prior,4);rows=[];dec=[];meta=[];checks=0
    for i,cards in ds:
        oracle=Deck(cards);m=Meter(1000000);orig=Live(cards,m,True);n=Meter(1000000);fact=Factored(cards,n,True);cache={}
        assert orig.groups==fact.groups and orig.refs==fact.refs and orig.ids==fact.ids
        for q in orig.order:
            assert orig.compile(q,m,'selection_compile')==fact.compile_shared(q,n,cache);checks+=1
        meta.append(dict(deck=i,oracle_checks=dict(oracle.audit),scan_setup_and_compile=m.used,factored_setup_and_compile=n.used))
        for cap,arm in product(CAPS,ARMS):
            rr,dd=play(cards,oracle,cap,arm);rows.extend(dict(deck=i,cap=cap,arm=arm,**r) for r in rr);dec.extend(dict(deck=i,cap=cap,arm=arm,**r) for r in dd)
        print('deck',i,'checks',checks,'rows',len(rows),flush=True)
    summary=[]
    for cap,arm in product(CAPS,ARMS):
        rr=[r for r in rows if (r['cap'],r['arm'])==(cap,arm)];n=len(rr)
        summary.append(dict(cap=cap,arm=arm,n=n,hits=sum(r['hit'] for r in rr),mean_fuel=sum(r['used'] for r in rr)/n,over=sum(r['used']>cap for r in rr),setup_exhausted=sum(r['reason']=='setup_exhausted' for r in rr),transaction_exhausted=sum(r['reason']=='transaction_exhausted' for r in rr)))
    Path(a.out).write_text(json.dumps(dict(evidence='exploratory fresh public matched decks',manifest=ds,prior_graph_hashes=old,compile_checks=checks,summary=summary,records=rows,decisions=dec,meta=meta),separators=(',',':')))
if __name__=='__main__':main()
