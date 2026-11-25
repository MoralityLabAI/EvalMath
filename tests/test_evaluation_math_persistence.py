from fractions import Fraction as F
from spiral_ln.evaluation_math_persistence import (persistent, exhaustive, homogeneous,
                                                   fixed_best, reset)


def test_equal_loss():
    assert persistent((F(1,2),)*2, 3) == F(1,2)
    assert persistent((1, F(1,4)), 3) == F(7,16)


def test_matched_budget():
    ps = (F(1,2),)*4
    assert persistent(ps, 8) == homogeneous(4, 8, F(1,2)) == F(163,256)
    assert fixed_best(ps, 8) == F(81,256)
    assert reset(4, 8, F(1,2)) < fixed_best(ps, 8)


def test_boundaries():
    assert persistent((), 0) == reset(0, 0, 0) == 1
    assert persistent((1,1), 1) == 0
    assert persistent((1,1), 2) == 1
    assert persistent((0,1), 5) == 0
    assert exhaustive((0,1), 5) == 0
    assert fixed_best((1,1), 1) == 0
