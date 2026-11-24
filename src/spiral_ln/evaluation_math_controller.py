"""Exact finite Bayesian proof controller; deterministic costs, binary observations."""
from fractions import Fraction as F
from functools import lru_cache
from itertools import product


def model(rows, costs, prior):
    """rows[obligation][action][latent type], costs[obligation][action]."""
    rows = tuple(tuple(tuple(map(F, a)) for a in r) for r in rows)
    costs = tuple(tuple(r) for r in costs)
    prior = tuple(map(F, prior))
    if not prior or sum(prior) != 1 or min(prior) < 0:
        raise ValueError('invalid prior')
    if len(rows) != len(costs) or any(not r or len(r) != len(c) for r,c in zip(rows,costs)):
        raise ValueError('invalid action dimensions')
    if any(len(a) != len(prior) or any(not 0 <= p <= 1 for p in a) for r in rows for a in r):
        raise ValueError('invalid probabilities')
    if any(type(c) is not int or c <= 0 for r in costs for c in r):
        raise ValueError('costs must be positive integers')
    return rows, costs, prior


def bayes(rows, costs, prior, budget):
    rows,costs,prior = model(rows,costs,prior)
    if budget < 0:
        raise ValueError('negative budget')
    d = len(rows)
    @lru_cache(None)
    def solve(i,b,w):
        if i == d:
            return sum(w), None
        if not any(w):
            return F(0), None
        best, action = F(0), None
        for a,(p,c) in enumerate(zip(rows[i],costs[i])):
            if c > b:
                continue
            yes = tuple(x*y for x,y in zip(w,p))
            no = tuple(x*(1-y) for x,y in zip(w,p))
            value = solve(i+1,b-c,yes)[0]+solve(i,b-c,no)[0]
            if value > best:
                best,action = value,a
        return best, action
    return solve(0,budget,prior)[0], solve


def alpha_oracle(rows,costs,prior,budget):
    """Independent oracle: enumerate nondominated conditional-closure vectors."""
    rows,costs,prior = model(rows,costs,prior)
    z = len(prior)
    @lru_cache(None)
    def frontier(i,b):
        if i == len(rows):
            return ((F(1),)*z,)
        vecs = {(F(0),)*z}
        for p,c in zip(rows[i],costs[i]):
            if c <= b:
                for y,n in product(frontier(i+1,b-c),frontier(i,b-c)):
                    vecs.add(tuple(pj*yj+(1-pj)*nj for pj,yj,nj in zip(p,y,n)))
        return tuple(v for v in vecs if not any(v != u and all(x<=y for x,y in zip(v,u)) for u in vecs))
    return max(sum(x*y for x,y in zip(prior,v)) for v in frontier(0,budget))


def blind(rows,costs,prior,budget):
    """Optimal deterministic clock/progress policy; one shared table for all types."""
    rows,costs,prior = model(rows,costs,prior)
    if budget < 0:
        raise ValueError('negative budget')
    states = set()
    def visit(i,b):
        if i == len(rows) or (i,b) in states or not any(c<=b for c in costs[i]):
            return
        states.add((i,b))
        for c in costs[i]:
            if c<=b:
                visit(i,b-c)
                visit(i+1,b-c)
    visit(0,budget)
    states = sorted(states)
    options = [tuple(a for a,c in enumerate(costs[i]) if c<=b) for i,b in states]
    best = F(0)
    for acts in product(*options):
        policy = dict(zip(states,acts))
        @lru_cache(None)
        def value(i,b,z):
            if i == len(rows):
                return F(1)
            if (i,b) not in policy:
                return F(0)
            a=policy[i,b]; c=costs[i][a]; p=rows[i][a][z]
            return p*value(i+1,b-c,z)+(1-p)*value(i,b-c,z)
        best = max(best,sum(w*value(0,budget,z) for z,w in enumerate(prior)))
    return best


def fixture(retrieval_cost=2):
    a,b,r=(F(3,4),F(1,4)),(F(1,4),F(3,4)),(F(3,4),F(3,4))
    return ((a,b,r),(a,b,r)), ((1,1,retrieval_cost),(1,1,retrieval_cost+1)), (F(1,2),F(1,2))
