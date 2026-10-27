"""Adversarial small-case checks independent of the manuscript's reduction."""
from fractions import Fraction
from itertools import product

import pytest

from spiral_ln.unique_games_topology import (
    Edge, TranslationGame, betti_one, coboundary_zero, cosystolic_value,
    cycle_signature, finite_census, fundamental_cycle_packing_bound,
    minimum_bad_edges, normalized_shifts, optimum_by_labels,
)


C4 = ((0, 2), (0, 3), (1, 2), (1, 3))
K23 = ((0, 2), (1, 2), (0, 3), (1, 3), (0, 4), (1, 4))


def game(n, bits, pairs, shifts):
    return TranslationGame(n, bits, tuple(Edge(u, v, c) for (u, v), c in zip(pairs, shifts)))


def test_c4_frustrated_cycle_and_tree():
    bad = game(4, 1, C4, (0, 0, 0, 1))
    good = game(4, 1, C4, (0, 0, 0, 0))
    assert cycle_signature(bad)[0][1] == 1
    assert optimum_by_labels(bad)[0] == Fraction(3, 4)
    assert cosystolic_value(bad) == Fraction(3, 4)
    assert minimum_bad_edges(bad)[0] == 1
    assert betti_one(bad) == 1
    assert fundamental_cycle_packing_bound(bad) == 1
    assert coboundary_zero(good) and cosystolic_value(good) == 1


def test_gauge_transform_preserves_signature_and_optimum():
    original = game(5, 2, K23, (0, 1, 2, 3, 1, 3))
    p = (3, 1, 2, 0, 3)
    transformed = game(5, 2, K23, tuple(c ^ p[u] ^ p[v]
                                          for (u, v), c in zip(K23, (0, 1, 2, 3, 1, 3))))
    assert cycle_signature(original) == cycle_signature(transformed)
    assert normalized_shifts(original) == normalized_shifts(transformed)
    assert optimum_by_labels(original)[0] == optimum_by_labels(transformed)[0]


def test_cycle_rank_alone_does_not_determine_optimum():
    c6 = game(6, 1, ((0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)),
              (1, 0, 0, 0, 0, 0))
    c4 = game(4, 1, C4, (1, 0, 0, 0))
    assert betti_one(c4) == betti_one(c6) == 1
    assert optimum_by_labels(c4)[0] == Fraction(3, 4)
    assert optimum_by_labels(c6)[0] == Fraction(5, 6)


def test_k23_rank_two_holonomies_have_different_distance():
    one = game(5, 2, K23, (0, 0, 0, 1, 0, 1))
    two = game(5, 2, K23, (0, 0, 0, 1, 0, 2))
    assert betti_one(one) == betti_one(two) == 2
    assert minimum_bad_edges(one)[0] == 1
    assert minimum_bad_edges(two)[0] == 2
    assert optimum_by_labels(one)[0] == Fraction(5, 6)
    assert optimum_by_labels(two)[0] == Fraction(2, 3)


def test_isolated_vertices_empty_edges_loops_and_parallel_edges():
    empty = TranslationGame(3, 2, ())
    assert betti_one(empty) == 0 and coboundary_zero(empty)
    assert optimum_by_labels(empty)[0] == cosystolic_value(empty) == 1
    loop = TranslationGame(2, 2, (Edge(0, 0, 1),))
    assert betti_one(loop) == 1 and minimum_bad_edges(loop)[0] == 1
    assert optimum_by_labels(loop)[0] == 0
    parallel = TranslationGame(2, 1, (Edge(0, 1, 0), Edge(0, 1, 1)))
    assert minimum_bad_edges(parallel)[0] == 1
    assert optimum_by_labels(parallel)[0] == Fraction(1, 2)


def test_input_validation():
    with pytest.raises(ValueError):
        TranslationGame(0, 1, ())
    with pytest.raises(ValueError):
        TranslationGame(2, 0, ())
    with pytest.raises(ValueError):
        TranslationGame(2, 2, (Edge(0, 3, 0),))
    with pytest.raises(ValueError):
        TranslationGame(2, 2, (Edge(0, 1, 4),))


def test_all_c4_labels_gauge_invariance_and_block_hamming():
    for shifts in product(range(4), repeat=4):
        g = game(4, 2, C4, shifts)
        assert optimum_by_labels(g)[0] == cosystolic_value(g)
        assert len(cycle_signature(g)) == 1
        assert (cycle_signature(g)[0][1] == 0) == coboundary_zero(g)


def test_full_exhaustive_receipt_counts():
    report = finite_census()
    assert report["checks"] == 1001
    assert report["c4_F2_2"] == {"0": 64, "1": 192}
    assert report["k23_F2_2_gauge_classes"] == {"0": 1, "1": 9, "2": 6}
    assert report["all_signed_simple_K4_subgraphs"] == 729
