"""RHT-01: independently check evaluation cycle / gold-reward quotient claims."""
from fractions import Fraction as Q
from itertools import product
import pytest

from spiral_ln.evaluation_leak_topology import (
    graph_from_sizes, box, cycle_rank, margins_of, fundamental_cycles,
)
from spiral_ln.evaluation_reward_hacking_topology import (
    cycle_periods, vertex_potential, exact_from_margins, cycle_alias_witness,
    hidden_gold_width, circulation_oracle, audit_reconstruction,
    reconstruct_gold, minimum_gold_audit, proxy_optimization_regret,
    ugc_reachable_records,
)
from spiral_ln.unique_games_topology import Edge, TranslationGame


def square(sizes=(1,1,1,1)):
    return graph_from_sizes(((0,0),(0,1),(1,0),(1,1)),sizes)


def K23():
    return graph_from_sizes(((0,0),(1,0),(0,1),(1,1),(0,2),(1,2)),
                            (1,1,1,1,1,1))


def true_value(t,x):
    return sum((Q(a)*b for a,b in zip(t,x)),Q(0))


def test_four_cell_hidden_reward_is_exact_cycle_period():
    graph=square()
    t=(1,0,0,1)
    assert cycle_rank(graph)==1
    assert len(cycle_periods(graph,t))==1
    assert abs(cycle_periods(graph,t)[0][1])==2
    assert not exact_from_margins(graph,t)
    witness=cycle_alias_witness(graph,t)
    assert witness is not None
    assert {witness["first"],witness["second"]}=={
        (1,0,0,1),(0,1,1,0)}
    assert witness["published_margins"]==(1,1,1,1)
    assert abs(witness["true_difference"])==2
    width=hidden_gold_width(graph,t)
    assert width["maximum_width"]==2
    assert circulation_oracle(graph,t)[0]==2


def test_coboundary_gold_is_identifiable_from_separate_margins():
    graph=square()
    # row potentials (2,-1) + column potentials (3,4)
    t=(5,6,2,3)
    assert all(p==0 for _,p in cycle_periods(graph,t))
    assert exact_from_margins(graph,t)
    assert vertex_potential(graph,t) is not None
    assert cycle_alias_witness(graph,t) is None
    assert hidden_gold_width(graph,t)["maximum_width"]==0
    assert minimum_gold_audit(graph,t)["count"]==0
    formula=audit_reconstruction(graph,t,())
    for x in box(graph["sizes"]):
        assert reconstruct_gold(graph,x,formula)==true_value(t,x)


def test_targeted_audit_is_one_cell_and_reconstructs_all_records():
    graph=square()
    t=(1,0,0,1)
    cert=minimum_gold_audit(graph,t)
    assert cert["count"]==1
    assert cert["universal_upper_bound"]==1
    assert cert["audited_cells"]==(0,)
    assert audit_reconstruction(graph,t,()) is None
    for x in box(graph["sizes"]):
        assert reconstruct_gold(graph,x,cert["formula"])==true_value(t,x)


def test_target_specific_audit_can_be_smaller_than_cycle_rank():
    graph=K23()
    assert cycle_rank(graph)==2
    # One independently measured gold interaction contaminates one edge.
    target=(0,0,0,1,0,0)
    assert minimum_gold_audit(graph,target)["count"]==1
    cert=minimum_gold_audit(graph,target)
    for x in box(graph["sizes"]):
        assert reconstruct_gold(graph,x,cert["formula"])==true_value(target,x)


def test_K23_two_independent_gold_periods_need_two_cells():
    graph=K23()
    t=(0,0,0,1,0,2)
    assert len(cycle_periods(graph,t))==2
    assert all(v!=0 for _,v in cycle_periods(graph,t))
    cert=minimum_gold_audit(graph,t)
    assert cert["count"]==2
    for x in box(graph["sizes"]):
        assert reconstruct_gold(graph,x,cert["formula"])==true_value(t,x)


def test_circulation_and_fibre_oracles_agree_across_all_small_signals():
    for cap in ((1,1,1,1),(1,2,1,2)):
        graph=square(cap)
        for weights in product((-1,0,1),repeat=4):
            width=hidden_gold_width(graph,weights)["maximum_width"]
            flow,_=circulation_oracle(graph,weights)
            assert width==flow
            assert (width==0)==exact_from_margins(graph,weights)
            assert (width>0)==(cycle_alias_witness(graph,weights) is not None)


