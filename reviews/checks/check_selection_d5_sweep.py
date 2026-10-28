"""Exact integer re-computation of D.5 (selection KL): M_n(K) = E max_k (X_k - n/2), X_k ~ Bin(n, 1/2),
D_n(K) = 2n (M_{n+1} - M_n) - M_n, and the two monotonicity statements
    (R)  rho_n >= 1  <=>  D_n >= 0,
    (A)  a_{n+1}^2 > a_n^2  <=>  n M_{n+1}^2 > (n+1) M_n^2.
With S_m = sum_{j<=m} C(n,j) (so F(m) = S_m / 2^n), N_n(K) := 2^{nK} M_n(K) = sum_{m<n} (S_m 2^{n(K-1)} - S_m^K),
    D_n > 0  <=>  2n N_{n+1} > (2n+1) 2^K N_n,
    (A)      <=>  n N_{n+1}^2 > (n+1) 4^K N_n^2.
Nothing is imported from spiral_ln.

Usage:
  python check_selection_d5_sweep.py sweep KMIN KMAX NMAX       # D_n>0 and (A) for all K, n<=NMAX
  python check_selection_d5_sweep.py gap   KMIN KMAX NMIN NMAX  # the unchecked (400, N_0) window for K=41..50
  python check_selection_d5_sweep.py values K n1 n2 ...         # print exact sqrt(n) D_n as floats
"""
from __future__ import annotations

import sys
from fractions import Fraction
from math import comb, sqrt


def prefix_sums(n):
    out = []
    s = 0
    for j in range(n):
        s += comb(n, j)
        out.append(s)
    return out  # S_0 .. S_{n-1}


def N_of(n, K, S=None):
    S = prefix_sums(n) if S is None else S
    shift = n * (K - 1)
    return sum((s << shift) - s**K for s in S)


def D_pos(n, K, Nn, Nn1):
    return 2 * n * Nn1 > ((2 * n + 1) << K) * Nn


def A_pos(n, K, Nn, Nn1):
    return n * Nn1 * Nn1 > (n + 1) * (Nn * Nn << (2 * K))


def sweep(kmin, kmax, nmax):
    S_cache = {}
    for K in range(kmin, kmax + 1):
        bad_D, bad_A, min_margin = [], [], None
        Nprev = None
        for n in range(1, nmax + 2):
            if n not in S_cache:
                S_cache[n] = prefix_sums(n)
            Nn = N_of(n, K, S_cache[n])
            if Nprev is not None:
                m = n - 1
                if not D_pos(m, K, Nprev, Nn):
                    bad_D.append(m)
                if not A_pos(m, K, Nprev, Nn):
                    bad_A.append(m)
            Nprev = Nn
        print(f"K={K}: n=1..{nmax}: D_n>0 fails at {bad_D or 'none'}; a_n^2 strictly increasing fails at {bad_A or 'none'}", flush=True)


def gap(kmin, kmax, nmin, nmax):
    S_cache = {}
    for K in range(kmin, kmax + 1):
        bad = []
        Nprev = None
        for n in range(nmin, nmax + 2):
            if n not in S_cache:
                S_cache[n] = prefix_sums(n)
            Nn = N_of(n, K, S_cache[n])
            if Nprev is not None and not D_pos(n - 1, K, Nprev, Nn):
                bad.append(n - 1)
            Nprev = Nn
        print(f"K={K}: D_n>0 for n in [{nmin},{nmax}]: failures {bad or 'none'}", flush=True)


def values(K, ns):
    for n in ns:
        Nn = N_of(n, K)
        Nn1 = N_of(n + 1, K)
        Mn = Fraction(Nn, 1 << (n * K))
        Mn1 = Fraction(Nn1, 1 << ((n + 1) * K))
        Dn = 2 * n * (Mn1 - Mn) - Mn
        print(f"K={K} n={n}: M_n={float(Mn):.12f} a_n={float(Mn)/sqrt(n):.12f} D_n={float(Dn):.12e} sqrt(n)*D_n={sqrt(n)*float(Dn):.12e}", flush=True)


if __name__ == "__main__":
    cmd = sys.argv[1]
    args = [int(a) for a in sys.argv[2:]]
    if cmd == "sweep":
        sweep(*args)
    elif cmd == "gap":
        gap(*args)
    elif cmd == "values":
        values(args[0], args[1:])
