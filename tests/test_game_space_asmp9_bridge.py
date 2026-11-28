"""ASMP-9 exact-query analogue and ASMP-2 low-order visibility controls."""
from collections import Counter
from fractions import Fraction
from itertools import combinations, product

import pytest

from spiral_ln.unique_games_topology import (
    Edge, TranslationGame, betti_one, cycle_signature,
    optimum_by_labels,
)
from spiral_ln.game_space_partition import balanced_subgraph_coefficients
from spiral_ln.game_space_asmp9_bridge import (
    canonical_connection, connected_components, gauge_witness, maxcut_count,
    partial_cycle_access_counterexample, quotient_coordinates,
    quotient_size_and_orbit_size, satisfaction_pattern_law,
)


C4 = ((0, 2), (0, 3), (1, 2), (1, 3))
K23 = ((0, 2), (1, 2), (0, 3), (1, 3), (0, 4), (1, 4))


def make_game(n, bits, pairs, shifts):
    return TranslationGame(n, bits, tuple(
        Edge(u, v, c) for (u, v), c in zip(pairs, shifts)
    ))


def test_all_C4_F2_squared_quotient_fibers_and_gauge_witness():
    sample = make_game(4, 2, C4, (0, 0, 0, 0))
    assert betti_one(sample) == 1
    assert quotient_size_and_orbit_size(sample) == (4, 64)
    histogram = Counter()
    by_class = {}
    for shifts in product(range(4), repeat=4):
        g = make_game(4, 2, C4, shifts)
        key = quotient_coordinates(g)
        histogram[key] += 1
        canonical = canonical_connection(g)
        witness = gauge_witness(g, canonical)
        assert witness is not None
        assert all(
            (e.shift ^ witness[e.u] ^ witness[e.v]) == f.shift
            for e, f in zip(g.edges, canonical.edges)
        )
        coeff = balanced_subgraph_coefficients(g)
        if key in by_class:
            assert by_class[key] == coeff
        else:
            by_class[key] = coeff
    assert len(histogram) == 4
    assert all(v == 64 for v in histogram.values())
    assert len(by_class) == 4


def test_K23_chord_query_access_is_sufficient_and_each_coordinate_necessary():
    base = make_game(5, 2, K23, (0,) * 6)
    assert connected_components(base) == 1
    assert quotient_size_and_orbit_size(base) == (16, 256)
    chords = tuple(i for i, h in cycle_signature(base))
    assert len(chords) == 2
    for observed in ((), (chords[0],), (chords[1],)):
        flat, bad = partial_cycle_access_counterexample(base, observed)
        assert tuple(dict(cycle_signature(flat))[i] for i in observed) == tuple(
            dict(cycle_signature(bad))[i] for i in observed
        )
        assert gauge_witness(flat, bad) is None
        assert optimum_by_labels(flat)[0] == 1
        assert optimum_by_labels(bad)[0] < 1
        assert balanced_subgraph_coefficients(flat) != balanced_subgraph_coefficients(bad)
    with pytest.raises(ValueError):
        partial_cycle_access_counterexample(base, chords)
    with pytest.raises(ValueError):
        partial_cycle_access_counterexample(base, (chords[0], chords[0]))


def test_connected_component_count_and_parallel_cycle():
    g = make_game(4, 1, ((0, 1), (0, 1)), (0, 1))
    assert connected_components(g) == 3
    assert betti_one(g) == 1
    assert quotient_size_and_orbit_size(g) == (2, 2)
    assert gauge_witness(g, make_game(4, 1, ((0, 1), (0, 1)), (0, 0))) is None


def test_mismatched_graph_is_rejected():
    a = make_game(4, 1, C4, (0,) * 4)
    b = make_game(4, 1, tuple(reversed(C4)), (0,) * 4)
    with pytest.raises(ValueError):
        gauge_witness(a, b)


def test_ASMP2_local_projection_law_agrees_below_holonomy_girth():
    for bits in (1, 2):
        flat = make_game(4, bits, C4, (0, 0, 0, 0))
        bad = make_game(4, bits, C4, (0, 0, 0, 1))
        for k in range(4):
            for queried in combinations(range(4), k):
                assert satisfaction_pattern_law(flat, queried) == (
                    satisfaction_pattern_law(bad, queried)
                )
        assert satisfaction_pattern_law(flat, (0, 1, 2, 3)) != (
            satisfaction_pattern_law(bad, (0, 1, 2, 3))
        )
        assert optimum_by_labels(flat)[0] - optimum_by_labels(bad)[0] == Fraction(1, 4)


def test_binary_complete_cycle_parity_separates_with_one_full_observation():
    flat = make_game(4, 1, C4, (0, 0, 0, 0))
    bad = make_game(4, 1, C4, (0, 0, 0, 1))
    a = satisfaction_pattern_law(flat, (0, 1, 2, 3))
    b = satisfaction_pattern_law(bad, (0, 1, 2, 3))
    assert set(a).isdisjoint(set(b))
    assert sum(a.values()) == sum(b.values()) == 1


def test_F2_squared_complete_cycle_has_rare_flat_joint_success():
    flat = make_game(4, 2, C4, (0, 0, 0, 0))
    bad = make_game(4, 2, C4, (0, 0, 0, 1))
    a = satisfaction_pattern_law(flat, (0, 1, 2, 3))
    b = satisfaction_pattern_law(bad, (0, 1, 2, 3))
    assert a[(True,) * 4] == Fraction(1, 4**3)
    assert b.get((True,) * 4, Fraction(0)) == 0


def test_maxcut_embeds_as_binary_all_one_translation_game():
    pairs = tuple(combinations(range(4), 2))
    for chosen in product((0, 1), repeat=len(pairs)):
        graph = tuple(e for flag, e in zip(chosen, pairs) if flag)
        g = make_game(4, 1, graph, (1,) * len(graph))
        val, _ = optimum_by_labels(g)
        expect = Fraction(maxcut_count(4, graph), len(graph)) if graph else Fraction(1)
        assert val == expect


def test_bad_edge_query_ids_rejected():
    g = make_game(4, 2, C4, (0, 0, 0, 1))
    with pytest.raises(ValueError):
        satisfaction_pattern_law(g, (5,))
    with pytest.raises(ValueError):
        satisfaction_pattern_law(g, (0, 0))
