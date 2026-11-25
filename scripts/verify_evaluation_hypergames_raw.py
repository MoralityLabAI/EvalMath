"""Source-hashed exact HG-07 finite F2 observability reference checks."""
from __future__ import annotations
import argparse
import hashlib
import json
from datetime import datetime,timezone
from itertools import product
from fractions import Fraction as Q
from pathlib import Path
from random import Random
from spiral_ln.evaluation_hypergames_raw import (
    fit_raw_system,independent_fit_predict,parity_mask,design_posterior_cardinality,
    identified_fraction_uniform_query,observation_goal_floor,sparse_collision_union_bound)
from spiral_ln.evaluation_hypergames_rank import rank

ROOT=Path(__file__).resolve().parents[1]
SOURCES=("src/spiral_ln/evaluation_hypergames_raw.py",
         "scripts/verify_evaluation_hypergames_raw.py",
         "tests/test_evaluation_hypergames_raw.py")


def verify():
    rng=Random(2026111707)
    cases=0;failures=0
    for d in range(1,7):
        for _ in range(32):
            inputs=tuple(rng.randrange(1<<d) for i in range(rng.randrange(1,5)))
            goals=tuple(rng.randrange(1<<d) for _ in range(2))
            labels=tuple(sum(parity_mask(x,m)<<j for j,m in enumerate(goals)) for x in inputs)
            fit=fit_raw_system(inputs,labels,d,2)
            check=independent_fit_predict(inputs,labels,tuple(range(1<<d)),d,2)
            if any(fit.predict_if_identified(x)!=c for x,c in zip(range(1<<d),check)):failures+=1
            cases+=1
    posterior_cases=0;posterior_failures=0
    for d in range(1,5):
        for x in range(1<<d):
            rows=(x,)
            actual=sum(parity_mask(m,x)==0 for m in range(1<<d))
            expected=design_posterior_cardinality(rows,d)
            posterior_failures+= actual!=expected
            posterior_cases+=1
    checks={
      '192_finite_rowspace_comparisons':cases==192 and failures==0,
      '30_bruteforce_posterior_counts':posterior_cases==30 and posterior_failures==0,
      'full_rank_exact_prediction':fit_raw_system((1,2,4,7),(1,0,1,0),3,1).predict_if_identified(5)==0,
      'zero_observation_uniform_query_fraction':identified_fraction_uniform_query((),6)==Q(1,64),
      'full_observation_uniform_query_fraction':identified_fraction_uniform_query((1,2,4,8,16,32),6)==Q(1),
      'one_missing_goal_bit_floor':observation_goal_floor((1,),(2,),2)==Q(1,2),
      'two_missing_goal_bit_floor':observation_goal_floor((),(1,2),2)==Q(1,4),
      '64_ambient_with_rank_2_posterior':design_posterior_cardinality((1,2),64)==2**62,
      'wide_world_sparse_bound_decays':sparse_collision_union_bound(512,6,2048)<Q(1,2**1900),
      'tiny_sparse_class_bound_zero':sparse_collision_union_bound(6,6,0)==0,
      'padding_rank_invariance':design_posterior_cardinality((1,2),3)==2 and design_posterior_cardinality((1,2),512)==2**510,
      'single_sample_collision_probability':Q(sum(parity_mask(x,1)==parity_mask(x,2) for x in range(4)),4)==Q(1,2),
      'one_sparse_mask_not_identified_by_zero_samples':design_posterior_cardinality((),3)==8,
      'rank_zero_stability':rank((0,0),100)==0
    }
    return {'schema_version':'HG-07/exact-raw-observability-v1',
        'generated_at_utc':datetime.now(timezone.utc).isoformat(),
        'evidence_level':'algebraic arguments plus independent exhaustive small-F2 verification',
        'counts':{'rowspace_oracle_cases':cases,'posterior_cases':posterior_cases},
        'checks':checks,'all_passed':all(checks.values()),
        'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES}}


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path);args=ap.parse_args()
    result=verify();rendered=json.dumps(result,sort_keys=True,indent=2)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with args.output.open('x') as file:file.write(rendered)
    else:print(rendered,end='')
    return 0 if result['all_passed'] else 1

if __name__=='__main__':raise SystemExit(main())
