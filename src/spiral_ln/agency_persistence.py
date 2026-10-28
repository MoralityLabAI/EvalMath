"""Exact persistent learning with fresh hidden polarity in each evaluation epoch.

A small operational agent learns using labeled calibration, makes held-out
choices with rewards sealed until the epoch ends, and pays for labels.  The
instance has no cryptographic hardness premise.  All arithmetic is rational.
"""

from __future__ import annotations

from fractions import Fraction as Q

from spiral_ln.agency_worlds import calibration_accuracy, heldout_success

Q_SIGNAL = Q(3, 4)
C_LABEL = Q(1, 32)


def _epoch(epoch: int) -> int:
    if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch < 1:
        raise ValueError("epoch must be a positive integer")
    return epoch


def _cost(cost: Q) -> Q:
    if not isinstance(cost, Q):
        raise TypeError("cost must be an exact Fraction")
    if cost < 0:
        raise ValueError("cost must be nonnegative")
    return cost


def label_budget(epoch: int) -> int:
    """5 * ceil(log2(t+1)), evaluated as an exact integer."""
    return 5 * _epoch(epoch).bit_length()


def epoch_metrics(epoch: int, cost: Q = C_LABEL) -> dict[str, object]:
    """Calibration then t+1 fresh held-out predictions with sealed feedback."""
    t = _epoch(epoch)
    c = _cost(cost)
    bits = t.bit_length()
    samples = label_budget(t)
    decisions = t + 1
    alpha = calibration_accuracy(Q_SIGNAL, samples)
    error = 1 - alpha
    accuracy = heldout_success(Q_SIGNAL, samples)
    oracle_regret = decisions * (Q_SIGNAL - accuracy)
    gross_gain = decisions * (accuracy - Q(1, 2))
    net_gain = gross_gain - samples*c
    # In the Chernoff calculation, p_error^2 <= (3/4)^m.
    # The pure-rational factor (3/4)^5 = 243/1024 <= 1/4 yields
    # p_error <= 2^(-bit_length(t)) <= 1/(t+1).
    certificate = {
        "chernoff_square": error**2 <= Q(3, 4)**samples,
        "five_label_factor": Q(243, 1024) <= Q(1, 4),
        "epoch_within_binary_scale": decisions <= (1 << bits),
        "polarity_error_bound": error <= Q(1, 2)**bits,
        "single_test_regret_bound": Q_SIGNAL-accuracy <= Q(1, 2*decisions),
        "epoch_oracle_regret_bound": oracle_regret <= Q(1, 2),
        "net_lower_bound": net_gain >= Q(8*(t-1)-5*bits, 32) if c == C_LABEL else True,
        "positive_net_witness": net_gain > 0 if c == C_LABEL else True,
    }
    return {
        "epoch": t,
        "bits": bits,
        "calibration_labels": samples,
        "independent_heldout_trials": decisions,
        "polarity_recovery": alpha,
        "polarity_error": error,
        "heldout_success": accuracy,
        "oracle_regret": oracle_regret,
        "baseline_gain": gross_gain,
        "label_cost": samples*c,
        "net_baseline_gain": net_gain,
        "net_lower_bound": Q(8*(t-1)-5*bits, 32) if c == C_LABEL else None,
        "certificate": certificate,
    }


