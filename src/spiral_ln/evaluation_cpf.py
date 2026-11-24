"""CPF-01: conditional error coupling and finite certified-rejection audits."""
from fractions import Fraction as F
from functools import lru_cache
from itertools import combinations


def probability(x):
    if not isinstance(x, (int, F)) or isinstance(x, bool) or not 0 <= x <= 1:
        raise ValueError("expected an exact probability")
    return F(x)


def bounds(a, b):
    a, b = map(probability, (a, b))
    return max(F(0), a + b - 1), min(a, b)


def coupling(a, b, r):
    a, b, r = map(probability, (a, b, r))
    lo, hi = bounds(a, b)
    if not lo <= r <= hi:
        raise ValueError("infeasible intersection")
    return r, a-r, b-r, 1-a-b+r  # both, A only, B only, neither


def residual(r, pass_given_both):
    return probability(r) * probability(pass_given_both)


def validate(weights, rows, budget):
    weights = tuple(map(probability, weights))
    rows = tuple(map(tuple, rows))
    if not rows or len(weights) != len(rows) or sum(weights) > 1:
        raise ValueError("invalid subprobability or empty world set")
    n = len(rows[0])
    if any(len(row) != n for row in rows) or any(
        not isinstance(x, str) or not x for row in rows for x in row
    ):
        raise ValueError("invalid outcome matrix")
    if not isinstance(budget, int) or isinstance(budget, bool) or not 0 <= budget <= n:
        raise ValueError("invalid budget")
    return weights, rows, n


def optimal(weights, rows, budget):
    """Unconditional surviving null mass; only a certified 'reject' blocks.

    Other outcomes may route subsequent audits. No repeat queries, at most budget.
    """
    weights, rows, n = validate(weights, rows, budget)

    @lru_cache(None)
    def dp(worlds, available, k):
        best = sum((weights[i] for i in worlds), F(0))
        if k == 0 or not worlds:
            return best
        for q in available:
            groups = {}
            for i in worlds:
                outcome = rows[i][q]
                if outcome != "reject":
                    groups.setdefault(outcome, []).append(i)
            remaining = tuple(j for j in available if j != q)
            cost = sum((dp(tuple(g), remaining, k-1) for g in groups.values()), F(0))
            best = min(best, cost)
        return best

    return dp(tuple(range(len(rows))), tuple(range(n)), budget)


def fixed(weights, rows, budget):
    weights, rows, n = validate(weights, rows, budget)
    return min(sum((w for w, row in zip(weights, rows)
                    if all(row[q] != "reject" for q in qs)), F(0))
               for qs in combinations(range(n), budget))


def example():
    # Shared false accepts; three detectable classes and an invisible class.
    return (F(1,100), F(1,100), F(1,100), F(1,50)), (
        ("L", "reject", "clear", "clear"),
        ("M", "clear", "reject", "clear"),
        ("R", "clear", "clear", "reject"),
        ("?", "clear", "clear", "clear"),
    )
