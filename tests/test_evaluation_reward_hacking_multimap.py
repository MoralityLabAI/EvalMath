"""RHT-06: exact integer-fibre activation and reachable reward-hacking tests."""
from fractions import Fraction as Q
from itertools import product, combinations

import pytest

from spiral_ln.evaluation_reward_hacking_multimap import (
    MultiMapSignals, primitive_integer_kernel_generators,
    bounded_kernel_differences, bounded_kernel_rank, gold_alias_report,
    minimum_private_audit, reachable_gold_alias,
    first_uniform_capacity_alias,
)
from spiral_ln.evaluation_leak_topology import (
    box, graph_from_sizes, margins_of,
)
from spiral_ln.evaluation_reward_hacking_topology import (
    hidden_gold_width, ugc_reachable_records,
)
from spiral_ln.unique_games_topology import Edge, TranslationGame


FIVE=((0,0,0),(0,0,1),(0,1,1),(1,0,1),(1,1,0))
SEPARATE=((0,),(1,),(2,))
PRIMITIVE=(1,-2,1,1,-1)


def three_map(capacities):
    return MultiMapSignals(FIVE,tuple(capacities),SEPARATE)


def independently_enumerate_fibre_pairs(space, gold):
    """Independent exhaustive records-and-margins oracle.

    Checks all pairs of records with equal observed margins, avoiding the
    difference-kernel enumeration used by the implementation under test.
    """
    m=space.matrix
    records=tuple(product(*(range(s+1) for s in space.capacities)))
    best=Q(0)
    witnesses=[]
    for i,hi in enumerate(records):
        yhi=tuple(sum(row[j]*hi[j] for j in range(len(hi))) for row in m)
        for lo in records[i:]:
            ylo=tuple(sum(row[j]*lo[j] for j in range(len(lo))) for row in m)
            if yhi!=ylo:
                continue
            delta=abs(sum((Q(t)*(a-b) for t,a,b in zip(gold,hi,lo)),Q(0)))
            if delta>best:
                best=delta
                witnesses=[(hi,lo)]
    return best,witnesses


def test_rational_nonzero_kernel_but_unit_capacity_no_integer_alias():
    s=three_map((1,)*5)
    assert s.rational_nullity==1
    assert primitive_integer_kernel_generators(s)==(PRIMITIVE,)
    assert bounded_kernel_differences(s)==((0,0,0,0,0),)
    assert bounded_kernel_rank(s)==0
    gold=(0,1,0,0,0)
    r=gold_alias_report(s,gold)
    assert r["rational_gold_observable"] is False
    assert r["bounded_gold_observable"] is True
    assert r["rational_periods"]==(-2,)
    assert r["maximum_hidden_gold_width"]==0
    assert r["number_bounded_differences"]==1
    assert independently_enumerate_fibre_pairs(s,gold)[0]==0
    assert minimum_private_audit(s,gold)["count"]==0


def test_one_additional_item_activates_hidden_gold_reward_hack():
    s=three_map((1,2,1,1,1))
    z=bounded_kernel_differences(s)
    assert set(z)=={
        (0,0,0,0,0),PRIMITIVE,
        tuple(-u for u in PRIMITIVE)
    }
    assert bounded_kernel_rank(s)==1
    gold=(0,1,0,0,0)
    r=gold_alias_report(s,gold)
    assert r["maximum_hidden_gold_width"]==2
    assert r["rational_nullity"]==1
    assert r["bounded_integer_rank"]==1
    assert r["rational_gold_observable"] is False
    assert r["bounded_gold_observable"] is False
    assert r["high_record"]==(0,2,0,0,1)
    assert r["low_record"]==(1,0,1,1,0)
    assert s.feedback(r["high_record"])==s.feedback(r["low_record"])
    assert independently_enumerate_fibre_pairs(s,gold)[0]==2
    assert minimum_private_audit(s,gold)["count"]==1
    assert minimum_private_audit(s,gold,tolerance=2)["count"]==0
    assert minimum_private_audit(s,gold,tolerance=1)["count"]==1


def test_capacity_threshold_is_exactly_two():
    initial=three_map((1,)*5)
    first=first_uniform_capacity_alias(initial,(0,1,0,0,0),
                                        max_capacity=2)
    assert first["uniform_capacity"]==2
    assert first["witness"]["maximum_hidden_gold_width"]==2
    exact_gold=(1,1,1,1,1)
    assert first_uniform_capacity_alias(initial,exact_gold,
                                        max_capacity=2) is None


def test_higher_order_full_two_by_two_by_two_pairwise_feedback():
    cells=tuple(product((0,1),repeat=3))
    faces=((0,1),(0,2),(1,2))
    s=MultiMapSignals(cells,(1,)*8,faces)
    assert s.rational_nullity==1
    gen=primitive_integer_kernel_generators(s)
    assert len(gen)==1
    assert all(abs(x)==1 for x in gen[0])
    assert bounded_kernel_rank(s)==1
    r=gold_alias_report(s,(1,0,0,0,0,0,0,0))
    assert r["maximum_hidden_gold_width"]==1
    assert r["bounded_gold_observable"] is False
    assert minimum_private_audit(s,(1,0,0,0,0,0,0,0))["count"]==1


