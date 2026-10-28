"""Independent checks on gold calibration §8 and §10 (four raters).

 1. Symbolic (sympy): on the four-rater Dawid-Skene model the six equalities of §8 hold identically,
    and with G2 copying G1 w.p. rho the residual c12 c34 - c13 c24 equals rho V1 c34 while
    c13 c24 - c14 c23 stays zero.
 2. Exact block law of the sign-test statistic Z (Test B) from the 16^4 quadruples; the resulting
    power at m = 742, 4000, 10000 against the copying grader (rho = 1/4, 1/2, 3/4, 1), to compare with
    the note's table (0.326 at 742/rho=1; 0.212, 0.519, 0.788, 0.930 at 4000; 0.417, 0.869, 0.990, 0.9996 at 10000).
 3. Non-specificity: a population with item-difficulty heterogeneity (raters conditionally independent
    given (Y, D) with D a binary difficulty, NO copying) has a nonzero tetrad; the "copying" test rejects
    with substantial power.  Exact tetrad and power reported.

Run:  python reviews/checks/check_gold_four_rater.py
"""
from __future__ import annotations

import itertools
from fractions import Fraction as Fr
from math import comb

import sympy as sp


# ------------------------------------------------------------------ 1. symbolic identities
def symbolic():
    pi, rho = sp.symbols("pi rho")
    al = sp.symbols("a1:5")
    be = sp.symbols("b1:5")

    def table(copy=False):
        # cells over x in {0,1}^4; P(x) = sum_y P(y) prod_i P(x_i | y) ; with copying, rater 2 = rater 1 w.p. rho
        cells = {}
        for x in itertools.product((0, 1), repeat=4):
            tot = 0
            for y in (0, 1):
                py = pi if y == 1 else 1 - pi

                def pr(i, xi, y=y):
                    if y == 1:
                        return 1 - al[i] if xi == 1 else al[i]
                    return be[i] if xi == 1 else 1 - be[i]

                if copy:
                    indep = pr(0, x[0]) * pr(1, x[1]) * pr(2, x[2]) * pr(3, x[3])
                    copied = pr(0, x[0]) * (1 if x[1] == x[0] else 0) * pr(2, x[2]) * pr(3, x[3])
                    tot += py * ((1 - rho) * indep + rho * copied)
                else:
                    tot += py * pr(0, x[0]) * pr(1, x[1]) * pr(2, x[2]) * pr(3, x[3])
            cells[x] = tot
        return cells

    def moments(cells):
        p = [sum(v for x, v in cells.items() if x[i] == 1) for i in range(4)]
        k = {}
        for S in [s for r in (2, 3, 4) for s in itertools.combinations(range(4), r)]:
            k[S] = sp.expand(sum(v * sp.prod([x[i] - p[i] for i in S]) for x, v in cells.items()))
        return p, k

    _, k = moments(table())
    c = lambda i, j: k[(i, j)]
    eqs = [
        c(0, 1) * c(2, 3) - c(0, 2) * c(1, 3),
        c(0, 2) * c(1, 3) - c(0, 3) * c(1, 2),
        k[(0, 1, 2)] * c(0, 3) - k[(0, 1, 3)] * c(0, 2),
        k[(0, 1, 2)] * c(0, 3) - k[(0, 2, 3)] * c(0, 1),
        k[(0, 1, 2)] * c(1, 3) - k[(1, 2, 3)] * c(0, 1),
        (k[(0, 1, 2, 3)] - c(0, 1) * c(2, 3)) * c(0, 1) - k[(0, 1, 2)] * k[(0, 1, 3)],
    ]
    ok = [sp.simplify(e) == 0 for e in eqs]
    print("six four-rater equalities hold identically:", ok, " [%s]" % ("OK" if all(ok) else "FAIL"))
    _, kc = moments(table(copy=True))
    cc = lambda i, j: kc[(i, j)]
    V1 = pi * al[0] * (1 - al[0]) + (1 - pi) * be[0] * (1 - be[0])
    res1 = sp.simplify(cc(0, 1) * cc(2, 3) - cc(0, 2) * cc(1, 3) - rho * V1 * cc(2, 3))
    res2 = sp.simplify(cc(0, 2) * cc(1, 3) - cc(0, 3) * cc(1, 2))
    print("copy grader: c12c34 - c13c24 = rho V1 c34 :", res1 == 0, "; c13c24 = c14c23 :", res2 == 0,
          " [%s]" % ("OK" if res1 == 0 and res2 == 0 else "FAIL"))
    return table, moments


# ------------------------------------------------------------------ 2. exact block law and power
def numeric_table(pi, al, be, rho=0.0, het=None):
    """16-cell table as Fractions.  het: (q_hard, factor_easy, factor_hard) multiplies all error rates
    by a difficulty factor; raters conditionally independent given (Y, D)."""
    cells = {}
    strata = [(Fr(1), Fr(1))] if het is None else [(1 - het[0], het[1]), (het[0], het[2])]
    for x in itertools.product((0, 1), repeat=4):
        tot = Fr(0)
        for qd, fac in strata:
            for y in (0, 1):
                py = pi if y == 1 else 1 - pi

                def pr(i, xi):
                    if y == 1:
                        a = al[i] * fac
                        return 1 - a if xi == 1 else a
                    b = be[i] * fac
                    return b if xi == 1 else 1 - b

                indep = pr(0, x[0]) * pr(1, x[1]) * pr(2, x[2]) * pr(3, x[3])
                copied = pr(0, x[0]) * (1 if x[1] == x[0] else 0) * pr(2, x[2]) * pr(3, x[3])
                tot += qd * py * ((1 - rho) * indep + rho * copied)
        cells[x] = tot
    return cells


