from itertools import product
from run import FAMILIES,make,h,valid,initial,move,least,terminal,oracle,teacher,rollout
from block_audit import repair


def test_rounding_trap():
    d=(((0,8),(8,0)),(1,3))
    assert least(d)==(10,11)
    assert terminal(d)==(13,14)
    assert all(move(d,terminal(d),i)==terminal(d) for i in range(2))
    assert repair(d)[0]==least(d)


def test_oracle_against_bruteforce():
    for f in FAMILIES:
        for s in range(3):
            d=make(f,s,4);p=initial(d);V=oracle(d)
            for k in (0,1,2,3):
                objectives=[]
                for seq in product(range(4),repeat=k):
                    q=p
                    for i in seq:
                        new=move(d,q,i);assert valid(d,new) and sum(new)<=sum(q);q=new
                    objectives.append(sum(q))
                assert V(p,k)==min(objectives)


def test_scc_exact_and_teacher():
    for f in FAMILIES:
        for s in range(6):
            d=make(f,s,4);p=initial(d);V=oracle(d);rows=teacher(d,4)
            assert repair(d)[0]==least(d)
            for t,(_,mask,labels) in enumerate(rows):
                assert any(labels) and all(not y or m for m,y in zip(mask,labels))
                i=labels.index(True);q=move(d,p,i);assert V(p,4-t)==V(q,3-t);p=q


def test_budget():
    d=make('ring',8,5)
    for k in (1,2,4,8,16):
        for policy in ('sweep','residual','dependency','lookahead'):
            r=rollout(d,k,policy);assert len(r['order'])==k
            assert r['candidate_checks']==1+5*k+(25*(k-1) if policy=='lookahead' else 0)
            assert sum(least(d))<=sum(terminal(d))<=oracle(d)(initial(d),k)<=r['objective']
