"""Sharp fixed-product completion envelopes for independent geometric retries."""
from fractions import Fraction as F
from math import prod


def coefficients(failures, k):
    """Coefficients of product (1-r*t)^(-1) through degree k."""
    if k < 0:
        return ()
    a = [F(1)] + [F(0)] * k
    for r in map(F, failures):
        for j in range(1, k+1):
            a[j] += r*a[j-1]
    return tuple(a)


def completion(ps, budget):
    ps = tuple(map(F, ps))
    if budget < 0 or any(not 0 <= p <= 1 for p in ps):
        raise ValueError('invalid probabilities or budget')
    k = budget-len(ps)
    if k < 0:
        return F(0)
    return prod(ps)*sum(coefficients((1-p for p in ps), k))


def pair_exchange(ps, replacement, budget):
    """Exact change replacing the first two probabilities at fixed product."""
    ps = tuple(map(F, ps)); a,b = ps[:2]; c,d = map(F, replacement)
    if a*b != c*d or budget < 0 or any(not 0 <= p <= 1 for p in (*ps,c,d)):
        raise ValueError('invalid exchange')
    k = budget-len(ps)
    if k <= 0:
        return F(0)
    failures = (1-a,1-b,1-c,1-d,*(1-p for p in ps[2:]))
    return prod(ps)*(a+b-c-d)*coefficients(failures,k-1)[-1]


def concentrated_lower(d, budget, q):
    q = F(q)
    if d < 1 or budget < 0 or not 0 <= q <= 1:
        raise ValueError('invalid envelope parameters')
    return F(0) if budget < d else 1-(1-q)**(budget-d+1)
