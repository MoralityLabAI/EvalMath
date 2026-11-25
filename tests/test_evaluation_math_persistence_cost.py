from fractions import Fraction as F
from spiral_ln.evaluation_math_persistence_cost import (
    tail, quota, static, mix_value, extreme_mixtures, robust_gap, break_even)

S = (F(1,4), F(1,2), F(3,4))
M = F(1,2)


def test_correlation_reverses_sign():
    mix = ((S[0], M), (S[2], M))
    assert mix_value(mix, lambda p: tail(4, 4, p))-tail(4, 4, M) == F(25,256)
    assert mix_value(mix, lambda p: tail(4, 8, p))-tail(4, 8, M) == -F(6125,65536)


def test_robust_charge():
    assert robust_gap(4, 8, 2, S, M) == F(7,256)
    assert robust_gap(4, 8, 3, S, M) == -F(33,256)
    assert break_even(4, 8, S, M, strict=True) == 2
    assert break_even(4, 12, S, M, strict=True) == 4


def test_degenerate_and_boundary():
    assert list(extreme_mixtures([0, 1], M)) == [((F(0), M), (F(1), M))]
    assert robust_gap(4, 8, 2, [0, 1], M) == 0
    assert break_even(4, 8, [0, 1], M, strict=True) is None
    assert quota(4, 2) == (1, 1, 0, 0)
    assert static(quota(4, 2), M) == 0
    assert tail(4, 2, M) == 0
