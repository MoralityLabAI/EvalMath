"""RHT-01..05 exact theorem and adversarial-UGC-source cross-check receipt.

The receipt is deterministic and fingerprints all claim-bearing source files,
and can be compared to independently run finite oracles. This script does
not train, run, or certify any real agent or human reward model.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

from spiral_ln.evaluation_leak_topology import (
    graph_from_sizes, cycle_rank, box
)
from spiral_ln.evaluation_reward_hacking_topology import (
    cycle_periods,hidden_gold_width,circulation_oracle,minimum_gold_audit,
    proxy_optimization_regret,ugc_reachable_records,reconstruct_gold
)
from spiral_ln.evaluation_reward_ugc_fixture import bipartite_goodhart_fixture
from spiral_ln.evaluation_reward_hacking_flow import maximum_hidden_width_flow
from spiral_ln.evaluation_reward_hacking_guard import (
    minimal_epsilon_gold_audit,robust_proxy_guard
)
from spiral_ln.evaluation_reward_path_gauge import (
    RewardPathGame,RewardTransition,boundary_relative_certificate,
    potential_if_exact,policy_rank_reversal
)
from spiral_ln.unique_games_topology import Edge,TranslationGame


SOURCE_PATHS = (
    "src/spiral_ln/evaluation_reward_hacking_topology.py",
    "src/spiral_ln/evaluation_reward_path_gauge.py",
    "src/spiral_ln/evaluation_reward_hacking_guard.py",
    "src/spiral_ln/evaluation_reward_ugc_fixture.py",
    "src/spiral_ln/evaluation_reward_hacking_flow.py",
    "tests/test_evaluation_reward_hacking_topology.py",
    "tests/test_evaluation_reward_path_gauge.py",
    "tests/test_evaluation_reward_hacking_guard.py",
    "tests/test_evaluation_reward_ugc_fixture.py",
    "tests/test_evaluation_reward_hacking_flow.py",
    "paper/reward_hacking_cohomology.md",
    "scripts/verify_reward_hacking_topology.py",
)


def receipt() -> dict:
    g = graph_from_sizes(((0,0),(0,1),(1,0),(1,1)),(1,1,1,1))
    t = (1,0,0,1)
    periods = cycle_periods(g,t)
    width = hidden_gold_width(g,t)
    independent_width, independent_circulation = circulation_oracle(g,t)
    flow_width=maximum_hidden_width_flow(g,t)
    cert = minimum_gold_audit(g,t)
    assert cycle_rank(g)==1 and abs(periods[0][1])==2
    assert width["maximum_width"]==independent_width==flow_width.maximum_hidden_width==2
    assert cert["count"]==1
    assert all(reconstruct_gold(g,x,cert["formula"])
               == sum((Q(ti)*xi for ti,xi in zip(t,x)),Q(0))
               for x in box(g["sizes"]))

    g_ugc = TranslationGame(4,1,(
        Edge(0,1,1),Edge(1,2,0),Edge(2,3,0),Edge(3,0,0)))
    reachable=ugc_reachable_records(g_ugc,g)
    exploit=proxy_optimization_regret(
        g,(1,0,0,0),(1,1,0,0),
        allowed_candidates=tuple(reachable))
    assert exploit.worst_true_regret==1
    assert exploit.selected_proxy_score==3
    assert exploit.worst_selected_true_utility==0
    epsilon_audit=minimal_epsilon_gold_audit(g,t,0)
    assert epsilon_audit["count"]==cert["count"]==1
    guarded=robust_proxy_guard(
        g,tuple(reachable),(1,1,0,0),((1,0,0,0),),
        max_regret=0,minimum_gold=1,
    )
    assert guarded.passed and guarded.worst_case_regret==0
    assert guarded.selected_proxy_score==3
    assert guarded.minimum_gold_level==1
    simple_bipartite=bipartite_goodhart_fixture()
    assert simple_bipartite["unguarded"].selected_proxy_score==7
    assert simple_bipartite["unguarded"].true_optimum==2
    assert simple_bipartite["unguarded"].worst_selected_true_utility==1
    assert simple_bipartite["guarded"].selected_proxy_score==5
    assert simple_bipartite["guarded"].minimum_gold_level==2
    large_graph=graph_from_sizes(
        tuple((i,j) for i in range(6) for j in range(6)),
        tuple((i%3)+1 for i in range(36))
    )
    large_weights=tuple(Q(((i*13)%11)-5,7) for i in range(36))
    large_flow=maximum_hidden_width_flow(large_graph,large_weights)
    assert large_flow.maximum_hidden_width>0
    assert cycle_rank(large_graph)==25

    benign=RewardPathGame(4,0,(2,3),(
        RewardTransition(0,1,Q(0),Q(1)),
        RewardTransition(1,2,Q(4),Q(5)),
        RewardTransition(1,3,Q(1),Q(2)),
        RewardTransition(0,2,Q(3),Q(5)),
        RewardTransition(0,3,Q(0),Q(2))))
    bad_boundary=RewardPathGame(3,0,(1,2),(
        RewardTransition(0,1,Q(2),Q(2)),
        RewardTransition(0,2,Q(0),Q(3))))
    assert boundary_relative_certificate(benign)["common_path_offset"]==2
    assert potential_if_exact(bad_boundary) is not None
    assert boundary_relative_certificate(bad_boundary) is None
    assert policy_rank_reversal(bad_boundary,(0,),(1,))

    root=Path(__file__).resolve().parents[1]
    return {
        "schema":"RHT-01.0",
        "claim_level":"exact algebraic identity and bounded finite world census",
        "model_training_or_external_reward_validation":False,
        "feedback_geometry":{
            "cycle_rank":cycle_rank(g),
            "nonzero_gold_cycle_period":str(periods[0][1]),
            "invisible_gold_fibre_width":str(width["maximum_width"]),
            "independent_max_circulation":str(independent_width),
            "exact_flow_width":str(flow_width.maximum_hidden_width),
            "exact_flow_augmentations":flow_width.cancelled_negative_cycles,
            "min_targeted_extra_cell_disclosures":cert["count"],
            "zero_tolerance_private_audit_count":epsilon_audit["count"],
        },
        "ugc_reward_hack":{
            "reachable_cell_records":len(reachable),
            "best_reported_score":str(exploit.selected_proxy_score),
            "worst_selected_true_utility":str(exploit.worst_selected_true_utility),
            "true_best":str(exploit.true_optimum),
            "worst_true_regret":str(exploit.worst_true_regret),
        },
        "guarded_ugc_selection":{
            "passed":guarded.passed,
            "selected_proxy_score":str(guarded.selected_proxy_score),
            "worst_case_true_regret":str(guarded.worst_case_regret),
            "minimum_gold_level":str(guarded.minimum_gold_level),
            "condition":"true gold belongs to protected frozen uncertainty set",
        },
        "simple_bipartite_game":{
            "vertices":simple_bipartite["constraint_game"].vertices,
            "edges":len(simple_bipartite["constraint_game"].edges),
            "unaltered_gold_observable_from_margins":True,
            "proxy_optimum":str(simple_bipartite["unguarded"].selected_proxy_score),
            "gold_at_proxy_optimum":str(simple_bipartite["unguarded"].worst_selected_true_utility),
            "gold_optimum":str(simple_bipartite["unguarded"].true_optimum),
            "gold_guarded_proxy_score":str(simple_bipartite["guarded"].selected_proxy_score),
            "gold_guarded_utility":str(simple_bipartite["guarded"].minimum_gold_level),
        },
        "large_flow":{
            "edges":36,
            "cycle_rank":25,
            "maximum_hidden_gold_width":str(large_flow.maximum_hidden_width),
            "cancelled_negative_cycles":large_flow.cancelled_negative_cycles,
            "method":"exact negative-cycle cancellation with integer capacities",
        },
        "relative_gauge":{
            "safe_terminal_equal_potential":True,
            "acyclic_terminal_misranking":True,
        },
        "source_sha256":{
            p:hashlib.sha256((root/p).read_bytes()).hexdigest()
            for p in SOURCE_PATHS
        },
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output",type=Path,default=None)
    args=ap.parse_args()
    text=json.dumps(receipt(),sort_keys=True,indent=2)+"\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with args.output.open("x",encoding="utf-8") as handle:
            handle.write(text)
    else:
        print(text,end="")


if __name__=="__main__":
    main()
