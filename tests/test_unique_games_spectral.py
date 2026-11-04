"""UG-FID-02: independent spectral oracle and exact syndrome enumeration."""
from fractions import Fraction
from itertools import product

import pytest

from spiral_ln.unique_games_topology import (
    Edge, TranslationGame, minimum_bad_edges, optimum_by_labels,
)
from spiral_ln.unique_games_spectral import (
    curvature, diagonal_operator_norm, frustration_ground_energy,
    gap_threshold, minimum_curvature_repair, satisfaction_spectrum,
)


C4 = ((0, 2), (0, 3), (1, 2), (1, 3))


def cycle(shifts):
    return TranslationGame(4, 2, tuple(
        Edge(u, v, c) for (u, v), c in zip(C4, shifts)
    ))


def test_frustrated_four_cycle_exact_eigenspaces():
    g = cycle((0, 0, 0, 1))
    spectrum = satisfaction_spectrum(g)
    assert len(spectrum) == 4 ** 4
    assert set(spectrum) <= {Fraction(1, 4), Fraction(3, 4)}
    assert diagonal_operator_norm(g) == Fraction(3, 4)
    assert frustration_ground_energy(g) == Fraction(1, 4)
    assert minimum_curvature_repair(g)[0] == 1


def test_all_four_cycle_shifts_spectral_holonomy_and_block_weight():
    for shifts in product(range(4), repeat=4):
        g = cycle(shifts)
        val, _ = optimum_by_labels(g)
        norm = diagonal_operator_norm(g)
        weight, correction = minimum_curvature_repair(g)
        assert val == norm == 1 - frustration_ground_energy(g)
        assert weight == minimum_bad_edges(g)[0]
        assert Fraction(weight, len(g.edges)) == 1 - val
        assert curvature(g, correction) == curvature(g, shifts)
        assert weight == sum(x != 0 for x in correction)


def test_parallel_edges_self_loops_and_empty_graph():
    games = (
        TranslationGame(2, 1, (Edge(0, 1, 0), Edge(0, 1, 1))),
        TranslationGame(2, 2, (Edge(0, 0, 3),)),
        TranslationGame(3, 2, ()),
    )
    for g in games:
        val, _ = optimum_by_labels(g)
        assert diagonal_operator_norm(g) == val
        assert frustration_ground_energy(g) == 1 - val
        assert minimum_curvature_repair(g)[0] == minimum_bad_edges(g)[0]


def test_curvature_input_mutations_are_rejected():
    g = cycle((0, 0, 0, 1))
    with pytest.raises(ValueError):
        curvature(g, (0,))
    with pytest.raises(ValueError):
        curvature(g, (0, 0, 0, 4))


def test_gap_threshold_exact_and_adversarial_limits():
    eps, delta, tau = Fraction(1, 10), Fraction(1, 10), Fraction(1, 10)
    threshold = gap_threshold(eps, delta, tau)
    assert delta + tau < threshold < 1 - eps - tau
    with pytest.raises(ValueError):
        gap_threshold(Fraction(1, 3), Fraction(1, 3), Fraction(1, 6))
    with pytest.raises(ValueError):
        gap_threshold(0, delta, tau)
