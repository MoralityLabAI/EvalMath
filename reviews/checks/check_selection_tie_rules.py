"""Scope of Theorems A/B (selection KL): record-dependent tie rules.

Theorem A/B assume the kept index is a function of the SCORE VECTOR and independent randomness.
A tie rule that looks at the records themselves (e.g. "among tied candidates keep the shortest
response", or any non-transitive tournament) is outside that hypothesis. This script asks whether
KL(pi_K || p0) <= lambda_K = ln K - (K-1)/K can fail for such rules.

Every deterministic record-dependent rule for K draws is a choice function on size-K multisets of
records, and pi_K is linear in the rule, so KL (convex in pi) is maximised at a deterministic rule.
We enumerate: K=2 on 3 and 4 records (all tournaments, i.e. all choice functions on pairs) and K=3
on 3 records (all choice functions on size-3 multisets), with all scores tied (the all-tied case is
the only one where tie rules act), and optimise p0 by random restarts + coordinate ascent.

Run:  python reviews/checks/check_selection_tie_rules.py
"""
from __future__ import annotations

import itertools
import math
import random
from collections import Counter


def lam(K):
    return math.log(K) - (K - 1) / K


def kl(pi, p):
    return sum(x * math.log(x / y) for x, y in zip(pi, p) if x > 0)


def kept_law(choice, p, K):
    """choice: dict multiset(tuple sorted) -> chosen record index."""
    N = len(p)
    pi = [0.0] * N
    for tup in itertools.product(range(N), repeat=K):
        w = 1.0
        for t in tup:
            w *= p[t]
        if w == 0:
            continue
        pi[choice[tuple(sorted(tup))]] += w
    return pi


def is_transitive_choice(choice, N, K):
    """Is the choice function induced by some total preorder (a refined score)?  We test the
    sufficient structure: there is a linear order such that every multiset picks its maximum."""
    for perm in itertools.permutations(range(N)):
        rank = {v: r for r, v in enumerate(perm)}
        if all(choice[ms] == max(ms, key=lambda v: rank[v]) for ms in choice):
            return True
    return False


def optimise(choice, N, K, rng, restarts=30):
    best = (-1.0, None)
    for _ in range(restarts):
        p = [rng.random() for _ in range(N)]
        s = sum(p)
        p = [x / s for x in p]
        val = kl(kept_law(choice, p, K), p)
        step = 0.2
        while step > 1e-7:
            improved = False
            for i in range(N):
                for j in range(N):
                    if i == j:
                        continue
                    q = p[:]
                    d = min(step, q[j])
                    q[i] += d
                    q[j] -= d
                    v = kl(kept_law(choice, q, K), q)
                    if v > val + 1e-15:
                        p, val, improved = q, v, True
            if not improved:
                step /= 2
        if val > best[0]:
            best = (val, p)
    return best


def main():
    rng = random.Random(7)
    print("lambda_2 = %.6f, lambda_3 = %.6f" % (lam(2), lam(3)))
    for N, K in [(3, 2), (4, 2), (3, 3)]:
        multisets = sorted(set(tuple(sorted(t)) for t in itertools.product(range(N), repeat=K)))
        options = [sorted(set(ms)) for ms in multisets]
        worst_nontrans = (-1.0, None, None)
        worst_trans = (-1.0, None, None)
        count = 0
        for combo in itertools.product(*options):
            choice = dict(zip(multisets, combo))
            count += 1
            val, p = optimise(choice, N, K, rng, restarts=8)
            trans = is_transitive_choice(choice, N, K)
            if trans:
                if val > worst_trans[0]:
                    worst_trans = (val, p, choice)
            else:
                if val > worst_nontrans[0]:
                    worst_nontrans = (val, p, choice)
        print(f"\nN={N} records, K={K}: {count} deterministic choice functions")
        print(f"  max KL over refinement (transitive) rules : {worst_trans[0]:.6f}   (lambda_K = {lam(K):.6f})")
        print(f"  max KL over non-transitive rules          : {worst_nontrans[0]:.6f}")
        if worst_nontrans[1] is not None:
            print("    at p0 =", [round(x, 4) for x in worst_nontrans[1]])
        ok = worst_nontrans[0] <= lam(K) + 1e-9 and worst_trans[0] <= lam(K) + 1e-9
        print(f"  [{'OK' if ok else 'FAIL'}] no rule found with KL > lambda_K")


if __name__ == "__main__":
    main()
