"""HG-05 EvalMath exact multi-goal information-rank verifier."""
from __future__ import annotations
import argparse
import hashlib
import json
from datetime import datetime,timezone
from fractions import Fraction as Q
from pathlib import Path
from random import Random
from itertools import combinations

from spiral_ln.evaluation_hypergames_rank import (
    deficiency, exact_joint_success, independent_fibre_success, rank,
    minimum_probe_cost, ideal_action_values, padding_invariant,
)

ROOT=Path(__file__).resolve().parents[1]
SOURCES=("src/spiral_ln/evaluation_hypergames_rank.py",
         "scripts/verify_evaluation_hypergames_rank.py",
         "tests/test_evaluation_hypergames_rank.py")


def independent_probe_minimum(c, p, probes, weights, d):
    """Independent explicit-world, finite-probe cost oracle for d<=5."""
    best=None
    for r in range(len(probes)+1):
        for idx in combinations(range(len(probes)),r):
            cc=c+tuple(probes[i] for i in idx)
            classes={}
            for x in range(1 << d):
                signature=tuple((x & bit).bit_count()%2 for bit in cc)
                label=tuple((x & bit).bit_count()%2 for bit in p)
                classes.setdefault(signature,set()).add(label)
            if all(len(labels)==1 for labels in classes.values()):
                item=(sum((weights[i] for i in idx),Q(0)),len(idx),idx)
                if best is None or item<best:best=item
    return None if best is None else best[0]


def verify():
    rng=Random(2026111705)
    checks={}
    small=0
    for d in range(1,7):
        for _ in range(32):
            obs=tuple(rng.randrange(1 << d) for _ in range(rng.randrange(5)))
            target=tuple(rng.randrange(1 << d) for _ in range(rng.randrange(5)))
            assert exact_joint_success(obs,target,d)==independent_fibre_success(obs,target,d)
            assert padding_invariant(obs,target,d,1024)
            small+=1
    checks['192_small_fibre_matches']=small==192
    a=tuple(1<<i for i in range(16))
    checks['rank_16_independent']=rank(a,140)==16
    checks['rank_deficiency_16']=deficiency((),a,140)==16
    checks['rank_16_joint_probability']=exact_joint_success((),a,140)==Q(1,65536)
    checks['observed_8_missing_8']=deficiency(a[:8],a,140)==8
    checks['ideal_certified_action']=ideal_action_values(1)=={
       'submit':Q(-5,2),'semantic_audit_then_submit':Q(9),'abstain':Q(0)}
    checks['long_horizon_audit_budget']=ideal_action_values(16)['semantic_audit_then_submit']==Q(-6)
    finite=0
    for d in (2,3,4,5):
        for _ in range(32):
            obs=tuple(rng.randrange(1<<d) for _ in range(2))
            tgt=tuple(rng.randrange(1<<d) for _ in range(2))
            probes=tuple(rng.randrange(1<<d) for _ in range(4))
            weights=tuple(Q(rng.randrange(1,7),rng.randrange(1,5)) for _ in range(4))
            actual=minimum_probe_cost(obs,tgt,probes,weights,d)
            oracle=independent_probe_minimum(obs,tgt,probes,weights,d)
            assert actual['cost']==oracle
            finite+=1
    checks['128_independent_weighted_audit_oracles']=finite==128
    checks['zero_rank_and_empty_target']=rank((),0)==0 and deficiency((),(),0)==0
    checks['rank_padding_sample']=padding_invariant((1,3),(5,7),4,1024)
    result={'schema_version':'HG-05/EvalMath-multigoal-rank-v1',
       'generated_at_utc':datetime.now(timezone.utc).isoformat(),
       'evidence':'algebraic rank theorem with independently enumerated finite F2 oracles',
       'counts':{'fibre_cases':small,'audit_cost_cases':finite},
       'checks':checks,'all_passed':all(checks.values()),
       'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES}}
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    report=verify()
    body=json.dumps(report,sort_keys=True,indent=2)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with args.output.open('x',encoding='utf8') as f:f.write(body)
    else:
        print(body,end='')
    return 0 if report['all_passed'] else 1


if __name__=='__main__':raise SystemExit(main())