def optimal_epoch(epoch: int, cost: Q = C_LABEL) -> dict[str, object]:
    """Choose the best label count in the SAME declared finite budget.

    This is a rational planning fixture with the outcome distribution known,
    rather than an experiment where a model designs its own evaluation.
    Computation cost is excluded; the acquisition cost is fully included.
    """
    t = _epoch(epoch)
    c = _cost(cost)
    decisions = t+1
    budget = label_budget(t)
    net_values = tuple(decisions*(heldout_success(Q_SIGNAL, n)-Q(1, 2)) - n*c
                       for n in range(budget+1))
    maximum = max(net_values)
    ties = tuple(n for n, utility in enumerate(net_values) if utility == maximum)
    chosen = ties[0]  # minimum acquisition cost among exact equal-utility ties
    accuracy = heldout_success(Q_SIGNAL, chosen)
    regret = decisions*(Q_SIGNAL-accuracy)
    scheduled = epoch_metrics(t, c)
    return {
        "epoch": t,
        "budget": budget,
        "selected_labels": chosen,
        "equally_optimal_label_counts": ties,
        "heldout_success": accuracy,
        "oracle_regret": regret,
        "net_baseline_gain": maximum,
        "certificate": {
            "budget_respected": chosen <= budget,
            "net_no_worse_than_schedule": maximum >= scheduled["net_baseline_gain"],
            # Optimality: N*r_opt+c*m_opt <= N*r_sched+c*m_sched
            "costed_oracle_regret_bound": regret + c*chosen <= Q(1, 2)+c*budget,
        },
    }


def horizon_metrics(horizon: int, cost: Q = C_LABEL) -> dict[str, object]:
    """Expected cumulative value of T independent epochs under both policies."""
    T = _epoch(horizon)
    c = _cost(cost)
    stages = tuple(epoch_metrics(t, c) for t in range(1, T+1))
    choices = tuple(optimal_epoch(t, c) for t in range(1, T+1))
    decisions = T*(T+3)//2
    labels = sum(s["calibration_labels"] for s in stages)
    regret = sum((s["oracle_regret"] for s in stages), Q(0))
    gross = sum((s["baseline_gain"] for s in stages), Q(0))
    net = gross - c*labels
    opt_labels = sum(x["selected_labels"] for x in choices)
    opt_regret = sum((x["oracle_regret"] for x in choices), Q(0))
    opt_net = sum((x["net_baseline_gain"] for x in choices), Q(0))
    bit_bound = 5*T*T.bit_length()
    opt_regret_upper = Q(T, 2)+c*bit_bound
    certificates = {
        "stage_certificates": all(all(x["certificate"].values()) for x in stages),
        "optimizer_certificates": all(all(x["certificate"].values()) for x in choices),
        "heldout_count": sum(s["independent_heldout_trials"] for s in stages) == decisions,
        "labels_at_most_5Tlog": labels <= bit_bound,
        "cumulative_regret_at_most_T_over_2": regret <= Q(T, 2),
        "average_regret_at_most_inverse_horizon": regret/decisions <= Q(1, T+3),
        "baseline_gain_identity": gross == Q(decisions, 4)-regret,
        "normalized_net_lower_bound": net/decisions >= Q(1, 4)-Q(1, T+3)-c*Q(10*T.bit_length(), T+3),
        "optimal_net_dominates_schedule": opt_net >= net,
        "optimal_regret_bound": opt_regret <= opt_regret_upper,
        "optimal_average_regret_bound": opt_regret/decisions <= Q(1, T+3)+c*Q(10*T.bit_length(), T+3),
        "schedule_positive_net": net > 0 if c == C_LABEL else True,
        "optimized_positive_net": opt_net > 0 if c == C_LABEL else True,
    }
    return {
        "horizon": T,
        "heldout_trials": decisions,
        "scheduled_calibration_labels": labels,
        "label_upper_bound": bit_bound,
        "schedule_oracle_regret": regret,
        "schedule_avg_oracle_regret": regret/decisions,
        "schedule_regret_bound_per_trial": Q(1, T+3),
        "schedule_net_gain_over_chance": net,
        "schedule_net_gain_per_trial": net/decisions,
        "optimized_calibration_labels": opt_labels,
        "optimized_oracle_regret": opt_regret,
        "optimized_avg_oracle_regret": opt_regret/decisions,
        "optimized_regret_bound_per_trial": Q(1, T+3)+c*Q(10*T.bit_length(), T+3),
        "optimized_net_gain_over_chance": opt_net,
        "optimized_net_gain_per_trial": opt_net/decisions,
        "certificates": certificates,
    }


