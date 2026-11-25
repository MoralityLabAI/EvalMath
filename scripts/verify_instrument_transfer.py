"""Regenerate MIT-01 receipt with exact oracle checks and source hashes."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys
from fractions import Fraction as F

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from spiral_ln.evaluation_instrument_transfer import shortlist, optimal_search, binary_query, fixed_prefix


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT/'output/evaluation_instrument_transfer/mit01_v0_1.json')
    args = parser.parse_args()
    paths = ('src/spiral_ln/evaluation_instrument_transfer.py','tests/test_instrument_transfer.py','scripts/verify_instrument_transfer.py')
    tests = runpy.run_path(str(ROOT/paths[1]))
    checks = {}
    for name in sorted(tests):
        if name.startswith('test_'):
            tests[name]()
            checks[name] = True
    masks = ((1,1,1,1,0,0,0,0),(1,1,0,0,0,0,0,0),(0,0,0,0,1,1,0,0))
    receipt = {'schema':'mit01-v0.1','evidence':'exact finite synthetic mechanism', 'checks':checks,
        'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},
        'paid_shortlist_half_reliable':list(map(str,shortlist(16,4,F(1,2),4,1))),
        'adaptive':str(optimal_search([1]*8,[binary_query(m) for m in masks],4)),
        'fixed_prefix':str(fixed_prefix([1]*8,masks,4))}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps(receipt,indent=2,sort_keys=True))


if __name__ == '__main__':
    main()
