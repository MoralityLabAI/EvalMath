"""Independent re-implementation of the tapered-Hermite valuation grid probe.

Transcribed directly from eq. (tensor-hermite-loss) in quantitative-contraction.tex,
not from the PR's proof_fidelity.py, so agreement is a second witness.
"""
from fractions import Fraction


def v2(x: int) -> int:
    x = abs(x)
    assert x > 0
    return (x & -x).bit_length() - 1


def probe(max_a: int = 7, m_window: int = 5):
    total = 0
    worst_ratio = Fraction(0)  # how close direct gets to the -6Dh bound
    for a in range(1, max_a + 1):
        L = 1 << a
        S = range(-L, L)  # complete residue system mod 2^(a+1), L odd points
        for u in range(1, a + 1):
            for M in range(u, u + m_window + 1):
                h = -(-3 * M // u)  # ceil(3M/u)
                q = lambda i: h * max(0, u - i)
                for t in S:
                    if t == 0:
                        continue
                    i = v2(t)
                    if i >= u:  # q_t == 0, node absent
                        continue
                    D = L >> i
                    direct = sum(q(v2(z)) * (v2(z) - v2(t - z)) for z in S if z not in (0, t))
                    grouped = sum((Fraction(D * j, 1 << j) * (q(i + j) - q(i)) for j in range(1, a - i + 1)), Fraction(0))
                    assert direct == grouped, (a, u, M, t, direct, grouped)
                    assert direct >= -6 * D * h, (a, u, M, t, direct, -6 * D * h)
                    worst_ratio = max(worst_ratio, Fraction(-direct, 6 * D * h))
                    total += 1
    return total, worst_ratio


if __name__ == "__main__":
    n, ratio = probe()
    print("cases:", n)
    print("max |v2(E_t(0))| / (6 D h) observed:", ratio, "~", float(ratio))
    # a slightly bigger grid, to see whether anything changes off the PR's window
    n2, ratio2 = probe(max_a=9, m_window=8)
    print("cases (a<=9, M<=u+8):", n2, " max ratio:", float(ratio2))
