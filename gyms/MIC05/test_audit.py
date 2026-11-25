from audit import threshold,exact_jump,scc_repair
from run import root,FAMILIES,fixed,best_jump,valid,prune,jump
from itertools import product


def test_threshold_oracle():
    for f in FAMILIES:
        for s in range(8):
            d=root(f,s,6);p,_=fixed(d,True)
            for t in (1,2,3):
                feasible=[]
                for bits in product((0,1),repeat=len(p)):
                    if valid(d,tuple(v-t*b for v,b in zip(p,bits))):feasible.append({i for i,b in enumerate(bits) if b})
                S,_=threshold(d,p,t);assert set(S)==set().union(*feasible) and set(S) in feasible
            assert exact_jump(d,p)[0][0]==best_jump(d,p)
            assert scc_repair(d,p)[0]==fixed(d,False)[0]


def test_largest_block_not_best_jump():
    d=(((9,0),(0,5)),(1,1));p=(19,3)
    S,_=prune(d,p);q,_=jump(d,p,S)
    assert S==(0,1) and sum(p)-sum(q)==2
    assert exact_jump(d,p)[0]==(9,9,(0,))
