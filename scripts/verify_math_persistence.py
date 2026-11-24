"""Reproduce EM-MPT-01 exact finite checks and source-hashed receipt."""
import argparse
import hashlib
import json
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from spiral_ln.evaluation_math_persistence import (persistent, homogeneous, exhaustive,
                                                    fixed_best, reset)


def build():
    grid = (F(0), F(1,4), F(1,2), F(3,4), F(1))
    heterogeneous = 0
    for d in range(5):
        for ps in product(grid, repeat=d):
            for b in range(9):
                assert persistent(ps, b) == exhaustive(ps, b)
                assert persistent(ps, b) >= fixed_best(ps, b)
                heterogeneous += 1
    hom = 0
    for d in range(6):
        for b in range(11):
            for p in grid:
                r = persistent((p,)*d, b)
                assert r == homogeneous(d, b, p)
                assert r >= reset(d, b, p)
                hom += 1
    a, c = (F(1,2), F(1,2)), (F(1), F(1,4))
    assert a[0]*a[1] == c[0]*c[1] == F(1,4)
    assert persistent(a, 3) == F(1,2) and persistent(c, 3) == F(7,16)
    values = {'balanced': persistent(a, 3), 'concentrated': persistent(c, 3),
              'persistent_d4_b8': persistent((F(1,2),)*4, 8),
              'fixed_d4_b8': fixed_best((F(1,2),)*4, 8),
              'reset_d4_b8': reset(4, 8, F(1,2))}
    paths = ['src/spiral_ln/evaluation_math_persistence.py',
             'scripts/verify_math_persistence.py', 'tests/test_evaluation_math_persistence.py']
    return {'schema': 'em-mpt-01-v0.1', 'evidence': 'exact finite synthetic mechanism',
            'heterogeneous_cases': heterogeneous, 'homogeneous_cases': hom,
            'values': {k: str(v) for k, v in values.items()},
            'checks': {'dp_matches_prefix_oracle': True, 'persistence_dominates_static': True,
                       'homogeneous_binomial_and_reset': True, 'equal_loss_witness': True},
            'source_sha256': {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'output/evaluation_math_persistence/em_mpt_01_v0_1.json')
    target = parser.parse_args().output
    result = build()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2, sort_keys=True))
