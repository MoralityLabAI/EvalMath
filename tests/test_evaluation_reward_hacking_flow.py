"""RHT-05 exact flow solver checked against independent exponential oracles.

This is a finite correctness audit, with a larger graph beyond feasible
brute-force enumeration as a separate scaling sanity check.
"""
from fractions import Fraction as Q
from itertools import product

import pytest

from spiral_ln.evaluation_leak_topology import (
    box, cycle_rank, graph_from_sizes, margins_of
)
from spiral_ln.evaluation_reward_hacking_flow import maximum_hidden_width_flow
from spiral_ln.evaluation_reward_hacking_topology import (
    circulation_oracle, hidden_gold_width
)
from spiral_ln.evaluation_reward_hacking_guard import augmented_feedback_width


def square(sizes=(1,1,1,1)):
    return graph_from_sizes(((0,0),(0,1),(1,0),(1,1)),sizes)


def k23():
    return graph_from_sizes(((0,0),(1,0),(0,1),(1,1),(0,2),(1,2)),
                            (1,)*6)


def gold(t,x):
    return sum((Q(a)*v for a,v in zip(t,x)),Q(0))


def test_complete_square_integer_and_rational_gold_census():
    for sizes in ((1,1,1,1),(1,2,1,2),(2,1,1,1)):
        g=square(sizes)
        for weights in product((-1,0,1),repeat=4):
            w=tuple(Q(v) for v in weights)
            flow=maximum_hidden_width_flow(g,w)
            brute=hidden_gold_width(g,w)["maximum_width"]
            circ,z=circulation_oracle(g,w)
            assert flow.maximum_hidden_width==brute==circ
            assert margins_of(g,flow.integer_circulation)==(0,0,0,0)
            assert flow.maximum_hidden_width==gold(w,flow.high_record)-gold(w,flow.low_record)
            assert flow.maximum_hidden_width>=0
            assert flow.audited_cells==()


def test_exact_flow_after_private_cell_audits():
    for sizes in ((1,1,1,1),(1,2,1,2)):
        g=square(sizes)
        for w in ((1,0,0,1),(2,-3,4,0),(Q(1,2),Q(-3,4),Q(5,6),Q(7,8))):
            for S in ((),(0,),(1,),(0,2),(0,1,2,3)):
                out=maximum_hidden_width_flow(g,w,audited_cells=S)
                direct=augmented_feedback_width(g,w,S)
                assert out.maximum_hidden_width==direct
                assert all(out.integer_circulation[i]==0 for i in S)
                assert all(out.high_record[i]==out.low_record[i] for i in S)


def test_two_independent_cycles_K23_flow_audit():
    g=k23()
    assert cycle_rank(g)==2
    for w in ((0,0,0,1,0,2),(3,0,0,1,0,2),(-1,2,3,-2,0,1)):
        out=maximum_hidden_width_flow(g,w)
        assert out.maximum_hidden_width==circulation_oracle(g,w)[0]
        assert out.maximum_hidden_width==hidden_gold_width(g,w)["maximum_width"]
        for S in ((0,),(2,),(0,3),(0,3,5)):
            result=maximum_hidden_width_flow(g,w,audited_cells=S)
            assert result.maximum_hidden_width==augmented_feedback_width(g,w,S)


def test_large_intersection_graph_structural_flow_witness():
    edges=tuple((row,col) for row in range(6) for col in range(6))
    sizes=tuple((i%3)+1 for i in range(len(edges)))
    g=graph_from_sizes(edges,sizes)
    assert cycle_rank(g)==25
    w=tuple(Q(((i*13)%11)-5,7) for i in range(len(edges)))
    out=maximum_hidden_width_flow(g,w)
    assert out.maximum_hidden_width>0
    assert len(out.integer_circulation)==36
    assert margins_of(g,out.integer_circulation)==(0,)*12
    assert gold(w,out.high_record)-gold(w,out.low_record)==out.maximum_hidden_width
    assert all(0<=hi<=s and 0<=lo<=s
               for hi,lo,s in zip(out.high_record,out.low_record,sizes))
    reduced=maximum_hidden_width_flow(g,w,audited_cells=tuple(range(6)))
    assert 0<=reduced.maximum_hidden_width<=out.maximum_hidden_width
    # 36 nontrivial cells cannot be handled by the existing enumerative
    # reference oracle under its ordinary resource budget.
    with pytest.raises(ValueError):
        hidden_gold_width(g,w,max_states=100000)


def test_forest_or_exact_gold_have_zero_hidden_width():
    g=graph_from_sizes(((0,0),(1,0),(1,1)),(2,1,2))
    assert cycle_rank(g)==0
    assert maximum_hidden_width_flow(g,(2,7,-3)).maximum_hidden_width==0
    g=square((3,4,5,6))
    assert maximum_hidden_width_flow(g,(5,6,2,3)).maximum_hidden_width==0


def test_flow_fails_closed_on_invalid_capacity_or_audit():
    g=square()
    with pytest.raises(ValueError):
        maximum_hidden_width_flow(g,(1,2))
    with pytest.raises(ValueError):
        maximum_hidden_width_flow(g,(1,0,0,1),audited_cells=(0,0))
    with pytest.raises(ValueError):
        maximum_hidden_width_flow(g,(1,0,0,1),audited_cells=(4,))
    with pytest.raises(ValueError):
        maximum_hidden_width_flow(g,(1,0,0,1),max_augmentations=0)


def test_augmentation_cap_enforced_on_two_separate_bad_cycles():
    # Two disconnected K2,2 components require two distinct improvements.
    # Build an abstract graph with rows 0,1,2,3 and columns 0,1,2,3;
    # the graph_from_sizes constructor includes all rows/columns.
    g=graph_from_sizes(
        ((0,0),(0,1),(1,0),(1,1),(2,2),(2,3),(3,2),(3,3)),
        (1,)*8
    )
    w=(1,0,0,1,1,0,0,1)
    assert maximum_hidden_width_flow(g,w).maximum_hidden_width==4
    with pytest.raises(ValueError):
        maximum_hidden_width_flow(g,w,max_augmentations=1)
