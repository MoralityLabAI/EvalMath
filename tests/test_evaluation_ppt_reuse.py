"""Independent exact expectations and selection-bias witnesses for PPT reuse."""
from fractions import Fraction as Q
from itertools import product

import pytest

from spiral_ln.evaluation_ppt_reuse import (
    Candidate, Estimate, FOUR_POINT_PRIOR, TWO_POINT_PRIOR,
    check_prior, closed_form_two_utility_gap, exact_selection_profile,
    exact_uniform_coverage, population_objective, ratio_interval,
    sample_estimate, tilt_weight, utility_mean,
)


def test_exact_ppt_weight_and_constant_ess():
    for p in (Q(1, 4), Q(3, 4)):
        assert tilt_weight(p, Q(1, 2), 6) == Q(1, 64)
    a = Candidate(Q(1, 2), 6, "one")
    assert sample_estimate((Q(1, 4), Q(3, 4)), a) == Estimate(
        Q(1, 128), Q(1, 64), Q(1, 2), Q(2))


def test_utility_selection_exact_witness_and_binomial_independent():
    cs = (Candidate(Q(1, 2), 6, "one"), Candidate(Q(1, 2), 6, "zero"))
    p = exact_selection_profile(TWO_POINT_PRIOR, cs, 2)
    assert p["true_values"] == (Q(1, 2), Q(1, 2))
    assert p["fixed_estimate_means"] == (Q(1, 2), Q(1, 2))
    assert p["selected_estimate_mean"] == Q(5, 8)
    assert p["selection_optimism"] == Q(1, 8) == closed_form_two_utility_gap(2)
    assert p["fixed_false_risks"] == (Q(1, 4), Q(1, 4))
    assert p["selected_false_risk"] == Q(1, 2)
    assert p["min_ess"] == p["max_ess"] == 2
    for n in range(1, 7):
        p = exact_selection_profile(TWO_POINT_PRIOR, cs, n)
        direct = sum((Q(1, 2 ** n) * abs(sum((1 if x else -1 for x in bits)))
                      / (4*n) for bits in product((0, 1), repeat=n)), Q(0))
        assert p["selection_optimism"] == closed_form_two_utility_gap(n) == direct
        assert p["min_ess"] == p["max_ess"] == n


def test_prefix_selection_fixed_utility_exact_witness():
    cs = (Candidate(Q(0), 1, "change"), Candidate(Q(1), 1, "change"))
    r = exact_selection_profile(FOUR_POINT_PRIOR, cs, 2, Q(1, 16))
    assert r["true_values"] == (Q(11, 32), Q(11, 32))
    assert r["fixed_estimate_means"] == (Q(113, 320), Q(113, 320))
    assert r["selected_estimate_mean"] == Q(73, 192)
    assert r["selection_optimism"] == Q(7, 192)
    assert r["extra_over_first_estimator"] == Q(13, 480)
    assert r["fixed_false_risks"] == (Q(1, 2), Q(1, 2))
    assert r["selected_false_risk"] == Q(3, 4)
    assert r["worlds"] == 16


def test_ratio_bounds_are_simultaneously_sound_on_good_event():
    cs = (Candidate(Q(1, 4), 2, "one"), Candidate(Q(3, 4), 2, "zero"),
          Candidate(Q(1, 2), 2, "change"))
    for eps in (Q(1, 64), Q(1, 8), Q(1, 4)):
        profile = exact_uniform_coverage(FOUR_POINT_PRIOR, cs, 3, eps)
        assert profile["uniform_event_implies_all_intervals"]
        assert (profile["selected_interval_coverage_probability"] >=
                profile["uniform_mean_event_probability"])
        assert (profile["all_interval_coverage_probability"] >=
                profile["uniform_mean_event_probability"])


def test_ratio_interval_near_zero_denominator_abstains():
    e = Estimate(Q(1, 256), Q(1, 128), Q(1, 2), Q(2))
    lo, hi = ratio_interval(e, Q(1, 64))
    assert lo <= e.value and hi == 1


def test_validation_rejects_illegal_support():
    with pytest.raises(ValueError):
        check_prior(((Q(1, 2), Q(2, 3)),))
    with pytest.raises(ValueError):
        Candidate(Q(1, 2), 0, "one")
    with pytest.raises(ValueError):
        sample_estimate([Q(1)], Candidate(Q(0), 1, "one"))
    with pytest.raises(ValueError):
        ratio_interval(Estimate(Q(0), Q(1), Q(0), Q(1)), Q(-1, 2))
