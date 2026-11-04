"""MP-02: finite experiment selection, exact SET COVER and adaptive oracle.

A baseline hidden hypothesis outputs zero to every test. Alternative i
outputs one on test e precisely when i is in the subset chosen by e.
Decision objective: distinguish baseline from every alternative with
zero errors and a worst-case limit on number of distinct tests.
"""
from functools import lru_cache
from itertools import combinations


def validate(n, masks):
    if type(n) is not int or n < 1:
        raise ValueError("positive number of alternatives required")
    target = (1 << n) - 1
    masks = tuple(masks)
    if any(type(mask) is not int or mask < 0 or mask > target for mask in masks):
        raise ValueError("experiment masks must be subsets of the alternatives")
    return masks


def min_cover_dp(n, masks):
    """Exact minimum cover via memoized uncovered-set DP, O(m 2^n) states."""
    masks = validate(n, masks)
    @lru_cache(None)
    def solve(missing):
        if missing == 0:
            return ()
        best = None
        for idx, mask in enumerate(masks):
            remainder = missing & ~mask
            if remainder == missing:
                continue
            suffix = solve(remainder)
            if suffix is None:
                continue
            candidate = (idx,) + suffix
            if best is None or (len(candidate), candidate) < (len(best), best):
                best = candidate
        return best
    return solve((1 << n) - 1)


def min_cover_bruteforce(n, masks):
    """Independent exhaustive subset oracle; avoids recursive DP."""
    masks = validate(n, masks)
    target = (1 << n) - 1
    for size in range(len(masks) + 1):
        for indices in combinations(range(len(masks)), size):
            covered = 0
            for idx in indices:
                covered |= masks[idx]
            if covered == target:
                return indices
    return None


def adaptive_minimax_depth(n, masks):
    """Independent belief-state minimax over arbitrary binary decision trees.

    Hidden hypothesis -1 denotes baseline, 0..n-1 the alternatives. The
    classifier must output baseline vs alternative with zero errors.
    """
    masks = validate(n, masks)
    @lru_cache(None)
    def solve(possible):
        if -1 not in possible or len(possible) == 1:
            return 0
        best = None
        for test in masks:
            yes = tuple(i for i in possible if i >= 0 and (test & (1 << i)))
            no = tuple(i for i in possible if i == -1 or not (test & (1 << i)))
            if not yes or not no:
                continue
            yes_cost, no_cost = solve(yes), solve(no)
            if yes_cost is None or no_cost is None:
                continue
            cost = 1 + max(yes_cost, no_cost)
            if best is None or cost < best:
                best = cost
        return best
    return solve((-1,) + tuple(range(n)))
