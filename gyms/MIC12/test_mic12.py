from mic12 import *
from run import root
from core import exact_table


def test_local_teacher():
    for f in FAMILIES:
        d=root(f,19,8);e=Solver(d,True,True);tab=exact_table(d)
        s=e.close(e.full);u=e.upper(s);b=0
        lo,hi,calls=local_branch(d,s,0,u,b)
        assert lo<=int(tab[s])<=hi and calls<=TEACH_CAP
        t=teach(d,s,0,u,b)
        assert t['success'] and len(t['x'])==10
        assert t['target']==int(F(t['utility'])>0)


def test_gate_never_prunes_unverified():
    torch.manual_seed(7);net=Gate()
    for f in FAMILIES:
        for seed in range(3):
            d=root(f,seed,9);gold=int(exact_table(d)[-1])
            for cap in (0,16,1000):
                a=search(d,'learned',net=net,cap=cap)
                assert a['value']<=gold<=a['upper'] and valid(d,int(a['mask'],16))
                assert a['normalizations']<=cap and a['gate_yes']<=a['gate_calls']
                assert all(verify(d,r) for r in a['ve_receipts'])
                if cap==1000:assert a['certified'] and a['value']==gold


def test_inherited_policy_replay():
    from mic11 import search as old
    for f in FAMILIES:
        d=root(f,12,16)
        for mode in ('baseline','root','periodic','always'):
            a=search(d,mode,cap=32);b=old(d,mode,cap=32)
            for key in ('value','upper','mask','normalizations','ve_cells','ve_scans','ve_attempts','ve_receipts'):
                assert a[key]==b[key]


def test_attempt_budget():
    d=root('mixed',1,24);a=search(d,'learned',net=Gate(),cap=32,cell_cap=1,scan_cap=1,attempt_cap=1)
    assert a['ve_cells']<=1 and a['ve_scans']<=1 and a['ve_attempts']<=1
    assert valid(d,int(a['mask'],16))
