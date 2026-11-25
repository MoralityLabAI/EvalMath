from mic09 import *
from audit import include_search

def test_propagation_exact():
    for f in FAMILIES:
        d=root(f,1,7);e=Solver(d,True,False)
        for s in range(128):
            for req in (0,s&85,s&42):
                feasible=[x for x in range(128) if not x&~s and not req&~x and valid(d,x)]
                q=e.propagate(s,req)
                if q is None:assert not feasible
                else:
                    a,b=q
                    assert all(not x&~a and not b&~x for x in feasible)

def test_factor_optimum_preservation():
    for f in FAMILIES:
        a=root(f,2,4);b=root(f,3,4)
        d=Root(a.w+b.w,a.edges+tuple((i+4,j+4) for i,j in b.edges),a.sup+tuple((i+4,s<<4) for i,s in b.sup))
        for req in (0,1,16,17):
            e=Solver(d,True,True);r=e.normalize(255,req)
            feasible=[x for x in range(256) if not req&~x and valid(d,x)]
            if r is None:assert not feasible
            else:
                s,q=r;remaining=[x for x in feasible if not x&~s and not q&~x]
                assert remaining and max(map(e.value,remaining))==max(map(e.value,feasible))

def test_search_small_exact():
    for f in FAMILIES:
        for seed in range(3):
            d=root(f,seed,9);gold=int(exact_table(d)[-1])
            for mode in ARMS:
                for cap in (0,2,16,4096):
                    r=solve(d,mode,cap)
                    assert valid(d,int(r['mask'],16)) and r['value']<=gold<=r['upper']
                    assert r['normalizations']<=cap
                    if cap==4096:assert r['certified'] and r['value']==gold

def test_mic08_baseline():
    for f in FAMILIES:
        for seed in range(3):
            d=root(f,seed,12);a=solve(d,'base',32);b=include_search(d,32)
            assert (a['value'],a['upper'],a['mask'],a['normalizations'])==(b['value'],b['upper'],b['mask'],b['closure_calls'])
