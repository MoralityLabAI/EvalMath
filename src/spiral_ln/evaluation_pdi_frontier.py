"""PDI-03: exact expected-risk frontiers and versioned evidence eligibility."""
from fractions import Fraction as F
from functools import lru_cache
from itertools import combinations, product
from spiral_ln.evaluation_pdi import holds
from spiral_ln.evaluation_pdi_noisy import setup

ZERO = (F(0), F(0))  # false weight, true weight


def pareto(points):
    """Keep nondominated points (minimize false, maximize true)."""
    best = F(-1)
    out = []
    for f, t in sorted(set(points), key=lambda p: (p[0], -p[1])):
        if t > best:
            out.append((f, t))
            best = t
    return tuple(out)


def combine(left, right):
    return pareto((f+g, t+u) for f, t in left for g, u in right)


def frontier(prior, claims, channels, budget, *, adaptive=True):
    """Nondominated (E[false], E[true]) points of deterministic policies.

    Same witness rule and independent conditional channel model as PDI-02.
    Terminal decisions may authorize any subset of eligible claims. No repair
    or revocation during this optimization; every path respects the budget.
    """
    p, c, a, _ = setup(prior, claims, channels, budget, 0)

    def terminal(mass, pos, neg):
        points = (ZERO,)
        for weight, masks in c:
            if holds(pos & ~neg, masks):
                good = weight*sum(v for w, v in enumerate(mass) if holds(w, masks))
                bad = weight*sum(v for w, v in enumerate(mass) if not holds(w, masks))
                points = combine(points, (ZERO, (bad, good)))
        return points

    def step(mass, pos, neg, j, y):
        i, t, f, _ = a[j]
        bit = 1 << i
        rates = tuple(t if w & bit else f for w in range(len(p)))
        return (tuple(v*(r if y else 1-r) for v, r in zip(mass, rates)),
                pos | (bit if y else 0), neg | (0 if y else bit))

    @lru_cache(None)
    def dp(mass, pos, neg, remaining, b):
        points = terminal(mass, pos, neg)
        for j in remaining:
            if a[j][3] <= b:
                rest = tuple(k for k in remaining if k != j)
                points = pareto(points + combine(*(dp(*step(mass, pos, neg, j, y), rest, b-a[j][3])
                                                    for y in (0, 1))))
        return points

    if adaptive:
        return dp(p, 0, 0, tuple(range(len(a))), budget)
    points = (ZERO,)
    for size in range(len(a)+1):
        for subset in combinations(range(len(a)), size):
            if sum(a[j][3] for j in subset) > budget:
                continue
            fixed = (ZERO,)
            for outcomes in product((0, 1), repeat=size):
                state = (p, 0, 0)
                for j, y in zip(subset, outcomes):
                    state = step(*state, j, y)
                fixed = combine(fixed, terminal(*state))
            points = pareto(points + fixed)
    return points


def at_risk(points, epsilon, *, randomized=True):
    """Optimal (false,true) and mixture (weight, point) under E[false]<=epsilon.

    Randomization is a precommitted independent choice of deterministic policy.
    The mixture records attainable endpoint values, not executable policy trees.
    """
    if not isinstance(epsilon, (int, F)) or epsilon < 0:
        raise ValueError('nonnegative exact risk budget required')
    points = pareto(tuple(points))
    feasible = [(p, ((F(1), p),)) for p in points if p[0] <= epsilon]
    if not feasible:
        raise ValueError('no feasible policy')
    if randomized:
        for p in points:
            for q in points:
                if p[0] < epsilon < q[0]:
                    w = (F(epsilon)-p[0])/(q[0]-p[0])
                    feasible.append(((F(epsilon), (1-w)*p[1]+w*q[1]), ((1-w, p), (w, q))))
    return max(feasible, key=lambda z: (z[0][1], -z[0][0]))


def accepted_versions(events, active):
    """Eligibility only: (obligation, version, outcome) records, active versions.

    Old observations remain in the ledger; only active version results count.
    This does not compute a posterior or remove selection information.
    """
    pos, neg = set(), set()
    for i, version, outcome in events:
        if type(i) is not int or i < 0 or outcome not in (0, 1):
            raise ValueError('invalid evidence event')
        if i in active and active[i] == version:
            (pos if outcome else neg).add(i)
    return sum(1 << i for i in pos-neg)


def selection_revocation_witness():
    """Fair hidden bit X; source observes X and routes to a constant probe.

    Removing its output while retaining the selected probe preserves X.
    A projection hiding the probe identity gives the original fair prior.
    """
    cells = [(x, F(1, 2), 'left' if x == 0 else 'right', 1) for x in (0, 1)]
    def posterior(key):
        groups = {}
        for x, mass, action, result in cells:
            k = key(action, result)
            den, num = groups.get(k, (F(0), F(0)))
            groups[k] = (den+mass, num+x*mass)
        return {k: num/den for k, (den, num) in groups.items()}
    return posterior(lambda a, y: (a, y)), posterior(lambda a, y: y)
