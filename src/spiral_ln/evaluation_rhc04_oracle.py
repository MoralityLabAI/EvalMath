"""RHC-04: exact-rational solver for the finite minimax detection problem.

    D*(alpha) = max_{f in [0,1]^n, P.f <= alpha}  min_j  Q_j.f

Everything is Fraction arithmetic (no floats). The solver is a sparse exact simplex with
Bland's rule; optimal duals are read from the final tableau and re-checked independently by
`check_certificate`, which never calls the solver.
"""

from __future__ import annotations

from fractions import Fraction as F
from typing import Sequence

ZERO, ONE = F(0), F(1)


def _dot(a: Sequence[F], b: Sequence[F]) -> F:
    return sum((x * y for x, y in zip(a, b)), ZERO)


def _validate(p, qs, alpha):
    p = tuple(F(x) for x in p)
    qs = tuple(tuple(F(x) for x in q) for q in qs)
    alpha = F(alpha)
    if not p or not qs or any(len(q) != len(p) for q in qs):
        raise ValueError("need a nonempty safe law and >= 1 attack law of matching length")
    for law in (p, *qs):
        if min(law) < 0 or sum(law) != 1:
            raise ValueError("laws must be nonnegative and sum to one")
    if not 0 <= alpha <= 1:
        raise ValueError("alpha outside [0,1]")
    return p, qs, alpha


def _simplex(p, qs, alpha):
    """max d s.t. P.f<=alpha, f_o<=1, d-Q_j.f<=0, all >= 0. Columns: f_0..f_{n-1}, d, slacks."""
    n, J = len(p), len(qs)
    m, nv = 1 + n + J, n + 1
    rows: list[dict[int, F]] = []
    rhs: list[F] = []
    rows.append({o: p[o] for o in range(n) if p[o]})
    rhs.append(alpha)
    for o in range(n):
        rows.append({o: ONE})
        rhs.append(ONE)
    for q in qs:
        r = {o: -q[o] for o in range(n) if q[o]}
        r[n] = ONE
        rows.append(r)
        rhs.append(ZERO)
    for i in range(m):
        rows[i][nv + i] = ONE
    basis = [nv + i for i in range(m)]
    z: dict[int, F] = {n: F(-1)}
    z_rhs, pivots, stall = ZERO, 0, 0
    while True:
        neg = [(c, v) for c, v in z.items() if v < 0]
        if not neg:
            break
        # Dantzig pricing (fast), switching to Bland's rule after a run of degenerate pivots
        # so that cycling is impossible; the leaving row always breaks ties by lowest index.
        enter = min(c for c, _ in neg) if stall >= 20 else min(neg, key=lambda cv: (cv[1], cv[0]))[0]
        best = None
        for i, r in enumerate(rows):
            a = r.get(enter)
            if a and a > 0:
                key = (rhs[i] / a, basis[i])
                if best is None or key < best[0]:
                    best = (key, i)
        assert best is not None, "LP is bounded (d <= 1)"
        r_idx = best[1]
        stall = stall + 1 if best[0][0] == 0 else 0
        piv = rows[r_idx][enter]
        prow = {c: v / piv for c, v in rows[r_idx].items()}
        rows[r_idx], rhs[r_idx] = prow, rhs[r_idx] / piv
        for i, r in enumerate(rows):
            coef = r.get(enter) if i != r_idx else None
            if coef:
                for c, v in prow.items():
                    nvl = r.get(c, ZERO) - coef * v
                    if nvl:
                        r[c] = nvl
                    else:
                        r.pop(c, None)
                rhs[i] -= coef * rhs[r_idx]
        coef = z.get(enter)
        if coef:
            for c, v in prow.items():
                nvl = z.get(c, ZERO) - coef * v
                if nvl:
                    z[c] = nvl
                else:
                    z.pop(c, None)
            z_rhs -= coef * rhs[r_idx]
        basis[r_idx] = enter
        pivots += 1
    x = [ZERO] * (nv + m)
    for i, b in enumerate(basis):
        x[b] = rhs[i]
    duals = [z.get(nv + i, ZERO) for i in range(m)]
    return tuple(x[:n]), x[n], duals, z_rhs, pivots


def check_certificate(p, qs, alpha, detector, lam, t) -> dict:
    """Independent primal/dual verification; does not call the solver."""
    p, qs, alpha = _validate(p, qs, alpha)
    f = tuple(F(x) for x in detector)
    lam = tuple(F(x) for x in lam)
    t = F(t)
    if len(f) != len(p) or any(x < 0 or x > 1 for x in f):
        raise ValueError("detector outside [0,1]^n")
    if _dot(p, f) > alpha:
        raise ValueError("detector false-positive rate exceeds alpha")
    if len(lam) != len(qs) or min(lam) < 0 or sum(lam) != 1:
        raise ValueError("lam is not in the simplex")
    if t < 0:
        raise ValueError("t must be nonnegative")
    lower = min(_dot(q, f) for q in qs)
    upper = alpha * t + sum(
        (max(ZERO, sum((l * q[o] for l, q in zip(lam, qs)), ZERO) - t * p[o])
         for o in range(len(p))), ZERO)
    return {"lower": lower, "upper": upper, "gap": upper - lower, "ok": lower == upper}


def solve_minimax(p, qs, alpha) -> dict:
    p, qs, alpha = _validate(p, qs, alpha)
    n, J = len(p), len(qs)
    f, d, duals, obj, pivots = _simplex(p, qs, alpha)
    per_attack = tuple(_dot(q, f) for q in qs)
    value = min(per_attack)
    assert d == value == obj, "tableau objective disagrees with the extracted detector"
    t, lam = duals[0], tuple(duals[1 + n + j] for j in range(J))
    assert t >= 0 and min(lam) >= 0, "dual multipliers must be nonnegative"
    total = sum(lam, ZERO)
    if total != 1:
        # sum(lam) >= 1 always; > 1 is possible only when the optimum is 0, where the dual
        # objective is 0 and dividing (lam, t) by the sum leaves it 0.
        assert total > 1 and value == 0, f"dual multipliers sum to {total}, expected 1"
        lam, t = tuple(l / total for l in lam), t / total
    excess = tuple(max(ZERO, sum((l * q[o] for l, q in zip(lam, qs)), ZERO) - t * p[o])
                   for o in range(n))
    upper = alpha * t + sum(excess, ZERO)
    cert = check_certificate(p, qs, alpha, f, lam, t)
    assert cert["upper"] == upper and cert["lower"] == value
    return {"value": value, "detector": f, "fpr": _dot(p, f), "per_attack": per_attack,
            "dual": {"lam": lam, "t": t, "excess": excess, "upper_bound": upper},
            "certified": cert["ok"] and upper == value, "pivots": pivots}


def neyman_pearson(p, q, alpha) -> dict:
    """Exact greedy likelihood-ratio detector for a single attack law."""
    p, (q,), alpha = _validate(p, (q,), alpha)
    n = len(p)
    free = [o for o in range(n) if p[o] == 0 and q[o] > 0]
    ranked = sorted((o for o in range(n) if p[o] > 0 and q[o] > 0),
                    key=lambda o: q[o] / p[o], reverse=True)
    f = [ZERO] * n
    for o in free:
        f[o] = ONE
    budget = alpha
    for o in ranked:
        take = min(ONE, budget / p[o])
        f[o] = take
        budget -= take * p[o]
        if budget <= 0:
            break
    return {"value": _dot(q, f), "detector": tuple(f)}
