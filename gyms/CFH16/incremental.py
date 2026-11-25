"""CFH-16: independently checked batch checkpointing under one logical fuel cap."""
import argparse, hashlib, json, sys
from collections import defaultdict
from dataclasses import dataclass
from itertools import product
from pathlib import Path
HERE=Path(__file__).resolve().parent
for name in ('CFH15','cfh15_dev'):
    sys.path.insert(0,str(HERE.parent/name))
from factored import Factored,choose,Deck,FULL,RR,bits,manifest
from fuel import Meter,Task,Exhausted,coefficient_task
CAPS=(30000,40000,50000,60000,90000)
ARMS=('uninterrupted','atomic_retry','checkpoint_retry')

@dataclass(frozen=True)
class Receipt:
    context:str
    group:int
    entries:tuple

class Verifier:
    """Reference belongs to the evaluator. Only candidate values are checked."""
    def __init__(self,live,oracle):
        self.context=hashlib.sha256(repr((live.refs,live.groups)).encode()).hexdigest()
        self.truth=tuple(oracle.values);self.owner=tuple(live.owner)
    def merge(self,cache,receipt,m):
        if receipt.context!=self.context or type(receipt.group) is not int or not receipt.entries:
            raise ValueError('batch identity')
        seen=set()
        for j,v in receipt.entries:
            m.tick('verification')
            if (type(j) is not int or type(v) is not int or not 0<=j<len(self.truth)
                or self.owner[j]!=receipt.group or j in seen or v!=self.truth[j]
                or (j in cache and cache[j]!=v)):
                raise ValueError('invalid batch')
            seen.add(j)
        # Charge the entire bounded update before mutating; no partial batch publication.
        m.tick('checkpoint',len(receipt.entries));cache.update(receipt.entries)


def attempt(live,verifier,S,values,data,m,checkpoint):
    """Return exact verified cache and partition, or cache and None on interruption."""
    original=dict(values);staged=dict(values);before=m.used;completed=0
    try:
        m.tick('acquisition',max(1,len(values)))
        B=sum(1<<j for j in values)
        _,need=live.state(S,B,values,data,m,'restriction');groups=defaultdict(int)
        for j in bits(need):m.tick('acquisition');groups[live.owner[j]]|=1<<j
        for group,mask in sorted(groups.items()):
            m.tick('acquisition');g,inv,cell=live.groups[group]
            ks=tuple(sorted(cell[j] for j in bits(mask)));whole=2*len(ks)>=len(cell)+1
            out=Task(coefficient_task(g,inv,ks,whole)).require(m,'acquisition')
            got=dict(enumerate(out)) if whole else dict(zip(ks,out,strict=True))
            entries=tuple((j,got[cell[j]]) for j in (cell if whole else bits(mask)))
            verifier.merge(staged,Receipt(verifier.context,group,entries),m);completed+=1
        m.tick('restriction',max(1,len(staged)));newB=sum(1<<j for j in staged)
        masks,missing=live.state(S,newB,staged,data,m,'restriction');assert not missing
        m.tick('restriction');children=tuple(t for t in masks if t);assert sum(children)==S
        return staged,children,dict(completed_batches=completed,new_cells=len(staged)-len(original),retained=len(staged)-len(original),fuel=m.used-before)
    except Exhausted:
        assert values==original
        retained=staged if checkpoint else original
        return retained,None,dict(completed_batches=completed,new_cells=len(staged)-len(original),retained=len(retained)-len(original),fuel=m.used-before)


def evaluate(cards,oracle,cap,arm):
    meter=Meter(cap);rows=[];decisions=[]
    def emit(S,values,h,m,reason):
        assert 0<=m.used<=cap and sum(m.ledger.values())==m.used
        assert all(v==oracle.values[j] for j,v in values.items())
        for i in bits(S):rows.append(dict(hidden=i,hit=S.bit_count()==1,remaining=S.bit_count(),queries=2-h,used=m.used,ledger=dict(m.ledger),cells=len(values),reason=reason))
    try:live=Factored(cards,meter,False)
    except Exhausted:emit(FULL,{},2,meter,'setup_exhausted');return rows,decisions
    verifier=Verifier(live,oracle)
    def walk(S,values,h,m,cache):
        if S.bit_count()==1 or not h or not m.left:emit(S,values,h,m,'terminal');return
        best,_,_=choose(live,S,sum(1<<j for j in values),values,cache,h,m,False)
        if best is None:emit(S,values,h,m,'no_query');return
        _,a,_=best;tries=1 if arm=='uninterrupted' else 2
        for step in range(tries):
            outer=m.cap
            if step==0 and tries==2:m.cap=m.used+m.left//2
            try:v,children,stats=attempt(live,verifier,S,values,cache[a],m,arm=='checkpoint_retry')
            finally:m.cap=outer
            assert all(v[j]==w for j,w in values.items()) and all(w==oracle.values[j] for j,w in v.items())
            decisions.append(dict(n=S.bit_count(),h=h,probe=a,attempt=step,committed=children is not None,**stats));values=v
            if children is not None:
                assert children==oracle.actual(S,a)
                for child in children:walk(child,values,h-1,m.fork(),cache.copy())
                return
        emit(S,values,h,m,'transaction_exhausted')
    walk(FULL,{},2,meter,{})
    assert len(rows)==len(RR) and len({r['hidden'] for r in rows})==len(RR)
    return rows,decisions


