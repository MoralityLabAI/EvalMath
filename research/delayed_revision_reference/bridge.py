"""Independent small-world Bayesian oracle for delayed evidence revisions.

No imports from Beyond Bayes. This is a finite reference for audit and
experimental design, not an authenticated evidence collector or a neural
mechanism test. A provisional report at a corrected slot is fair noise.
"""
from __future__ import annotations

from fractions import Fraction as Q
from itertools import product
from math import comb

PRIORS = (Q(9,20), Q(7,20), Q(1,5))
MATCH = (Q(19,20), Q(13,20), Q(3,20))


def binom(n: int, k: int, p: Q) -> Q:
    if not 0 <= k <= n:
        return Q(0)
    return Q(comb(n,k))*p**k*(1-p)**(n-k)


def norm(weights):
    z = sum(weights,Q(0))
    if not z:
        raise ValueError("impossible observation")
    return tuple(w/z for w in weights)


def analytic(n: int, slots: tuple[int,...], old_m: int,
             new: tuple[int,...], revealed_old: tuple[int,...]):
    """Pr(K | S, old_count, new, old prefix from slots), exact rational."""
    j=len(slots);r=len(revealed_old);q=sum(new);s=sum(revealed_old)
    if not (1 <= n <= 6 and 0 <= j <= n and 0 <= r <= j
            and len(new)==j and len(set(slots))==j
            and all(type(i)==int and 0<=i<n for i in slots)
            and all(type(i)==int and i in (0,1) for i in new+revealed_old)
            and type(old_m)==int and 0<=old_m<=n):
        raise ValueError("invalid contract")
    weights=[]
    for prior,t in zip(PRIORS,MATCH):
        old_valid = sum(binom(n-j,u,t)*binom(j-r,old_m-s-u,Q(1,2))
                        for u in range(n-j+1))
        weights.append(prior*t**q*(1-t)**(j-q)*old_valid)
    return norm(weights)


def independent_raw_oracle(n: int, slots: tuple[int,...], old_m: int,
                           new: tuple[int,...], revealed_old: tuple[int,...]):
    """Brute-force all old bit vectors; no call to the analytic count scorer."""
    j=len(slots);r=len(revealed_old)
    weights=[]
    schedule=set(slots)
    for prior,t in zip(PRIORS,MATCH):
        weight=Q(0)
        for old in product((0,1),repeat=n):
            if sum(old)!=old_m or tuple(old[s] for s in slots[:r])!=revealed_old:
                continue
            w=prior
            for i,bit in enumerate(old):
                w*=Q(1,2) if i in schedule else (t if bit else (1-t))
            for bit in new:
                w*=t if bit else (1-t)
            weight+=w
        weights.append(weight)
    return norm(weights)


def final_full(n: int, old: tuple[int,...], slots: tuple[int,...],
               new: tuple[int,...]):
    if len(old)!=n or len(slots)!=len(new):
        raise ValueError("wrong dimensions")
    accepted=list(old)
    for i,bit in zip(slots,new):
        accepted[i]=bit
    m=sum(accepted)
    return norm(tuple(prior*t**m*(1-t)**(n-m)
                      for prior,t in zip(PRIORS,MATCH)))


def brier(p, regime: int):
    return sum((x-int(i==regime))**2 for i,x in enumerate(p))


def raw_population(n: int, slots: tuple[int,...], r: int):
    """Exact expected Brier and squared gap; small-domain completeness oracle."""
    j=len(slots)
    if not (1<=n<=5 and 0<=j<=n and 0<=r<=j):
        raise ValueError("outside audit domain")
    schedule=set(slots)
    full_risk=limited_risk=gap=mass=Q(0)
    for k,(prior,t) in enumerate(zip(PRIORS,MATCH)):
        for old in product((0,1),repeat=n):
            likelihood=prior
            for i,v in enumerate(old):
                likelihood*=Q(1,2) if i in schedule else (t if v else (1-t))
            for new in product((0,1),repeat=j):
                p=likelihood
                for v in new:
                    p*=t if v else (1-t)
                limited=independent_raw_oracle(n,slots,sum(old),new,
                                               tuple(old[i] for i in slots[:r]))
                full=final_full(n,old,slots,new)
                full_risk+=p*brier(full,k)
                limited_risk+=p*brier(limited,k)
                gap+=p*sum((a-b)**2 for a,b in zip(full,limited))
                mass+=p
    assert mass==1
    assert limited_risk-full_risk==gap
    return {"full_brier":full_risk,"limited_brier":limited_risk,
            "regret":gap,"mass":mass}


def information_capacity(n:int,j:int):
    """Worst-case *self-contained* continuation bits under delayed schedule."""
    if not (type(n)==int and type(j)==int and 1<=j<n<=12):
        raise ValueError("1 <= j < n <= 12 required")
    biggest=max(comb(n,m) for m in range(n+1))
    return {"histories":2**n,"initial_posterior_labels":n+1,
            "self_contained_bits":n,"max_label_fiber":biggest,
            "extra_fixed_tag_bits":(biggest-1).bit_length(),
            "verified_old_sum_message_bits":j.bit_length(),
            "early_count_field_bits":n.bit_length()}
