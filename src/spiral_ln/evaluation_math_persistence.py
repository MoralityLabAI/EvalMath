"""Exact synthetic proof persistence; no model execution."""
from fractions import Fraction as F
from itertools import product
from math import comb, prod


def persistent(ps, budget):
    """Independent attempts, fixed topological order, irreversible verified progress."""
    ps = tuple(map(F, ps))
    if budget < 0 or any(not 0 <= p <= 1 for p in ps):
        raise ValueError("invalid budget or probability")
    d = len(ps)
    mass = [F(1)] + [F(0)] * d
    for _ in range(budget):
        nxt = [F(0)] * d + [mass[d]]
        for i, p in enumerate(ps):
            nxt[i] += mass[i] * (1 - p)
            nxt[i + 1] += mass[i] * p
        mass = nxt
    return mass[d]


def homogeneous(d, budget, p):
    p = F(p)
    if min(d, budget) < 0 or not 0 <= p <= 1:
        raise ValueError("invalid parameters")
    return sum((comb(budget, k) * p**k * (1-p)**(budget-k)
                for k in range(d, budget+1)), F(0))


def exhaustive(ps, budget):
    """Independent oracle: sum probabilities of first-completion bit prefixes."""
    ps = tuple(map(F, ps))
    d = len(ps)
    if not d:
        return F(1)
    out = F(0)
    for t in range(d, budget+1):
        for bits in product((0, 1), repeat=t-1):
            if sum(bits) != d-1:
                continue
            i, weight = 0, F(1)
            for bit in (*bits, 1):
                weight *= ps[i] if bit else 1-ps[i]
                i += bit
            out += weight
    return out


def allocations(d, budget):
    """All positive static attempt allocations with sum <= budget (unused budget harmless)."""
    if d == 0:
        yield ()
    else:
        for a in range(1, budget-d+2):
            for rest in allocations(d-1, budget-a):
                yield (a, *rest)


def fixed_best(ps, budget):
    """Best clairvoyant static quota policy, independent retry slots per obligation."""
    ps = tuple(map(F, ps))
    return max((prod(1-(1-p)**a for p, a in zip(ps, quota))
                for quota in allocations(len(ps), budget)), default=F(0))


def reset(d, budget, p):
    """Restricted sham: any failure clears all previous progress; success is absorbing."""
    p = F(p)
    if min(d, budget) < 0 or not 0 <= p <= 1:
        raise ValueError("invalid parameters")
    mass = [F(1)] + [F(0)] * d
    for _ in range(budget):
        nxt = [F(0)] * d + [mass[d]]
        for i in range(d):
            nxt[0] += mass[i] * (1-p)
            nxt[i+1] += mass[i] * p
        mass = nxt
    return mass[d]
