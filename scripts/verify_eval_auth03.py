"""Regenerate source-hashed EVAL-AUTH-03 exact rational evidence.

PYTHONPATH=src python scripts/verify_eval_auth03.py --output /tmp/eval_auth03.json
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spiral_ln.evaluation_noisy_authorization import (
    AuditCandidate, AuditChannel, audit_value, audited_error,
    audit_budget_frontier, brute_force_budget_gain, public_error,
    rule_audit_value,
    weighted_public_error, weighted_audited_error, weighted_audit_value,
    weighted_expected_error_under_rule,
)


def calculate() -> dict[str, object]:
    calibration = {
        "balanced_reliable": AuditChannel(Q(1, 2), Q(9,10), Q(1,10)),
        "balanced_weak": AuditChannel(Q(1, 2), Q(3,5), Q(2,5)),
        "rare_reliable": AuditChannel(Q(1, 8), Q(9,10), Q(1,10)),
        "rare_weak": AuditChannel(Q(1, 8), Q(3,5), Q(2,5)),
        "intermediate_reliable": AuditChannel(Q(1,3), Q(9,10), Q(1,10)),
    }
    values = {
        name: {
            "risk_without_audit": str(public_error(ch)),
            "risk_after_audit": str(audited_error(ch)),
            "audit_value": str(audit_value(ch)),
        } for name,ch in calibration.items()
    }
    grid = (Q(0),Q(1,4),Q(1,2),Q(3,4),Q(1))
    audited = 0
    for p,t,f in product(grid,repeat=3):
        ch = AuditChannel(p,t,f)
        assert Q(0) <= audit_value(ch) <= public_error(ch)
        audited += 1

    scores = (-Q(1,4),Q(0),Q(1,8),Q(2,5))
    checked = 0
    for n in range(5):
        for vector in product(scores,repeat=n):
            rows = [AuditCandidate(f"case{i}",score) for i,score in enumerate(vector)]
            frontier = audit_budget_frontier(rows)
            for b in range(n+1):
                assert frontier[b] == brute_force_budget_gain(rows,b)
                checked += 1

    bad_model = rule_audit_value(
        AuditChannel(Q(3,5),Q(1,2),Q(1,2)),
        AuditChannel(Q(3,5),Q(99,100),Q(1,100)),
    )
    assert bad_model == -Q(1,10)

    cost_grid = 0
    for false_grant_cost in (Q(1,2),Q(1),Q(2),Q(5)):
        for p,t,f in product(grid,repeat=3):
            ch=AuditChannel(p,t,f)
            before=weighted_public_error(
                ch,false_grant_cost=false_grant_cost
            )
            after=weighted_audited_error(
                ch,false_grant_cost=false_grant_cost
            )
            assert Q(0) <= after <= before
            assert weighted_audit_value(
                ch,false_grant_cost=false_grant_cost
            )==before-after
            assert weighted_expected_error_under_rule(
                ch,ch,inspect=True,false_grant_cost=false_grant_cost
            )==after
            cost_grid+=1
    crossover=Q(76,59)
    assert crossover*(461-343)==644-492

    paths = (
        "src/spiral_ln/evaluation_noisy_authorization.py",
        "tests/test_evaluation_noisy_authorization.py",
        "scripts/verify_eval_auth03.py",
        "paper/noisy_authorization_audit_budget.md",
    )
    return {
        "schema": "eval_auth03_exact_v1",
        "evidence_level": "algebraic identities and finite exact oracle enumeration",
        "neural_models_run": 0,
        "named_channels": values,
        "noisy_channel_grid_checked": audited,
        "fixed_budget_bruteforce_checks": checked,
        "counterexample_fitted_rule_negative_value": str(bad_model),
        "cost_weighted_channel_grid_checked": cost_grid,
        "eca02_observed_frozen_action_cost_crossover": str(crossover),
        "source_sha256": {name: sha256((ROOT / name).read_bytes()).hexdigest()
                          for name in paths},
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output",type=Path)
    args = parser.parse_args()
    result = calculate()
    serialized = json.dumps(result,indent=2,sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(serialized,encoding="utf-8")
        print(args.output)
    else:
        print(serialized,end="")
