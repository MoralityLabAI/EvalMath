from mic10 import *

def test_conditioning():
    for f in FAMILIES:
        for seed in range(3):
            d=instance(f,seed,16,'one_hub')
            rng=Random(seed+100003*16+1009*FAMILIES.index(f)+17);ids=list(range(16));rng.shuffle(ids)
            s=1<<ids[0];cs=parts(primal(d),((1<<16)-1)&~s)
            a=conditional(d,s,cs);assert verify_conditional(d,a)
            assert a['value']==int(exact_table(d)[-1])
            bad={**a,'upper':a['upper']+1};assert not verify_conditional(d,bad)

def test_crossing_disjunction():
    d=Root((7,3,4),(),((0,6),))
    try:conditional(d,1,[2,4])
    except ValueError:pass
    else:raise AssertionError('accepted crossing clause')
    assert parts(primal(d),6)==[6]

def test_elimination():
    for f in FAMILIES:
        for seed in range(8):
            d=root(f,seed,9);gold=int(exact_table(d)[-1])
            for p in ('degree','fill'):
                o,w,_=elimination_order(d,p);a=eliminate(d,o)
                assert a and a['width']==w and a['value']==gold and valid(d,int(a['mask'],16))
                assert verify_elimination(d,a)
                assert not verify_elimination(d,{**a,'upper':gold+1})

def test_boundary():
    d=Root((5,2,3,4),((0,1),(0,2)),((0,8),))
    a=conditional(d,1,[2,4,8]);assert a['value']==9 and verify_conditional(d,a)
    d=Root((1,2,3),((0,1),(1,2),(0,2)),())
    assert eliminate(d,[0,1,2],1) is None


def test_hybrid():
    for f in FAMILIES:
        d=root(f,91,9);a=hybrid(d);gold=int(exact_table(d)[-1])
        assert a['value']==a['upper']==gold and valid(d,int(a['mask'],16))