def tetrad(cells):
    p = [sum(v for x, v in cells.items() if x[i] == 1) for i in range(4)]
    c = {}
    for i, j in itertools.combinations(range(4), 2):
        c[(i, j)] = sum(v * (x[i] - p[i]) * (x[j] - p[j]) for x, v in cells.items())
    return c[(0, 1)] * c[(2, 3)] - c[(0, 2)] * c[(1, 3)]


def block_law(cells):
    """P(Z=+1), P(Z=-1) for Z = sign(K) 1{U < |K|}, U uniform on {0,1,2,3}, from all 16^4 quadruples."""
    xs = list(cells)
    pz = {1: Fr(0), -1: Fr(0)}
    for quad in itertools.product(xs, repeat=4):
        w = cells[quad[0]] * cells[quad[1]] * cells[quad[2]] * cells[quad[3]]
        if w == 0:
            continue
        i, j, k, l = quad
        D = lambda a, u, v: u[a] - v[a]
        K = 0
        for (A, B), (C, E) in [((i, j), (k, l)), ((i, k), (j, l)), ((i, l), (j, k))]:
            d14 = D(0, A, B) * D(3, C, E) - D(0, C, E) * D(3, A, B)
            d23 = D(1, A, B) * D(2, C, E) - D(1, C, E) * D(2, A, B)
            K += d14 * d23
        if K > 0:
            pz[1] += w * Fr(K, 4)
        elif K < 0:
            pz[-1] += w * Fr(-K, 4)
    return pz


def sign_test_power(pz, m, alpha=0.05):
    B = m // 4
    pnz = float(pz[1] + pz[-1])
    q = float(pz[1]) / pnz
    # critical value per N: smallest c with P(Bin(N,1/2) >= c) <= alpha
    from math import log, exp, lgamma

    def logbin(n, k, p):
        return lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1) + k * log(p) + (n - k) * log(1 - p)

    power = 0.0
    for N in range(0, B + 1):
        pN = exp(logbin(B, N, pnz)) if 0 < pnz < 1 else (1.0 if N == B else 0.0)
        if pN < 1e-14:
            continue
        # tail of Bin(N,1/2)
        tail = 0.0
        c = N + 1
        for k in range(N, -1, -1):
            tail += exp(logbin(N, k, 0.5)) if N > 0 else (1.0 if k == 0 else 0.0)
            if tail > alpha:
                c = k + 1
                break
        else:
            c = 0
        if c > N:
            continue
        rej = sum(exp(logbin(N, k, q)) for k in range(c, N + 1)) if 0 < q < 1 else (1.0 if q == 1 else 0.0)
        power += pN * rej
    return power


def main():
    symbolic()
    pi = Fr(1, 4)
    al = [Fr(1, 10), Fr(1, 5), Fr(1, 5), Fr(1, 10)]
    be = [Fr(1, 5), Fr(1, 10), Fr(2, 5), Fr(3, 10)]
    print("\nSign test (Test B), copying grader at the §8 fixture, one-sided alpha=1/20:")
    note = {742: [None, None, None, 0.326], 4000: [0.212, 0.519, 0.788, 0.930], 10000: [0.417, 0.869, 0.990, 0.9996]}
    for rho in [Fr(1, 4), Fr(1, 2), Fr(3, 4), Fr(1)]:
        cells = numeric_table(pi, al, be, rho=rho)
        tau = tetrad(cells)
        pz = block_law(cells)
        pows = {m: sign_test_power(pz, m) for m in (742, 4000, 10000)}
        exp_tau = Fr(513, 80000) * rho
        print(f"  rho={rho}: tau={tau} (= 513/80000 rho: {tau == exp_tau}); P(Z=+1)={float(pz[1]):.6f} P(Z=-1)={float(pz[-1]):.6f}; "
              f"power m=742 {pows[742]:.3f}, 4000 {pows[4000]:.3f}, 10000 {pows[10000]:.4f}")
    cells0 = numeric_table(pi, al, be, rho=Fr(0))
    pz0 = block_law(cells0)
    print(f"  null (rho=0): P(Z=+1)={pz0[1]} P(Z=-1)={pz0[-1]} equal: {pz0[1] == pz0[-1]}  [{'OK' if pz0[1] == pz0[-1] else 'FAIL'}] size control")
    print(f"  zeta_1-type ratio check: P0(Z!=0) = {float(pz0[1] + pz0[-1]):.6f}")

    print("\nNon-specificity: difficulty heterogeneity WITHOUT copying (raters cond. independent given (Y,D)):")
    for q_hard, f_easy, f_hard in [(Fr(1, 2), Fr(1, 2), Fr(3, 2)), (Fr(1, 3), Fr(1, 4), Fr(5, 2)), (Fr(1, 2), Fr(0), Fr(2))]:
        cells = numeric_table(pi, al, be, rho=Fr(0), het=(q_hard, f_easy, f_hard))
        tau = tetrad(cells)
        pz = block_law(cells)
        pows = {m: sign_test_power(pz, m) for m in (742, 4000, 10000)}
        marg_err = [float(sum(v for x, v in cells.items() if x[i] != y_)) for i, y_ in []]
        print(f"  P(hard)={q_hard}, error-rate factors easy {f_easy} / hard {f_hard}: tau={float(tau):+.6f} "
              f"(copy rho=1 gives +0.006413); one-sided sign-test power m=742 {pows[742]:.3f}, 4000 {pows[4000]:.3f}, 10000 {pows[10000]:.3f}")
    print("  => the tetrad test rejects conditional independence given a BINARY latent; it does not identify copying.")


if __name__ == "__main__":
    main()
