"""RHT-03: separate audit cost and robust-policy regression tests."""
from fractions import Fraction as Q
from itertools import combinations, product

import pytest

from spiral_ln.evaluation_leak_topology import graph_from_sizes, margins_of, box
from spiral_ln.evaluation_reward_hacking_topology import (
    minimum_gold_audit, ugc_reachable_records, proxy_optimization_regret,
)
from spiral_ln.evaluation_reward_hacking_guard import (
    augmented_feedback_width, minimal_epsilon_gold_audit, robust_proxy_guard,
)
from spiral_ln.unique_games_topology import Edge, TranslationGame


def square(sizes=(1,1,1,1)):
    return graph_from_sizes(((0,0),(0,1),(1,0),(1,1)),sizes)


def frustrated_game():
    return TranslationGame(4,1,(
        Edge(0,1,1),Edge(1,2,0),Edge(2,3,0),Edge(3,0,0),
    ))


def brute_augmented_width(graph,t,selected):
    """Independent pairwise alias search using only margins and true values."""
    X=tuple(box(graph["sizes"]))
    gold=lambda x:sum((Q(a)*b for a,b in zip(t,x)),Q(0))
    feasible=tuple((x,y) for x,y in product(X,repeat=2)
                   if margins_of(graph,x)==margins_of(graph,y)
                   and all(x[e]==y[e] for e in selected))
    return max((abs(gold(x)-gold(y)) for x,y in feasible),default=Q(0))


def test_epsilon_zero_recovers_cosystolic_audit_exactly():
    graph=square()
    t=(1,0,0,1)
    assert augmented_feedback_width(graph,t,())==2
    assert minimal_epsilon_gold_audit(graph,t,2)["count"]==0
    assert minimal_epsilon_gold_audit(graph,t,1)["count"]==1
    assert minimal_epsilon_gold_audit(graph,t,0)["count"]==1
    assert minimal_epsilon_gold_audit(graph,t,0)["count"]==(
        minimum_gold_audit(graph,t)["count"])
    for e in range(4):
        assert augmented_feedback_width(graph,t,(e,))==0


def test_worst_hidden_reward_width_matches_pairwise_alias_enumerator():
    for caps in ((1,1,1,1),(1,2,1,2)):
        graph=square(caps)
        for t in product((-1,0,1),repeat=4):
            for e in ((),(0,),(1,3)):
                a=augmented_feedback_width(graph,t,e)
                b=brute_augmented_width(graph,t,e)
                assert a==b
            assert minimal_epsilon_gold_audit(graph,t,0)["count"]==(
                minimum_gold_audit(graph,t)["count"])


def test_robust_guard_blocks_UGC_reward_hacking_with_gold_anchor():
    graph=square()
    reachable=ugc_reachable_records(frustrated_game(),graph)
    unguarded=proxy_optimization_regret(
        graph,(1,0,0,0),(1,1,0,0),
        allowed_candidates=tuple(reachable))
    assert unguarded.worst_true_regret==1
    safe=robust_proxy_guard(
        graph,tuple(reachable),(1,1,0,0),((1,0,0,0),),
        max_regret=0,minimum_gold=1)
    assert safe.passed
    assert safe.selected_proxy_score==3
    assert safe.selected_record[0]==1
    assert safe.worst_case_regret==0
    assert safe.minimum_gold_level==1
    assert safe.safe_candidate_count>=1


def test_two_independent_gold_anchors_can_still_certify_progress():
    graph=square()
    reachable=ugc_reachable_records(frustrated_game(),graph)
    safe=robust_proxy_guard(
        graph,tuple(reachable),(1,1,0,0),
        ((1,0,0,0),(0,1,0,0)),
        max_regret=0,minimum_gold=1)
    assert safe.passed
    assert safe.selected_proxy_score==3
    assert safe.selected_record[0]==safe.selected_record[1]==1
    assert safe.minimum_gold_level==1


def test_overconstrained_gold_roster_produces_explicit_non_inert_block():
    graph=square()
    reachable=ugc_reachable_records(frustrated_game(),graph)
    gold=tuple(tuple(int(i==j) for i in range(4)) for j in range(4))
    blocked=robust_proxy_guard(
        graph,tuple(reachable),(1,1,0,0),gold,
        max_regret=0,minimum_gold=1)
    assert not blocked.passed
    assert blocked.selected_record is None
    assert blocked.safe_candidate_count==0


def test_misspecified_gold_set_cannot_certify_actual_reward():
    graph=square()
    reachable=ugc_reachable_records(frustrated_game(),graph)
    policy=robust_proxy_guard(
        graph,tuple(reachable),(1,1,0,0),((1,0,0,0),),
        max_regret=0,minimum_gold=1)
    assert policy.passed
    # This independently unregistered utility values passing item #1.
    # The certified set contains only item #0 and cannot speak to item #1.
    other_gold=tuple(x[1] for x in reachable)
    assert max(other_gold)==1
    assert policy.selected_record[1]==0


def test_no_novel_gold_signal_can_be_inferred_from_proxy_only():
    graph=square()
    x=(1,0,0,1)
    y=(0,1,1,0)
    assert margins_of(graph,x)==margins_of(graph,y)
    # Two outside gold evaluators disagree on which world deserves reward,
    # while every disclosed margin and proxy total is unchanged.
    t1=(1,0,0,1)
    t2=(0,1,1,0)
    d1=sum(a*(u-v) for a,u,v in zip(t1,x,y))
    d2=sum(a*(u-v) for a,u,v in zip(t2,x,y))
    assert (d1,d2)==(2,-2)


def test_reject_invalid_private_audit_or_gold_certification_scope():
    graph=square()
    with pytest.raises(ValueError):
        augmented_feedback_width(graph,(1,0,0,1),(4,))
    with pytest.raises(ValueError):
        augmented_feedback_width(graph,(1,0,0,1),(0,0))
    with pytest.raises(ValueError):
        minimal_epsilon_gold_audit(graph,(1,0,0,1),Q(-1))
    with pytest.raises(ValueError):
        minimal_epsilon_gold_audit(graph,(1,0,0,1),0,max_cells=2)
    with pytest.raises(ValueError):
        robust_proxy_guard(graph,(),(1,1,0,0),((1,0,0,0),),
                           max_regret=0,minimum_gold=0)
    with pytest.raises(ValueError):
        robust_proxy_guard(graph,((0,0,0,0),),(1,1,0,0),(),
                           max_regret=0,minimum_gold=0)
    with pytest.raises(ValueError):
        robust_proxy_guard(graph,((0,0,0,0),),(1,1,0,0),
                           ((1,0,0,0),),max_regret=-1,minimum_gold=0)
    with pytest.raises(ValueError):
        robust_proxy_guard(graph,((2,0,0,0),),(1,1,0,0),
                           ((1,0,0,0),),max_regret=0,minimum_gold=0)
