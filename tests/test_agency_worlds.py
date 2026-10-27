"""Exact tests of the finite agency witness; no empirical model invocation."""

from fractions import Fraction as Q

import pytest

from spiral_ln.agency_worlds import (
    calibration_accuracy, enumerate_heldout_success, fixture,
    heldout_success, net_value, optimal_calibration,
)


@pytest.mark.parametrize("q", (Q(1, 2), Q(2, 3), Q(3, 4), Q(1)))
@pytest.mark.parametrize("samples", range(9))
def test_formula_matches_independent_enumeration(q, samples):
    assert heldout_success(q, samples) == enumerate_heldout_success(q, samples)


def test_heldout_learning_and_always_holdout():
    assert [heldout_success(Q(3, 4), n) for n in range(6)] == [
        Q(1, 2), Q(5, 8), Q(5, 8), Q(43, 64), Q(43, 64), Q(715, 1024),
    ]
    assert calibration_accuracy(Q(3, 4), 0) == Q(1, 2)
    assert calibration_accuracy(Q(3, 4), 1) == Q(3, 4)
    assert calibration_accuracy(Q(3, 4), 3) == Q(27, 32)


def test_degenerate_channels():
    for samples in range(11):
        assert heldout_success(Q(1, 2), samples) == Q(1, 2)
        assert heldout_success(Q(1), samples) == (Q(1, 2) if samples == 0 else Q(1))


def test_agent_choice_is_cost_sensitive():
    q = Q(3, 4)
    costly = optimal_calibration(q, 5, Q(1, 32))
    assert costly["optimal_sample_counts"] == (1,)
    assert costly["optimal_value"] == Q(19, 32)
    free = optimal_calibration(q, 5, Q(0))
    assert free["optimal_sample_counts"] == (5,)
    assert free["optimal_value"] == Q(715, 1024)
    assert net_value(q, 1, Q(1, 32)) > net_value(q, 0, Q(1, 32))


def test_ties_and_zero_budget():
    assert optimal_calibration(Q(1, 2), 3, Q(0))["optimal_sample_counts"] == (0, 1, 2, 3)
    assert optimal_calibration(Q(3, 4), 0, Q(1, 32))["optimal_sample_counts"] == (0,)


@pytest.mark.parametrize("bad", (Q(-1), Q(0), Q(2, 5), Q(5, 4)))
def test_probability_validation(bad):
    with pytest.raises(ValueError):
        heldout_success(bad, 1)


@pytest.mark.parametrize("bad", (-1, 1.0, True))
def test_sample_validation(bad):
    with pytest.raises(ValueError):
        calibration_accuracy(Q(3, 4), bad)


def test_requires_rational_inputs():
    with pytest.raises(TypeError):
        heldout_success(.75, 1)
    with pytest.raises(TypeError):
        net_value(Q(3, 4), 1, .1)
    with pytest.raises(ValueError):
        optimal_calibration(Q(3, 4), 3, Q(-1))


def test_receipt_fixture_has_all_checks_true():
    report = fixture()
    assert report["all_passed"]
    assert all(value is True for value in report["checks"].values())
    assert report["memorized_training_label_score"] == Q(1)
    assert report["training_vs_heldout_gap_at_one_label"] == Q(3, 8)
    assert report["real_agent_evidence"] is False
    assert report["cryptographic_world_identified"] is False
    assert report["theological_hypothesis_identified"] is False
