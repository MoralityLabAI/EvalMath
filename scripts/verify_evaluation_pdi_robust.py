"""Regenerate PDI-04--06 exact receipt with independent small policy oracles."""
import argparse
from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import random
from spiral_ln.evaluation_pdi_frontier import at_risk, frontier
from spiral_ln.evaluation_pdi_robust import (hazard_audit, hazard_bound, projected_posterior,
    robust_frontier, robust_mix, source_law, transfer_profile)

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ('src/spiral_ln/evaluation_pdi.py', 'src/spiral_ln/evaluation_pdi_noisy.py',
    'src/spiral_ln/evaluation_pdi_frontier.py', 'src/spiral_ln/evaluation_pdi_robust.py',
    'scripts/verify_evaluation_pdi_robust.py', 'tests/test_evaluation_pdi_robust.py',
    'paper/proof_dependency_robust.md')


def valid(w, masks, n):
    return any(all((w >> i) & 1 for i in range(n) if (m >> i) & 1) for m in masks)


def trees(a, claims, n, budget, path=()):
    accepted = sum(1 << i for i in range(n) if (ys := [y for j, y in path if a[j][0] == i]) and all(ys))
    eligible = [j for j, (_, ms) in enumerate(claims) if valid(accepted, ms, n)]
    for k in range(len(eligible)+1):
        for ids in combinations(eligible, k):
            yield ('leaf', ids)
    for j, (_, _, _, cost) in enumerate(a):
        if cost <= budget and all(j != h for h, _ in path):
            for l, r in product(trees(a, claims, n, budget-cost, path+((j, 0),)),
                                trees(a, claims, n, budget-cost, path+((j, 1),))):
                yield ('audit', j, l, r)


def replay(tree, scenarios, claims):
    out = []
    for p, a in scenarios:
        n = len(p).bit_length()-1
        false = true = F(0)
        for w, prior in enumerate(p):
            for ys in product((0, 1), repeat=len(a)):
                mass = prior
                for (i, t, f, _), y in zip(a, ys):
                    r = t if w & (1 << i) else f
                    mass *= r if y else 1-r
                node = tree
                while node[0] == 'audit':
                    node = node[2+ys[node[1]]]
                for j in node[1]:
                    weight, ms = claims[j]
                    if valid(w, ms, n):
                        true += weight*mass
                    else:
                        false += weight*mass
        out.extend((false, true))
    return tuple(out)


def brute_frontier(scenarios, claims, budget):
    p, a = scenarios[0]
    points = {replay(t, scenarios, claims) for t in trees(a, claims, len(p).bit_length()-1, budget)}
    return tuple(sorted(v for v in points if not any(u != v and all(
        x <= y if i % 2 == 0 else x >= y for i, (x, y) in enumerate(zip(u, v))) for u in points)))


def random_case(rng):
    topology = [(rng.randrange(2), rng.randint(1, 2)) for _ in range(2)]
    scenarios = []
    for _ in range(2):
        masses = [rng.randrange(4) for _ in range(4)]
        if not sum(masses):
            masses[0] = 1
        p = tuple(F(m, sum(masses)) for m in masses)
        a = tuple((i, rng.choice((F(1,2), F(3,4), F(1))), rng.choice((F(0), F(1,4), F(1,2))), cost)
                  for i, cost in topology)
        scenarios.append((p, a))
    claims = [(rng.randint(1, 3), tuple(rng.randrange(1, 4) for _ in range(2)))]
    return tuple(scenarios), claims, rng.randrange(4)


def brute_false(k, q, p, f, shared):
    """Independent Bernoulli enumeration of bad-root acceptance and branch validity."""
    roots = 1 if shared else k
    out = [F(0)]*(k+1)
    for root, branch in product(product((0,1), repeat=roots), product((0,1), repeat=k)):
        mass = F(1)
        for r in root:
            v = (1-q)*f
            mass *= v if r else 1-v
        for b in branch:
            mass *= p if b else 1-p
        count = sum(b*root[0 if shared else i] for i, b in enumerate(branch))
        out[count] += mass
    return tuple(out)