def test_two_map_k22_recovers_original_exact_capacity_theorem():
    graph=graph_from_sizes(((0,0),(0,1),(1,0),(1,1)),(1,1,1,1))
    s=MultiMapSignals(tuple((u,v) for u,v in graph["edges"]),
                      tuple(graph["sizes"]),((0,),(1,)))
    for t in product((-1,0,1),repeat=4):
        report=gold_alias_report(s,t)
        earlier=hidden_gold_width(graph,t)
        assert report["maximum_hidden_gold_width"]==earlier["maximum_width"]
        assert report["bounded_integer_rank"]==report["rational_nullity"]
        assert (not report["rational_gold_observable"]) == (
            earlier["maximum_width"]>0
        )


def test_UGC_reachability_erases_an_ambient_cycle_alias_in_frustrated_game():
    graph=graph_from_sizes(((0,0),(0,1),(1,0),(1,1)),(1,1,1,1))
    s=MultiMapSignals(tuple(graph["edges"]),tuple(graph["sizes"]),
                      ((0,),(1,)))
    t=(1,0,0,1)
    assert gold_alias_report(s,t)["maximum_hidden_gold_width"]==2

    frustrated=TranslationGame(4,1,(
        Edge(0,1,1),Edge(1,2,0),Edge(2,3,0),Edge(3,0,0)))
    flat=TranslationGame(4,1,(
        Edge(0,1,0),Edge(1,2,0),Edge(2,3,0),Edge(3,0,0)))
    X_bad=tuple(ugc_reachable_records(frustrated,graph))
    X_flat=tuple(ugc_reachable_records(flat,graph))
    assert {sum(x)%2 for x in X_bad}=={1}
    assert {sum(x)%2 for x in X_flat}=={0}
    r_bad=reachable_gold_alias(s,t,X_bad)
    r_flat=reachable_gold_alias(s,t,X_flat)
    assert r_bad["maximum_hidden_gold_width"]==0
    assert r_bad["reachable_difference_rank"]==0
    assert r_bad["reachable_gold_observable"]
    assert r_flat["maximum_hidden_gold_width"]==2
    assert r_flat["reachable_difference_rank"]==1
    assert not r_flat["reachable_gold_observable"]
    assert r_bad["reachable_records"]==8
    assert r_flat["reachable_records"]==8


def test_subselected_actor_roster_can_remove_a_global_reward_alias():
    s=three_map((1,2,1,1,1))
    t=(0,1,0,0,0)
    full=gold_alias_report(s,t)
    assert full["maximum_hidden_gold_width"]==2
    limited=((0,0,0,0,0),(0,1,0,0,0))
    r=reachable_gold_alias(s,t,limited)
    assert r["reachable_fibres"]==2
    assert r["reachable_gold_observable"]
    assert r["maximum_hidden_gold_width"]==0


def test_independent_gold_utility_can_be_misranked_with_zero_alias():
    s=three_map((1,)*5)
    X=tuple(product((0,1),repeat=5))
    t=(0,1,0,0,0)
    assert gold_alias_report(s,t)["maximum_hidden_gold_width"]==0
    # A legitimate *published* score based on the two first-map margins
    # rewards category-one outcomes and penalizes category-zero outcomes.
    # It achieves its maximum only when the protected cell x[1] is zero.
    # Since the unit-capacity feedback is injective, this is pure
    # cross-feedback Goodhart with zero hidden-fibre width.
    scores=[]
    for x in X:
        y=s.feedback(x)
        proxy=y[1]-y[0]
        gold=x[1]
        scores.append((proxy,gold,x))
    best=max(p for p,_,_ in scores)
    assert best==2
    assert all(gold==0 for p,gold,_ in scores if p==best)
    assert max(gold for _,gold,_ in scores)==1
    assert any(gold==1 for p,gold,_ in scores if p<best)


def test_invalid_faces_caps_roster_and_exponential_budget_fail_closed():
    with pytest.raises(ValueError):
        MultiMapSignals(tuple(reversed(FIVE)),(1,)*5,SEPARATE)
    with pytest.raises(ValueError):
        MultiMapSignals(FIVE,(1,0,1,1,1),SEPARATE)
    with pytest.raises(ValueError):
        MultiMapSignals(FIVE,(1,)*5,((0,),(0,)))
    with pytest.raises(ValueError):
        MultiMapSignals(FIVE,(1,)*5,((0,),(3,)))
    s=three_map((1,2,1,1,1))
    with pytest.raises(ValueError):
        gold_alias_report(s,(1,0))
    with pytest.raises(ValueError):
        gold_alias_report(s,(0,1,0,0,0),max_vectors=1)
    with pytest.raises(ValueError):
        minimum_private_audit(s,(0,1,0,0,0),tolerance=-1)
    with pytest.raises(ValueError):
        reachable_gold_alias(s,(0,1,0,0,0),())
    with pytest.raises(ValueError):
        reachable_gold_alias(s,(0,1,0,0,0),((1,3,0,0,0),))
    with pytest.raises(ValueError):
        first_uniform_capacity_alias(s,(0,1,0,0,0),max_capacity=0)
