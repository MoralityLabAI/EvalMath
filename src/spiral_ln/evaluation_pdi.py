"""PDI-01: exact certificate reliability and budgeted perfect audits."""
from fractions import Fraction as F
from functools import lru_cache
from itertools import combinations


def probability(x):
    if not isinstance(x, (int, F)) or not 0 <= x <= 1:
        raise ValueError("expected exact probability in [0,1]")
    return F(x)


def shared_failure(q, r, k):
    q, r = probability(q), probability(r)
    if type(k) is not int or k < 1:
        raise ValueError("positive integer certificate count required")
    return q + (1-q)*r**k


def independent_failure(q, r, k):
    shared_failure(q, r, k)
    return (F(q) + (1-F(q))*F(r))**k


def intersection_bounds(marginals):
    p = tuple(map(probability, marginals))
    if not p:
        raise ValueError("at least one event required")
    return max(F(0), sum(p)-len(p)+1), min(p)


def product_prior(validity):
    p = tuple(map(probability, validity))
    out = [F(1)]
    for v in p:
        out = [x*(1-v) for x in out] + [x*v for x in out]
    return tuple(out)


def instance(prior, claims):
    p = tuple(map(probability, prior))
    if not p or len(p) & (len(p)-1) or sum(p) != 1:
        raise ValueError("prior must be a normalized power-of-two table")
    raw = tuple(claims)
    if any(not isinstance(weight, (int, F)) for weight, _ in raw):
        raise ValueError("expected exact claim weight")
    c = tuple((F(weight), tuple(certs)) for weight, certs in raw)
    if any(weight < 0 or not certs or any(type(m) is not int or not 0 <= m < len(p) for m in certs)
           for weight, certs in c):
        raise ValueError("invalid claim weight or certificate mask")
    return p, c


def holds(world, certificates):
    return any(world & mask == mask for mask in certificates)


def failure(prior, certificates):
    p, c = instance(prior, [(1, certificates)])
    return sum((v for w, v in enumerate(p) if not holds(w, c[0][1])), F(0))


def audit_value(prior, claims, costs, budget, *, adaptive=True):
    """Return optimal expected *certainly certified* weight; no posterior threshold.

    A world is a bitmask of valid obligations. Prior indices are worlds, and
    each claim is (weight, tuple of alternative conjunctive certificate masks).
    Audit i reveals bit i perfectly. No audit changes the latent world.
    """
    p, c = instance(prior, claims)
    n = len(p).bit_length()-1
    costs = tuple(costs)
    if len(costs) != n or any(type(x) is not int or x <= 0 for x in costs) or type(budget) is not int or budget < 0:
        raise ValueError("invalid audit costs or budget")
    worlds = tuple(w for w, mass in enumerate(p) if mass)

    def terminal(ws):
        if not ws:
            return F(0)
        return sum(p[w] for w in ws)*sum(weight for weight, certs in c
                                         if all(holds(w, certs) for w in ws))

    if not adaptive:
        best = F(0)
        for size in range(n+1):
            for subset in combinations(range(n), size):
                if sum(costs[i] for i in subset) > budget:
                    continue
                mask = sum(1 << i for i in subset)
                groups = {}
                for w in worlds:
                    groups.setdefault(w & mask, []).append(w)
                best = max(best, sum(terminal(ws) for ws in groups.values()))
        return best

    @lru_cache(None)
    def solve(ws, remaining, b):
        best = terminal(ws)
        if not ws:
            return best
        for i, cost in enumerate(costs):
            bit = 1 << i
            if remaining & bit and cost <= b:
                yes = tuple(w for w in ws if w & bit)
                no = tuple(w for w in ws if not w & bit)
                value = solve(yes, remaining ^ bit, b-cost) + solve(no, remaining ^ bit, b-cost)
                best = max(best, value)
        return best

    return solve(worlds, (1 << n)-1, budget)