def test_exact_goodhart_proxy_gain_with_true_loss_on_frustrated_UGC_cycle():
    graph=square()
    game=TranslationGame(4,1,(
        Edge(0,1,1),Edge(1,2,0),Edge(2,3,0),Edge(3,0,0)))
    reachable=ugc_reachable_records(game,graph)
    # Labels [0,1,0,1] yield 1000 (one proxy pass, gold pass).
    assert reachable[(1,0,0,0)]==(0,1,0,1)
    # Labels [0,0,0,0] yield 0111 (three proxy passes, gold fails).
    assert reachable[(0,1,1,1)]==(0,0,0,0)
    t=(1,0,0,0)
    alpha=(1,1,0,0)  # row category totals, ordinary total pass count
    r=proxy_optimization_regret(graph,t,alpha,
                                allowed_candidates=tuple(reachable))
    assert r.true_optimum==1
    assert r.selected_proxy_score==3
    assert r.worst_selected_true_utility==0
    assert r.worst_true_regret==1
    assert r.wrong_fibre_gap==1
    assert r.hidden_fibre_gap==0


def test_hacking_from_proxy_ties_within_a_Unique_Games_feedback_fibre():
    graph=square()
    flat=TranslationGame(4,1,(
        Edge(0,1,0),Edge(1,2,0),Edge(2,3,0),Edge(3,0,0)))
    reachable=ugc_reachable_records(flat,graph)
    assert (1,0,0,1) in reachable
    assert (0,1,1,0) in reachable
    t=(1,0,0,1)
    alpha=(1,1,0,0)
    r=proxy_optimization_regret(
        graph,t,alpha,allowed_candidates=((1,0,0,1),(0,1,1,0)))
    assert r.selected_proxy_score==2
    assert r.worst_true_regret==2
    assert r.wrong_fibre_gap==0
    assert r.hidden_fibre_gap==2
    assert r.worst_true_regret==r.wrong_fibre_gap+r.hidden_fibre_gap


def test_full_box_nonnegative_gold_and_total_proxy_has_zero_regret():
    graph=square()
    r=proxy_optimization_regret(graph,(1,0,0,1),(1,1,0,0))
    assert r.selected_proxy_score==4
    assert r.worst_true_regret==0
    assert r.hidden_fibre_gap==0


def test_exact_gap_decomposition_on_reachable_subsets():
    graph=square()
    X=((1,0,0,1),(0,1,1,0),(0,1,1,1))
    t=(1,0,0,1)
    r=proxy_optimization_regret(
        graph,t,(1,1,0,0),allowed_candidates=X)
    assert r.selected_proxy_score==3
    assert r.true_optimum==2
    assert r.worst_selected_true_utility==1
    assert r.worst_true_regret==1
    assert r.wrong_fibre_gap==1
    assert r.hidden_fibre_gap==0


def test_invalid_reward_and_audit_contracts():
    graph=square()
    with pytest.raises(ValueError):
        cycle_periods(graph,(1,2))
    with pytest.raises(ValueError):
        vertex_potential(graph,(1,0,0,1),(0,0))
    with pytest.raises(ValueError):
        minimum_gold_audit(graph,(1,0,0,1),max_cells=3)
    with pytest.raises(ValueError):
        hidden_gold_width(graph,(1,0,0,1),max_states=1)
    with pytest.raises(ValueError):
        circulation_oracle(graph,(1,0,0,1),max_states=1)
    with pytest.raises(ValueError):
        proxy_optimization_regret(graph,(1,0,0,1),(1,2))
    with pytest.raises(ValueError):
        proxy_optimization_regret(graph,(1,0,0,1),(1,1,0,0),
                                 allowed_candidates=((2,0,0,0),))
    with pytest.raises(ValueError):
        reconstruct_gold(graph,(2,0,0,0),
                         audit_reconstruction(graph,(1,0,0,1),(0,)))
    with pytest.raises(ValueError):
        ugc_reachable_records(TranslationGame(2,1,()),graph)


def test_full_margin_map_has_expected_rank_and_basis():
    graph=K23()
    cycles=fundamental_cycles(graph)
    assert len(cycles)==2
    for chord,z in cycles:
        assert abs(z[chord])==1
        assert margins_of(graph,z)==(0,0,0,0,0)
