#!/usr/bin/env python3
"""Generate a deterministic SRG-01 receipt from the exact reference module."""
import hashlib
import json
from fractions import Fraction as F
from itertools import product
from pathlib import Path

from spiral_ln.evaluation_storyworld_reasoning import (
    DecisionProblem, effect_audit, formula_audit, independent_fixed_value,
    linear_scores, parity_problem,
)

ROOT = Path(__file__).resolve().parents[1]


def encode(x):
    if isinstance(x,F):
        return str(x)
    raise TypeError(type(x))


def receipt():
    parity = {str(k): parity_problem(k).profile() for k in range(1,5)}
    hidden = parity_problem(3,visible=(0,1)).profile()
    padded = parity_problem(3,nuisance=2).profile()
    states = tuple(product((0,1),repeat=3))
    p = DecisionProblem([(int(s[1+s[0]]==0),int(s[1+s[0]]==1)) for s in states],
                        [tuple(s[i] for s in states) for i in range(3)], [F(1,8)]*8)
    adaptive = p.value(2)
    fixed = independent_fixed_value(p,2)
    scores = [linear_scores(x, ((1,1,0),(-1,1,0)), (-F(1,2),F(1,2)))
              for x in states]
    formula = formula_audit(states,scores)
    gradual = effect_audit((0,),[(F(i,4),) for i in range(1,5)],(1,),(1,))
    jump = effect_audit((0,),[(0,),(0,),(0,),(1,)],(1,),(1,))
    checks = {
        "parity_curve": all(p["adaptive_curve"] == [F(1,2)]*int(k)+[F(1)]
                            for k,p in parity.items()),
        "independent_fixed_policy_census": all(
            independent_fixed_value(parity_problem(k),b) == parity[str(k)]["adaptive_curve"][b]
            for k in range(1,4) for b in range(k+1)),
        "hidden_gate": hidden["unobservable_gap"] == F(1,2),
        "nuisance_invariant": padded["min_budget_full"] == 3,
        "adaptive_advantage": adaptive == 1 and fixed == F(3,4),
        "semantic_support": formula["winner_set_changes"] == [4,0,0],
        "effect_apportionment": gradual["max_energy_share"] == F(1,4)
                               and jump["max_energy_share"] == 1
                               and gradual["net_progress"] == jump["net_progress"] == 1,
    }
    paths = ["src/spiral_ln/evaluation_storyworld_reasoning.py",
             "tests/test_storyworld_reasoning.py", "scripts/verify_storyworld_reasoning.py"]
    return {"evidence": "exact synthetic finite audit", "checks": checks,
            "parity": parity, "hidden": hidden, "padded": padded,
            "adaptive_vs_fixed": {"adaptive": adaptive,"fixed": fixed},
            "formula": formula, "gradual": gradual, "jump": jump,
            "sha256": {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--out",type=Path, default=ROOT/"output/evaluation_storyworld_reasoning/srg01.json")
    args = parser.parse_args()
    data = receipt()
    if not all(data["checks"].values()):
        raise SystemExit("SRG-01 verification failed")
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(data,default=encode,sort_keys=True,indent=2)+"\n",
                        encoding="utf-8")
    print(f"{sum(data['checks'].values())}/{len(data['checks'])} exact checks passed")