def cutoff_audit(cards,oracle):
    # Diagnostic: largest dependency query selected using only symbolic information.
    m=Meter(1000000);live=Factored(cards,m,False);v=Verifier(live,oracle);cache={};candidates=[]
    for a in live.order:
        data=live.compile_shared(a,m,cache);_,need=live.state(FULL,0,{},data,m,'selection')
        if need:candidates.append((need.bit_count(),a,data))
    _,a,data=max(candidates,key=lambda x:x[0]);full=Meter(1000000);baseline,ch,_=attempt(live,v,FULL,{},data,full,True)
    assert ch==oracle.actual(FULL,a)
    checks=partial=atomic_success=checkpoint_success=0
    for total in (full.used,full.used*5//4,full.used*3//2):
        for cut in sorted({0,1,*[total*k//20 for k in range(1,20)]}):
            for mode in (False,True):
                m=Meter(total);m.cap=cut;c,first,_=attempt(live,v,FULL,{},data,m,mode)
                if first is None:
                    assert mode or not c;partial+=bool(mode and c);m.cap=total
                    c,first,_=attempt(live,v,FULL,c,data,m,mode)
                assert m.used<=total and sum(m.ledger.values())==m.used and all(w==oracle.values[j] for j,w in c.items())
                if first is not None:
                    assert first==ch
                    if mode:checkpoint_success+=1
                    else:atomic_success+=1
                checks+=1
    j=next(iter(baseline));group=live.owner[j];wrong=(group+1)%len(live.groups)
    bad=[Receipt(v.context,group,((j,baseline[j]+1),)),Receipt(v.context,wrong,((j,baseline[j]),)),Receipt(v.context,group,((j,baseline[j]),(j,baseline[j]))),Receipt('wrong',group,((j,baseline[j]),))]
    for receipt in bad:
        c={};m=Meter(1000)
        try:v.merge(c,receipt,m)
        except ValueError:assert c=={}
        else:raise AssertionError('accepted corrupted receipt')
    return dict(cutoff_checks=checks,partial_retention=partial,atomic_success=atomic_success,checkpoint_success=checkpoint_success,mutations=len(bad),full_fuel=full.used,probe=a)


def main():
    p=argparse.ArgumentParser();p.add_argument('--prior',nargs='+',required=True);p.add_argument('--out',required=True);p.add_argument('--decks',type=int,default=4);a=p.parse_args()
    old,ds=manifest(a.prior,a.decks);rows=[];dec=[];audit=[]
    for i,cards in ds:
        oracle=Deck(cards);audit.append(dict(deck=i,**cutoff_audit(cards,oracle),reference=dict(oracle.audit)))
        for cap,arm in product(CAPS,ARMS):
            rr,dd=evaluate(cards,oracle,cap,arm);rows.extend(dict(deck=i,cap=cap,arm=arm,**r) for r in rr);dec.extend(dict(deck=i,cap=cap,arm=arm,**r) for r in dd)
        print('deck',i,'audit',audit[-1],flush=True,file=sys.stderr)
    summary=[]
    for cap,arm in product(CAPS,ARMS):
        rr=[r for r in rows if (r['cap'],r['arm'])==(cap,arm)];dd=[r for r in dec if (r['cap'],r['arm'])==(cap,arm)]
        summary.append(dict(cap=cap,arm=arm,n=len(rr),hits=sum(r['hit'] for r in rr),mean_fuel=sum(r['used'] for r in rr)/len(rr),attempts=len(dd),interruptions=sum(not d['committed'] for d in dd),partial_batches=sum(d['completed_batches'] for d in dd if not d['committed']),retained_on_interrupt=sum(d['retained'] for d in dd if not d['committed']),resumed_observations=sum(d['attempt']==1 and d['committed'] for d in dd)))
    Path(a.out).write_text(json.dumps(dict(evidence='public deterministic logical fuel pilot; external verified reference',prior_graph_hashes=old,manifest=ds,audit=audit,summary=summary,records=rows,decisions=dec),separators=(',',':')))
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
