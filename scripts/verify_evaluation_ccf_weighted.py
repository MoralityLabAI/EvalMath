"""Reproduce CCF-01B finite weighted frontier and selection witnesses."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'tests')]
from test_evaluation_ccf_weighted import census, witness, test_selection_changes_optimal_encoding, test_hidden_mismatch


def verify():
    count, tradeoffs = census()
    test_selection_changes_optimal_encoding()
    test_hidden_mismatch()
    paths = ('src/spiral_ln/evaluation_ccf.py', 'src/spiral_ln/evaluation_ccf_weighted.py',
             'tests/test_evaluation_ccf_weighted.py', 'scripts/verify_evaluation_ccf_weighted.py')
    return {'experiment': 'CCF-01B', 'evidence': 'finite verified example; synthetic',
            'weighted_budget_cases': count, 'strict_pareto_tradeoff_cases': tradeoffs,
            'visibility_order': ['none', 'receipt', 'world'],
            'visible_coupling': {p: list(map(str, v)) for p, v in witness().items()},
            'hidden_coupling': {p: list(map(str, v)) for p, v in witness(True).items()},
            'checks': {'all_frontiers_agree': count == 384, 'selection_oracles_agree': True,
                       'optimum_changes': True, 'hidden_gap': True},
            'source_sha256': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT / 'output/evaluation_ccf/ccf01b.json')
    args = parser.parse_args()
    receipt = verify()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps(receipt, sort_keys=True))
    if not all(receipt['checks'].values()):
        sys.exit(1)
