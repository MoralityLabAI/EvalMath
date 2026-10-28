"""An exact finite agency witness independent of cryptographic hardness assumptions.

The calibration and held-out draws are independent.  This is a *synthetic*
decision experiment; it neither settles P vs NP nor tests a real model or God.
All reported probabilities use Fraction, without random sampling.
"""

from __future__ import annotations

from fractions import Fraction as Q
from itertools import product
from math import comb


def _check(q: Q, samples: int) -> None:
    if not isinstance(q, Q):
        raise TypeError("q must be a fractions.Fraction")
    if q < Q(1, 2) or q > 1:
        raise ValueError("q must be in [1/2, 1]")
    if not isinstance(samples, int) or isinstance(samples, bool) or samples < 0:
        raise ValueError("samples must be a nonnegative integer")


def calibration_accuracy(q: Q, samples: int) -> Q:
    """Probability a majority decoder learns a uniformly random channel polarity.

    A calibration item discloses its true state s and noisy signal y.  If the
    hidden polarity is theta, y = s XOR theta XOR noise; P(noise=0) = q.
    Ties are broken in favor of theta=0 (equivalently half a chance of correct
    polarity under the uniform prior).  No item is reused for held-out scoring.
    """
    _check(q, samples)
    threshold = samples // 2
    total = sum(Q(comb(samples, k)) * q**k * (1 - q)**(samples - k)
                for k in range(threshold + 1, samples + 1))
    if samples % 2 == 0:
        total += Q(1, 2) * Q(comb(samples, threshold)) * q**threshold * (1-q)**threshold
    return total


def heldout_success(q: Q, samples: int) -> Q:
    """Held-out correctness under learned polarity; all inputs exact."""
    alpha = calibration_accuracy(q, samples)
    return (1-q) + (2*q-1)*alpha


def enumerate_heldout_success(q: Q, samples: int) -> Q:
    """Independent finite sum over theta, labeled errors and future error.

    Enumeration uses a literal majority vote and fresh test noise rather than
    the binomial closed form.  Intended for small sample counts as a check.
    """
    _check(q, samples)
    result = Q(0)
    for theta in (0, 1):
        for errors in product((0, 1), repeat=samples):
            probability = Q(1, 2)
            observed_polarities = [theta ^ e for e in errors]
            for e in errors:
                probability *= q if e == 0 else 1-q
            estimate = int(2 * sum(observed_polarities) > samples)
            for fresh_error in (0, 1):
                if estimate == (theta ^ fresh_error):
                    result += probability * (q if fresh_error == 0 else 1-q)
    return result


def net_value(q: Q, samples: int, label_cost: Q) -> Q:
    """Accuracy less a per-label rational cost, with no score reuse."""
    _check(q, samples)
    if not isinstance(label_cost, Q):
        raise TypeError("label_cost must be a fractions.Fraction")
    if label_cost < 0:
        raise ValueError("label_cost must be nonnegative")
    return heldout_success(q, samples) - samples * label_cost


def optimal_calibration(q: Q, max_samples: int, label_cost: Q) -> dict[str, object]:
    """Enumerate feasible training budgets; preserve all ties explicitly."""
    _check(q, max_samples)
    values = tuple(net_value(q, n, label_cost) for n in range(max_samples+1))
    best = max(values)
    return {
        "max_samples": max_samples,
        "label_cost": label_cost,
        "value_by_samples": values,
        "optimal_value": best,
        "optimal_sample_counts": tuple(n for n, value in enumerate(values) if value == best),
    }


def fixture() -> dict[str, object]:
    """Exact finite checks, not a claim about real or hypothetical universes."""
    q = Q(3, 4)
    samples = (0, 1, 2, 3, 4, 5)
    successes = tuple(heldout_success(q, n) for n in samples)
    plan = optimal_calibration(q, 5, Q(1, 32))
    independent_checks = {
        "formula_matches_enumeration": all(
            heldout_success(rate, n) == enumerate_heldout_success(rate, n)
            for rate in (Q(1, 2), Q(2, 3), Q(3, 4), Q(1)) for n in range(8)),
        "no_feedback_is_chance": successes[0] == Q(1, 2),
        "one_label_improves_heldout": successes[1] == Q(5, 8),
        "three_labels_improve_further": successes[3] == Q(43, 64),
        "even_tie_matches_previous_odd": successes[2] == successes[1] and successes[4] == successes[3],
        "uninformative_channel_stays_chance": all(
            heldout_success(Q(1, 2), n) == Q(1, 2) for n in range(10)),
        "perfect_channel_after_one_label": all(
            heldout_success(Q(1), n) == Q(1) for n in range(1, 10)),
        "success_bounded_by_oracle": all(value <= q for value in successes),
        "reused_label_score_exceeds_heldout": Q(1) - successes[1] == Q(3, 8),
        "finite_plan_favors_one_label": plan["optimal_sample_counts"] == (1,),
        "one_label_net_value": plan["optimal_value"] == Q(19, 32),
        "finite_learning_gap_is_positive": (successes[1] - successes[0]) == Q(1, 8),
    }
    return {
        "channel_accuracy": q,
        "hidden_polarity_prior": (Q(1, 2), Q(1, 2)),
        "sample_counts": samples,
        "heldout_success": successes,
        "unlimited_calibration_oracle_accuracy": q,
        "memorized_training_label_score": Q(1),
        "training_vs_heldout_gap_at_one_label": Q(1) - successes[1],
        "plan": plan,
        "checks": independent_checks,
        "all_passed": all(independent_checks.values()),
        "evidence_level": "algebraic_identity_and_finite_verified_example",
        "real_agent_evidence": False,
        "cryptographic_world_identified": False,
        "theological_hypothesis_identified": False,
    }
