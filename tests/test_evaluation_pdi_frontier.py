from fractions import Fraction as F
import pytest
from spiral_ln.evaluation_pdi import product_prior
from spiral_ln.evaluation_pdi_frontier import (accepted_versions, at_risk, frontier,
                                               pareto, selection_revocation_witness)
from spiral_ln.evaluation_pdi_noisy import optimal_audit


def witness():
    return (product_prior([F(1, 2)]*3), [(2, (3,)), (1, (4,))],
            [(i, F(9, 10), F(1, 10), 1) for i in range(3)], 2)


def test_frontier_witness():
    args = witness()
    fixed = frontier(*args, adaptive=False)
    adaptive = frontier(*args)
    assert fixed == ((0, 0), (F(1, 40), F(9, 40)), (F(1, 20), F(9, 20)))
    assert adaptive == fixed + ((F(3, 25), F(63, 100)),)
    assert at_risk(adaptive, F(3, 40), randomized=False)[0] == (F(1, 20), F(9, 20))
    point, mix = at_risk(adaptive, F(3, 40))
    assert point == (F(3, 40), F(18, 35))
    assert tuple(w for w, _ in mix) == (F(9, 14), F(5, 14))


def test_lagrangian_support():
    for adaptive in (False, True):
        args = witness()
        points = frontier(*args, adaptive=adaptive)
        for lam in (0, 1, 2, 3, 9, 10):
            assert max(t-lam*f for f, t in points) == optimal_audit(*args, lam, adaptive=adaptive)[0]


def test_single_gate_randomization_and_zero():
    points = frontier(product_prior([F(1, 2)]), [(1, (1,))], [(0, F(9, 10), F(1, 10), 1)], 1)
    assert at_risk(points, F(1, 40))[0] == (F(1, 40), F(9, 40))
    assert at_risk(points, F(1, 40), randomized=False)[0] == (0, 0)
    assert at_risk(points, 0)[0] == (0, 0)
    assert at_risk(points, 10)[0] == (F(1, 20), F(9, 20))


def test_pareto_and_exact_budget():
    assert pareto([(0, 0), (1, 0), (1, 2), (2, 2)]) == ((0, 0), (1, 2))
    with pytest.raises(ValueError):
        at_risk([(0, 0)], 0.1)


def test_revocation_version_eligibility():
    events = [(0, 'a', 1), (0, 'a', 0), (0, 'b', 1), (1, 'c', 1)]
    assert accepted_versions(events, {0: 'a', 1: 'c'}) == 2
    assert accepted_versions(events, {0: 'b', 1: 'c'}) == 3
    assert accepted_versions(events, {1: 'c'}) == 2
    assert accepted_versions(events, {0: 'unseen'}) == 0


def test_revocation_selection():
    retained, hidden = selection_revocation_witness()
    assert retained == {('left', 1): 0, ('right', 1): 1}
    assert hidden == {1: F(1, 2)}
