"""RHT-04: simple-bipartite F2 translation game with strict proxy Goodhart.

The UGC constraint graph and the evaluation cell-intersection graph are both
K_{2,4}, with separate coefficient spaces: environment shifts are in F2
and protected utility weights are rational. One 'gold' two-edge path
requires equal terminal labels; three distractor paths require unequal
terminal labels. The proxy counts all satisfied constraints equally.

The unique proxy-optimal *orbit* has unequal terminal labels and satisfies
7/8 constraints but only 1/2 gold tests. A gold-optimal equal-terminal
assignment satisfies five proxy constraints and 2/2 gold tests.
The gold cochain is exactly representable by category margins,
so every cohomological period of that gold signal is zero. This is a
clean cross-fibre Goodhart exploit despite full true-score observability.
"""
from __future__ import annotations

from fractions import Fraction as Q

from spiral_ln.unique_games_topology import Edge, TranslationGame
from spiral_ln.evaluation_leak_topology import graph_from_sizes
from spiral_ln.evaluation_reward_hacking_topology import (
    cycle_periods, exact_from_margins, proxy_optimization_regret,
    ugc_reachable_records,
)
from spiral_ln.evaluation_reward_hacking_guard import robust_proxy_guard


def bipartite_goodhart_fixture():
    edges = (
        (0,0), (1,0), (0,1), (1,1),
        (0,2), (1,2), (0,3), (1,3),
    )
    disclosure = graph_from_sizes(edges, (1,)*8)
    game = TranslationGame(6,1,(
        Edge(0,2,0), Edge(1,2,0),
        Edge(0,3,0), Edge(1,3,1),
        Edge(0,4,0), Edge(1,4,1),
        Edge(0,5,0), Edge(1,5,1),
    ))
    # graph_from_sizes canonicalizes cells in row-major order, unlike
    # the input list grouped by intermediate vertex. Column w0 is cells 0,4.
    true_weights = (1,0,0,0,1,0,0,0)
    proxy_margin_weights = (1,1,0,0,0,0)
    reachable = ugc_reachable_records(game, disclosure)
    report = proxy_optimization_regret(
        disclosure, true_weights, proxy_margin_weights,
        allowed_candidates=tuple(reachable),
    )
    guard = robust_proxy_guard(
        disclosure,tuple(reachable),proxy_margin_weights,
        (true_weights,),max_regret=0,minimum_gold=2,
    )
    assert exact_from_margins(disclosure,true_weights)
    assert all(period==0 for _,period in cycle_periods(disclosure,true_weights))
    assert report.true_optimum==2
    assert report.selected_proxy_score==7
    assert report.worst_selected_true_utility==1
    assert report.worst_true_regret==1
    assert report.wrong_fibre_gap==1 and report.hidden_fibre_gap==0
    assert guard.passed and guard.selected_proxy_score==5
    assert guard.worst_case_regret==0 and guard.minimum_gold_level==2

    return {
        "constraint_game":game,
        "disclosure_graph":disclosure,
        "reachable":reachable,
        "gold_weights":true_weights,
        "proxy_weights":proxy_margin_weights,
        "unguarded":report,
        "guarded":guard,
        "low_proxy_gold_assignment":(0,0,0,0,0,0),
        "high_proxy_low_gold_assignment":(0,1,0,0,0,0),
    }
