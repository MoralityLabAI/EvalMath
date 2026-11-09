"""Finite exact examples and boundary checks for the four UG game-space proposals."""
from fractions import Fraction
from itertools import product

import pytest

from spiral_ln.unique_games_topology import Edge, TranslationGame, optimum_by_labels
from spiral_ln.game_space_conjectures import (
    anf_degree, degree_probe_min_detection, double_covers,
    edited_holonomy_degree, first_frustrated_cycles, ground_moment,
    holonomy_image, latent_stability, mean_twisted_gap,
    minimal_double_cover_frustration, moment_obstruction_probe,
    regular_holonomy_cover, signed_laplacian_gap, spectral_cosystolic_probe,
)

C4 = ((0, 2), (0, 3), (1, 2), (1, 3))
K23 = ((0, 2), (1, 2), (0, 3), (1, 3), (0, 4), (1, 4))


def game(n, bits, pairs, shifts):
    return TranslationGame(n, bits, tuple(
        Edge(u, v, s) for (u, v), s in zip(pairs, shifts)
    ))


def test_spectral_twisted_gap_and_universal_upper_bound():
    for bits in (1, 2):
        for shifts in product(range(1 << bits), repeat=4):
            g = game(4, bits, C4, shifts)
            probe = spectral_cosystolic_probe(g)
            assert probe["upper_bound_verified"]
            assert probe["twisted_gap_mean"] >= 0
            if probe["cosystolic_fraction"] == 0:
                assert probe["twisted_gap_mean"] < 1e-9
            else:
                assert probe["twisted_gap_mean"] > 0


def test_spectral_gauge_invariance_and_reject_isolated():
    g = game(5, 2, K23, (0, 1, 2, 3, 1, 3))
    p = (3, 1, 2, 0, 3)
    twisted = game(5, 2, K23, tuple(
        c ^ p[u] ^ p[v] for (u, v), c in zip(K23, (0, 1, 2, 3, 1, 3))))
    assert abs(mean_twisted_gap(g) - mean_twisted_gap(twisted)) < 1e-10
    with pytest.raises(ValueError):
        signed_laplacian_gap(game(3, 1, ((0, 1),), (0,)), 1)
    with pytest.raises(ValueError):
        signed_laplacian_gap(game(1, 1, ((0, 0),), (1,)), 1)


def test_shortest_obstruction_moment_formula_all_C4_F2_squared():
    for shifts in product(range(4), repeat=4):
        g = game(4, 2, C4, shifts)
        report = moment_obstruction_probe(g)
        if shifts[0] ^ shifts[1] ^ shifts[2] ^ shifts[3]:
            assert report["first_frustrated_length"] == 4
            assert report["cycle_count"] == 1
            assert report["low_moments_equal"]
            assert report["first_coefficient_equal"]
            assert report["coefficient"] == str(Fraction(-24, 4**4 * 4**3))
        else:
            assert report["all_matching"]


def test_first_obstruction_handles_loops_parallel_edges_triangles():
    cases = (
        (game(1, 1, ((0, 0),), (1,)), 1),
        (game(2, 1, ((0, 1), (0, 1)), (0, 1)), 2),
        (game(3, 1, ((0, 1), (1, 2), (2, 0)), (0, 0, 1)), 3),
    )
    for g, length in cases:
        assert first_frustrated_cycles(g) == (length, 1)
        rep = moment_obstruction_probe(g)
        assert rep["first_frustrated_length"] == length
        assert rep["first_coefficient_equal"]
        assert rep["low_moments_equal"]


def test_partition_moments_not_just_satisfiability():
    flat = game(4, 1, C4, (0, 0, 0, 0))
    frustrated = game(4, 1, C4, (0, 0, 0, 1))
    assert ground_moment(flat, 3) == ground_moment(frustrated, 3)
    assert ground_moment(flat, 4) != ground_moment(frustrated, 4)


def test_anf_degree_and_polynomial_probe_barrier():
    quad = tuple((x & 1) and ((x >> 1) & 1) for x in range(8))
    quad = tuple(int(x) for x in quad)
    assert anf_degree(quad) == 2
    assert anf_degree((0,) * 8) == -1
    assert anf_degree(tuple(x.bit_count() % 2 for x in range(8))) == 1
    noise = ((1, 1), (1, 2), (0, 3), (0, 4))
    p = latent_stability(quad, noise)
    min_linear, _ = degree_probe_min_detection(3, noise, degree=1)
    min_quadratic, witness = degree_probe_min_detection(3, noise, degree=2)
    assert 0 <= min_quadratic <= p <= 1
    assert min_quadratic <= min_linear
    assert isinstance(witness, tuple)


def test_latent_validation():
    with pytest.raises(ValueError):
        anf_degree((0, 1, 0))
    with pytest.raises(ValueError):
        latent_stability((0, 1), ())
    with pytest.raises(ValueError):
        degree_probe_min_detection(4, ((0, 0),), 1)


def test_exact_holonomy_cover_rank_one_c4():
    g = game(4, 2, C4, (0, 0, 0, 1))
    assert holonomy_image(g) == (0, 1)
    cover, labels = regular_holonomy_cover(g)
    assert cover.vertices == 8
    assert len(cover.edges) == 8
    assert all((labels[e.u] ^ labels[e.v]) == e.shift for e in cover.edges)
    assert optimum_by_labels(cover)[0] == 1
    assert len(double_covers(g)) == 1
    assert minimal_double_cover_frustration(g) == 0
    assert edited_holonomy_degree(g, 0) == 2
    assert edited_holonomy_degree(g, 1) == 1


def test_exact_holonomy_cover_rank_two_K23():
    g = game(5, 2, K23, (0, 0, 0, 1, 0, 2))
    assert holonomy_image(g) == (0, 1, 2, 3)
    cover, labels = regular_holonomy_cover(g)
    assert cover.vertices == 20
    assert len(cover.edges) == 24
    assert all((labels[e.u] ^ labels[e.v]) == e.shift for e in cover.edges)
    assert len(double_covers(g)) == 3
    assert minimal_double_cover_frustration(g) > 0
    assert edited_holonomy_degree(g, 0) == 4
    assert edited_holonomy_degree(g, 1) == 2


def test_cover_rejects_disconnected_base():
    with pytest.raises(ValueError):
        regular_holonomy_cover(game(3, 1, ((0, 1),), (1,)))
