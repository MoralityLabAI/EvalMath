from fractions import Fraction as F

import pytest

from spiral_ln.certificate_efficiency import CheckedCost, CostBounds, aggregate, interval


def test_exact_and_capped():
    assert interval(CostBounds('r', 'p', 4, 4), CheckedCost('r', 'p', 8)) == (F(1, 2), F(1, 2))
    assert interval(CostBounds('r', 'p', 4, 7), CheckedCost('r', 'p', 8)) == (F(1, 2), F(7, 8))
    assert interval(CostBounds('r', 'p', 4, 7), CheckedCost('r', 'p', 6)) == (F(2, 3), F(1))
    assert interval(CostBounds('r', 'p', 4), CheckedCost('r', 'p', 6)) == (F(2, 3), F(1))


def test_coverage():
    rows = [(CostBounds('a', 'p', 2, 2), CheckedCost('a', 'p', 4)),
            (CostBounds('b', 'p', 1), None)]
    assert aggregate(rows) == {'roots': 2, 'solved': 1, 'coverage': F(1, 2),
                               'efficiency_lower': F(1, 4), 'efficiency_upper': F(1, 4)}


@pytest.mark.parametrize('checked', [CheckedCost('x', 'p', 4), CheckedCost('r', 'q', 4),
                                    CheckedCost('r', 'p', 1), CheckedCost('r', 'p', True)])
def test_mismatch(checked):
    with pytest.raises(ValueError):
        interval(CostBounds('r', 'p', 2), checked)


def test_aggregate_rejections():
    with pytest.raises(ValueError):
        aggregate([])
    with pytest.raises(ValueError):
        aggregate([(CostBounds('a', 'p', 1), None)] * 2)
    with pytest.raises(ValueError):
        aggregate([(CostBounds('a', 'p', 1), None), (CostBounds('b', 'q', 1), None)])


@pytest.mark.parametrize('lower,upper', [(0, None), (2, 1), (True, None), (1, True)])
def test_bad_bounds(lower, upper):
    with pytest.raises(ValueError):
        CostBounds('r', 'p', lower, upper)


def test_exhaustive_intervals():
    for c in range(1, 21):
        for optimum in range(1, c + 1):
            for lower in range(1, optimum + 1):
                for upper in range(optimum, 22):
                    a, b = interval(CostBounds('r', 'p', lower, upper), CheckedCost('r', 'p', c))
                    assert 0 < a <= F(optimum, c) <= b <= 1
