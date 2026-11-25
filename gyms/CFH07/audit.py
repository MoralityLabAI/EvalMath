"""Replay CFH-06 terminal policy with independently built truth tables."""
import copy, gzip, json, sys
from functools import cache
from itertools import combinations
from pathlib import Path
from collections import Counter
from transition import Env, verify
here = Path(__file__).resolve().parent
for p in ('CFH04','CFH05','CFH06','cfh04_dev','cfh05_dev','cfh06_dev'):
    sys.path.insert(0, str(here.parent/p))
from hidden_invariant import direct_coefficients
from lazy_acquisition import Deck, cheap_value

@cache
def independent_route(g,r):
    l,rt,c,inv,d,s=r;n,es=g;m=n-l-rt
    E={(a-l,b-l) for a,b in es if l<=a<b<n-rt}
    if c:E=set(combinations(range(m),2))-E
    a=direct_coefficients((m,tuple(sorted(E))))[inv]
    for _ in range(d):a=tuple(k*a[k] for k in range(1,len(a)))
    q=[0]
    for v in reversed(a):
        q=[s*q[0]+v]+[q[i-1]+s*q[i] for i in range(1,len(q))]+[q[-1]]
    return tuple((q+[0]*(n+1))[:n+1])

def build_env(d):
    ks={k:i for i,k in enumerate(d.keys)};t=[];c=[];gs=[];mod=[]
    for h,k,p in d.probes:
        truth=tuple(independent_route(d.cards[h],r)[k]%p for r in d.rr)
        cheap=tuple(cheap_value(d.cards[h],r,k,p) for r in d.rr)
        assert all(d.truth[len(t)][v]>>i&1 for i,v in enumerate(truth))
        t.append(truth);c.append(cheap);gs.append(tuple(h*d.k+ks[r[:4]] for r in d.rr));mod.append(p)
    e=Env(tuple(t),tuple(c),tuple(gs),tuple(mod),len(d.cards)*d.k);assert e.validate()==220
    return e

def generate(d,env,hidden,cap):
    S=d.full;bought=(0,)*len(d.cards);left=cap;asked=steps=0;trace=[];events=[]
    while S.bit_count()>1 and steps<4:
        best,_=d.choose(S,bought,asked,True,steps==3)
        while left and S.bit_count()>1 and (best is None or best[3]*2<S.bit_count()**2 or (steps==3 and best[0][0]<S.bit_count())):
            b,c,v=d.acquire(S,bought,left,'symbolic_terminal')
            if not c:break
            gs=[h*d.k+j for h,(old,new) in enumerate(zip(bought,b)) for j in range(d.k) if (new^old)>>j&1]
            assert c==len(gs);bought=b;left-=c
            for idx,answer in trace:
                masks=d.known_masks(idx,bought,True);S &= (~sum(masks)|masks[answer])
            events.append(dict(kind='buy',groups=gs,remaining=S))
            if S.bit_count()==1:break
            best,_=d.choose(S,bought,asked,True,steps==3)
        if S.bit_count()==1 or best is None:break
        _,idx,masks,_=best;answer=env.truth[idx][hidden]
        S &= (~sum(masks)|masks[answer]);trace.append((idx,answer));asked|=1<<idx;steps+=1
        events.append(dict(kind='observe',probe=idx,reply=answer,remaining=S))
    events.append(dict(kind='finish',claim=S.bit_length()-1 if S.bit_count()==1 else None,remaining=S))
    return events

def mutations(env,events,h,cap):
    variants=[]
    def add(label,i,key,value):
        x=copy.deepcopy(events);x[i][key]=value;variants.append((label,x,cap,4))
    add('mask',0,'remaining',events[0]['remaining']^(1<<h))
    add('promotion',-1,'claim',(h+1)%len(env.truth[0]))
    variants.append(('no_finish',events[:-1],cap,4))
    variants.append(('post_finish',events+[events[-1]],cap,4))
    for i,e in enumerate(events):
        if e['kind']=='buy':
            add('repeat_buy',i,'groups',e['groups']+[e['groups'][0]])
            add('bad_group',i,'groups',[env.n_groups]);variants.append(('base_budget',events,0,4));break
    for i,e in enumerate(events):
        if e['kind']=='observe':
            add('wrong_reply',i,'reply',(e['reply']+1)%env.moduli[e['probe']]);add('bad_probe',i,'probe',len(env.truth));variants.append(('query_budget',events,cap,0));break
    count=Counter()
    for label,v,b,q in variants:
        try:verify(env,v,h,b,q)
        except ValueError:count[label]+=1
        else:raise AssertionError(('accepted mutation',label))
    return count

def main():
    source=Path(sys.argv[1]) if len(sys.argv)>1 else here.parent/'cfh06_dev/receipt.json.gz'
    with gzip.open(source,'rt') as f: meta=json.load(f)['meta']
    counts=Counter();mut=Counter();results=[];decks=[];traces=[]
    for row in meta:
        cards=tuple((n,tuple(map(tuple,es))) for n,es in row['cards']);d=Deck(cards);env=build_env(d)
        counts['residue_comparisons']+=sum(map(len,env.truth));counts['known_residue_comparisons']+=sum(v is not None for r in env.cheap for v in r)
        decks.append(dict(seed=row['seed'],cards=cards,probes=d.probes,base_keys=d.keys))
        for cap in (39,100):
            s=Counter()
            for h in range(220):
                events=generate(d,env,h,cap);v=verify(env,events,h,cap,4)
                s.update(v);s['episodes']+=1;s['events']+=len(events)
                if h%11==0:mut.update(mutations(env,events,h,cap))
                traces.append(dict(seed=row['seed'],cap=cap,hidden_evaluator_only=h,events=events,verified=v))
            results.append(dict(seed=row['seed'],cap=cap,**s));counts['episodes']+=s['episodes'];counts['events']+=s['events'];counts['identified']+=s['identified']
        print(row['seed'],results[-2:],flush=True,file=sys.stderr)
        env.restrict.cache_clear();d.coverage.cache_clear();independent_route.cache_clear();direct_coefficients.cache_clear()
    return dict(schema='cfh07/public-development/v1',training_ready=False,counts=dict(counts),mutations=dict(mut),results=results,decks=decks,traces=traces)
if __name__=='__main__':print(json.dumps(main(),separators=(',',':')))
