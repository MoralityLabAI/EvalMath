from run import *

def test_closure_and_bound():
    for f in FAMILIES:
        d=root(f,13,7);e=Engine(d);tab=exact_table(d)
        for s in range(128):
            q=e.close(s);assert q&~s==0 and tab[q]==tab[s]
            brute=max(e.value(x) for x in range(128) if x&~s==0 and valid(d,x))
            assert tab[s]==brute and e.upper(s)>=brute

def test_search():
    for f in FAMILIES:
        d=root(f,21,9);gold=int(exact_table(d)[-1]);net=Ranker()
        for p in ('bound','loss','best_first','learned'):
            for cap in (0,2,16,10000):
                a=search(d,p,net,cap=cap)
                assert a['closure_calls']<=cap and valid(d,int(a['mask'],16))
                assert a['value']<=gold<=a['upper']
                assert not a['certified'] or a['value']==gold
                if cap==10000:assert a['certified'] and a['value']==gold

def test_teacher():
    for f in FAMILIES:assert teacher(root(f,27,8))

def test_include_exclude():
    from audit import include_search
    for f in FAMILIES:
        for seed in range(3):
            d=root(f,seed,9);gold=int(exact_table(d)[-1]);a=include_search(d,10000)
            assert a['certified'] and a['value']==gold and valid(d,int(a['mask'],16))
            for cap in (0,2,16):
                a=include_search(d,cap);assert a['closure_calls']<=cap and a['value']<=gold<=a['upper']
