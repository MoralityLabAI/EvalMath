"""Small exact checks of replay actions and history controls."""
from copy import deepcopy
from collections import Counter
import os,sys
from pathlib import Path
from mic14 import *
from cost14 import CostReplay,BUDGET
sys.path.insert(0,os.environ.get('MIC13_SOURCE',str(Path(__file__).parent.parent/'MIC13')))
from mic13 import produce,Checker
from core import Root
from run import root


def explicit_endpoints(replay,front,perm,first,budget=None):
    """Enumerate all allowed sequences of length one/two; independently form frontier."""
    def reveal(f,p,i):
        m={j:u for j,u in f};cap=m.pop(i);node=replay.nodes[i];u=min(cap,replay.bounds[i]);k=node['kind']
        if k=='branch' and u>replay.lower:m.update({j:u for j in node['children']})
        if k=='open':p=max(p,u)
        return tuple(sorted(m.items())),p
    def ub(f,p):return max([replay.lower,p]+[u for _,u in f])
    f,p=reveal(front,perm,first);choices=sorted(f,key=lambda z:(-z[1],-replay.weights[z[0]],z[0]))
    if budget is not None:choices=[x for x in choices if replay.cost[x[0]]+replay.cost[first]<=budget]
    endpoints=[ub(f,p)]
    for j,_ in choices[:C]:
        f2,p2=reveal(f,p,j);endpoints.append(ub(f2,p2))
    return ub(front,perm)-min(endpoints)


def test_oracle_and_bounds():
    decisions=0
    for fam in ('conflict','mixed','implication','disjunction'):
        for seed in (17,23):
            d=root(fam,seed,10);proof=produce(d,'baseline',cap=64);check=Checker(d).check(proof)
            for cls in (Replay,CostReplay):
                r=cls(d,proof);f=((0,r.total),);p=0
                while f:
                    old=r.upper(f,p);cs=r.candidates(f) if cls is Replay else r.eligible(f,BUDGET)
                    for i,_ in cs:
                        g=r.utility(f,p,i) if cls is Replay else r.budget_gain(f,p,i)
                        assert g==explicit_endpoints(r,f,p,i,None if cls is Replay else BUDGET)
                        assert 0<=g<=old-r.lower;decisions+=1
                    i,_=r.candidates(f)[0];f,p=r.step(f,p,i);assert r.upper(f,p)<=old
                assert check['lower']<=r.upper(f,p)<=check['upper']
    assert decisions>0


def test_shuffle_and_masks():
    r=dict(history=[[float(i)]*15 for i in range(H)],root=['conflict','original',32,1],mode='baseline',step=8,candidates=[[0.]*11,[1.]*11],common=[0.]*5,gains=[1,0],total=10)
    for s in SEEDS:
        h=order_history(r,s,'shuffle');assert h[-1]==r['history'][-1] and Counter(map(tuple,h))==Counter(map(tuple,r['history']))
        assert order_history(r,s,'shuffle')==h
    hh,c,x,m,g=tensorize([r],17,'ordered');assert tuple(m[0].tolist())==(True,True,False,False)
    net=Model();assert all(net(hh,c,x,m,a)[0,2:].isneginf().tolist()==[True,True] for a in ARMS)


def test_budget_excludes_expensive_second_reveal():
    d=Root((8,7,6),((0,1),(1,2),(0,2)),());proof=produce(d,'baseline',cap=32);Checker(d).check(proof);r=CostReplay(d,proof)
    f=((0,r.total),);p=0
    for i,_ in r.eligible(f,BUDGET):
        assert r.budget_gain(f,p,i)==explicit_endpoints(r,f,p,i,BUDGET)
    assert r.eligible(f,min(r.cost)-1)==[]


def test_family_split_and_metadata():
    assert not set(TRAIN)&set(DEV)
    assert set(TRAIN+DEV)=={'conflict','mixed','implication','disjunction'}
