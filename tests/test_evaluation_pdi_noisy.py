from fractions import Fraction as F
from itertools import product
from spiral_ln.evaluation_pdi import product_prior
from spiral_ln.evaluation_pdi_noisy import (amplification_cap, false_weights, incidence,
                                            optimal_audit, selection_risk)


def test_incidence_bound():
    claims = [(2, (3, 4)), (3, (1,)), (1, (6,))]
    costs = [1, 2, 3]
    assert incidence(claims, 3) == (5, 3, 3)
    assert amplification_cap(claims, costs) == 5
    for world, accepted in product(range(8), repeat=2):
        f, x = false_weights(world, accepted, claims, costs)
        assert f <= 5*x


def test_sharp_shared_gate():
    claims = [(1, (1,))]*8
    assert false_weights(0, 1, claims, [1]) == (8, 1)
    assert amplification_cap(claims, [1]) == 8


def test_selection():
    assert selection_risk(F(1, 20), 2) == F(39, 400)
    assert selection_risk(F(1, 20), 0) == 0


def test_single_noisy_gate():
    p = product_prior([F(1, 2)])
    a = [(0, F(9, 10), F(1, 10), 1)]
    assert optimal_audit(p, [(1, (1,))], a, 1, 2) == (F(7, 20), F(9, 20), F(1, 20))
    assert optimal_audit(p, [(1, (1,))], a, 1, 9) == (0, 0, 0)


def test_adaptive_perfect_and_noisy():
    p = product_prior([F(1, 2)]*3)
    claims = [(2, (3,)), (1, (4,))]
    a = [(i, 1, 0, 1) for i in range(3)]
    assert optimal_audit(p, claims, a, 2, 1) == (F(3, 4), F(3, 4), 0)
    a = [(i, F(9, 10), F(1, 10), 1) for i in range(3)]
    assert optimal_audit(p, claims, a, 2, 1)[0] > optimal_audit(p, claims, a, 2, 1, adaptive=False)[0]
