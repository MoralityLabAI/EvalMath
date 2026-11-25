"""Exploratory matched-deck dependency-index control for CFH-14."""
import argparse,json,random
from collections import defaultdict
from itertools import product
from pathlib import Path
from time import thread_time_ns as clock
from pilot import Live,Predictor,Deck,bits,read,new_decks,graph_key,known_coeff,replay,CAPS

class Indexed(Live):
    def __init__(self,cards):
        super().__init__(cards);t=clock();self.dep=[];self.full_need=[]
        for row in self.needs:
            d=defaultdict(int)
            for i,need in enumerate(row):
                if need:d[need]|=1<<i
            self.dep.append(tuple(d.items()));mask=0
            for need in d:mask|=need
            self.full_need.append(mask)
        self.setup_ns+=clock()-t
    def state(self,S,B,values,a):
        masks=[m&S for m in self.cheap[a]]
        if not B and S==self.full:return masks,self.full_need[a]
        p=len(masks);need=0
        for dep,rs in self.dep[a]:
            active=S&rs
            if not active:continue
            missing=dep&~B;need|=missing
            if missing:continue
            for i in bits(active):
                c,ts=self.expr[a][i];masks[(c+sum(w*values[j] for j,w in ts))%p]|=1<<i
        return masks,need

def main():
    p=argparse.ArgumentParser();p.add_argument('--train',required=True);p.add_argument('--prior',nargs='+',required=True);p.add_argument('--out',required=True);p.add_argument('--decks',type=int,default=4);args=p.parse_args()
    used=set();train=read(args.train)['profiles'];pred=Predictor(train,False)
    for path in [args.train,*args.prior]:
        r=read(path);ds=[z[1] if len(z)==2 else z[2] for z in r['manifest']] if 'manifest' in r else [d['cards'] for d in r.get('decks',r.get('eval_decks',[]))]
        for cs in ds:
            for n,e in cs:used.add(graph_key((n,tuple(map(tuple,e)))))
    prior=len(used);manifest=list(new_decks(used,args.decks));rows=[];dec=[];meta=[];checks=0
    for i,cards in manifest:
        # Alternate setup order to reduce systematic order effects. Clear sparse
        # identity cache before each setup; no evaluator data in the policy.
        objects={}
        for name,cls in (('scan',Live),('index',Indexed))[::(-1 if i%2 else 1)]:
            known_coeff.cache_clear();objects[name]=cls(cards)
        a,b=objects['scan'],objects['index'];oracle=Deck(cards)
        assert a.needs==b.needs==oracle.rneeds
        rng=random.Random(14000+i)
        # Compare partially bought states, including missing coefficients.
        for _ in range(300):
            S=rng.getrandbits(a.n) or 1;B=rng.getrandbits(len(a.owner));v={j:oracle.values[j] for j in bits(B)};q=rng.randrange(len(a.probes));assert a.state(S,B,v,q)==b.state(S,B,v,q);checks+=1
        orders=list(product(CAPS,('free','shortlist_basic'),('scan','index')));rng.shuffle(orders)
        for cap,arm,kind in orders:
            obj=objects[kind];rr,dd=replay(obj,oracle,pred,cap,arm)
            rows.extend(dict(deck=i,cap=cap,arm=arm,kind=kind,setup_ns=obj.setup_ns,**r) for r in rr);dec.extend(dict(deck=i,cap=cap,arm=arm,kind=kind,**r) for r in dd)
        meta.append(dict(deck=i,setup_ns={k:v.setup_ns for k,v in objects.items()},oracle_checks=dict(oracle.audit),dependency_bins=sum(len(v) for v in b.dep)))
        print('deck',i,'rows',len(rows),flush=True)
    summary=[]
    for cap,arm,kind in product(CAPS,('free','shortlist_basic'),('scan','index')):
        rr=[r for r in rows if (r['cap'],r['arm'],r['kind'])==(cap,arm,kind)];n=len(rr)
        summary.append(dict(cap=cap,arm=arm,kind=kind,n=n,hits=sum(r['hit'] for r in rr),over=sum(r['over'] for r in rr),cold_hits=sum(r['hit'] and r['elapsed_ns']+r['setup_ns']<=cap*1000 for r in rr),mean_us=sum(r['elapsed_ns'] for r in rr)/n/1000,mean_plan_us=sum(r['plan_ns'] for r in rr)/n/1000,mean_buy_us=sum(r['buy_ns'] for r in rr)/n/1000))
    Path(args.out).write_text(json.dumps(dict(evidence='exploratory matched-deck dependency index; public development',manifest=manifest,prior_graph_hashes=prior,state_equivalence_checks=checks,summary=summary,records=rows,decisions=dec,meta=meta),separators=(',',':')))
if __name__=='__main__':main()
