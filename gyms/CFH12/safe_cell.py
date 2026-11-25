"""Exploratory CFH-12: adaptive certified cell purchases, same development decks."""
import argparse, json, hashlib
from pathlib import Path
from collections import Counter, defaultdict
from itertools import product
from coefficients_joint import Deck, Planner, Free, bits, load, CAPS, PRICES, SCALE, hist_vectors, LIMIT
from certified import allocate_min, immediate

class Safe:
    def __init__(self,d,free,coupled):
        self.d=d;self.free=free;self.coupled=coupled;self.memo={};self.bounds={};self.stats=Counter()
    def hist(self,S,B,a,U):
        d=self.d;p=d.probes[a][2];out={(0,)*p}
        for g in d.groups:
            inds=[i for i in g if U>>i&1]
            if not inds:continue
            es=[]
            for i in inds:
                off,terms=d.expr[a][i]
                off=(off+sum(w*d.values[j] for j,w in terms if B>>j&1))%p
                es.append(((off,tuple((j,w) for j,w in terms if not B>>j&1)),(0,())))
            h=hist_vectors(tuple(es),p)
            if h is None:return None
            opts={tuple(z[v*p] for v in range(p)) for z in h};nxt=set()
            for x,y in product(out,opts):
                nxt.add(tuple(a+b for a,b in zip(x,y,strict=True)))
                if len(nxt)>LIMIT:return None
            out=nxt
        return out
    def lower(self,S,B,a,h):
        key=S,B,a,h
        if key in self.bounds:return self.bounds[key]
        d=self.d;cells=d.known(S,B,a);U=S&~sum(cells);u=U.bit_count();ks=tuple(m.bit_count() for m in cells)
        new=B|d.need(S,a,'cell');profiles=[]
        for K,k in zip(cells,ks,strict=True):
            guarantee=0
            if K and h==2:
                for q in range(len(d.probes)):
                    self.stats['second_scans']+=1
                    if d.need(K|U,q,'cell')&~new:continue
                    known=[m.bit_count() for m in d.known(K,B,q)]
                    guarantee=max(guarantee,sum(v==1 for v in known)-(k-sum(known)))
            profiles.append(tuple(max(int(k+z==1),guarantee-z,0) for z in range(u+1)))
        profiles=tuple(profiles);lo=allocate_min(profiles,u);v=lo
        if self.coupled:
            hist=self.hist(S,B,a,U);self.stats['hist_attempts']+=1
            if hist is None:self.stats['fallbacks']+=1
            else:
                z=tuple((U&m).bit_count() for m in d.truth[a]);assert z in hist
                self.stats['hist_checks']+=1;v=min(sum(row[z] for row,z in zip(profiles,x,strict=True)) for x in hist)
                assert v>=lo;self.stats['improved']+=v>lo
        # Offline audit only: true purchased first split and exact free continuation.
        actual=sum(self.free.plan(t,new,h-1)[0]//SCALE for t in d.actual(S,a))
        assert 0<=v<=actual
        self.stats['bounds']+=1;self.stats['tight']+=v==actual;self.stats['zero_missed']+=v==0<actual
        self.bounds[key]=v;return v
    def plan(self,S,B,left,h,p):
        if S.bit_count()==1:return SCALE,-1
        if not h:return 0,-1
        key=S,B,left,h,p
        if key not in self.memo:
            best=self.free.plan(S,B,h)
            for a in range(len(self.d.probes)):
                need=self.d.need(S,a,'cell')&~B;k=need.bit_count()
                if k>left:continue
                self.stats['action_scans']+=1
                if k:
                    v=SCALE*self.lower(S,B,a,h)-p*S.bit_count()*k
                elif h==2:
                    cells=[m for m in self.d.known(S,B,a) if m];assert sum(cells)==S
                    if len(cells)<2:continue
                    v=sum(self.plan(t,B,left,h-1,p)[0] for t in cells)
                else:continue
                if v>best[0]:best=v,a
            self.memo[key]=best
        return self.memo[key]

def play(d,safe,free,oracle,cap,p):
    rows=[];dec=[]
    def emit(S,B,h):
        for i in bits(S):rows.append(dict(hidden=i,hit=S.bit_count()==1,cost=B.bit_count(),queries=2-h,remaining=S.bit_count()))
        return SCALE if S.bit_count()==1 else 0
    def walk(S,B,left,h):
        if S.bit_count()==1 or h==0:return emit(S,B,h)
        v,a=safe.plan(S,B,left,h,p);inc=free.plan(S,B,h)[0];opt=oracle.plan(S,B,left,h,p)[0];assert inc<=v<=opt
        if a==-1:assert v==0;return emit(S,B,h)
        need=d.need(S,a,'cell')&~B;k=need.bit_count();new=B|need;assert k<=left
        cells=tuple(m for m in d.known(S,new,a) if m);assert cells==d.actual(S,a) and sum(cells)==S
        result=sum(walk(t,new,left-k,h-1) for t in cells)-p*S.bit_count()*k
        assert v<=result<=opt
        if k:
            assert v>inc
            dec.append(dict(h=h,cost=k,certificate=v,free=inc,realized=result,n=S.bit_count()))
        return result
    v=walk(d.full,0,cap,2);assert len(rows)==d.n and len({r['hidden'] for r in rows})==d.n
    assert v==sum(SCALE*r['hit']-p*r['cost'] for r in rows)
    assert all(r['cost']<=cap and r['queries']<=2 for r in rows)
    return rows,dec

def main():
    ap=argparse.ArgumentParser();ap.add_argument('source');ap.add_argument('--out',required=True);a=ap.parse_args();r=load(a.source)
    records=[];decisions=[];meta=[]
    for i,cs in r['manifest']:
        d=Deck(tuple((n,tuple(map(tuple,e))) for n,e in cs));free=Free(d);oracle=Planner(d,'cell');arms={x:Safe(d,free,x=='safe_coupled') for x in ('safe_independent','safe_coupled')}
        for cap,p,arm in product(CAPS,PRICES,arms):
            rr,dd=play(d,arms[arm],free,oracle,cap,p)
            records.extend(dict(deck=i,cap=cap,price=p,arm=arm,**z) for z in rr)
            decisions.extend(dict(deck=i,cap=cap,price=p,arm=arm,**z) for z in dd)
        meta.append(dict(deck=i,arms={x:dict(s.stats) for x,s in arms.items()}));print(meta[-1],flush=True)
    groups=defaultdict(list)
    for r0 in records:groups[r0['cap'],r0['price'],r0['arm']].append(r0)
    summary=[]
    for (cap,p,arm),rr in sorted(groups.items()):
        n=len(rr);hits=sum(z['hit'] for z in rr);cost=sum(z['cost'] for z in rr)
        summary.append(dict(cap=cap,price=p,arm=arm,n=n,hits=hits,cost=cost,mean_cost=cost/n,mean_utility=(SCALE*hits-p*cost)/(SCALE*n)))
    out=dict(evidence='exploratory public same-deck follow-up',source_receipt_sha256=hashlib.sha256(Path(a.source).read_bytes()).hexdigest(),source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),meta=meta,summary=summary,records=records,decisions=decisions);Path(a.out).write_text(json.dumps(out,separators=(',',':')))
if __name__=='__main__':main()
