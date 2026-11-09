"""RHT-07: lazy weighted audit correctness against exact independent oracles."""
from fractions import Fraction as Q
from itertools import product

import pytest

from spiral_ln.evaluation_leak_topology import graph_from_sizes
from spiral_ln.evaluation_reward_hacking_multimap import (
    MultiMapSignals, gold_alias_report, minimum_private_audit,
    reachable_gold_alias,
)
from spiral_ln.evaluation_reward_hacking_audit_optimizer import (
    maximum_hidden_gold_dp, maximum_reachable_gold,
    minimum_private_gold_audit_lazy,
)
from spiral_ln.evaluation_reward_hacking_guard import (
    augmented_feedback_width, minimal_epsilon_gold_audit,
)
from spiral_ln.evaluation_reward_hacking_topology import ugc_reachable_records
from spiral_ln.unique_games_topology import Edge, TranslationGame


FIVE=((0,0,0),(0,0,1),(0,1,1),(1,0,1),(1,1,0))
FACES=((0,),(1,),(2,))


def five(cap=(1,2,1,1,1)):
    return MultiMapSignals(FIVE, tuple(cap), FACES)


def cube_pairwise(cap=1):
    cells=tuple(product((0,1),repeat=3))
    return MultiMapSignals(cells,(cap,)*8,((0,1),(0,2),(1,2)))


def twobytwobythree(cap=3):
    cells=tuple(product((0,1),(0,1),(0,1,2)))
    return MultiMapSignals(cells,(cap,)*12,((0,1),(0,2),(1,2)))


def _gold(t,z):
    return sum((Q(w)*x for w,x in zip(t,z)),Q(0))


def test_rank_one_activation_and_analytic_maximum_width():
    t=(0,1,0,0,0)
    for cap,expected in (((1,)*5,0),((1,2,1,1,1),2),((2,4,2,2,2),4)):
        s=five(cap)
        result=maximum_hidden_gold_dp(s,t)
        assert result.method=="primitive-rank-one"
        assert result.maximum_width==expected
        assert s.feedback(result.high_record)==s.feedback(result.low_record)
        assert result.maximum_width==_gold(t,result.difference)
        if cap[1]<=2:
            assert result.maximum_width==gold_alias_report(s,t)["maximum_hidden_gold_width"]
        audit=minimum_private_gold_audit_lazy(s,t)
        assert audit.count==(0 if expected==0 else 1)
        assert audit.remaining_gold_width==0
        assert audit.source_scope=="capacity-box"


def test_weighted_rank_one_prefers_cheaper_cell():
    s=five()
    t=(0,1,0,0,0)
    audit=minimum_private_gold_audit_lazy(
        s,t,cell_costs=(9,1,3,5,4)
    )
    assert audit.audited_cells==(1,)
    assert audit.cost==1
    assert audit.count==1
    assert len(audit.witnessed_obstructions)==1
    assert audit.rounds==2
    assert maximum_hidden_gold_dp(s,t,audited_cells=(1,)).maximum_width==0
    assert minimum_private_gold_audit_lazy(s,t,tolerance=2).count==0


def test_higher_rank_DP_two_by_two_by_three_joint_pair_margins():
    s=twobytwobythree(3)
    t=tuple(2 if c==(0,0,0) else 1 if c==(0,0,1) else 0
            for c in s.cells)
    assert s.rational_nullity==2
    # For 2x2x3 with all pairwise margins, each vertical 2x2 slice
    # is checkerboard with coefficients a,b,-a-b. The signed objective
    # is 2a+b with |a|,|b|,|a+b|<=3.
    independent=max(2*a+b for a in range(-3,4)
                    for b in range(-3,4) if abs(a+b)<=3)
    assert independent==6
    r=maximum_hidden_gold_dp(s,t,max_states=30000)
    assert r.method=="exact-margin-dp"
    assert r.maximum_width==independent
    assert s.feedback(r.high_record)==s.feedback(r.low_record)
    assert r.maximum_width==_gold(t,r.difference)
    assert r.visited_states<30000
    # Naive oracle would enumerate 7**12 integer difference vectors.
    assert 7**12>1000000000
    audit=minimum_private_gold_audit_lazy(
        s,t,max_states=30000,max_rounds=50
    )
    assert audit.count==2
    assert audit.remaining_gold_width==0
    assert audit.rounds>=2
    for i in audit.audited_cells:
        assert r.difference[i]!=0 or audit.rounds>2
    assert maximum_hidden_gold_dp(
        s,t,audited_cells=audit.audited_cells,max_states=30000
    ).maximum_width==0
    approx=minimum_private_gold_audit_lazy(
        s,t,tolerance=3,max_states=30000
    )
    assert approx.count==1
    assert approx.remaining_gold_width<=3


