"""Exact dynamic likelihood quotient and perturbation bounds (MIT-07)."""
from collections import Counter
from fractions import Fraction as F
from functools import lru_cache


def validate(weights, queries, budget):
    w = tuple(map(F, weights))
    if not w or any(x < 0 for x in w) or sum(w) <= 0:
        raise ValueError('invalid prior')
    if type(budget) is not int or budget < 0:
        raise ValueError('invalid budget')
    qs = tuple((cost, tuple(tuple(map(F, row)) for row in rows)) for cost, rows in queries)
    for cost, rows in qs:
        if type(cost) is not int or cost < 1 or not rows or any(len(r) != len(w) for r in rows):
            raise ValueError('invalid query shape or cost')
        if any(x < 0 for row in rows for x in row) or any(sum(r[i] for r in rows) != 1 for i in range(len(w))):
            raise ValueError('invalid likelihood')
    return w, qs


def canonical(groups):
    """Canonical tuples (per-individual mass, remaining column signature, count)."""
    counts = Counter()
    for mass, sig, count in groups:
        if mass > 0 and count > 0:
            counts[mass, sig] += count
    return tuple((mass, sig, n) for (mass, sig), n in sorted(counts.items()))


def initial_groups(w, qs):
    return canonical((wi, tuple(tuple(row[i] for row in rows) for _, rows in qs), 1)
                     for i, wi in enumerate(w))


def top(groups, budget):
    value = F(0)
    for mass, _, count in reversed(groups):
        n = min(budget, count)
        value += mass*n
        budget -= n
        if budget == 0:
            break
    return value


class Quotient:
    """Single winner; conditionally independent once-only finite queries; perfect guesses."""
    def __init__(self, weights, queries, budget, dynamic=True):
        w, qs = validate(weights, queries, budget)
        self.total = sum(w)
        self.dynamic = dynamic
        self.start = (initial_groups(w, qs), tuple(c for c, _ in qs), budget)
        self.value = lru_cache(None)(self._value)

    def _value(self, groups, costs, budget):
        if budget == 0 or not groups:
            return F(0)
        total = sum(m*n for m, _, n in groups)
        best = top(groups, budget)
        if best == total or not any(c < budget for c in costs):
            return best
        for i, (mass, sig, n) in enumerate(groups):
            nxt = canonical(groups[:i] + ((mass, sig, n-1),) + groups[i+1:])
            best = max(best, mass + self.value(nxt, costs, budget-1))
        for j, cost in enumerate(costs):
            if cost >= budget:
                continue
            # Constant likelihood columns are pure noise and can be omitted.
            if all(sig[j] == groups[0][1][j] for _, sig, _ in groups):
                continue
            newcost = costs[:j] + costs[j+1:] if self.dynamic else costs[:j]+(budget+1,)+costs[j+1:]
            score = F(0)
            for y in range(len(groups[0][1][j])):
                nxt = canonical((m*sig[j][y], sig[:j]+sig[j+1:] if self.dynamic else sig, n)
                                for m, sig, n in groups)
                score += self.value(nxt, newcost, budget-cost)
            best = max(best, score)
        return best

    def solve(self):
        return self.value(*self.start)/self.total


def tv(p, q):
    return sum(abs(a-b) for a,b in zip(p,q))/2


def perturbation_bound(weights, queries, other_weights, other_queries, budget):
    """Coupling bound for optimal closure and all common legal policies.

    Same labels, query outcome alphabets, costs and budget in both environments.
    Returns (closure discrepancy bound, upper bound on approximate-policy regret).
    Policies omit queries whose cost leaves no unit for any guess.
    """
    w, qs = validate(weights, queries, budget)
    z, rs = validate(other_weights, other_queries, budget)
    if len(w)!=len(z) or len(qs)!=len(rs):
        raise ValueError('incompatible environments')
    if any(c!=d or len(a)!=len(b) for (c,a),(d,b) in zip(qs,rs)):
        raise ValueError('incompatible query alphabets or costs')
    if budget == 0:
        return F(0), F(0)
    prior = tv(tuple(x/sum(w) for x in w),tuple(x/sum(z) for x in z))
    eps = [max(tv(tuple(row[i] for row in a),tuple(row[i] for row in b)) for i in range(len(w)))
           for (_,a),(_,b) in zip(qs,rs)]
    # Worst survival product over feasible sets of queries, reserving one guess.
    # One-dimensional exact 0/1 multiplicative knapsack; no query reuse.
    dp = [F(1)]*budget
    for (cost,_), error in zip(qs,eps):
        for b in range(budget-1,cost-1,-1):
            dp[b] = min(dp[b], (1-error)*dp[b-cost])
    bound = 1-(1-prior)*dp[-1]
    return bound,min(F(1),2*bound)


def approximate_policy_value(weights, queries, other_weights, other_queries, budget):
    """Exact evaluation in the true environment of an approximate-optimal policy.

    Expanded reference for small roots. In impossible approximate histories, choose
    a fixed legal first remaining guess. Ties use deterministic action order.
    """
    perturbation_bound(weights,queries,other_weights,other_queries,budget)
    w, qs = validate(weights,queries,budget)
    z, rs = validate(other_weights,other_queries,budget)
    n=len(w)

    def actions(alive,available,b):
        if not alive or b<=0:
            return ()
        return tuple(('g',i) for i in alive)+tuple(('q',j) for j in available if rs[j][0]<b)

    @lru_cache(None)
    def opt(a,alive,available,b):
        best = F(0); choice = None
        for k,i in actions(alive,available,b):
            if k=='g':
                nxt=tuple(j for j in alive if j!=i)
                v=a[i]+opt(a[:i]+(F(0),)+a[i+1:],nxt,available,b-1)[0]
            else:
                cost,rows=rs[i];nxt=tuple(j for j in available if j!=i)
                v=sum(opt(tuple(x*y for x,y in zip(a,row)),alive,nxt,b-cost)[0] for row in rows)
            if choice is None or v>best:
                best,choice=v,(k,i)
        return best,choice

    @lru_cache(None)
    def execute(t,a,alive,available,b):
        _, act=opt(a,alive,available,b)
        if act is None or not any(t):return F(0)
        k,i=act
        if k=='g':
            nxt=tuple(j for j in alive if j!=i)
            return t[i]+execute(t[:i]+(F(0),)+t[i+1:],a[:i]+(F(0),)+a[i+1:],nxt,available,b-1)
        cost,rows=qs[i];nxt=tuple(j for j in available if j!=i)
        return sum(execute(tuple(x*y for x,y in zip(t,row)),tuple(x*y for x,y in zip(a,arow)),alive,nxt,b-cost)
                   for row,arow in zip(rows,rs[i][1]))

    alive=tuple(range(n));avail=tuple(range(len(qs)))
    return execute(w,z,alive,avail,budget)/sum(w),opt(z,alive,avail,budget)[0]/sum(z)
