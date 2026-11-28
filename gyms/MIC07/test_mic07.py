from run import *
from audit import clique_bound,strong

def test_subset_oracle():
    for f in FAMILIES:
        for seed in range(3):
            d=root(f,seed,6);table=exact_table(d)
            for s in range(64):
                gold=max(val(d,q) for q in range(64) if q&~s==0 and valid(d,q))
                assert table[s]==gold and clique_bound(d,s)>=gold

def test_branch_and_bound():
    for f in FAMILIES:
        for seed in range(5):
            d=root(f,seed,7);gold=int(exact_table(d)[-1]);a=strong(d,10000);b=branch(d,10000)
            assert a['certified_optimal'] and b['certified_optimal'] and a['value']==b['value']==gold
            assert valid(d,a['mask']) and valid(d,b['mask'])
            for budget in (16,32):
                for r in (strong(d,budget),branch(d,budget),greedy(d,'degree',budget=budget)):
                    assert r['calls']<=budget and valid(d,r['mask']) and r['value']<=gold

def test_teacher():
    for f in FAMILIES:
        d=root(f,9,7);table=exact_table(d);s,_=closure(d,127)
        for _,_,i,j,y in trajectory(d):
            q,_=closure(d,s&~(1<<i));r,_=closure(d,s&~(1<<j));a,b=table[q],table[r]
            assert y==float(b>a)+.5*float(a==b)
            assert max(a,b)==table[s];s=q if a>=b else r
        assert valid(d,s) and val(d,s)==table[-1]
