"""Independent policy/authorization enumeration for PDI-03."""
import argparse
from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import random
from spiral_ln.evaluation_pdi import product_prior
from spiral_ln.evaluation_pdi_frontier import accepted_versions, at_risk, frontier, selection_revocation_witness
from spiral_ln.evaluation_pdi_noisy import optimal_audit

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ('src/spiral_ln/evaluation_pdi.py', 'src/spiral_ln/evaluation_pdi_noisy.py',
           'src/spiral_ln/evaluation_pdi_frontier.py', 'tests/test_evaluation_pdi_frontier.py',
           'scripts/verify_evaluation_pdi_frontier.py', 'paper/proof_dependency_frontier.md')


def trees(indices, a, b):
    yield None
    for j in indices:
        if a[j][3] <= b:
            children = tuple(trees(tuple(i for i in indices if i != j), a, b-a[j][3]))
            for no, yes in product(children, repeat=2):
                yield j, no, yes


def run_tree(tree, ys):
    path = ()
    while tree is not None:
        j, no, yes = tree
        path += ((j, ys[j]),)
        tree = yes if ys[j] else no
    return path


def brute(p, c, a, b, adaptive):
    n = len(p).bit_length()-1
    def valid(w, masks):
        return any(all((w >> i) & 1 for i in range(n) if (mask >> i) & 1) for mask in masks)
    cells = []
    for w, prior in enumerate(p):
        for ys in product((0, 1), repeat=len(a)):
            mass = prior
            for (i, t, f, _), y in zip(a, ys):
                r = t if (w >> i) & 1 else f
                mass *= r if y else 1-r
            if mass:
                cells.append((w, ys, mass))
    if adaptive:
        routes = [lambda ys, tree=tree: run_tree(tree, ys) for tree in trees(tuple(range(len(a))), a, b)]
    else:
        routes = [lambda ys, subset=subset: tuple((j, ys[j]) for j in subset)
                  for k in range(len(a)+1) for subset in combinations(range(len(a)), k)
                  if sum(a[j][3] for j in subset) <= b]
    points = set()
    for route in routes:
        groups = {}
        for w, ys, mass in cells:
            groups.setdefault(route(ys), []).append((w, mass))
        leaf_options = []
        for path, group in groups.items():
            accepted = 0
            for i in range(n):
                results = [y for j, y in path if a[j][0] == i]
                if results and all(results):
                    accepted |= 1 << i
            eligible = [(weight, masks) for weight, masks in c if valid(accepted, masks)]
            options = []
            for k in range(len(eligible)+1):
                for subset in combinations(eligible, k):
                    f = sum(weight*mass for weight, masks in subset for w, mass in group if not valid(w, masks))
                    t = sum(weight*mass for weight, masks in subset for w, mass in group if valid(w, masks))
                    options.append((f, t))
            leaf_options.append(options)
        for choice in product(*leaf_options):
            points.add((sum(f for f, t in choice), sum(t for f, t in choice)))
    return tuple(sorted(x for x in points if not any(y != x and y[0] <= x[0] and y[1] >= x[1] for y in points)))


def verify():
    rng = random.Random(26112503)
    comparisons = support_checks = 0
    for _ in range(32):
        masses = [rng.randrange(4) for _ in range(4)]
        if not sum(masses):
            masses[0] = 1
        p = tuple(F(m, sum(masses)) for m in masses)
        c = [(rng.randint(1, 3), tuple(rng.randrange(4) for _ in range(2))) for _ in range(2)]
        a = tuple((rng.randrange(2), rng.choice((F(1, 2), F(3, 4), F(1))),
                   rng.choice((F(0), F(1, 4), F(1, 2))), rng.randint(1, 2)) for _ in range(2))
        b = rng.randrange(4)
        for adaptive in (False, True):
            pts = frontier(p, c, a, b, adaptive=adaptive)
            assert pts == brute(p, c, a, b, adaptive)
            comparisons += 1
            for lam in (0, 1, 2, 4):
                assert max(t-lam*f for f, t in pts) == optimal_audit(p, c, a, b, lam, adaptive=adaptive)[0]
                support_checks += 1
    args = (product_prior([F(1, 2)]*3), [(2, (3,)), (1, (4,))],
            [(i, F(9, 10), F(1, 10), 1) for i in range(3)], 2)
    fixed = frontier(*args, adaptive=False)
    adapt = frontier(*args)
    det, _ = at_risk(adapt, F(3, 40), randomized=False)
    opt, mix = at_risk(adapt, F(3, 40))
    assert sum(w for w, p in mix) == 1
    assert opt == tuple(sum(w*p[i] for w, p in mix) for i in range(2))
    retained, hidden = selection_revocation_witness()
    checks = {'independent_frontiers': comparisons == 64, 'scalar_support': support_checks == 256,
              'risk_mixture': det == (F(1, 20), F(9, 20)) and opt == (F(3, 40), F(18, 35)),
              'version_eligibility': accepted_versions([(0, 'old', 1), (0, 'new', 0)], {0: 'new'}) == 0,
              'selection_leak': retained == {('left', 1): 0, ('right', 1): 1} and hidden == {1: F(1, 2)}}
    assert all(checks.values())
    as_pair = lambda p: list(map(str, p))
    return {'schema': 'PDI-03-v1', 'evidence': 'exact synthetic finite frontiers, no empirical safety estimate',
            'point_order': ['false_weight', 'true_weight'], 'frontier_comparisons': comparisons,
            'scalar_support_checks': support_checks, 'fixed': list(map(as_pair, fixed)),
            'adaptive': list(map(as_pair, adapt)), 'risk_budget': '3/40', 'deterministic': as_pair(det),
            'randomized': as_pair(opt), 'mixture': [[str(w), as_pair(p)] for w, p in mix],
            'revocation': {'left': str(retained['left', 1]), 'right': str(retained['right', 1]),
                           'hidden_action': str(hidden[1])}, 'checks': checks,
            'source_sha256': {p: sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT/'output/evaluation_pdi/pdi_03.json')
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(verify(), indent=2, sort_keys=True)+'\n', encoding='utf-8')
