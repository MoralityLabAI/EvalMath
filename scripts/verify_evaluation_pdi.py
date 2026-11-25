"""PDI-01 deterministic receipt; independently enumerate policy trees."""
import argparse
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import random
from spiral_ln.evaluation_pdi import (audit_value, failure, independent_failure,
                                      intersection_bounds, product_prior, shared_failure)

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ('src/spiral_ln/evaluation_pdi.py', 'tests/test_evaluation_pdi.py',
           'scripts/verify_evaluation_pdi.py', 'paper/proof_dependency_information.md',
           'lean/FeedbackChannel/ProofDependency.lean')


def trees(indices, costs, budget):
    yield None
    for i in indices:
        if costs[i] <= budget:
            rest = tuple(j for j in indices if j != i)
            children = tuple(trees(rest, costs, budget-costs[i]))
            for left, right in product(children, repeat=2):
                yield (i, left, right)


def path(tree, world):
    steps = []
    while tree is not None:
        i, left, right = tree
        v = (world >> i) & 1
        steps.append((i, v))
        tree = right if v else left
    return tuple(steps)


def tree_value(tree, prior, claims):
    groups = {}
    for w, mass in enumerate(prior):
        if mass:
            groups.setdefault(path(tree, w), []).append(w)
    total = F(0)
    for ws in groups.values():
        for weight, certs in claims:
            # Independent representation: explicit sets of required valid bits.
            if all(any(all((w >> i) & 1 for i in range(len(prior).bit_length()-1) if (m >> i) & 1)
                       for m in certs) for w in ws):
                total += weight*sum(prior[w] for w in ws)
    return total


def verify():
    shared_cases = 0
    for q, r, n in product((F(0), F(1, 5), F(1, 2), F(1)),
                           (F(0), F(1, 5), F(1, 2), F(1)), range(1, 5)):
        p = product_prior([1-q]+[1-r]*n)
        assert failure(p, [1 | (2 << i) for i in range(n)]) == shared_failure(q, r, n)
        assert shared_failure(q, r, n) >= independent_failure(q, r, n)
        shared_cases += 1
    rng = random.Random(2601125)
    policy_cases = 0
    for _ in range(64):
        masses = [rng.randrange(4) for _ in range(8)]
        if not sum(masses):
            masses[0] = 1
        p = tuple(F(m, sum(masses)) for m in masses)
        claims = [(rng.randrange(1, 4), tuple(rng.randrange(1, 8) for _ in range(2))) for _ in range(2)]
        costs = tuple(rng.randrange(1, 3) for _ in range(3))
        b = rng.randrange(4)
        actual = audit_value(p, claims, costs, b)
        brute = max(tree_value(t, p, claims) for t in trees(tuple(range(3)), costs, b))
        assert actual == brute
        assert actual >= audit_value(p, claims, costs, b, adaptive=False)
        policy_cases += 1
    p = product_prior([F(1, 2)]*3)
    claims = [(2, (3,)), (1, (4,))]
    adaptive = audit_value(p, claims, [1]*3, 2)
    fixed = audit_value(p, claims, [1]*3, 2, adaptive=False)
    lo, hi = intersection_bounds([F(3, 4), F(2, 3)])
    # Explicit endpoint couplings, both with the declared failure marginals.
    for joint in (lo, hi):
        cells = (joint, F(3, 4)-joint, F(2, 3)-joint, 1-F(3, 4)-F(2, 3)+joint)
        assert min(cells) >= 0 and sum(cells) == 1
        assert cells[0]+cells[1] == F(3, 4) and cells[0]+cells[2] == F(2, 3)
    checks = {'shared_grid': shared_cases == 64, 'policy_tree_agreement': policy_cases == 64,
              'strict_adaptive_gain': adaptive == F(3, 4) and fixed == F(1, 2),
              'two_event_sharp_bounds': (lo, hi) == (F(5, 12), F(2, 3))}
    assert all(checks.values())
    return {'schema': 'PDI-01-v1', 'evidence': 'exact finite synthetic audit; no model or manuscript validity estimate',
            'shared_cases': shared_cases, 'policy_cases': policy_cases,
            'adaptive_witness': {'fixed': str(fixed), 'adaptive': str(adaptive)},
            'two_event_bounds': [str(lo), str(hi)], 'checks': checks,
            'source_sha256': {p: sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT/'output/evaluation_pdi/pdi_01.json')
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(verify(), indent=2, sort_keys=True)+'\n', encoding='utf-8')
