from fractions import Fraction as F
from itertools import combinations, product
from functools import lru_cache
import pytest
from spiral_ln.evaluation_instrument_transfer import shortlist, optimal_search, binary_query, fixed_prefix


def subset_oracle(weights, masks, budget):
    """Independent deterministic oracle: partition explicit possible worlds."""
    @lru_cache(None)
    def rec(worlds, remaining, b):
        if b == 0 or not worlds:
            return 0
        guesses = [weights[i] + rec(tuple(j for j in worlds if j != i), remaining, b-1) for i in worlds]
        queries = []
        for k in remaining:
            nxt = tuple(j for j in remaining if j != k)
            queries.append(sum(rec(tuple(i for i in worlds if masks[k][i] == bit), nxt, b-1) for bit in (0, 1)))
        return max(guesses + queries)
    return F(rec(tuple(range(len(weights))), tuple(range(len(masks))), budget), sum(weights))


def test_shortlist_exhaustive():
    for n in range(2, 9):
        for k in range(1, n):
            for j in range(9):
                q = F(j, 8)
                w = [q/k]*k + [(1-q)/(n-k)]*(n-k)
                for budget in range(n+2):
                    for cost in range(budget+1):
                        best, priority, base = shortlist(n,k,q,budget,cost)
                        r = min(n,budget-cost)
                        assert best == max(sum(w[i] for i in s) for s in combinations(range(n),r))
                        assert priority == sum(w[:r])
                        assert base == F(min(n,budget),n)


def test_break_even_and_anti_hint():
    assert shortlist(16,4,F(1,2),4,1) == (F(3,8),F(3,8),F(1,4))
    assert shortlist(16,4,F(1,3),4,1)[0] == F(1,4)
    assert shortlist(16,4,F(1,4),4,1)[0] == F(3,16)
    assert shortlist(16,4,0,4,1) == (F(1,4),F(0),F(1,4))


def test_adaptive_gap():
    masks = ((1,1,1,1,0,0,0,0), (1,1,0,0,0,0,0,0), (0,0,0,0,1,1,0,0))
    assert optimal_search([1]*8, [binary_query(m) for m in masks], 4) == 1
    assert fixed_prefix([1]*8, masks, 4) == F(3,4)


def test_dp_against_independent_oracle():
    masks = ((1,0,0),(0,1,0),(0,0,1))
    for w in product(range(3),repeat=3):
        if not sum(w):
            continue
        for size in range(4):
            for bank in combinations(masks,size):
                for b in range(5):
                    assert optimal_search(w, [binary_query(m) for m in bank], b) == subset_oracle(w,bank,b)


def test_noisy_query_and_validation():
    q = (1, ((F(3,4),F(1,4),F(1,4),F(1,4)), (F(1,4),F(3,4),F(3,4),F(3,4))))
    assert optimal_search([1]*4,[q],2) == F(1,2)  # optional query can be ignored
    assert optimal_search([1]*4,[],0) == 0
    with pytest.raises(ValueError):
        optimal_search([1,1],[(1,((1,0),))],1)
