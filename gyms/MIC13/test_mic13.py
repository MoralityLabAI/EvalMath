from mic13 import *
from run import root
from core import exact_table
from itertools import product
from copy import deepcopy
import pytest


def test_propagation():
    for f in FAMILIES:
        d=root(f,4,6);c=Checker(d);all_masks=[p for p in range(64) if feasible(d,p)]
        for a in product(range(3),repeat=6):
            s=sum(1<<i for i,x in enumerate(a) if x);r=sum(1<<i for i,x in enumerate(a) if x==2)
            original={p for p in all_masks if not p&~s and not r&~p};out=c.unit(s,r)
            if out is None:assert not original
            else:
                q,t=out;assert original=={p for p in all_masks if not p&~q and not t&~p}


def test_full_and_partial():
    for f in FAMILIES:
        for seed in range(4):
            d=root(f,seed,9);gold=int(exact_table(d)[-1])
            for mode in MODES:
                for cap in (0,2,16,1024):
                    p=produce(d,mode,cap,width=3);v=Checker(d).check(p)
                    assert v['lower']<=gold<=v['upper']
                    if cap==1024:assert v['certified'] and v['lower']==gold


def test_component_and_ve():
    d=Root((5,2,3,4,8,3),((0,1),(2,3),(4,5)),((0,2),(2,8)))
    p=produce(d,'baseline');assert Checker(d).check(p)['lower']==int(exact_table(d)[-1])
    # Independent direct component checks exercise a proper disconnected block.
    c=Checker(d);assert c.component(63,0,3,2)==(62,2)
    for f in FAMILIES:
        d=root(f,22,10);p=produce(d,'periodic');assert Checker(d).check(p)['upper']==int(exact_table(d)[-1])


def test_tampering():
    d=root('mixed',17,12);p=produce(d,'baseline',cap=16);Checker(d).check(p)
    mutations=[]
    for k,v in [('upper',p['upper']+1),('value',p['value']+1),('mask','0x0'),('normalizations',p['normalizations']+2)]:
        q=deepcopy(p);q[k]=v;mutations.append(q)
    for i,n in enumerate(p['nodes']):
        if n['kind']=='branch':
            q=deepcopy(p);q['nodes'][i]['children']=n['children'][:1];mutations.append(q);break
    for i,n in enumerate(p['nodes']):
        if n['kind'] in ('pruned','open') and n['cliques']:
            q=deepcopy(p);q['nodes'][i]['cliques'].pop();mutations.append(q);break
    q=deepcopy(p);q['nodes'][0]['prop']=['0x0','0x0'];mutations.append(q)
    q=deepcopy(p);q['nodes'].append(deepcopy(q['nodes'][0]));mutations.append(q)
    for q in mutations:
        with pytest.raises(ValueError):Checker(d).check(q)