def verify():
    rng = random.Random(26112504)
    vectors = single = 0
    for _ in range(32):
        sc, c, b = random_case(rng)
        rows = robust_frontier(sc, c, b)
        assert tuple(v for v, _ in rows) == brute_frontier(sc, c, b)
        for v, tree in rows:
            assert replay(tree, sc, c) == v
            vectors += 1
        z, v, mix = robust_mix(rows, F(1, 10))
        assert sum(w for w, _ in mix) == 1 and max(v[::2]) <= F(1,10) and z == min(v[1::2])
        assert v == tuple(sum(w*replay(tree, sc, c)[i] for w, tree in mix) for i in range(4))
        p, a = sc[0]
        for e in (F(0), F(1,10), F(1,2)):
            r = robust_frontier(sc[:1], c, b)
            assert robust_mix(r, e)[0] == at_risk(frontier(p, c, a, b), e)[0][1]
            single += 1
    p = (F(1,2), F(1,2)); c = [(1, (1,))]
    a = ((0, 1, F(1,5), 1), (0, F(1,5), 0, 1))
    sc = ((p, a), (p, a[::-1]))
    rows = robust_frontier(sc, c, 1)
    z, v, mix = robust_mix(rows, F(1,20))
    assert z == F(3,10) and v == (F(1,20), F(3,10))*2
    assert max(min(x[1::2]) for x, _ in rows if max(x[::2]) <= F(1,20)) == 0
    assert max(sum(x[1::2]) for x, _ in rows) == F(3,5)
    # Exact product-bound equality for independent hazards; conditional audit sees the whole past.
    alphas = (F(1,5), F(1,3), F(1,4))
    paths = []
    for ys in product((0,1), repeat=3):
        mass = F(1)
        for y, a in zip(ys, alphas):
            mass *= a if y else 1-a
        paths.append((mass, tuple(('public', y) for y in ys)))
    maxima, risk, ok = hazard_audit(paths, alphas)
    assert ok and maxima == alphas and risk == hazard_bound(alphas) == F(3,5)
    # Actor selects the passing invalid candidate after observing the private bit.
    peek = [(F(1,2), ((s, 1),)) for s in (0,1)]
    assert hazard_audit(peek, [F(1,2)]) == ((1,), 1, False)
    law = source_law(F(3,4))
    assert projected_posterior(law, (0,1), (0,1))[1] == projected_posterior(law, (0,1), (1,0))[1] == F(1,2)
    assert projected_posterior(law, (1,), (1,))[1] == F(3,4)
    assert projected_posterior(law, (1,), (0,))[1] == F(1,4)
    assert projected_posterior(law, (1,2,3), (1,0,1))[1] == F(1,2)
    assert projected_posterior(source_law(F(1,2), F(3,4)), (1,2,3), (1,0,1))[1] == F(3,4)
    distributions = 0
    for n, b, q, bp, f in product(range(1,5), range(8), (F(1,2), F(3,4)), (F(1,2), F(1)), (F(0), F(1,5))):
        pair = transfer_profile(n, 2, 1, b, q, bp, F(3,4), f)
        for shared, (k, t, dist) in zip((True, False), pair):
            assert sum(dist) == 1 and dist == brute_false(k, q, bp, f, shared)
            assert t == k*q*F(3,4)*bp
            distributions += 1
    shared, independent = transfer_profile(8, 3, 1, 11, F(9,10), F(1), F(9,10), F(1,10))
    assert shared[:2] == (8, F(162,25)) and independent[:2] == (2, F(81,50))
    assert shared[2][-1] == F(1,100) and independent[2][-1] == F(1,10000)
    checks = dict(robust_frontier=True, witness_replay=True, one_scenario_reduction=single == 96,
                  robust_mixture=True, conditional_hazard=True, selection_prepeek=True,
                  versioned_posterior=True, transfer_distribution=distributions == 512)
    assert all(checks.values())
    return {'schema': 'PDI-04-06-v1', 'evidence': 'exact finite synthetic; no neural measurements or new Lean verification',
        'robust_cases': 32, 'replayed_vectors': vectors, 'single_scenario_checks': single,
        'robust_witness': {'risk_cap': '1/20', 'best_deterministic': '0', 'worst_true': str(z),
            'scenario_vector': list(map(str,v)), 'mixture': [{'weight': str(w), 'tree': tree} for w, tree in mix]},
        'hazard_witness': {'product_bound': str(risk), 'prepeek_risk': '1'},
        'transfer_distributions': distributions,
        'transfer_witness': {'shared_targets': shared[0], 'independent_targets': independent[0],
            'shared_true': str(shared[1]), 'independent_true': str(independent[1]),
            'shared_all_false': str(shared[2][-1]), 'independent_all_false': str(independent[2][-1])},
        'checks': checks, 'source_sha256': {p: sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT/'output/evaluation_pdi/pdi_04_06.json')
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(verify(), indent=2, sort_keys=True)+'\n', encoding='utf-8')
