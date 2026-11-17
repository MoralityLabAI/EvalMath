"""Source-hashed EvalMath HG-04 exact quotient and audit-value receipt."""
from __future__ import annotations
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from fractions import Fraction as F
from spiral_ln.evaluation_hypergame_quotient_math import (
    rank_gf2, uniform_parity_error, independently_enumerated_error,
    audited_release_expectation, prior_optimal_value,
)
from spiral_ln.hypergames_single_player import make_scenario, initial_state, optimal_value

ROOT=Path(__file__).resolve().parents[1]
SOURCES=("src/spiral_ln/evaluation_hypergame_quotient_math.py",
         "tests/test_evaluation_hypergame_quotient_math.py",
         "scripts/verify_evaluation_hypergame_quotient_math.py",
         "Hypergames/HG04_QUOTIENT_THEOREMS.md")

def verify():
    comparisons=0
    for rows in ((),(0,),(1,2),(3,5),(1,2,4),(1,3,7)):
        for target in range(16):
            assert independently_enumerated_error(rows,target,4)==uniform_parity_error(rows,target,4)
            comparisons+=1
    s=make_scenario(17,140)
    bellman=0
    for h in (4,5):
        for p in (F(1,2),F(3,5),F(4,5),F(24,25),F(1)):
            b=tuple((initial_state(secret,h),m)
                for secret,m in ((0,1-p),(1,p)) if m>0)
            assert optimal_value(s,b)==prior_optimal_value(p,h)
            bellman+=1
    checks={
        'rank_basis':rank_gf2((1,2,4),4)==3,
        'rank_dependent':rank_gf2((3,5,6),4)==2,
        'identified_target':uniform_parity_error((3,5),6,4)==0,
        'unidentified_target':uniform_parity_error((1,2),4,4)==F(1,2),
        'independent_fibre_oracle':comparisons==96,
        'independent_bellman_comparison':bellman==10,
        'audit_boundary':audited_release_expectation(F(16,25))==0,
        'prior_four_actions':prior_optimal_value(F(4,5),4)==5,
        'prior_five_actions':prior_optimal_value(F(1,2),5)==9,
    }
    return {'schema_version':'HG-04/quotient-math-v1',
            'generated_at_utc':datetime.now(timezone.utc).isoformat(),
            'evidence_level':'algebraic identities and exact finite confirmations; no Lean/model',
            'case_counts':{'independent_fibre_cases':comparisons,'bellman_cases':bellman},
            'checks':checks,'all_passed':all(checks.values()),
            'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES}}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    report=verify()
    output=json.dumps(report,sort_keys=True,indent=2)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with args.output.open('x',encoding='utf8') as f:f.write(output)
    else:print(output,end='')
    return 0 if report['all_passed'] else 1

if __name__=='__main__':raise SystemExit(main())
