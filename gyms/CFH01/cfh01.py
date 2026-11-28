"""CFH-01 public development oracle; Python 3.10+, standard library only.
Source: Davis et al., solved-conjectures, CFH proof, pinned in README.
"""
from functools import cache
from itertools import combinations
from math import comb
from fractions import Fraction
import json

R = (1, 2, 3, 4)
EXPECTED = (-11062769241414341239970603495681493737981374532130995,
            -11061733404916469626152098526056073213151599377977031)


def prime_power(q):
    if type(q) is not int or q < 2:
        return False
    p = 2
    while p * p <= q and q % p:
        p += 1
    if p*p > q:
        return True
    while q % p == 0:
        q //= p
    return q == 1


@cache
def gaussian(q, d, i):
    if not 0 <= i <= d:
        return 0
    a = b = 1
    for j in range(i):
        a *= q ** (d-j) - 1
        b *= q ** (i-j) - 1
    assert a % b == 0
    return a // b


@cache
def alpha(q, d, t, ranks):
    if not ranks:
        return 1
    s = ranks[-1]
    return sum(gaussian(q, d, i) * comb(t, s-i)
               * alpha(q, i, s-i, ranks[:-1])
               for i in range(max(0, s-t), min(d, s)+1))


def subsets(s):
    return [c for k in range(len(s)+1) for c in combinations(s, k)]


def gamma(q, m, b, augmented=False):
    if not prime_power(q) or type(m) is not int or type(b) is not int:
        raise ValueError('expected prime power q and integer m, b')
    if m < q**4 or not 0 <= b <= q**16:
        raise ValueError('outside certified construction')
    n = lambda i: gaussian(q, 8, i)
    types = [(4, 0, n(4)-b), (4, 1, b),
             (3, 1, m*n(3)-b*gaussian(q, 4, 3))]
    types += [(4-j, j, n(4-j)*comb(m, j)) for j in range(2, 5)]
    assert all(w >= 0 for _, _, w in types)

    def flag(s):
        if not s or s[-1] < 4:
            return alpha(q, 8, m, s)
        return sum(w*alpha(q, d, t, s[:-1]) for d, t, w in types)

    def beta(s):
        return sum((-1)**(len(s)-len(t))*flag(t) for t in subsets(s))

    return tuple(sum(beta(tuple(r for r in R if r not in s))
                     for s in subsets(R if augmented else R[:-1])
                     if len(s) == j and all(y-x > 1 for x, y in zip(s, s[1:])))
                 for j in range(3))


def disc(g):
    return g[1]**2 - 4*g[0]*g[2]


def quadratic(q, m, augmented=False):
    u, v, w = gamma(q, m, 0, augmented)
    a, c, e = (y-x for x, y in zip((u, v, w), gamma(q, m, 1, augmented)))
    return c*c-4*a*e, 2*v*c-4*(u*e+a*w), v*v-4*u*w


def boundary(q, m, augmented=False):
    a, b, c = quadratic(q, m, augmented)
    cap = q**16
    # A linear derivative has its maximum at one of the two endpoints.
    if max(b, 2*a*cap+b) >= 0:
        raise ValueError('strict monotonicity certificate failed')
    def d(x):
        return (a*x+b)*x+c
    if d(0) < 0:
        return 0
    if d(cap) >= 0:
        return None
    lo, hi = 0, cap
    while hi-lo > 1:
        mid = (lo+hi)//2
        if d(mid) < 0:
            hi = mid
        else:
            lo = mid
    assert disc(gamma(q, m, hi, augmented)) < 0
    assert disc(gamma(q, m, hi-1, augmented)) >= 0
    assert gamma(q, m, hi, augmented)[2] > 0
    return hi


def audit():
    assert all(prime_power(q) for q in (2, 3, 4, 8, 9, 17, 19, 64, 128))
    assert not any(prime_power(q) for q in (0, 1, 6, 12, 15, 18, 21))
    assert tuple(disc(gamma(17, 17**4, 17**16, a))
                 for a in (False, True)) == EXPECTED
    rows = []
    for q in (2, 3, 4, 5, 7, 8, 9, 11, 13, 16, 17, 19, 23, 25, 27, 29, 31, 32, 37, 64, 128):
        for k in (1, 2, 4):
            m = k*q**4
            for aug in (False, True):
                a, b, c = quadratic(q, m, aug)
                for x in (0, 1, q**16//2, q**16):
                    assert disc(gamma(q, m, x, aug)) == (a*x+b)*x+c
                t = boundary(q, m, aug)
                rows.append(dict(q=q, m=m, augmented=aug, minimum_b=t,
                                 minimum_fraction=None if t is None else str(Fraction(t, q**16))))
    for q, m, b in ((6, 6**4, 0), (2, 15, 0), (2, 16, -1), (2, 16, 2**16+1)):
        try:
            gamma(q, m, b)
        except ValueError:
            continue
        raise AssertionError('invalid construction admitted')
    return {'evidence': 'exact finite arithmetic, one construction family', 'rows': rows}


if __name__ == '__main__':
    print(json.dumps(audit(), indent=2))
