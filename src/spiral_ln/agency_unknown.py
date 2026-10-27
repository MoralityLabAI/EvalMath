"""FAW-03: exact Bayesian calibration with unknown persistent channel reliability.

Within each epoch polarity is fresh; q persists across epochs and belongs to
an explicitly declared finite rational prior. Labeled calibration returns
z=s XOR y; reward labels remain sealed until all test decisions finish.

Dynamic programming charges each acquired gold label and maximizes expected
held-out reward net of label costs. No live models, graders or cryptography.
"""

from __future__ import annotations

from functools import lru_cache
from fractions import Fraction as Q
from itertools import product
from math import comb

Prior = tuple[tuple[Q, Q], ...]  # (reliability, probability), sorted uniquely
DEFAULT_PRIOR: Prior = ((Q(1, 2), Q(1, 2)), (Q(1), Q(1, 2)))


def validate_prior(prior: Prior) -> Prior:
    if not isinstance(prior, tuple) or not prior:
        raise ValueError("prior must be a nonempty tuple")
    qs: list[Q] = []
    weight = Q(0)
    for entry in prior:
        if not isinstance(entry, tuple) or len(entry) != 2:
            raise ValueError("prior entries must be (q, weight) tuples")
        q, w = entry
        if not isinstance(q, Q) or not isinstance(w, Q):
            raise TypeError("reliabilities and weights must be Fractions")
        if not Q(1, 2) <= q <= 1 or w <= 0:
            raise ValueError("reliabilities in [1/2,1], weights positive")
        qs.append(q)
        weight += w
    if qs != sorted(set(qs)) or weight != 1:
        raise ValueError("distinct q values must be sorted and weights sum to 1")
    return prior


