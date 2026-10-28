"""Does the KL budget of best-of-K selection survive correlated (perturbative) candidates?

Theorem B' (this review): the record kept from GK+1 i.i.d. draws by ANY rule has
KL(law || p0) <= lambda_{GK+1}.  The multigen mutation chain (§5) draws candidates by perturbing the
incumbent item by item (copy w.p. 1-q, redraw Bernoulli(p) w.p. q), so its candidates are not i.i.d.
from p0.  We compute the exact law of the reported count c_G for the naive rule and
KL(law of c_G || Bin(n,p)); by data processing this is a LOWER bound on the KL of the record law.
If it exceeds lambda_{GK+1}, the i.i.d. divergence budget does not cover perturbative loops.

Run:  python reviews/checks/check_mutation_chain_kl.py
"""
from __future__ import annotations

from fractions import Fraction as Fr
from math import comb, log


def binom(n, p):
    return [comb(n, k) * p**k * (1 - p) ** (n - k) for k in range(n + 1)]


def candidate_law(n, c, p, q):
    """Count of one candidate given incumbent count c: c - L + U, L~Bin(c, q(1-p)), U~Bin(n-c, qp)."""
    L = binom(c, q * (1 - p))
    U = binom(n - c, q * p)
    out = [Fr(0)] * (n + 1)
    for l, pl in enumerate(L):
        for u, pu in enumerate(U):
            out[c - l + u] += pl * pu
    return out


def step_naive(dist, n, K, p, q):
    new = [Fr(0)] * (n + 1)
    for c, mass in enumerate(dist):
        if mass == 0:
            continue
        law = candidate_law(n, c, p, q)
        F = [sum(law[: j + 1]) for j in range(n + 1)]
        # M = max of K candidates; accept iff M > c
        stay = F[c] ** K
        new[c] += mass * stay
        for j in range(c + 1, n + 1):
            new[j] += mass * (F[j] ** K - F[j - 1] ** K)
    return new


def kl(a, b):
    return sum(float(x) * log(float(x) / float(y)) for x, y in zip(a, b) if x > 0)


def main():
    p = Fr(1, 2)
    base = binom(8, p)
    print("mutation chain, n=8, K=2, p=1/2, naive rule; KL(law of c_G || Bin(n,p)) vs lambda_{GK+1} and G*lambda_{K+1}")
    print(" q     G   gap rho_G   KL(count)   lambda_{GK+1}   G*lambda_{K+1}   exceeds i.i.d. budget?")
    for q in [Fr(1), Fr(3, 4), Fr(1, 2), Fr(1, 4)]:
        dist = base[:]
        for G in range(1, 21):
            dist = step_naive(dist, 8, 2, p, q)
            if G in (1, 5, 10, 20):
                m = G * 2 + 1
                lam = log(m) - (m - 1) / m
                lamK1 = log(3) - 2 / 3
                gap = float(sum(c * x for c, x in enumerate(dist)) / 8 - p)
                k = kl(dist, base)
                print(f" {str(q):4s} {G:3d}   {gap:.4f}     {k:.4f}      {lam:.4f}          {G*lamK1:.4f}          {'YES' if k > lam + 1e-12 else 'no'}")


if __name__ == "__main__":
    main()
