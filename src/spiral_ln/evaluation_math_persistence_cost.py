"""Exact charged proof persistence under a shared latent success rate."""
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
from math import comb, prod


@lru_cache(None)
def tail(d, n, p):
    return sum((comb(n, k)*p**k*(1-p)**(n-k)
                for k in range(d, n+1)), F(0))


def quota(d, budget):
    a, r = divmod(budget, d)
    return (a+1,)*r + (a,)*(d-r)


def static(a, p):
    return prod(1-(1-p)**k for k in a)


def mix_value(mix, fn):
    return sum((w*fn(p) for p, w in mix), F(0))


def extreme_mixtures(support, mean):
    """Vertices of finite probability simplex cut by a first-moment constraint."""
    s = sorted(set(map(F, support)))
    mean = F(mean)
    if not s or s[0] < 0 or s[-1] > 1 or not s[0] <= mean <= s[-1]:
        raise ValueError('invalid support or mean')
    if mean in s:
        yield ((mean, F(1)),)
    for lo in s:
        for hi in s:
            if lo < mean < hi:
                yield ((lo, (hi-mean)/(hi-lo)), (hi, (mean-lo)/(hi-lo)))


def robust_gap(d, budget, charge, support, mean):
    if d < 1 or budget < 0 or not 0 <= charge <= budget:
        raise ValueError('invalid obligations, budget or charge')
    a = quota(d, budget)
    return min(mix_value(m, lambda p: tail(d, budget-charge, p)-static(a, p))
               for m in extreme_mixtures(support, mean))


def break_even(d, budget, support, mean, strict=False):
    """Largest integer charge giving a nonnegative (or positive) worst-case gap."""
    support = tuple(support)
    gaps = (robust_gap(d, budget, c, support, mean) for c in range(budget+1))
    return max((c for c, g in enumerate(gaps) if (g > 0 if strict else g >= 0)),
               default=None)


def allocations(d, b):
    if d == 1:
        yield (b,)
    else:
        for k in range(b+1):
            for rest in allocations(d-1, b-k):
                yield (k, *rest)


def binary_oracle(d, n, p):
    return sum((p**sum(bits)*(1-p)**(n-sum(bits))
                for bits in product((0, 1), repeat=n) if sum(bits) >= d), F(0))
