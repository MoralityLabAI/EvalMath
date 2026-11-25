from fractions import Fraction as F
from itertools import product
import pytest
from spiral_ln.evaluation_pdi import (audit_value, failure, independent_failure,
                                      intersection_bounds, product_prior, shared_failure)


def test_shared_oracle():
    for q, r, k in product((F(0), F(1, 5), F(1)), (F(0), F(1, 3), F(1)), range(1, 5)):
        p = product_prior([1-q]+[1-r]*k)
        assert failure(p, [1 | (2 << i) for i in range(k)]) == shared_failure(q, r, k)
        assert shared_failure(q, r, k) >= independent_failure(q, r, k)


def test_adaptive_witness():
    p = product_prior([F(1, 2)]*3)
    claims = [(2, (3,)), (1, (4,))]
    assert audit_value(p, claims, [1]*3, 2) == F(3, 4)
    assert audit_value(p, claims, [1]*3, 2, adaptive=False) == F(1, 2)
    assert audit_value(p, claims, [1]*3, 3) == 1


def test_correlated_support():
    p = (F(1, 2), F(0), F(0), F(1, 2))
    assert audit_value(p, [(1, (3,))], [1, 1], 1) == F(1, 2)
    assert audit_value(p, [(1, (3,))], [1, 1], 0) == 0


def test_bounds():
    assert intersection_bounds([F(3, 4), F(2, 3)]) == (F(5, 12), F(2, 3))
    assert intersection_bounds([F(1, 5)]*4) == (0, F(1, 5))


def test_invalid():
    with pytest.raises(ValueError):
        product_prior([0.5])
    with pytest.raises(ValueError):
        audit_value([F(1, 2)]*2, [(1, (2,))], [1], 1)
    with pytest.raises(ValueError):
        audit_value([F(1, 2)]*2, [(1, (1,))], [0], 1)
    with pytest.raises(ValueError):
        audit_value([F(1, 2)]*2, [(0.5, (1,))], [1], 1)
