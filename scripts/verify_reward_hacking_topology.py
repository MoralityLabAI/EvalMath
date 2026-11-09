"""RHT-01 exact finite theorem and adversarial-UCG-source cross-check receipt.

The receipt is deterministic, fingerprints four claim-bearing source files,
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
from spiral_ln.evaluation_reward_path_gauge import (
    RewardPathGame,RewardTransition,boundary_relative_certificate,
    potential_if_exact,policy_rank_reversal
)
from spiral_ln.unique_games_topology import Edge,TranslationGame


SOURCE_PATHS = (
    "src/spiral_ln/evaluation_reward_hacking_topology.py",
    "src/spiral_ln/evaluation_reward_path_gauge.py",
    "tests/test_evaluation_reward_hacking_topology.py",
    "tests/test_evaluation_reward_path_gauge.py",
    "paper/reward_hacking_cohomology.md",
    "scripts/verify_reward_hacking_topology.py",
)


def receipt() -> dict:
    g = graph_from_sizes(((0,0),(0,1),(1,0),(1,1)),(1,1,1,1))
    t = (1,0,0,1)
    periods = cycle_periods(g,t)
    width = hidden_gold_width(g,t)
    independent_width, independent_circulation = circulation_oracle(g,t)
    cert = minimum_gold_audit(g,t)
    assert cycle_rank(g)==1 and abs(periods[0][1])==2
    assert width["maximum_width"]==independent_width==2
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
            "min_targeted_extra_cell_disclosures":cert["count"],
        },
        "ugc_reward_hack":{
            "reachable_cell_records":len(reachable),
            "best_reported_score":str(exploit.selected_proxy_score),
            "worst_selected_true_utility":str(exploit.worst_selected_true_utility),
            "true_best":str(exploit.true_optimum),
            "worst_true_regret":str(exploit.worst_true_regret),
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
