"""HG-08 EvalMath independent GF(2) causal derivative and sparse query verifier."""
from __future__ import annotations
import argparse
import hashlib
import json
from fractions import Fraction as Q
from math import comb
from pathlib import Path
from random import Random

from spiral_ln.evaluation_hypergames_causal import (
    parity, causal_difference, direct_difference, peel_known,
    support_certified, information_lower_bound, ideal_joint_code_success,
    forced_release_utility,
)

ROOT=Path(__file__).resolve().parents[1]
SOURCES=('src/spiral_ln/evaluation_hypergames_causal.py',
         'scripts/verify_evaluation_hypergames_causal.py',
         'tests/test_evaluation_hypergames_causal.py')


def verify()->dict:
    checks={}
    count=0
    for d in range(1,5):
        for p in range(1<<d):
            for x in range(1<<d):
                for flip in range(1<<d):
                    assert parity(p,x^flip,d)^parity(p,x,d)==causal_difference((p,),flip,d)[0]
                    count+=1
    checks['4680_exhaustive_derivatives']=count==4680
    rng=Random(202611170818);random_cases=0
    for d in (140,512,1024):
        for _ in range(100):
            p=(rng.getrandbits(d),rng.getrandbits(d))
            x=rng.getrandbits(d);s=rng.getrandbits(d)
            assert direct_difference(p,x,s,d)==causal_difference(p,s,d)
            random_cases+=1
    checks['300_independent_multioutput_differences']=random_cases==300
    checks['sparse_information_bounds']=[information_lower_bound(d,6) for d in (140,512,1024)]==[34,45,51]
    checks['entropy_is_integer_ceiling']=all(1<<information_lower_bound(d,k)>=comb(d,k) for d in range(1,12) for k in range(d+1))
    checks['entropy_is_tight_ceiling']=all(information_lower_bound(d,k)==0 or (1<<(information_lower_bound(d,k)-1))<comb(d,k) for d in range(1,12) for k in range(d+1))
    checks['peel_known_involution']=peel_known(peel_known((1,0),0b11010,(frozenset((1,3)),frozenset((2,))),5),0b11010,(frozenset((1,3)),frozenset((2,))),5)==(1,0)
    checks['single_support_certified']=support_certified({0:(1,),2:(1,),5:(1,)},8,1,3)
    checks['missing_positive_rejected']=not support_certified({0:(1,),2:(1,)},8,1,3)
    checks['two_output_certificate']=support_certified({0:(1,0),2:(1,0),3:(0,1),5:(0,1)},8,2,2)
    checks['one_bit_forced_release_utility']=forced_release_utility(Q(1,2))==Q(-5,2)
    checks['complete_information_utility']=forced_release_utility(Q(1))==Q(10)
    checks['two_missing_bits_ceiling']=ideal_joint_code_success((1,), (2,4), 4)==Q(1,4)
    checks['zero_deficiency_ceiling']=ideal_joint_code_success((1,2),(1,2),4)==Q(1)
    checks['nonlinear_group_parity_absence']=causal_difference((0b111111,),0b000011,6)==(0,)
    return {'schema':'HG-08/EvalMath-causal-v1',
        'evidence':'exact finite-field mathematics and independent explicit finite enumeration; no neural claims',
        'counts':{'finite_differences':count,'multioutput_highdim_cases':random_cases},
        'checks':checks,'all_passed':all(checks.values()),
        'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES}}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path)
    args=p.parse_args()
    result=verify();blob=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with args.output.open('x',encoding='utf8') as f:f.write(blob)
    else:print(blob,end='')
    raise SystemExit(0 if result['all_passed'] else 1)
