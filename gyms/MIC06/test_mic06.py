from run import Root,root,valid,objective,closure,repair,exact,FAMILIES

def test_counterexample():
    d=Root((2,3),((0,1),),())
    assert valid(d,1) and valid(d,2) and not valid(d,3)
    assert closure(d,3)[0]==3 and exact(d)[0]==3

def test_closure_maximal():
    for f in FAMILIES:
        for seed in range(5):
            d=root(f,seed,6)
            for initial in (17,42,63):
                s,_=closure(d,initial)
                candidates=[x for x in range(64) if x&~initial==0 and all(not(x>>i&1) or x&js for i,js in d.support)]
                assert s in candidates and all(x&~s==0 for x in candidates)

def test_exact_independent():
    for f in FAMILIES:
        for seed in range(8):
            d=root(f,seed,7)
            options=[objective(d,s) for s in range(128) if valid(d,s)]
            assert exact(d)[0]==max(options)
            for r in (repair(d,d.weights),repair(d,lookahead=True)):
                assert valid(d,r['mask']) and r['value']==objective(d,r['mask'])<=max(options)

def test_disjunction():
    d=Root((10,2,3),((1,2),),((0,6),))
    assert valid(d,3) and valid(d,5) and not valid(d,1) and not valid(d,7)
    assert exact(d)[0]==13

def test_retrospective_controls():
    from audit import global_remove, dynamic_degree
    for f in FAMILIES:
        for seed in range(8):
            d=root(f,seed,7);best,_=exact(d)
            for a in (global_remove(d),dynamic_degree(d)):
                assert valid(d,a['mask']) and a['value']==objective(d,a['mask'])<=best
