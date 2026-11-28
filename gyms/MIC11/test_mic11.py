from mic11 import *
from run import root
from itertools import product


def test_forced_disjunction():
    d=Root((9,3,4),((1,2),),((0,6),));v=Residual(d)
    for s,r,expected in [(7,1,13),(3,1,12),(1,1,None),(7,6,None),(0,0,0)]:
        a=v.attempt(s,r);assert a is not None and a['value']==expected and verify(d,a)
        assert not verify(d,{**a,'value':999})


def test_exhaustive_residual():
    for f in FAMILIES:
        d=root(f,3,6);valid_masks=[p for p in range(64) if valid(d,p)]
        for assignment in product(range(3),repeat=6):
            s=sum(1<<i for i,x in enumerate(assignment) if x);r=sum(1<<i for i,x in enumerate(assignment) if x==2)
            gold=max((sum(d.w[i] for i in bits(p)) for p in valid_masks if not p&~s and not r&~p),default=None)
            a=Residual(d).attempt(s,r);assert a is not None and a['value']==gold,(f,s,r,gold,a)
            assert verify(d,a),(f,s,r,a)


def test_bounds_and_replay():
    for f in FAMILIES:
        for seed in range(4):
            d=root(f,seed,9);gold=max(sum(d.w[i] for i in bits(p)) for p in range(512) if valid(d,p))
            b=prior_solve(d,'both',cap=16);a=search(d,'baseline',cap=16)
            for k in ('value','upper','mask','normalizations','expansions'):assert a[k]==b[k]
            for mode in ('root','periodic','always'):
                a=search(d,mode,cap=16,width=3)
                assert a['value']<=gold<=a['upper'] and all(verify(d,c,3) for c in a['ve_receipts'])
                a=search(d,mode,cap=10000);assert a['value']==a['upper']==gold and all(verify(d,c) for c in a['ve_receipts'])


def test_caps():
    d=root('mixed',1,16)
    for c,k,a,w in [(1,10000,10,10),(10000,1,10,10),(10000,10000,0,10),(10000,10000,10,0)]:
        v=Residual(d,c,k,a,w);v.attempt((1<<16)-1,0)
        assert v.cells<=c and v.scans<=k and v.attempts<=a
        assert all(verify(d,q,w) for q in v.receipts)
