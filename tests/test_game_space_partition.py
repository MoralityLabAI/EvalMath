"""Exact finite gain-graph partition and a non-expander spectral negative control."""
from fractions import Fraction
from itertools import product

import pytest

from spiral_ln.unique_games_topology import Edge, TranslationGame
from spiral_ln.game_space_conjectures import first_frustrated_cycles, mean_twisted_gap
from spiral_ln.game_space_partition import (
    balanced_subgraph_coefficients, flat_subgraph_coefficients,
    direct_partition, polynomial_value, balanced_random_cluster_probability,
    annealed_coefficients, frustrated_cycle_closed_form,
    flat_cycle_closed_form, cycle_spectral_closed_form,
)

C4 = ((0, 2), (0, 3), (1, 2), (1, 3))
K23 = ((0, 2), (1, 2), (0, 3), (1, 3), (0, 4), (1, 4))


def game(n, bits, pairs, shifts):
    return TranslationGame(n, bits, tuple(Edge(u, v, c) for (u, v), c in zip(pairs, shifts)))


def cycle(n, bits=2):
    return game(n, bits, tuple((i, (i+1) % n) for i in range(n)), (1,) + (0,) * (n-1))


def test_all_256_C4_exact_partition_equality():
    for shifts in product(range(4), repeat=4):
        g = game(4, 2, C4, shifts)
        coeffs = balanced_subgraph_coefficients(g)
        for z in (0, 1, 3):
            assert polynomial_value(coeffs, z) == direct_partition(g, z)


def test_K23_nontrivial_holonomy_coeffs_against_label_enumeration():
    for shifts in ((0,0,0,1,0,2), (0,0,0,0,0,0), (1,2,3,1,0,2)):
        g = game(5, 2, K23, shifts)
        coeffs = balanced_subgraph_coefficients(g)
        for z in (1, 4):
            assert polynomial_value(coeffs, z) == direct_partition(g, z)


def test_first_frustrated_coefficient_matches_girth_formula():
    for shifts in product(range(4), repeat=4):
        g = game(4, 2, C4, shifts)
        flat = flat_subgraph_coefficients(g)
        coeffs = balanced_subgraph_coefficients(g)
        ell, count = first_frustrated_cycles(g)
        if ell is None:
            assert coeffs == flat
        else:
            assert coeffs[:ell] == flat[:ell]
            assert coeffs[ell] - flat[ell] == -Fraction(count, 4 ** (ell - 1))


def test_cycle_closed_formula_including_loop_and_double_edge():
    for n in (1, 2, 3, 4, 6):
        g = cycle(n)
        flat = game(n, 2, tuple((i, (i+1) % n) for i in range(n)), (0,) * n)
        for z in (0, 1, 3, 10):
            assert polynomial_value(balanced_subgraph_coefficients(g), z) == frustrated_cycle_closed_form(n, 4, z)
            assert polynomial_value(balanced_subgraph_coefficients(flat), z) == flat_cycle_closed_form(n, 4, z)
            assert flat_cycle_closed_form(n, 4, z) - frustrated_cycle_closed_form(n, 4, z) == Fraction(z**n, 4**(n - 1))


def test_annealed_edges_factorize_independently():
    pairs = tuple((i, (i+1) % 4) for i in range(4))
    mean = [Fraction(0)] * 5
    for shifts in product(range(4), repeat=4):
        coeffs = balanced_subgraph_coefficients(game(4, 2, pairs, shifts))
        mean = [a + b / 256 for a, b in zip(mean, coeffs)]
    assert tuple(mean) == annealed_coefficients(game(4, 2, pairs, (0,)*4))


def test_balanced_probability_is_flat_random_cluster_event():
    g = cycle(4)
    for z in (0, 1, 3, 10):
        t = Fraction(z, 4+z)
        expected = (1-t**4) / (1+3*t**4)
        got = balanced_random_cluster_probability(g, z)
        assert got == expected
        assert 0 <= got <= 1
    with pytest.raises(ValueError):
        balanced_random_cluster_probability(g, -1)


def test_bad_loop_forces_constant_missing_factor():
    bad = game(1, 1, ((0, 0),), (1,))
    assert balanced_subgraph_coefficients(bad) == (1, 0)
    assert flat_subgraph_coefficients(bad) == (1, 1)
    assert balanced_random_cluster_probability(bad, 3) == Fraction(1, 4)


def test_nonexpander_cycle_analytic_spectral_ratio_tends_to_zero():
    for n in (4, 6, 8, 12, 16, 24):
        g = cycle(n)
        predicted = cycle_spectral_closed_form(n, 4)
        observed = mean_twisted_gap(g)
        assert abs(predicted - observed) < 1e-10
        assert 0 < predicted * n < 4 / n  # ratio Lambda/phi; phi=1/n
    assert cycle_spectral_closed_form(24, 4) * 24 < cycle_spectral_closed_form(4, 4) * 4
