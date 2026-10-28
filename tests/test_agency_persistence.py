"""Independent exact controls for FAW-02.  No model or judge is executed."""

from fractions import Fraction as Q

import pytest

from spiral_ln.agency_worlds import heldout_success
from spiral_ln.agency_persistence import (
    C_LABEL, Q_SIGNAL, epoch_metrics, fixed_label_regret_floor, fixture,
    horizon_metrics, label_budget, optimal_epoch, prior_epoch_transfer,
)


def independent_majority_accuracy(q: Q, m: int) -> Q:
    """Convolve independent Bernoulli noises; no binomial coefficients."""
    mass = [Q(1)]
    for _ in range(m):
        new = [Q(0)] * (len(mass)+1)
        for successes, weight in enumerate(mass):
            new[successes] += weight*(1-q)
            new[successes+1] += weight*q
        mass = new
    return sum((v for k, v in enumerate(mass) if 2*k > m), Q(0)) + (
        Q(1, 2)*mass[m//2] if m % 2 == 0 else Q(0))


@pytest.mark.parametrize("m", tuple(range(25)))
@pytest.mark.parametrize("q", (Q(1, 2), Q(2, 3), Q(3, 4), Q(4, 5), Q(1)))
def test_independent_convolution_agrees_with_closed_form(q, m):
    alpha = independent_majority_accuracy(q, m)
    assert heldout_success(q, m) == (1-q)+(2*q-1)*alpha


@pytest.mark.parametrize("t", (1, 2, 3, 4, 7, 8, 15, 16, 31, 32, 63, 64, 127, 128))
def test_schedule_and_all_single_epoch_certificates(t):
    stage = epoch_metrics(t)
    assert label_budget(t) == 5*t.bit_length()
    assert stage["calibration_labels"] == label_budget(t)
    assert stage["independent_heldout_trials"] == t+1
    assert all(stage["certificate"].values())
    assert stage["net_baseline_gain"] > 0


def test_first_epoch_receipt_and_cost_control():
    a = epoch_metrics(1)
    assert a["polarity_recovery"] == Q(459, 512)
    assert a["polarity_error"] == Q(53, 512)
    assert a["heldout_success"] == Q(715, 1024)
    assert a["net_baseline_gain"] == Q(123, 512)
    assert epoch_metrics(2)["net_baseline_gain"] > 0
    # Worst-case analytic net lower bound becomes positive from t=3 onward.
    assert a["net_lower_bound"] < 0
    assert epoch_metrics(3)["net_lower_bound"] == Q(3, 16)


def test_margin_monotonicity_for_all_larger_integer_epochs():
    # Exact induction: at each t->t+1, bit_length rises by at most one,
    # hence 8(t-1)-5 bit_length(t) increases by at least three.
    def margin(t):
        return 8*(t-1)-5*t.bit_length()
    assert margin(3) == 6
    for t in range(3, 1024):
        assert margin(t+1)-margin(t) >= 3
    assert margin(1024) > 0


@pytest.mark.parametrize("T", (1, 2, 3, 4, 8, 16, 32, 64))
def test_horizon_aggregation_and_rate_certificates(T):
    report = horizon_metrics(T)
    assert all(report["certificates"].values())
    assert report["heldout_trials"] == T*(T+3)//2
    assert report["scheduled_calibration_labels"] <= 5*T*T.bit_length()
    assert report["schedule_avg_oracle_regret"] <= Q(1, T+3)
    assert report["optimized_avg_oracle_regret"] <= report["optimized_regret_bound_per_trial"]
    assert report["optimized_net_gain_over_chance"] >= report["schedule_net_gain_over_chance"]


@pytest.mark.parametrize("t", (1, 2, 3, 4, 8, 16, 32, 64))
def test_exact_cost_optimization(t):
    chosen = optimal_epoch(t)
    cap = label_budget(t)
    assert chosen["selected_labels"] <= cap
    assert chosen["selected_labels"] == min(chosen["equally_optimal_label_counts"])
    # Independent brute-force utility calculation from held-out probabilities.
    for m in range(cap+1):
        alternative = (t+1)*(heldout_success(Q_SIGNAL, m)-Q(1, 2))-m*C_LABEL
        assert chosen["net_baseline_gain"] >= alternative
    assert all(chosen["certificate"].values())
    # With a positive price, even label counts are dominated by previous odd.
    assert chosen["selected_labels"] % 2 == 1


@pytest.mark.parametrize("q", (Q(2, 3), Q(3, 4), Q(4, 5)))
@pytest.mark.parametrize("cap", (0, 1, 2, 4, 8, 16))
def test_fixed_label_cap_has_strict_oracle_regret_floor(q, cap):
    floor = fixed_label_regret_floor(q, cap)
    assert floor > 0
    assert all(q-heldout_success(q, m) >= floor for m in range(cap+1))


def test_transfer_control_and_feedback_sealing():
    assert prior_epoch_transfer(Q_SIGNAL, 1, True) == Q(5, 8)
    assert prior_epoch_transfer(Q_SIGNAL, 1, False) == Q(1, 2)
    assert prior_epoch_transfer(Q_SIGNAL, 0, True) == Q(1, 2)
    assert prior_epoch_transfer(Q_SIGNAL, 8, False) == Q(1, 2)
    assert heldout_success(Q(1, 2), 99) == Q(1, 2)


@pytest.mark.parametrize("bad", (0, -2, 1.5, True, False))
def test_bad_epoch_rejected(bad):
    with pytest.raises(ValueError):
        label_budget(bad)
    with pytest.raises(ValueError):
        horizon_metrics(bad)


@pytest.mark.parametrize("bad", (Q(-1), Q(1, 2), Q(1), Q(3, 2), .75))
def test_fixed_floor_domain_rejected(bad):
    with pytest.raises(ValueError):
        fixed_label_regret_floor(bad, 3)


@pytest.mark.parametrize("bad", (-1, True, 2.5))
def test_bad_label_cap_rejected(bad):
    with pytest.raises(ValueError):
        fixed_label_regret_floor(Q_SIGNAL, bad)


def test_cost_and_type_controls():
    with pytest.raises(ValueError):
        epoch_metrics(1, Q(-1))
    with pytest.raises(TypeError):
        optimal_epoch(1, .01)
    with pytest.raises(ValueError):
        horizon_metrics(1, Q(-1))
    with pytest.raises(TypeError):
        prior_epoch_transfer(Q_SIGNAL, 1, 0)
    # Costs are accounted for: high costs can rationally suppress calibration.
    assert optimal_epoch(1, Q(1))["selected_labels"] == 0
    assert optimal_epoch(1, Q(1))["net_baseline_gain"] == 0


def test_fixture_metadata_and_exact_checks():
    report = fixture()
    assert report["all_passed"]
    assert all(report["checks"].values())
    assert report["theological_hypothesis_identified"] is False
    assert report["empirical_agents_evaluated"] is False
    assert report["public_key_cryptography_assumed"] is False
    assert report["lean_formalized"] is False
