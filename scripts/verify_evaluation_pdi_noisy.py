"""Independent finite PDI-02 oracle, with exact source-hashed receipt."""
import argparse
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import random
from spiral_ln.evaluation_pdi import product_prior
from spiral_ln.evaluation_pdi_noisy import (amplification_cap, false_weights,
                                            optimal_audit, selection_risk)

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ('src/spiral_ln/evaluation_pdi.py', 'src/spiral_ln/evaluation_pdi_noisy.py',
           'tests/test_evaluation_pdi_noisy.py', 'scripts/verify_evaluation_pdi_noisy.py',
           'paper/proof_dependency_noisy.md')


def trees(remaining, channels, b):
    yield None
    for j in remaining:
        cost = channels[j][3]
        if cost <= b:
            children = tuple(trees(tuple(i for i in remaining if i != j), channels, b-cost))
            for no, yes in product(children, repeat=2):
                yield (j, no, yes)


def brute_value(tree, p, claims, channels, penalty):
    # Sample all potential channel outcomes first, then execute a fixed policy tree.
    # Partition worlds/outcomes by the actual public transcript at each leaf.
    groups = {}
    n = len(p).bit_length()-1
    valid = lambda world, masks: any(all((world >> i) & 1 for i in range(n) if (m >> i) & 1) for m in masks)
    for w, prior in enumerate(p):
        for ys in product((0, 1), repeat=len(channels)):
            mass = prior
            for (i, t, f, _), y in zip(channels, ys):
                r = t if (w >> i) & 1 else f
                mass *= r if y else 1-r
            if not mass:
                continue
            node, path = tree, ()
            while node is not None:
                j, no, yes = node
                path += ((j, ys[j]),)
                node = yes if ys[j] else no
            groups.setdefault(path, []).append((w, mass))
    true = false = F(0)
    for path, cells in groups.items():
        accepted = 0
        for i in range(n):
            results = [y for j, y in path if channels[j][0] == i]
            if results and all(results):
                accepted |= 1 << i
        for weight, masks in claims:
            if valid(accepted, masks):
                good = weight*sum(m for w, m in cells if valid(w, masks))
                bad = weight*sum(m for w, m in cells if not valid(w, masks))
                if good > penalty*bad:
                    true += good
                    false += bad
    return true-penalty*false, true, false


def verify():
    rng = random.Random(26112502)
    worlds_checked = policies_checked = 0
    for _ in range(64):
        claims = [(rng.randint(1, 4), tuple(rng.randrange(8) for _ in range(2))) for _ in range(3)]
        weights = tuple(rng.randint(1, 3) for _ in range(3))
        cap = amplification_cap(claims, weights)
        for world, accepted in product(range(8), repeat=2):
            f, x = false_weights(world, accepted, claims, weights)
            assert f <= cap*x
            worlds_checked += 1
    for _ in range(48):
        masses = [rng.randrange(4) for _ in range(8)]
        if not sum(masses):
            masses[0] = 1
        p = tuple(F(m, sum(masses)) for m in masses)
        claims = [(rng.randint(1, 3), tuple(rng.randrange(8) for _ in range(2))) for _ in range(2)]
        a = tuple((rng.randrange(3), rng.choice((F(1, 2), F(3, 4), F(1))),
                   rng.choice((F(0), F(1, 4), F(1, 2))), rng.randint(1, 2)) for _ in range(3))
        b, lam = rng.randrange(4), rng.randrange(4)
        actual = optimal_audit(p, claims, a, b, lam)
        expected = max((brute_value(t, p, claims, a, lam) for t in trees(tuple(range(3)), a, b)),
                       key=lambda v: (v[0], -v[2], v[1]))
        assert actual == expected
        assert actual[0] >= optimal_audit(p, claims, a, b, lam, adaptive=False)[0]
        policies_checked += 1
    p = product_prior([F(1, 2)]*3)
    claims = [(2, (3,)), (1, (4,))]
    a = [(i, F(9, 10), F(1, 10), 1) for i in range(3)]
    fixed = optimal_audit(p, claims, a, 2, 1, adaptive=False)
    adapt = optimal_audit(p, claims, a, 2, 1)
    checks = {'pathwise_bound': worlds_checked == 4096,
              'independent_noisy_oracle': policies_checked == 48,
              'sharp_gate': false_weights(0, 1, [(1, (1,))]*8, [1]) == (8, 1),
              'utility_risk_tradeoff': fixed == (F(2, 5), F(9, 20), F(1, 20)) and adapt == (F(51, 100), F(63, 100), F(3, 25)),
              'selection_two': selection_risk(F(1, 20), 2) == F(39, 400)}
    assert all(checks.values())
    return {'schema': 'PDI-02-v1', 'evidence': 'synthetic exact finite oracle; conditional independent noise; no model measurements',
            'world_acceptance_pairs': worlds_checked, 'policy_instances': policies_checked,
            'fixed': list(map(str, fixed)), 'adaptive': list(map(str, adapt)),
            'utility_tuple_order': ['utility', 'true_weight', 'false_weight'],
            'selection_risk_8_at_5_percent': str(selection_risk(F(1, 20), 8)), 'checks': checks,
            'source_sha256': {p: sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT/'output/evaluation_pdi/pdi_02.json')
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(verify(), indent=2, sort_keys=True)+'\n', encoding='utf-8')
