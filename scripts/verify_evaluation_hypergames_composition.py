"""HG-06 EvalMath source-hashed exact finite-composition verifier."""
from __future__ import annotations
import argparse
import hashlib
import json
from datetime import datetime,timezone
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
from random import Random

from spiral_ln.evaluation_hypergames_composition import (
    fragment_weight_floor, exact_shortest_xor,parity_disagreement_probability,
    independent_parity_collision,spurious_fit_union_bound,
    exact_signed_candidates,posterior_joint_predictive_accuracy,
    certified_joint_goal_capacity)
from spiral_ln.evaluation_hypergames_rank import independent_fibre_success

ROOT=Path(__file__).resolve().parents[1]
SOURCES=('src/spiral_ln/evaluation_hypergames_composition.py',
         'scripts/verify_evaluation_hypergames_composition.py',
         'tests/test_evaluation_hypergames_composition.py')


def verify():
    checks={}
    target=63
    rows=tuple((1<<i)|(1<<j) for i,j in combinations(range(6),2))
    checks['six_bit_three_pair_lower_bound']=fragment_weight_floor(target,2)==3
    checks['two_pair_impossibility_exhaustive']=exact_shortest_xor(target,rows,6,2) is None
    checks['three_pair_constructive_witness']=exact_shortest_xor(target,(3,12,48),6,3)==(0,1,2)
    full=certified_joint_goal_capacity((3,12,48),(63,),6)
    missing=certified_joint_goal_capacity((3,12),(63,),6)
    checks['full_dictionary_goal_exact']=full['optimal_joint_success']==Q(1)
    checks['missing_fragment_halves_success']=missing['optimal_joint_success']==Q(1,2)
    collisions=0
    for d in range(1,5):
        for a in range(1<<d):
            for b in range(1<<d):
                for n in (0,1,2):
                    assert parity_disagreement_probability(a,b,d,n)==independent_parity_collision(a,b,d,n)
                    collisions+=1
    checks['1020_independent_parity_collisions']=collisions==1020
    rng=Random(2026111706)
    fibres=0
    for d in range(1,7):
        for _ in range(24):
            obs=tuple(rng.randrange(1<<d) for _ in range(rng.randrange(4)))
            tgt=tuple(rng.randrange(1<<d) for _ in range(rng.randrange(4)))
            assert certified_joint_goal_capacity(obs,tgt,d)['optimal_joint_success']==independent_fibre_success(obs,tgt,d)
            fibres+=1
    checks['144_independent_goal_fibres']=fibres==144
    support=exact_signed_candidates((1,2),(0,),(0,),2)
    checks['posterior_two_candidates']=support==((1,0),(2,0))
    checks['posterior_bayes_three_quarters']=posterior_joint_predictive_accuracy(support,2)==Q(3,4)
    checks['vacuous_union_bound_reported']=spurious_fit_union_bound(100,8,8)==Q(1)
    checks['nonvacuous_union_bound']=spurious_fit_union_bound(5,2,64)==Q(18,1<<64)
    checks['zero_goal_boundary']=fragment_weight_floor(0,2)==0
    return {'schema_version':'HG-06/EvalMath-compositional-v1',
      'generated_at_utc':datetime.now(timezone.utc).isoformat(),
      'evidence':'algebraic inequalities and independently enumerated finite binary oracles',
      'counts':{'collision_oracles':collisions,'goal_fibre_oracles':fibres},
      'checks':checks,'all_passed':all(checks.values()),
      'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES}}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    report=verify()
    body=json.dumps(report,sort_keys=True,indent=2)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with args.output.open('x',encoding='utf8') as file:file.write(body)
    else:print(body,end='')
    return 0 if report['all_passed'] else 1

if __name__=='__main__':raise SystemExit(main())
