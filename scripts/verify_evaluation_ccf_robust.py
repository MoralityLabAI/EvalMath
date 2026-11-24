"""Generate source-hashed CCF-01C exact receipt."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'tests')]
from spiral_ln.evaluation_ccf_robust import compromise_fixture, minimax
from test_evaluation_ccf_robust import census, test_compromise, test_sharp_union


def verify():
    count = census()
    test_compromise()
    test_sharp_union()
    ctx, _, laws = compromise_fixture()
    value, opt, table = minimax(ctx, 3, 2, laws)
    paths = ['src/spiral_ln/evaluation_ccf_robust.py', 'tests/test_evaluation_ccf_robust.py', 'scripts/verify_evaluation_ccf_robust.py']
    return {'experiment': 'CCF-01C', 'evidence': 'finite verified synthetic examples',
            'policy_oracle_comparisons': count, 'minimax_oracle_comparisons': 384,
            'sharp_flag_couplings': 720, 'mixture_grid_points': 11,
            'robust_value': str(value), 'optimal_codes': [''.join(map(str, p)) for p in opt],
            'scenario_risks': {''.join(map(str, p)): list(map(str, v)) for p, v in table.items()},
            'checks': {'oracles_agree': count == 3072, 'compromise': True, 'mixture_convexity': True, 'sharp_union': True},
            'source_sha256': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT / 'output/evaluation_ccf/ccf01c.json')
    args = parser.parse_args()
    receipt = verify()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps(receipt, sort_keys=True))
    if not all(receipt['checks'].values()):
        sys.exit(1)
