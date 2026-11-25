"""Regenerate the source-hashed ADG-01 development receipt."""
import hashlib
import json
from fractions import Fraction as F
from pathlib import Path
from spiral_ln.evaluation_abductive_discovery import solve, world

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ['src/spiral_ln/evaluation_abductive_discovery.py', 'tests/test_abductive_discovery.py',
           'scripts/verify_abductive_discovery.py']


def run():
    rows = []
    for k in (1, 2, 3):
        for seed in range(16):
            budget = k + 2
            a = world(seed + 1000*k, k)
            scores = {str(h): solve(a, budget, h) for h in (1, 2, None)}
            scores['ungated'] = solve(world(seed + 1000*k, k, ungated=True), budget)
            scores['sham'] = solve(world(seed + 1000*k, k, sham=True), budget)
            assert sum(x*y for x,y in zip(scores['None'], (1,3))) == sum(x*y for x,y in zip(scores['sham'], (1,3)))
            rows.append({'k': k, 'seed': seed+1000*k, 'budget': budget,
                         'scores': {h: list(map(str, pair)) for h,pair in scores.items()}})
    summary = {}
    for k in (1,2,3):
        subset = [r for r in rows if r['k'] == k]
        summary[str(k)] = {h: [str(sum(F(r['scores'][h][j]) for r in subset)/len(subset)) for j in (0,1)]
                           for h in subset[0]['scores']}
    return {'schema': 'ADG-01/v1', 'evidence': 'finite synthetic development census; no model runs',
            'source_sha256': {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES},
            'summary_correct_certified': summary, 'rows': rows}


if __name__ == '__main__':
    result = run()
    p = ROOT/'output/evaluation_adg/adg_01.json'
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result['summary_correct_certified'], indent=2))
