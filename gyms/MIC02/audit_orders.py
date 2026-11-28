"""Regenerate exhaustive schedule diagnostic from the public MIC-02 generator."""
from fractions import Fraction as F
from itertools import permutations
import json
from statistics import mean
from spiral_ln.mic02 import FAMILIES, N, root, run, score, walk


def audit():
    data = run()
    out = {}
    for f in FAMILIES:
        diff, regret, spread = [], [], []
        invariant = 0
        for row in data['results'][f]['rows']:
            d = root(f, row['seed'])
            values = [score(f, d, walk(f, d, list(o))) for o in permutations(range(N))]
            z = max(1, row['initial'])
            diff.append((mean(map(F, values)) - row['scores'][0]) / z)
            regret.append(F(row['scores'][0] - min(values), z))
            spread.append(F(max(values) - min(values), z))
            invariant += len(set(values)) == 1
        out[f] = {'mean_advantage_vs_all_orders': str(mean(diff)),
                  'mean_order_regret': str(mean(regret)),
                  'max_order_spread': str(max(spread)), 'order_invariant_roots': invariant}
    return {'schema': 'MIC-02/order-audit/v1', 'source_sha256': data['source_sha256'],
            'schedules': len(FAMILIES) * data['roots_per_family'] * 120, 'families': out}


if __name__ == '__main__':
    print(json.dumps(audit(), sort_keys=True, indent=2))
