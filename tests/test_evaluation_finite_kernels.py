"""Independent finite-event checks for the RHT-27/28 probability primitives."""
from fractions import Fraction as Q
from itertools import product

import pytest

from spiral_ln.evaluation_finite_kernels import (
    Kernel, apply, compose, dobrushin, expectation, identity, law, point_mass,
    probability, rational, row_distance, total_variation,
)


def test_exact_values_and_strict_inputs():
    assert rational("1/3") == Q(1, 3)
    assert rational("0.125") == Q(1, 8)
    for value in (True, False, 0.5, float("nan"), None):
        with pytest.raises(TypeError):
            rational(value)
    for value in (-1, "4/3"):
        with pytest.raises(ValueError):
            probability(value)
    for values in ((), (0, 0), (Q(1, 3), Q(1, 3)), (-1, 2)):
        with pytest.raises(ValueError):
            law(values)
    for values in ("10", b"10"):
        with pytest.raises(TypeError):
            law(values)
        with pytest.raises(TypeError):
            expectation((1, 0), values)


def test_rectangular_composition_and_immutable_rows():
    rows = [[1, 0], [0, 1], [Q(1, 2), Q(1, 2)]]
    first = Kernel(rows)
    rows[0][0] = 0
    second = Kernel(((Q(1, 3), Q(2, 3), 0), (0, 0, 1)))
    mu = (Q(1, 4), Q(1, 4), Q(1, 2))
    assert first.rows[0] == (1, 0)
    assert apply(mu, compose(first, second)) == apply(apply(mu, first), second)
    assert compose(identity(3), first) == compose(first, identity(2)) == first
    assert apply(mu, compose(first, second)) == (Q(1, 6), Q(1, 3), Q(1, 2))


def test_tv_is_maximum_event_gap_over_all_three_state_events():
    laws = [tuple(Q(x, 4) for x in counts)
            for counts in product(range(5), repeat=3) if sum(counts) == 4]
    events = list(product((0, 1), repeat=3))
    for p, q in product(laws, repeat=2):
        event_gap = max(abs(sum((p[i] - q[i]) * event[i] for i in range(3)))
                        for event in events)
        assert total_variation(p, q) == event_gap
        assert all(abs(expectation(p, event) - expectation(q, event)) <= event_gap
                   for event in events)


def test_singleton_and_complete_reset_boundaries():
    assert dobrushin(Kernel(((Q(1, 4), Q(3, 4)),))) == 0
    reset = Kernel(((1, 0),) * 3)
    assert dobrushin(reset) == 0
    assert dobrushin(identity(3)) == 1
    assert row_distance(reset, Kernel(((0, 1),) * 3)) == 1
    assert total_variation((1,), (1,)) == 0
    assert expectation((1,), (Q(2, 7),)) == Q(2, 7)


def test_dimensions_and_degenerate_spaces_are_rejected():
    for rows in ((), ((1,), (1, 0)), ((0, 0),)):
        with pytest.raises(ValueError):
            Kernel(rows)
    for size in (0, -1, True, Q(2), 1.5):
        with pytest.raises(ValueError):
            identity(size)
    for index in (-1, 2, True, Q(1)):
        with pytest.raises(ValueError):
            point_mass(index, 2)
    calls = (
        lambda: apply((1,), identity(2)),
        lambda: compose(identity(2), identity(3)),
        lambda: total_variation((1,), (1, 0)),
        lambda: row_distance(identity(2), identity(3)),
        lambda: expectation((1,), (0, 1)),
        lambda: expectation((1,), (2,)),
    )
    for call in calls:
        with pytest.raises(ValueError):
            call()
