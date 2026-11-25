"""Reproduce CCF-04 synthetic receipt and missingness witnesses."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'tests')]
from test_evaluation_ccf_scope import scope_cases, test_scope_boundaries, gate_census, missingness_census


def verify():
    test_scope_boundaries()
    count, accepted, legacy_invalid = gate_census()
    cells = missingness_census()
    paths = ('src/spiral_ln/evaluation_ccf_scope.py', 'tests/test_evaluation_ccf_scope.py', 'scripts/verify_evaluation_ccf_scope.py')
    return {'experiment': 'CCF-04', 'evidence': 'finite synthetic fixtures, no verifier execution',
            'scope_cases': len(scope_cases()), 'scope_positive_cases': sum(c[2] for c in scope_cases()),
            'gate_combinations': count, 'strict_acceptances': accepted, 'legacy_invalid_acceptances': legacy_invalid,
            'missingness_configurations': 1024, 'missingness_count_classes': cells,
            'checks': {'scope_cases_agree': True, 'gate_census_agrees': (count,accepted,legacy_invalid)==(4096,1,1023),
                       'missingness_bounds_sharp': cells==21},
            'source_sha256': {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT/'output/evaluation_ccf/ccf04.json')
    args = parser.parse_args()
    receipt = verify()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    print(json.dumps(receipt, sort_keys=True))
    if not all(receipt['checks'].values()):
        sys.exit(1)
