from fractions import Fraction as F
from itertools import product
from spiral_ln.evaluation_archival_provenance import (
    Source, Planner, Result, profiles, likelihood, exhaustive_likelihood,
    revocation_witness, brute_value,
)


def test_source_factor_matches_independent_complete_world_sum():
    for q,acc,quality in product((F(1,3),F(5,6)),(F(3,4),F(1)),(F(2,3),F(5,6))):
        s=Source(q,acc,audit=quality)
        for r,a,v,h in product((-1,0,1),(-1,0,1),(-1,0,1),(0,1)):
            o=(0,r,a,v)
            assert likelihood(s,o,h)==exhaustive_likelihood(s,o,h)


def test_revocation_and_duplicate_witness():
    w=revocation_witness()
    assert w['left_before']==w['right_before']==F(1,2)
    assert w['left_after']==F(1,6) and w['right_after']==F(5,6)
    assert w['left_after_naive_copies']==F(5,6) and w['right_after_naive_copies']==F(1,6)


def test_copy_count_irrelevant_to_correct_posterior():
    sources,_=next(profiles())
    for n in (1,2,3,10):
        p=Planner(sources,n)
        assert p.posterior(p.initial)==F(7,12)
    assert Planner(sources,10).posterior(Planner(sources,10).initial,True)>F(4,5)


def test_gate_legality_and_mass_conservation():
    sources,budget=next(profiles()); p=Planner(sources)
    assert (1,'fetch',1) not in p.actions(p.initial,budget)
    [(prob,nxt)]=p.transitions(p.initial,(1,'gate',1))
    assert prob==1 and p.posterior(nxt)==p.posterior(p.initial)
    assert (1,'fetch',1) in p.actions(nxt,budget-1)
    for a in p.actions(nxt,budget-1):
        assert sum(x for x,_ in p.transitions(nxt,a))==1


def test_exact_utility_independent_tree():
    samples=list(profiles())
    for i in (0,24,40,61):
        sources,_=samples[i]
        p=Planner(sources)
        assert p.run(3,'full').utility==brute_value(sources,3)


def test_budget_dominance_and_zero_budget():
    sources,_=next(profiles()); p=Planner(sources)
    assert p.run(0,'full')==p.run(0,'stop')
    for b in range(1,5):
        r=p.run(b,'full')
        assert r.correct+r.false+r.abstain==1 and r.spent<=b
        assert r.utility>=p.run(b,'macro').utility
        assert r.utility>=p.run(b-1,'full').utility
        assert r.false<=F(1,5)*(r.correct+r.false)
