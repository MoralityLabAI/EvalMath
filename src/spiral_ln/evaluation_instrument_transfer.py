"""MIT-01: exact finite search with costly, fallible instruments."""
from fractions import Fraction as F
from functools import lru_cache
from itertools import combinations


def shortlist(n, k, q, budget, cost=0):
    """Posterior mass captured by optimal search and by blind shortlist priority.

    One winner, exchangeable within each group, all guesses cost one, no repeats.
    The instrument has already been acquired at cost; outside guesses are legal.
    """
    q = F(q)
    if not (0 < k < n and 0 <= q <= 1 and 0 <= cost <= budget):
        raise ValueError("invalid shortlist parameters")
    r = min(n, budget - cost)
    a, b = q / k, (1 - q) / (n - k)
    lo, hi = max(0, r - (n - k)), min(k, r)
    priority = hi * a + (r - hi) * b
    complement = lo * a + (r - lo) * b
    return max(priority, complement), priority, F(min(n, budget), n)


def optimal_search(weights, queries, budget):
    """Exact success probability for a single hidden winner.

    Each query is (positive integer cost, tuple of outcome likelihood rows).
    Columns index worlds; each column sums to 1. Queries are conditionally
    independent given the winner, and can be used at most once. Failed guesses
    remove the guessed world; guesses cost one. A hit ends the search.
    """
    w = tuple(map(F, weights))
    if not w or any(x < 0 for x in w) or sum(w) <= 0 or budget < 0:
        raise ValueError("invalid prior or budget")
    qs = tuple((c, tuple(tuple(map(F, row)) for row in rows)) for c, rows in queries)
    n = len(w)
    for c, rows in qs:
        if not isinstance(c, int) or c < 1 or not rows or any(len(row) != n for row in rows):
            raise ValueError("invalid query shape or cost")
        if any(x < 0 for row in rows for x in row) or any(sum(row[i] for row in rows) != 1 for i in range(n)):
            raise ValueError("invalid likelihood")

    @lru_cache(None)
    def value(mass, available, b):
        if b == 0 or not any(mass):
            return F(0)
        best = sum(sorted(mass, reverse=True)[:b])
        for i, wi in enumerate(mass):
            if wi:
                miss = mass[:i] + (F(0),) + mass[i + 1:]
                best = max(best, wi + value(miss, available, b - 1))
        for j in available:
            c, rows = qs[j]
            if c <= b:
                rest = tuple(i for i in available if i != j)
                gain = sum(value(tuple(x * y for x, y in zip(mass, row)), rest, b - c) for row in rows)
                best = max(best, gain)
        return best

    return value(w, tuple(range(len(qs))), budget) / sum(w)


def binary_query(mask, cost=1):
    """Convert a deterministic membership mask into a query."""
    yes = tuple(F(int(x)) for x in mask)
    return cost, (yes, tuple(1 - x for x in yes))


def fixed_prefix(weights, masks, budget):
    """Best subset of unit-cost deterministic queries bought before guesses."""
    w = tuple(map(F, weights))
    masks = tuple(tuple(m) for m in masks)
    best = F(0)
    for size in range(min(budget, len(masks)) + 1):
        for chosen in combinations(masks, size):
            cells = {}
            for i, wi in enumerate(w):
                signature = tuple(m[i] for m in chosen)
                cells.setdefault(signature, []).append(wi)
            score = sum(sum(sorted(cell, reverse=True)[:budget-size]) for cell in cells.values())
            best = max(best, score / sum(w))
    return best
