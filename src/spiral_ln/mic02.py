"""Public-development, finite certificate scheduling controls for MIC-02."""
from fractions import Fraction as F
from itertools import product
from random import Random
import hashlib
import json
from pathlib import Path

N = 5
FAMILIES = ('recurrence', 'amortized', 'counting', 'derandomization')
ROOTS = 32


def ceildiv(a, b):
    return -(-a // b)


def root(family, seed):
    r = Random(seed + 10000 * FAMILIES.index(family))
    if family == 'recurrence':
        m = []
        for i in range(N):
            rem = 8
            row = [0] * N
            for j in range(i + 1, N):
                row[j] = r.randint(0, rem)
                rem -= row[j]
            m.append(tuple(row))
        b = tuple(r.randint(1, 9) for _ in range(N))
        return tuple(m), b
    if family == 'amortized':
        edges = [(i, (i + 1) % (N + 1), r.randint(1, 9)) for i in range(N + 1)]
        edges += [(u, v, r.randint(1, 9)) for u, v in (r.sample(range(N + 1), 2) for _ in range(8))]
        return tuple(edges)
    if family == 'counting':
        a = [[r.randint(0, 2) for _ in range(N)] for _ in range(N)]
        for j in range(N):
            a[j][j] = max(1, a[j][j])
        return tuple(map(tuple, a)), tuple(r.randint(1, 9) for _ in range(N))
    if family == 'derandomization':
        return tuple(tuple((i, r.randrange(2)) for i in r.sample(range(N), 3)) for _ in range(10))
    raise ValueError(family)


def start(f, d):
    if f == 'recurrence':
        m, b = d
        k = max(ceildiv(10 * b[i], 10 - sum(m[i])) for i in range(N))
        return (k,) * N
    return {'amortized': (0,) * N, 'counting': (4,) * N,
            'derandomization': (-1,) * N}[f]


def score(f, d, p):
    """Integer-scaled certified objective; invalid proposals raise."""
    if len(p) != N or any(type(x) is not int for x in p):
        raise ValueError('bad state')
    if f == 'recurrence':
        m, b = d
        if any(p[i] < 0 or 10 * p[i] < 10 * b[i] + sum(m[i][j] * p[j] for j in range(N)) for i in range(N)):
            raise ValueError('infeasible recurrence')
        return sum(p)
    if f == 'amortized':
        if any(x not in (-2, 0, 2) for x in p):
            raise ValueError('outside potential grid')
        phi = (0,) + p
        return max(0, *(c + phi[v] - phi[u] for u, v, c in d))
    if f == 'counting':
        a, b = d
        if any(not 0 <= x <= 4 for x in p) or any(sum(a[i][j] * p[i] for i in range(N)) < 4 for j in range(N)):
            raise ValueError('infeasible covering certificate')
        return sum(x * c for x, c in zip(p, b))
    if f == 'derandomization':
        if any(x not in (-1, 0, 1) for x in p):
            raise ValueError('invalid assignment')
        return sum(0 if any(p[i] == b for i, b in cl) else 32 >> sum(p[i] == -1 for i, _ in cl) for cl in d)
    raise ValueError(f)


def update(f, d, p, i):
    if f == 'recurrence':
        m, b = d
        q = list(p)
        q[i] = b[i] + ceildiv(sum(m[i][j] * p[j] for j in range(N)), 10)
        return tuple(q)
    if f == 'counting':
        a, _ = d
        q = list(p)
        q[i] = max([0] + [ceildiv(4 - sum(a[k][j] * p[k] for k in range(N) if k != i), a[i][j]) for j in range(N) if a[i][j]])
        return tuple(q)
    choices = (-2, 0, 2) if f == 'amortized' else (0, 1)
    candidates = [p[:i] + (v,) + p[i+1:] for v in choices]
    if f == 'amortized':
        candidates = [p] + candidates
    return min(candidates, key=lambda q: score(f, d, q))


def walk(f, d, order):
    if sorted(order) != list(range(N)):
        raise ValueError('order must contain each coordinate once')
    p = start(f, d)
    for i in order:
        q = update(f, d, p, i)
        if score(f, d, q) > score(f, d, p):
            raise AssertionError('certificate got worse')
        p = q
    if f == 'derandomization' and -1 in p:
        raise AssertionError('incomplete assignment')
    return p


def oracle(f, d):
    if f == 'recurrence':
        return score(f, d, walk(f, d, list(reversed(range(N)))))
    values = {'amortized': (-2, 0, 2), 'counting': range(5), 'derandomization': (0, 1)}[f]
    best = score(f, d, start(f, d))
    for p in product(values, repeat=N):
        try:
            best = min(best, score(f, d, p))
        except ValueError:
            pass
    return best


def replay(f, seed):
    d = root(f, seed)
    p = start(f, d)
    initial = score(f, d, p)
    # All arms are charged the same initial candidate scan and N updates.
    initial_gain = [initial - score(f, d, update(f, d, p, i)) for i in range(N)]
    ordered = sorted(range(N), key=lambda i: (-initial_gain[i], i))
    rng = Random(98765 + seed + 10000 * FAMILIES.index(f))
    orders = [ordered, ordered[::-1]]
    for _ in range(3):
        perm = list(range(N))
        rng.shuffle(perm)
        orders.append(perm)
    scores = [score(f, d, walk(f, d, seq)) for seq in orders]
    gold = oracle(f, d)
    if any(not gold <= s <= initial for s in scores):
        raise AssertionError('oracle or baseline violation')
    scale = max(1, initial)
    return {'seed': seed, 'initial': initial, 'oracle': gold, 'orders': orders,
            'scores': scores, 'paired_effect': str(F(scores[2] - scores[0], scale)),
            'reverse_effect': str(F(scores[1] - scores[0], scale)),
            'sham': str(F(scores[3] - scores[4], scale))}


def run():
    results = {}
    for f in FAMILIES:
        rows = [replay(f, s) for s in range(ROOTS)]
        effects = [F(r['paired_effect']) for r in rows]
        reverse = [F(r['reverse_effect']) for r in rows]
        shams = [F(r['sham']) for r in rows]
        results[f] = {'rows': rows, 'mean_effect': str(sum(effects)/ROOTS),
                      'mean_reverse_effect': str(sum(reverse)/ROOTS),
                      'wins_ties_losses': [sum(x > 0 for x in effects), sum(x == 0 for x in effects), sum(x < 0 for x in effects)],
                      'max_abs_sham': str(max(map(abs, shams))),
                      'mean_sham': str(sum(shams)/ROOTS),
                      'ordered_oracle_hits': sum(r['scores'][0] == r['oracle'] for r in rows),
                      'shuffled_oracle_hits': sum(r['scores'][2] == r['oracle'] for r in rows)}
    preflight = {'schema_version': 1, 'experiment_id': 'MIC-02-public-proxy',
                 'independent_unit': 'structural task family (independence unverified)',
                 'alpha': '1/20', 'scientific_min_effect': '1/20', 'target_effect': '1/10',
                 'measurement_resolution': '0', 'sham_quantile': '19/20', 'sham_confidence': '19/20',
                 'planned_comparisons': 1, 'confirm_units_planned': 128,
                 'pilot_from_development_only': True, 'heldout_sealed': False, 'units_independent': False,
                 'pilot': [{'unit_id': f, 'paired_effect': results[f]['mean_effect'],
                            'sham_effects': [results[f]['max_abs_sham']]} for f in FAMILIES]}
    return {'schema': 'MIC-02/public-finite-proxy/v1', 'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'roots_per_family': ROOTS, 'results': results, 'preflight_input': preflight,
            'evidence': 'public finite diagnostic only; no model runs, no sealed roots'}


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True, indent=2))