def fixed_label_regret_floor(q: Q, max_labels: int) -> Q:
    """A positive gap if every fresh-polarity epoch has <= M labels.

    With m>=1 the all-flipped-noise event yields erroneous polarity with
    probability (1-q)^m; with m=0 error is 1/2.  Even adaptive choices
    based solely on past independent epochs cannot predict fresh theta.
    This formula addresses declared nonadaptive within-epoch sample counts;
    adaptively stopping from current-epoch labels needs separate analysis.
    """
    if not isinstance(q, Q) or not Q(1, 2) < q < 1:
        raise ValueError("q must be an exact Fraction strictly inside (1/2,1)")
    if isinstance(max_labels, bool) or not isinstance(max_labels, int) or max_labels < 0:
        raise ValueError("max_labels must be a nonnegative integer")
    return (2*q-1)*min(Q(1, 2), (1-q)**max_labels)


def prior_epoch_transfer(q: Q, calibration_labels: int, shared_polarity: bool) -> Q:
    """Control: old labels help only when the hidden polarity persists.

    Each held-out signal's state is fresh and uniform, and feedback stays
    sealed.  With independently refreshed hidden polarity, a past-epoch
    estimate has probability 1/2 of being correct in the next epoch.
    """
    accuracy = heldout_success(q, calibration_labels)  # validate both inputs
    if not isinstance(shared_polarity, bool):
        raise TypeError("shared_polarity must be boolean")
    return accuracy if shared_polarity else Q(1, 2)


def fixture() -> dict[str, object]:
    """Exact finite fixtures; all-horizon proofs are stated in the note."""
    horizons = (1, 2, 4, 8, 16, 32, 64)
    reports = tuple(horizon_metrics(t) for t in horizons)
    floors = tuple((q, m, fixed_label_regret_floor(q, m))
                   for q in (Q(2, 3), Q(3, 4), Q(4, 5)) for m in (0, 1, 3, 8))
    checks = {
        "stage_certificates": all(all(epoch_metrics(t)["certificate"].values()) for t in range(1, 65)),
        "horizon_certificates": all(all(x["certificates"].values()) for x in reports),
        "first_budget_five": label_budget(1) == 5,
        "power_of_two_boundary_budgets": (label_budget(2), label_budget(3), label_budget(4)) == (10, 10, 15),
        "first_epoch_exact_accuracy": epoch_metrics(1)["heldout_success"] == Q(715, 1024),
        "every_tested_epoch_positive_net": all(epoch_metrics(t)["net_baseline_gain"] > 0 for t in range(1, 65)),
        "optimized_nets_dominate": all(optimal_epoch(t)["net_baseline_gain"] >= epoch_metrics(t)["net_baseline_gain"]
                                       for t in range(1, 65)),
        "finite_fixed_budget_regret_floor": all(floor > 0 and all(q-heldout_success(q, n) >= floor
                                                                for n in range(m+1))
                                                for q, m, floor in floors),
        "fresh_polarity_prevents_cross_epoch_transfer": prior_epoch_transfer(Q_SIGNAL, 1, False) == Q(1, 2),
        "shared_polarity_allows_transfer": prior_epoch_transfer(Q_SIGNAL, 1, True) == Q(5, 8),
        "uninformative_signal_negative_control": all(heldout_success(Q(1, 2), label_budget(t)) == Q(1, 2)
                                                     for t in range(1, 32)),
    }
    return {
        "schema_version": "1.0",
        "mechanism": "fresh_uniform_polarity_each_epoch; sealed_heldout_feedback",
        "signal_reliability": Q_SIGNAL,
        "label_cost": C_LABEL,
        "fixed_schedule": "m_t=5*bit_length(t)",
        "heldout_schedule": "n_t=t+1",
        "five_label_cher_bound_squared": Q(243, 1024),
        "finite_horizon_reports": reports,
        "fixed_budget_lower_bound_controls": floors,
        "checks": checks,
        "all_passed": all(checks.values()),
        "evidence_level": "algebraic_argument_plus_finite_exact_tests",
        "theological_hypothesis_identified": False,
        "public_key_cryptography_assumed": False,
        "empirical_agents_evaluated": False,
        "lean_formalized": False,
    }
