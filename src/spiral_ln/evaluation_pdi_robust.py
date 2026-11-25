"""PDI-04--06: robust policies, full-filtration risk, versioned evidence and reuse."""
from fractions import Fraction as F
from functools import lru_cache
from itertools import combinations, product
from math import comb
from spiral_ln.evaluation_pdi import holds, probability
from spiral_ln.evaluation_pdi_noisy import setup


def prune(rows):
    """Rows map scenario-vector (false,true,...) to a deterministic tree."""
    unique = dict(rows)
    def dominates(x, y):
        return x != y and all(a <= b if i % 2 == 0 else a >= b
                              for i, (a, b) in enumerate(zip(x, y)))
    return tuple((v, unique[v]) for v in sorted(unique)
                 if not any(dominates(u, v) for u in unique))


def robust_frontier(scenarios, claims, budget):
    """One common policy tree, even when priors and channel rates differ.

    Each scenario is (prior, channels). Channel identity, cost, bit and claims
    must agree. Noise is conditionally independent within each scenario.
    """
    claims = tuple((w, tuple(ms)) for w, ms in claims)
    sc = tuple(setup(p, claims, a, budget, 0) for p, a in scenarios)
    if not sc:
        raise ValueError('empty ambiguity set')
    p, c, a, _ = sc[0]
    topology = tuple((i, cost) for i, _, _, cost in a)
    if any(len(q) != len(p) or d != c or tuple((i, cost) for i, _, _, cost in b) != topology
           for q, d, b, _ in sc):
        raise ValueError('scenario topology mismatch')
    n = len(sc)

    def leaf(masses, pos, neg):
        eligible = tuple(j for j, (_, ms) in enumerate(c) if holds(pos & ~neg, ms))
        for size in range(len(eligible)+1):
            for ids in combinations(eligible, size):
                v = []
                for mass in masses:
                    f = t = F(0)
                    for j in ids:
                        weight, ms = c[j]
                        for w, m in enumerate(mass):
                            if holds(w, ms):
                                t += weight*m
                            else:
                                f += weight*m
                    v.extend((f, t))
                yield tuple(v), ('leaf', ids)

    def step(masses, j, y):
        bit = 1 << a[j][0]
        out = []
        for mass, (_, _, channels, _) in zip(masses, sc):
            _, t, f, _ = channels[j]
            rates = tuple(t if w & bit else f for w in range(len(p)))
            out.append(tuple(m*(r if y else 1-r) for m, r in zip(mass, rates)))
        return tuple(out)

    @lru_cache(None)
    def dp(masses, pos, neg, remaining, b):
        rows = prune(leaf(masses, pos, neg))
        for j in remaining:
            i, _, _, cost = a[j]
            if cost > b:
                continue
            bit = 1 << i
            rest = tuple(k for k in remaining if k != j)
            no = dp(step(masses, j, 0), pos, neg | bit, rest, b-cost)
            yes = dp(step(masses, j, 1), pos | bit, neg, rest, b-cost)
            rows = prune(rows + tuple((tuple(x+y for x, y in zip(u, v)), ('audit', j, l, r))
                                       for u, l in no for v, r in yes))
        return rows
    return dp(tuple(q for q, _, _, _ in sc), 0, 0, tuple(range(len(a))), budget)


def solve_square(rows, rhs):
    m = [list(map(F, row))+[F(b)] for row, b in zip(rows, rhs)]
    n = len(m)
    for i in range(n):
        j = next((j for j in range(i, n) if m[j][i]), None)
        if j is None:
            return None
        m[i], m[j] = m[j], m[i]
        d = m[i][i]
        m[i] = [v/d for v in m[i]]
        for j in range(n):
            if j != i:
                d = m[j][i]
                m[j] = [x-d*y for x, y in zip(m[j], m[i])]
    return tuple(row[-1] for row in m)


def robust_mix(rows, epsilon):
    """Exact max-min expected true weight, per-scenario expected false caps.

    Returns (worst true, vector, ((probability, tree), ...)). Enumerates LP
    vertices; intended for small finite frontiers only.
    """
    rows = prune(rows)
    if not rows or not isinstance(epsilon, (int, F)) or epsilon < 0:
        raise ValueError('invalid robust problem')
    m = len(rows[0][0])//2
    if not m or any(len(v) != 2*m for v, _ in rows):
        raise ValueError('invalid scenario vectors')
    best = None
    # k positive mixing weights plus z; sum(weights)=1 and k active inequalities.
    for k in range(1, min(2*m, len(rows))+1):
        for support in combinations(rows, k):
            inequalities = [(tuple(v[2*i] for v, _ in support)+(0,), F(epsilon)) for i in range(m)]
            inequalities += [(tuple(-v[2*i+1] for v, _ in support)+(1,), F(0)) for i in range(m)]
            for active in combinations(inequalities, k):
                solution = solve_square([(1,)*k+(0,)]+[a for a, _ in active], [1]+[b for _, b in active])
                if solution is None or min(solution[:-1]) < 0:
                    continue
                if any(sum(x*y for x, y in zip(a, solution)) > b for a, b in inequalities):
                    continue
                weights, z = solution[:-1], solution[-1]
                vector = tuple(sum(w*v[i] for w, (v, _) in zip(weights, support)) for i in range(2*m))
                candidate = (z, vector, tuple((w, tree) for w, (_, tree) in zip(weights, support) if w))
                if best is None or (z, -max(vector[::2])) > (best[0], -max(best[1][::2])):
                    best = candidate
    if best is None:
        raise ValueError('infeasible risk cap')
    return best