def test_cube_pairwise_DP_equals_capacity_box_enum():
    s=cube_pairwise(1)
    assert s.rational_nullity==1
    for weights in (
        (1,0,0,0,0,0,0,0),
        (2,-1,0,1,0,0,1,-2),
        (Q(3,5),Q(-1,2),0,1,0,0,0,0),
    ):
        r=maximum_hidden_gold_dp(s,weights)
        assert r.maximum_width==gold_alias_report(s,weights)["maximum_hidden_gold_width"]
        for S in ((),(0,),(0,1),(3,6)):
            remaining=maximum_hidden_gold_dp(s,weights,audited_cells=S)
            old=minimum_private_audit(s,weights)["count"]
            assert remaining.maximum_width==max((
                _gold(weights,z) for z in
                __import__(
                    "spiral_ln.evaluation_reward_hacking_multimap",
                    fromlist=["bounded_kernel_differences"]
                ).bounded_kernel_differences(s)
                if all(z[i]==0 for i in S)
            ),default=Q(0))
            assert 0<=old<=1


def test_two_map_matches_existing_private_audit_oracle():
    graph=graph_from_sizes(((0,0),(0,1),(1,0),(1,1)),(1,2,1,2))
    s=MultiMapSignals(tuple(graph["edges"]),tuple(graph["sizes"]),
                      ((0,),(1,)))
    assert s.rational_nullity==1
    for w in product((-1,0,1),repeat=4):
        sep=maximum_hidden_gold_dp(s,w)
        assert sep.maximum_width==augmented_feedback_width(graph,w,())
        new=minimum_private_gold_audit_lazy(s,w,tolerance=0)
        old=minimal_epsilon_gold_audit(graph,w,0)
        assert new.count==old["count"]
        assert new.remaining_gold_width==0


def test_UGC_actor_roster_separation_can_save_private_audit():
    graph=graph_from_sizes(((0,0),(0,1),(1,0),(1,1)),(1,)*4)
    s=MultiMapSignals(tuple(graph["edges"]),tuple(graph["sizes"]),
                      ((0,),(1,)))
    t=(1,0,0,1)
    flat=TranslationGame(4,1,(
        Edge(0,1,0),Edge(1,2,0),Edge(2,3,0),Edge(3,0,0),
    ))
    frustrated=TranslationGame(4,1,(
        Edge(0,1,1),Edge(1,2,0),Edge(2,3,0),Edge(3,0,0),
    ))
    flatX=tuple(ugc_reachable_records(flat,graph))
    badX=tuple(ugc_reachable_records(frustrated,graph))
    box_audit=minimum_private_gold_audit_lazy(s,t)
    flat_audit=minimum_private_gold_audit_lazy(
        s,t,reachable_records=flatX
    )
    bad_audit=minimum_private_gold_audit_lazy(
        s,t,reachable_records=badX
    )
    assert (box_audit.count,flat_audit.count,bad_audit.count)==(1,1,0)
    assert box_audit.cost==flat_audit.cost==1
    assert bad_audit.cost==0
    assert bad_audit.source_scope=="frozen-reachable-roster"
    assert maximum_reachable_gold(s,t,badX).maximum_width==0
    assert maximum_reachable_gold(s,t,flatX).maximum_width==2
    assert reachable_gold_alias(s,t,flatX)["maximum_hidden_gold_width"]==2


def test_reachable_two_rank_fibres_have_exact_hitting_cover():
    # Explicitly freeze the complete unit-capacity roster on 12 cells.
    # This exercises the reachable-record separator independently of the
    # integer-margin dynamic-programming separator.
    s=twobytwobythree(cap=1)
    t=tuple(2 if c==(0,0,0) else 1 if c==(0,0,1) else 0
            for c in s.cells)
    X=tuple(product((0,1),repeat=len(s.cells)))
    assert len(X)==4096
    r=maximum_reachable_gold(s,t,X)
    assert r.maximum_width==2
    audit=minimum_private_gold_audit_lazy(
        s,t,reachable_records=X,max_rounds=50
    )
    assert audit.count==2
    assert audit.remaining_gold_width==0
    assert audit.source_scope=="frozen-reachable-roster"
    assert audit.rounds>=2


def test_weighted_hitting_node_and_separator_budgets_fail_closed():
    s=twobytwobythree()
    t=tuple(2 if c==(0,0,0) else 1 if c==(0,0,1) else 0
            for c in s.cells)
    with pytest.raises(ValueError):
        maximum_hidden_gold_dp(s,t,max_states=1)
    with pytest.raises(ValueError):
        minimum_private_gold_audit_lazy(s,t,max_rounds=1)
    with pytest.raises(ValueError):
        minimum_private_gold_audit_lazy(s,t,max_hitting_nodes=1)
    with pytest.raises(ValueError):
        minimum_private_gold_audit_lazy(s,t,cell_costs=(1,)*11)
    with pytest.raises(ValueError):
        minimum_private_gold_audit_lazy(s,t,cell_costs=(1,)*11+(-1,))
    with pytest.raises(ValueError):
        minimum_private_gold_audit_lazy(s,t,tolerance=-1)
    with pytest.raises(ValueError):
        maximum_hidden_gold_dp(s,t,audited_cells=(0,0))
    with pytest.raises(ValueError):
        maximum_reachable_gold(s,t,())
    with pytest.raises(ValueError):
        maximum_reachable_gold(s,t,((4,)*12,))
