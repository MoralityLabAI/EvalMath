"""Independent dynamic programme for the adaptive patching problem (lattice note §3): expected number
of patches to H hits, categories (n_c, F_c), a patch in c hits w.p. F_c/n_c.  Checks Theorem 10,
Theorem 11's closed form on random states, Corollary 14's witness, and the one-part-in-739 witness.
Nothing imported from spiral_ln.

Run:  python reviews/checks/check_lattice_patching.py
"""
from __future__ import annotations

import random
from fractions import Fraction as Fr
from functools import lru_cache
from math import comb


@lru_cache(maxsize=None)
def V(h, state):
    """Optimal expected patches to h hits from state (sorted tuple of (n, F))."""
    if h == 0:
        return Fr(0)
    if sum(F for _, F in state) < h:
        raise ValueError("infeasible")
    best = None
    for i, (n, F) in enumerate(state):
        if F == 0:
            continue
        rest = state[:i] + state[i + 1:]
        hit = tuple(sorted(rest + (((n - 1, F - 1),) if n - 1 > 0 else ())))
        miss = tuple(sorted(rest + (((n - 1, F),) if n - 1 > 0 else ())))
        p = Fr(F, n)
        val = 1 + p * V(h - 1, hit) + ((1 - p) * V(h, miss) if p < 1 else 0)
        if best is None or val < best:
            best = val
    return best


@lru_cache(maxsize=None)
def Kcommit(h, state):
    """Best committing value: pick a category, patch it until it hits, then recurse (best committing)."""
    if h == 0:
        return Fr(0)
    best = None
    for i, (n, F) in enumerate(state):
        if F == 0:
            continue
        rest = state[:i] + state[i + 1:]
        # first hit at position t = 1..n-F+1 w.p. C(n-t, F-1)/C(n, F); after it the category is (n-t, F-1)
        val = Fr(0)
        for t in range(1, n - F + 2):
            pr = Fr(comb(n - t, F - 1), comb(n, F))
            nxt = tuple(sorted(rest + (((n - t, F - 1),) if n - t > 0 else ())))
            val += pr * (t + Kcommit(h - 1, nxt))
        if best is None or val < best:
            best = val
    return best


def theorem10(state):
    return min(Fr(n + 1, F + 1) for n, F in state if F >= 1)


def theorem11(state):
    """V*_2 = min_c kappa(n_c, F_c, M_{-c}), kappa = (n+1)/(F+1) + E[min(phi(T), M)], phi(T) = (n-T+1)/F."""
    best = None
    for i, (n, F) in enumerate(state):
        if F == 0:
            continue
        others = [Fr(m + 1, G + 1) for j, (m, G) in enumerate(state) if j != i and G >= 1]
        M = min(others) if others else None
        e = Fr(0)
        for t in range(1, n - F + 2):
            pr = Fr(comb(n - t, F - 1), comb(n, F))
            phi = Fr(n - t + 1, F) if F >= 2 else None
            if phi is None:
                term = M
            elif M is None:
                term = phi
            else:
                term = min(phi, M)
            e += pr * term
        val = Fr(n + 1, F + 1) + e
        if best is None or val < best:
            best = val
    return best


def main():
    rng = random.Random(1)
    bad10 = bad11 = 0
    for _ in range(300):
        C = rng.randint(1, 3)
        state = tuple(sorted((lambda n: (n, rng.randint(1, n)))(rng.randint(1, 7)) for _ in range(C)))
        if V(1, state) != theorem10(state):
            bad10 += 1
        if sum(F for _, F in state) >= 2 and V(2, state) != theorem11(state):
            bad11 += 1
    print(f"Theorem 10 vs DP on 300 random states: mismatches {bad10}  [{'OK' if bad10 == 0 else 'FAIL'}]")
    print(f"Theorem 11 vs DP on random two-hit states: mismatches {bad11}  [{'OK' if bad11 == 0 else 'FAIL'}]")
    s = ((4, 2), (5, 2), (14, 7))
    v, k = V(3, s), Kcommit(3, s)
    print(f"Corollary 14 witness {s}, H=3: V*={v} (note 1055429/205920), commit={k} (note 351823/68640), gap={k - v}"
          f"  [{'OK' if (v, k) == (Fr(1055429, 205920), Fr(351823, 68640)) else 'FAIL'}]")
    s = ((10, 2), (12, 2), (19, 3))
    v, k = V(4, s), Kcommit(4, s)
    print(f"one-in-739 witness {s}, H=4: V*={v} (note 7477604/479655), commit={k} (note 22463159/1438965), rel gap 1/{float(v/(k - v)):.1f}"
          f"  [{'OK' if (v, k) == (Fr(7477604, 479655), Fr(22463159, 1438965)) else 'FAIL'}]")
    s = ((4, 2), (4, 2), (6, 3))
    v, k = V(4, s), Kcommit(4, s)
    print(f"commit-until-hit witness {s}, H=4: V*={v} (note 763/120), commit={k} (note 509/80)  [{'OK' if (v, k) == (Fr(763, 120), Fr(509, 80)) else 'FAIL'}]")
    # Corollary 14: committing is exact at H<=2 on an exhaustive small grid (sizes <= 6, <= 3 categories)
    bad = 0
    tot = 0
    states = set()
    for C in (1, 2, 3):
        def rec(prefix, C):
            if len(prefix) == C:
                states.add(tuple(sorted(prefix)))
                return
            for n in range(1, 7):
                for F in range(1, n + 1):
                    rec(prefix + [(n, F)], C)
        rec([], C)
    for st in states:
        for h in (1, 2):
            if sum(F for _, F in st) >= h:
                tot += 1
                if V(h, st) != Kcommit(h, st):
                    bad += 1
    print(f"committing exact at H<=2 on {tot} (state,H) pairs with sizes<=6, <=3 categories: violations {bad}  [{'OK' if bad == 0 else 'FAIL'}]")


if __name__ == "__main__":
    main()