def hazard_bound(alphas):
    """Deterministic full-history conditional hazard limits, including stops."""
    survival = F(1)
    for a in alphas:
        survival *= 1-probability(a)
    return 1-survival


def projected_posterior(cells, keep, observed):
    """Cells (world, transcript tuple, probability); retain selected coordinates."""
    cells = tuple((world, transcript, probability(mass)) for world, transcript, mass in cells)
    if sum(m for _, _, m in cells) != 1:
        raise ValueError('joint law must normalize')
    keep, observed = tuple(keep), tuple(observed)
    if len(keep) != len(observed) or any(i < 0 or any(i >= len(t) for _, t, _ in cells) for i in keep):
        raise ValueError('invalid projection')
    posterior = {}
    for w, transcript, mass in cells:
        if tuple(transcript[i] for i in keep) == observed and mass:
            posterior[w] = posterior.get(w, F(0))+mass
    total = sum(posterior.values())
    if not total:
        raise ValueError('zero-probability observation')
    return {w: m/total for w, m in posterior.items()}


def source_law(reliability, second=None):
    """Two independent reports about a fair bit; the first also routes an audit."""
    r = probability(reliability)
    u = r if second is None else probability(second)
    return tuple((x, (s, t, s, 1), F(1,2)*(r if x == s else 1-r)*(u if x == t else 1-u))
                 for x, s, t in product((0, 1), repeat=3))


def reuse_workload(targets, root_cost, branch_cost, independent_cost, budget):
    """Declared perfect shared-root vs independent per-target audit workload."""
    if any(type(x) is not int or x < 0 for x in (targets, root_cost, budget)) or any(
        type(x) is not int or x <= 0 for x in (branch_cost, independent_cost)):
        raise ValueError('invalid workload')
    reused = min(targets, max(0, budget-root_cost)//branch_cost)
    independent = min(targets, budget//independent_cost)
    return reused, independent


def hazard_audit(paths, limits):
    """Finite full-information path audit, before first bad authorization.

    Paths are (mass, ((pretrial signal, bad-event bit), ...)); after stopping,
    remaining positions must be padded with a stop signal and event zero.
    Caller supplies the complete pretrial information, including selection.
    """
    limits = tuple(map(probability, limits))
    paths = tuple((probability(m), tuple(path)) for m, path in paths)
    if sum(m for m, _ in paths) != 1 or any(len(p) != len(limits) or any(y not in (0, 1) for _, y in p) for _, p in paths):
        raise ValueError('invalid finite paths')
    maxima = []
    for i, limit in enumerate(limits):
        groups = {}
        for mass, path in paths:
            if mass and not any(y for _, y in path[:i]):
                key = (path[:i], path[i][0])
                den, num = groups.get(key, (F(0), F(0)))
                groups[key] = (den+mass, num+mass*path[i][1])
        maxima.append(max((n/d for d, n in groups.values()), default=F(0)))
    risk = sum(m for m, p in paths if any(y for _, y in p))
    return tuple(maxima), risk, all(h <= a for h, a in zip(maxima, limits))


def transfer_profile(targets, root_cost, branch_cost, budget, root_valid, branch_valid, sensitivity, false_pos):
    """Fixed worst-case-cost schedules; branch audits perfect, root noisy.

    Shared schedule audits one root, then up to k branch obligations. Independent
    schedule uses fresh independent root/branch pairs per target. No reallocation.
    Returns (scheduled targets, expected true weight, full false-count law).
    """
    q, p, t, f = map(probability, (root_valid, branch_valid, sensitivity, false_pos))
    kr, ki = reuse_workload(targets, root_cost, branch_cost, root_cost+branch_cost, budget)
    def binomial(k, v):
        return tuple(comb(k, j)*v**j*(1-v)**(k-j) for j in range(k+1))
    bad_gate = (1-q)*f
    shared = tuple(bad_gate*x + (1-bad_gate if j == 0 else 0) for j, x in enumerate(binomial(kr, p)))
    independent = binomial(ki, bad_gate*p)
    return (kr, kr*q*t*p, shared), (ki, ki*q*t*p, independent)
