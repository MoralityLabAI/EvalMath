"""Exact two-type recursive-work certificate proxy for MIC-01."""
from __future__ import annotations

from fractions import Fraction as F
from random import Random


def root(seed: int):
    rng = Random(seed)
    rows = []
    for _ in range(2):
        a = rng.randrange(0, 8)
        rows.append((F(a, 10), F(rng.randrange(0, 9 - a), 10)))
    return tuple(rows), tuple(F(rng.randrange(1, 11)) for _ in range(2))


def check(m, b, p):
    return len(p) == 2 and all(
        p[i] >= 0 and p[i] >= b[i] + sum(m[i][j] * p[j] for j in range(2))
        for i in range(2)
    )


def baseline(m, b):
    k = max(b[i] / (1 - sum(m[i])) for i in range(2))
    return (k, k)


def optimum(m, b):
    a, d = 1 - m[0][0], 1 - m[1][1]
    det = a * d - m[0][1] * m[1][0]
    return ((d * b[0] + m[0][1] * b[1]) / det,
            (a * b[1] + m[1][0] * b[0]) / det)


def tighten(m, b, p, i):
    out = list(p)
    j = 1 - i
    out[i] = (b[i] + m[i][j] * p[j]) / (1 - m[i][i])
    return tuple(out)


def walk(m, b, order):
    p = baseline(m, b)
    for i in order:
        nxt = tighten(m, b, p, i)
        if not check(m, b, nxt) or any(nxt[j] > p[j] for j in range(2)):
            raise AssertionError('invalid tightening')
        p = nxt
    return p


def task(seed):
    m, b = root(seed)
    return {"id": f"public-dev-{seed}", "matrix": [[str(x) for x in row] for row in m],
            "overhead": [str(x) for x in b], "baseline": [str(x) for x in baseline(m, b)],
            "request": "Return two nonnegative rational strings p with p >= b + M p and smaller sum than baseline."}


def grade(seed, proposal):
    m, b = root(seed)
    initial = baseline(m, b)
    try:
        if not isinstance(proposal, list) or len(proposal) != 2 or not all(isinstance(x, str) for x in proposal):
            raise ValueError("expected two rational strings")
        p = tuple(F(x) for x in proposal)
    except (ValueError, ZeroDivisionError):
        return {"valid": False, "improved": False, "objective_ratio": None}
    valid = check(m, b, p)
    return {"valid": valid, "improved": valid and sum(p) < sum(initial),
            "objective_ratio": str(sum(p) / sum(initial)) if valid else None}


def pilot(n=64):
    rows = []
    for seed in range(n):
        m, b = root(seed)
        initial = baseline(m, b)
        exact = optimum(m, b)
        # Choose the greatest immediate reduction without seeing the oracle.
        first = min(range(2), key=lambda i: (sum(tighten(m, b, initial, i)), i))
        ordered = [first, 1 - first] * 2
        rng = Random(100000 + seed)
        permutations = []
        for _ in range(3):
            seq = [0, 0, 1, 1]
            rng.shuffle(seq)
            permutations.append(seq)
        # Normalize against the starting certificate, including zero-headroom roots.
        values = [sum(walk(m, b, order)) / sum(initial) for order in [ordered, *permutations]]
        assert check(m, b, exact)
        assert all(sum(walk(m, b, order)) >= sum(exact) for order in [ordered, *permutations])
        rows.append({'unit_id': f'public-dev-{seed}', 'paired_effect': str(values[1] - values[0]),
                     'sham_effects': [str(values[2] - values[3])]})
    return {'schema_version': 1, 'experiment_id': 'MIC-01-CPU-proxy',
            'independent_unit': 'synthetic matrix root (public development)',
            'alpha': '1/20', 'scientific_min_effect': '1/20', 'target_effect': '1/10',
            'measurement_resolution': '0', 'sham_quantile': '19/20', 'sham_confidence': '19/20',
            'planned_comparisons': 1, 'confirm_units_planned': 128,
            'pilot_from_development_only': True, 'heldout_sealed': False,
            'units_independent': False, 'pilot': rows}


if __name__ == '__main__':
    import json
    print(json.dumps(pilot(), indent=2, sort_keys=True))