def _nonnegative_int(value: int, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer")
    return value


def _cost(value: Q) -> Q:
    if not isinstance(value, Q):
        raise TypeError("cost must be a Fraction")
    if value < 0:
        raise ValueError("cost must be nonnegative")
    return value


def agreement_probability(q: Q) -> Q:
    """Probability two within-epoch calibration polarities are equal."""
    if not isinstance(q, Q) or not Q(1, 2) <= q <= 1:
        raise ValueError("q must be a Fraction in [1/2,1]")
    return q*q + (1-q)*(1-q)


def _joint(prior: Prior, zeros: int, ones: int) -> tuple[tuple[Q, int, Q], ...]:
    """Joint posterior on (q, theta) for one ordered calibration history.

    Counts are sufficient for the likelihood of the *ordered* observations.
    The combinatorial multiplicity is used only when integrating all sequences.
    """
    _nonnegative_int(zeros, "zeros")
    _nonnegative_int(ones, "ones")
    unnormalized = []
    for q, w in prior:
        unnormalized.append((q, 0, w*Q(1, 2)*q**zeros*(1-q)**ones))
        unnormalized.append((q, 1, w*Q(1, 2)*(1-q)**zeros*q**ones))
    total = sum((weight for _, _, weight in unnormalized), Q(0))
    if total == 0:
        raise ValueError("observation path has probability zero under prior")
    return tuple((q, theta, weight/total) for q, theta, weight in unnormalized)


def state(prior: Prior, zeros: int, ones: int) -> dict[str, object]:
    """Posterior prediction on a fresh item, independent of training samples."""
    validate_prior(prior)
    masses = _joint(prior, zeros, ones)
    p_same = sum((w*(q if theta == 0 else 1-q) for q, theta, w in masses), Q(0))
    q_posterior = tuple((q, sum((w for x, _, w in masses if x == q), Q(0)))
                        for q, _ in prior)
    oracle = sum((q*w for q, w in q_posterior), Q(0))
    return {
        "observations_zero": zeros,
        "observations_one": ones,
        "q_posterior": q_posterior,
        "next_zero_probability": p_same,
        "predict_flip": p_same < Q(1, 2),  # on equality, predict s=y
        "fresh_accuracy": max(p_same, 1-p_same),
        "oracle_accuracy": oracle,
        "oracle_gap": oracle-max(p_same, 1-p_same),
    }


def after_pairs(prior: Prior, agree: int, differ: int) -> Prior:
    """Bayes update from pairs in independent epochs with fresh theta."""
    validate_prior(prior)
    _nonnegative_int(agree, "agree")
    _nonnegative_int(differ, "differ")
    raw = tuple((q, w*agreement_probability(q)**agree*
                 (1-agreement_probability(q))**differ) for q, w in prior)
    z = sum((w for _, w in raw), Q(0))
    if z == 0:
        raise ValueError("pair data impossible under prior")
    return tuple((q, w/z) for q, w in raw if w > 0)


def _posterior_state(prior: Prior, zeros: int, ones: int) -> dict[str, object]:
    """Internal state with zero-probability prior members retained for memoization."""
    return state(prior, zeros, ones)


def solve_epochs(
    prior: Prior,
    trials: tuple[int, ...],
    caps: tuple[int, ...],
    costs: tuple[Q, ...],
) -> dict[str, object]:
    """Exact global Bayes-optimal acquisition policy over a finite horizon.

    At epoch boundary q persists and theta is redrawn uniformly; only the
    posterior of q carries forward. All held-out judgments remain sealed.
    The state contains the current epoch's calibration counts, remaining
    acquisition budget, and the current q prior. Planning computation is free.
    """
    validate_prior(prior)
    if not trials or not (len(trials) == len(caps) == len(costs)):
        raise ValueError("nonempty equal-length epoch tuples required")
    for n, cap, c in zip(trials, caps, costs):
        _nonnegative_int(n, "heldout trials")
        _nonnegative_int(cap, "label cap")
        _cost(c)

    decisions: dict[tuple[int, Prior, int, int], dict[str, object]] = {}

    @lru_cache(maxsize=None)
    def epoch_start(i: int, epoch_prior: Prior) -> Q:
        if i == len(trials):
            return Q(0)
        return within(i, epoch_prior, 0, 0)

    @lru_cache(maxsize=None)
    def within(i: int, epoch_prior: Prior, zeros: int, ones: int) -> Q:
        current = _posterior_state(epoch_prior, zeros, ones)
        acquired = zeros + ones
        # Bayes value of ending the current epoch, with future q learning.
        q_next = tuple((q, w) for q, w in current["q_posterior"] if w > 0)
        stop = trials[i]*(current["fresh_accuracy"]-Q(1, 2)) + epoch_start(i+1, q_next)
        p0 = current["next_zero_probability"]
        buy: Q | None = None
        if acquired < caps[i]:
            next0 = within(i, epoch_prior, zeros+1, ones) if p0 > 0 else Q(0)
            next1 = within(i, epoch_prior, zeros, ones+1) if p0 < 1 else Q(0)
            buy = -costs[i] + p0*next0+(1-p0)*next1
        decision = "buy" if buy is not None and buy > stop else "stop"
        decisions[(i, epoch_prior, zeros, ones)] = {
            "stop_value": stop,
            "buy_value": buy,
            "decision": decision,
            "value": buy if decision == "buy" else stop,
            "predict_flip": current["predict_flip"],
            "fresh_accuracy": current["fresh_accuracy"],
            "next_zero_probability": p0,
            "q_posterior": q_next,
        }
        return decisions[(i, epoch_prior, zeros, ones)]["value"]

    value = epoch_start(0, prior)

    @lru_cache(maxsize=None)
    def assess(i: int, epoch_prior: Prior, zeros: int, ones: int) -> tuple[Q, Q, Q, Q]:
        """Expected (acquired labels, number of useful tests, correct, oracle).

        Correct and oracle are unnormalized expected *counts* across remaining
        epochs. These are evaluated under the saved optimal policy.
        """
        if i == len(trials):
            return Q(0), Q(0), Q(0), Q(0)
        decision = decisions[(i, epoch_prior, zeros, ones)]
        if decision["decision"] == "stop":
            next_prior = decision["q_posterior"]
            labs, tests, correct, oracle = assess(i+1, next_prior, 0, 0)
            current = _posterior_state(epoch_prior, zeros, ones)
            return (labs, tests+trials[i], correct+trials[i]*current["fresh_accuracy"],
                    oracle+trials[i]*current["oracle_accuracy"])
        p0 = decision["next_zero_probability"]
        x0 = assess(i, epoch_prior, zeros+1, ones) if p0 > 0 else (Q(0),)*4
        x1 = assess(i, epoch_prior, zeros, ones+1) if p0 < 1 else (Q(0),)*4
        return tuple((Q(1) if j == 0 else Q(0)) + p0*x0[j]+(1-p0)*x1[j]
                     for j in range(4))

    labels, tests, correct, oracle = assess(0, prior, 0, 0)
    assert tests == sum(trials)
    initial_stop = decisions[(0, prior, 0, 0)]
    # Source of optional planner diagnostics: public top-level decisions only.
    return {
        "epochs": len(trials),
        "heldout_trials": sum(trials),
        "value_over_chance": value,
        "first_action": initial_stop["decision"],
        "first_stop_value": initial_stop["stop_value"],
        "first_buy_value": initial_stop["buy_value"],
        "expected_gold_labels": labels,
        "expected_heldout_correct": correct,
        "expected_oracle_correct": oracle,
        "expected_oracle_regret": oracle-correct,
        "expected_label_cost": sum_expected_cost(prior, trials, caps, costs, decisions),
        "value_identity": value == correct-Q(tests, 2)-sum_expected_cost(
            prior, trials, caps, costs, decisions),
        "policy_states": len(decisions),
        "_policy": decisions,
    }


def sum_expected_cost(prior: Prior, trials: tuple[int, ...], caps: tuple[int, ...],
                      costs: tuple[Q, ...], policy: dict) -> Q:
    """Evaluate acquisition charges from a policy tree, across epoch boundaries."""
    @lru_cache(maxsize=None)
    def visit(i: int, epoch_prior: Prior, zeros: int, ones: int) -> Q:
        if i == len(trials):
            return Q(0)
        d = policy[(i, epoch_prior, zeros, ones)]
        if d["decision"] == "stop":
            return visit(i+1, d["q_posterior"], 0, 0)
        p0 = d["next_zero_probability"]
        return costs[i] + (p0*visit(i, epoch_prior, zeros+1, ones) if p0 > 0 else Q(0)) + (
            (1-p0)*visit(i, epoch_prior, zeros, ones+1) if p0 < 1 else Q(0))
    return visit(0, prior, 0, 0)


def fixed_budget_value(prior: Prior, trials: int, labels: int, cost: Q) -> Q:
    """Exhaustive fixed number of labels, with posterior-optimal heldout action."""
    validate_prior(prior)
    _nonnegative_int(trials, "trials")
    _nonnegative_int(labels, "labels")
    _cost(cost)
    ans = Q(0)
    for n0 in range(labels+1):
        n1 = labels-n0
        prob = sum((w*Q(1, 2)*(q**n0*(1-q)**n1+
                                   (1-q)**n0*q**n1) for q, w in prior), Q(0))
        if prob > 0:
            acc = state(prior, n0, n1)["fresh_accuracy"]
            ans += Q(comb(labels, n0))*prob*trials*(acc-Q(1, 2))
    return ans-cost*labels


def one_label_posterior_invariant(prior: Prior) -> bool:
    """With an independent uniform polarity, one gold label reveals no q."""
    validate_prior(prior)
    return (state(prior, 1, 0)["q_posterior"] == prior and
            state(prior, 0, 1)["q_posterior"] == prior)


def _closest_q(prior: Prior, empirical: Q) -> Q:
    """Nearest agreement rate, deterministic lower-q tie break."""
    return min((q for q, _ in prior), key=lambda q: (abs(agreement_probability(q)-empirical), q))


def identification_success(prior: Prior, true_q: Q, pairs: int) -> Q:
    """Exact probability the agreement-rate estimator identifies true q."""
    validate_prior(prior)
    _nonnegative_int(pairs, "pairs")
    if true_q not in tuple(q for q, _ in prior):
        raise ValueError("true q must be in prior support")
    a = agreement_probability(true_q)
    return sum((Q(comb(pairs, k))*a**k*(1-a)**(pairs-k)
                for k in range(pairs+1)
                if _closest_q(prior, Q(k, pairs) if pairs else Q(1, 2)) == true_q), Q(0))


def identification_chebyshev_bound(prior: Prior, true_q: Q, pairs: int) -> Q:
    """Exact upper bound on P(misidentification) from separated agreement rates."""
    validate_prior(prior)
    _nonnegative_int(pairs, "pairs")
    others = tuple(abs(agreement_probability(q)-agreement_probability(true_q))
                   for q, _ in prior if q != true_q)
    if true_q not in tuple(q for q, _ in prior) or not others or pairs == 0:
        raise ValueError("need >0 pairs and true q in support of at least two q")
    delta = min(others)
    a = agreement_probability(true_q)
    return min(Q(1), 4*a*(1-a)/(pairs*delta**2))


def fixture() -> dict[str, object]:
    """A predeclared finite toy witness; no claims of asymptotic PKE relevance."""
    prior = DEFAULT_PRIOR
    # A preliminary zero-test audit of q can improve costs on later episodes:
    # 12 fresh polarities, each with 6 independently held-out decisions and cap 1.
    # The early two-label q-audit can be worthwhile despite no immediate reward.
    episode = solve_epochs(prior, (0,)+(6,)*12, (2,)+(1,)*12, (Q(1),)*13)
    fixed_one = fixed_budget_value(prior, 6, 1, Q(1))
    first = state(prior, 1, 0)
    same = state(prior, 2, 0)
    different = state(prior, 1, 1)
    seen = tuple((k, identification_success(prior, Q(1), k)) for k in (1, 2, 4, 8, 16))
    checks = {
        "one_label_q_uninformative": one_label_posterior_invariant(prior),
        "two_label_same_event_probability": Q(3, 4) == sum(
            (w*agreement_probability(q) for q, w in prior), Q(0)),
        "same_pair_updates_q": same["q_posterior"] == ((Q(1, 2), Q(1, 3)), (Q(1), Q(2, 3))),
        "different_pair_identifies_noisy_channel": different["q_posterior"] == ((Q(1, 2), Q(1)), (Q(1), Q(0))),
        "one_label_accuracy": first["fresh_accuracy"] == Q(3, 4),
        "fixed_one_label_net": fixed_one == Q(1, 2),
        "global_optimal_first_action_buy": episode["first_action"] == "buy",
        "forward_utility_identity": episode["value_identity"],
        "expected_global_gain_is_seven": episode["value_over_chance"] == Q(7),
        "no_early_experiment_gain_six": episode["first_stop_value"] == Q(6),
        "gold_label_budget_bounded": episode["expected_gold_labels"] <= Q(14),
        "oracle_gap_nonnegative": episode["expected_oracle_regret"] >= 0,
        "separated_rates_identifiable": all(agreement_probability(prior[i][0]) < agreement_probability(prior[i+1][0])
                                             for i in range(len(prior)-1)),
        "exact_identification_converges_in_fixture": seen[-1][1] >= seen[0][1],
    }
    return {
        "schema_version": "1.0",
        "mechanism": "q_shared_across_epochs; fresh_uniform_theta; sealed_heldout_feedback",
        "prior": prior,
        "posterior_after_one_label": first["q_posterior"],
        "posterior_after_agree": same["q_posterior"],
        "posterior_after_disagree": different["q_posterior"],
        "same_pair_probability": Q(3, 4),
        "single_label_epoch_value": fixed_one,
        "adaptive_epoch_result": {k: v for k, v in episode.items() if k != "_policy"},
        "pair_identification": seen,
        "checks": checks,
        "all_passed": all(checks.values()),
        "evidence_level": "algebraic_proof_and_finite_exact_bayes_planning",
        "real_agent_evidence": False,
        "cryptographic_world_identified": False,
        "theological_hypothesis_identified": False,
        "lean_formalized": False,
    }
