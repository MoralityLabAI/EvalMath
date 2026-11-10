"""Exact finite tests for RHC-01."""
from fractions import Fraction as F
from itertools import product

import pytest

from spiral_ln.evaluation_reward_hacking_bootstrap import (
    chain_boundary, detector_certificate, distribution, dual_certificate, expected,
    finite_witness, gradient, optimal_detector, path_integral, pushforward,
    total_variation, SAFE_PATH, HACK_PATH,
)


def test_primal_dual_exact_and_unique():
    a = F(1, 4)
    p = (F(1, 2), F(1, 4), F(1, 4))
    qs = ((F(0), F(1), F(0)), (F(0), F(0), F(1)))
    optimum = optimal_detector(p, qs, a)
    assert optimum["value"] == F(1, 2)
    assert optimum["detector"] == (F(0), F(1, 2), F(1, 2))
    dual = dual_certificate(p, qs, a, (F(1, 2), F(1, 2)), F(2))
    assert dual["upper_bound"] == optimum["value"]
    assert dual["excess"] == (F(0), F(0), F(0))


@pytest.mark.parametrize("alpha,expected_value", [
    (F(0), F(0)), (F(1, 8), F(1, 4)), (F(1, 4), F(1, 2)),
    (F(3, 8), F(3, 4)), (F(1, 2), F(1)), (F(1), F(1)),
])
def test_budget_curve(alpha, expected_value):
    p = (F(1, 2), F(1, 4), F(1, 4))
    qs = ((F(0), F(1), F(0)), (F(0), F(0), F(1)))
    assert optimal_detector(p, qs, alpha)["value"] == expected_value


def test_observation_blind_mixture():
    p = (F(1, 2), F(1, 2))
    qs = ((F(1), F(0)), (F(0), F(1)))
    for alpha in (F(0), F(1, 8), F(1, 2), F(1)):
        primal = optimal_detector(p, qs, alpha)
        dual = dual_certificate(p, qs, alpha, (F(1, 2), F(1, 2)), F(1))
        assert primal["value"] == dual["upper_bound"] == alpha
        assert primal["detector"] == (alpha, alpha) or alpha == 1


def test_data_processing_refinement_cannot_hurt():
    # Two latent trajectories have exactly the same coarse report.
    safe = (F(1), F(0))
    attack = (F(0), F(1))
    for alpha in (F(0), F(1, 4), F(3, 4), F(1)):
        coarse_p = pushforward(safe, (0, 0), 1)
        coarse_q = pushforward(attack, (0, 0), 1)
        fine_p = pushforward(safe, (0, 1), 2)
        fine_q = pushforward(attack, (0, 1), 2)
        coarse = optimal_detector(coarse_p, (coarse_q,), alpha)["value"]
        fine = optimal_detector(fine_p, (fine_q,), alpha)["value"]
        assert coarse == alpha
        assert fine == 1
        assert fine >= coarse


def test_total_variation_mixture_ceiling():
    p = (F(1, 2), F(1, 4), F(1, 4))
    qs = ((F(0), F(1), F(0)), (F(0), F(0), F(1)))
    mixed = (F(0), F(1, 2), F(1, 2))
    alpha = F(1, 4)
    assert total_variation(p, mixed) == F(1, 2)
    assert optimal_detector(p, qs, alpha)["value"] <= alpha + total_variation(p, mixed)
    assert total_variation(p, p) == 0


def test_gradient_exactness_and_holonomy():
    cycle = (-1, -1, 1, 1)
    assert set(chain_boundary(cycle).values()) == {F(0)}
    for a, b, end in product((-2, 0, 3), (F(1, 3), F(4)), (F(-2), F(1, 2))):
        g = gradient({"s":F(0), "a":F(a), "b":F(b), "t":F(end)})
        assert path_integral(g, SAFE_PATH) == F(end)
        assert path_integral(g, HACK_PATH) == F(end)
        assert sum((F(x) * y for x, y in zip(cycle, g)), F(0)) == 0
    omega = (F(0), F(0), F(1), F(0))
    assert path_integral(omega, HACK_PATH) - path_integral(omega, SAFE_PATH) == 1
    assert sum((F(x) * y for x, y in zip(cycle, omega)), F(0)) == 1


def test_grid_oracle_lower_and_dual_upper():
    # Independent 1/4 grid, never used by the vertex oracle.
    p = (F(1, 2), F(1, 4), F(1, 4))
    qs = ((F(0), F(1), F(0)), (F(0), F(0), F(1)))
    alpha = F(1, 4)
    lp = optimal_detector(p, qs, alpha)["value"]
    for xs in product(range(5), repeat=3):
        f = tuple(F(x, 4) for x in xs)
        if expected(p, f) <= alpha:
            assert min(expected(q, f) for q in qs) <= lp


def test_invalid_probabilities_and_fpr():
    with pytest.raises(ValueError):
        distribution((F(1, 2), F(1, 3)))
    with pytest.raises(ValueError):
        optimal_detector((F(1),), (), F(1, 4))
    with pytest.raises(ValueError):
        optimal_detector((F(1),), ((F(1),),), F(-1))
    with pytest.raises(ValueError):
        detector_certificate((F(1),), ((F(1),),), F(1, 4), (F(1, 2),))
    with pytest.raises(ValueError):
        dual_certificate((F(1),), ((F(1),),), F(1, 4), (F(1),), F(-1))
    with pytest.raises(ValueError):
        pushforward((F(1),), (2,), 2)


def test_reproduction_receipt():
    witness = finite_witness()
    assert witness["all_passed"]
    assert all(witness["checks"].values())
