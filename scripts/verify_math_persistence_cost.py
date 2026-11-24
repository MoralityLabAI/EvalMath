"""Reproduce EM-MPT-02 on a finite grid, using independent exact oracles."""
import argparse
import hashlib
import json
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from spiral_ln.evaluation_math_persistence_cost import (
    tail, quota, static, mix_value, extreme_mixtures, robust_gap, break_even,
    allocations, binary_oracle)


def build():
    grid = tuple(F(k,4) for k in range(5))
    counts = dict(binary=0, static=0, moment=0)
    for d, b, p in product(range(1,5), range(9), grid):
        assert tail(d,b,p) == binary_oracle(d,b,p)
        counts['binary'] += 1
        assert static(quota(d,b),p) == max(static(a,p) for a in allocations(d,b))
        counts['static'] += 1
    # Independent oracle: enumerate every integer-weight law with denominator 8.
    # On the five-point grid at mean 1/2, all extreme laws have denominator 2 or 3 (or are point masses).
    laws = [tuple((p,F(w,8)) for p,w in zip(grid,a) if w)
            for a in allocations(5,8) if sum(p*w for p,w in zip(grid,a)) == 4]
    # Some vertices have denominator 3, so include all denominator-3 laws too.
    laws += [tuple((p,F(w,3)) for p,w in zip(grid,a) if w)
             for a in allocations(5,3) if sum(p*w for p,w in zip(grid,a)) == F(3,2)]
    for d in range(1,5):
        for b in range(9):
            a = quota(d,b)
            previous = None
            for c in range(b+1):
                gap = robust_gap(d,b,c,grid,F(1,2))
                assert gap == min(mix_value(m,lambda p: tail(d,b-c,p)-static(a,p)) for m in laws)
                assert previous is None or previous >= gap
                previous = gap
                counts['moment'] += 1
    s = grid[1:-1]
    m = F(1,2)
    mix = ((s[0],m),(s[2],m))
    values = {'iid_d4_b4': tail(4,4,m), 'mixture_d4_b4': mix_value(mix,lambda p: tail(4,4,p)),
              'iid_d4_b8': tail(4,8,m), 'mixture_d4_b8': mix_value(mix,lambda p: tail(4,8,p)),
              'robust_gaps_d4_b8': [str(robust_gap(4,8,c,s,m)) for c in range(5)],
              'strict_charge_d4_b8': break_even(4,8,s,m,True),
              'strict_charge_d4_b12': break_even(4,12,s,m,True)}
    paths = ['src/spiral_ln/evaluation_math_persistence_cost.py',
             'scripts/verify_math_persistence_cost.py', 'tests/test_evaluation_math_persistence_cost.py']
    return {'schema':'em-mpt-02-v0.1','evidence':'exact finite synthetic mechanism',
            'counts':counts,'oracle_laws':len(laws),
            'values':{k:str(v) if isinstance(v,F) else v for k,v in values.items()},
            'checks':{'binomial_vs_binary':True,'balanced_vs_all_quotas':True,
                      'moment_vertices_vs_integer_laws':True,'charge_monotonicity':True},
            'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'output/evaluation_math_persistence_cost/em_mpt_02_v0_1.json')
    out = parser.parse_args().output
    receipt = build()
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(receipt,indent=2,sort_keys=True))
