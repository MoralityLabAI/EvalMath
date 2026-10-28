"""Conjecture B' (beyond Theorem B): for ANY deterministic selection rule f: Omega^K -> {1..K}
(not necessarily symmetric, not necessarily in the argmax of any score), the law pi of the selected
record from K i.i.d. draws satisfies KL(pi || p0) <= lambda_K = ln K - (K-1)/K.

Exhaustive over rules (KL is convex in pi and pi is linear in a randomised rule, so deterministic
rules suffice), with p0 optimised by coordinate ascent from random restarts.

Run:  python reviews/checks/check_selection_any_rule.py
"""
from __future__ import annotations

import itertools
import math
import random


def lam(K):
    return math.log(K) - (K - 1) / K


def kl(pi, p):
    return sum(x * math.log(x / y) for x, y in zip(pi, p) if x > 0)


def kept_law(rule, p, K, tuples):
    N = len(p)
    pi = [0.0] * N
    for idx, tup in enumerate(tuples):
        w = 1.0
        for t in tup:
            w *= p[t]
        pi[tup[rule[idx]]] += w
    return pi


def optimise(rule, N, K, tuples, rng, restarts):
    best = -1.0
    bestp = None
    for _ in range(restarts):
        p = [rng.random() for _ in range(N)]
        s = sum(p)
        p = [x / s for x in p]
        val = kl(kept_law(rule, p, K, tuples), p)
        step = 0.25
        while step > 1e-6:
            improved = False
            for i in range(N):
                for j in range(N):
                    if i == j:
                        continue
                    q = p[:]
                    d = min(step, q[j])
                    q[i] += d
                    q[j] -= d
                    v = kl(kept_law(rule, q, K, tuples), q)
                    if v > val + 1e-15:
                        p, val, improved = q, v, True
            if not improved:
                step /= 2
        if val > best:
            best, bestp = val, p
    return best, bestp


def main():
    rng = random.Random(11)
    for N, K, restarts in [(2, 2, 4), (3, 2, 4), (2, 3, 4), (2, 4, 3), (3, 3, 2)]:
        tuples = list(itertools.product(range(N), repeat=K))
        nrules = K ** len(tuples)
        if nrules > 60000:
            # sample rules
            rules = (tuple(rng.randrange(K) for _ in tuples) for _ in range(20000))
            label = "20000 sampled rules of %d" % nrules
        else:
            rules = itertools.product(range(K), repeat=len(tuples))
            label = "all %d rules" % nrules
        worst = (-1.0, None, None)
        for rule in rules:
            val, p = optimise(rule, N, K, tuples, rng, restarts)
            if val > worst[0]:
                worst = (val, p, rule)
        print(f"N={N}, K={K}: {label}; max KL = {worst[0]:.6f} vs lambda_K = {lam(K):.6f}"
              f"  [{'OK' if worst[0] <= lam(K) + 1e-9 else 'FAIL'}]")
        print("   at p0 =", [round(x, 4) for x in worst[1]], " rule =", worst[2])


if __name__ == "__main__":
    main()


# ---------------------------------------------------------------------------------------------
# Theorem B' (this review): for ANY selection rule and any convex f with f(1)=0,
#   D_f(pi || p0) <= \int_0^1 f(K u^{K-1}) du,
# because pi(A) <= 1-(1-p0(A))^K for every A, so dpi/dp0 is majorised by K(1-u)^{K-1} and
# Hardy-Littlewood-Polya applies.  Numerical check with f = (x-1)^2 (chi-square):
#   bound = K^2/(2K-1) - 1 = (K-1)^2/(2K-1).
def chi2(pi, p):
    return sum((x - y) ** 2 / y for x, y in zip(pi, p) if y > 0)


def chi2_check():
    rng = random.Random(5)
    for N, K in [(3, 2), (2, 3)]:
        tuples = list(itertools.product(range(N), repeat=K))
        bound = (K - 1) ** 2 / (2 * K - 1)
        worst = -1.0
        for rule in itertools.product(range(K), repeat=len(tuples)):
            for _ in range(3):
                p = [rng.random() for _ in range(N)]
                s = sum(p)
                p = [x / s for x in p]
                val = chi2(kept_law(rule, p, K, tuples), p)
                step = 0.25
                while step > 1e-6:
                    improved = False
                    for i in range(N):
                        for j in range(N):
                            if i == j:
                                continue
                            q = p[:]
                            d = min(step, q[j])
                            q[i] += d
                            q[j] -= d
                            v = chi2(kept_law(rule, q, K, tuples), q)
                            if v > val + 1e-15:
                                p, val, improved = q, v, True
                    if not improved:
                        step /= 2
                worst = max(worst, val)
        print(f"chi^2, N={N}, K={K}: max over all rules {worst:.6f} vs bound (K-1)^2/(2K-1) = {bound:.6f}"
              f"  [{'OK' if worst <= bound + 1e-9 else 'FAIL'}]")


if __name__ == "__main__":
    chi2_check()
