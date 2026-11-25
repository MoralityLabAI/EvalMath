from itertools import product
from run import FAMILIES,root,fixed,valid,prune,jump,solve,best_jump,slack


def test_exhaustive_closure():
    for f in FAMILIES:
        for seed in range(8):
            d=root(f,seed,6);p,_=fixed(d,True);n=len(p)
            feasible=[]
            for bits in product((0,1),repeat=n):
                if valid(d,tuple(v-b for v,b in zip(p,bits))):
                    feasible.append({i for i,b in enumerate(bits) if b})
            union=set().union(*feasible);S,_=prune(d,p)
            assert set(S)==union and set(S) in feasible
            for mask in (set(range(0,n,2)),set(range(1,n,2))):
                B,_=prune(d,p,mask)
                assert set(B)==set().union(*(s for s in feasible if s<=mask))


def test_least_and_trap():
    d=(((0,8),(8,0)),(1,3));p,_=fixed(d,True)
    assert p==(13,14) and fixed(d,False)[0]==(10,11)
    assert solve(d,p)[0]==(10,11)
    for f in FAMILIES:
        for seed in range(16):
            d=root(f,seed,6);p,_=fixed(d,True);gold,_=fixed(d,False)
            assert solve(d,p)[0]==gold
            assert bool(prune(d,p)[0])==(p!=gold)
            assert prune(d,gold)[0]==()


def test_jump_and_bound():
    for f in FAMILIES:
        for seed in range(8):
            d=root(f,seed,6);p,_=fixed(d,True);B,_=prune(d,p);q,t=jump(d,p,B)
            assert valid(d,q) and sum(p)-sum(q)==t*len(B)
            assert sum(p)-sum(q)<=best_jump(d,p)
            if B:assert not valid(d,tuple(v-t-1 if i in B else v for i,v in enumerate(p)))


def test_arbitrary_feasible_start():
    # Non-fixed feasible certificates, including unequal slack and self dependencies.
    for a,b,c,e in product(range(3),repeat=4):
        d=(((a,b),(c,e)),(1,2));gold,_=fixed(d,False)
        for p in product(range(1,6),repeat=2):
            if valid(d,p):assert solve(d,p)[0]==gold
