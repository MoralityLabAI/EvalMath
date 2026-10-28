"""Independent exact Bayes, policy enumeration, and impossibility tests for FAW-03."""

from fractions import Fraction as Q
from itertools import product

import pytest

from spiral_ln.agency_unknown import (
    DEFAULT_PRIOR, agreement_probability, after_pairs, fixed_budget_value,
    fixture, identification_chebyshev_bound, identification_success,
    one_label_posterior_invariant, solve_epochs, state, validate_prior,
)

ALT_PRIOR = ((Q(1, 2), Q(1, 3)), (Q(3, 4), Q(1, 3)), (Q(1), Q(1, 3)))


def reference_mass(prior, observations):
    """Weight each latent world by multiplying independent sample factors."""
    weights = {}
    for q, prior_q in prior:
        for theta in (0, 1):
            w = prior_q/2
            for z in observations:
                w *= q if z == theta else (1-q)
            weights[q, theta] = w
    evidence = sum(weights.values(), Q(0))
    return weights, evidence


def reference_prediction(prior, observations):
    """Independent Bayes action using joint world enumeration, not state()."""
    masses, evidence = reference_mass(prior, observations)
    if evidence == 0:
        return None
    correct_if_equal = sum((w*(q if theta == 0 else 1-q)
                            for (q, theta), w in masses.items()), Q(0))
    return correct_if_equal >= evidence/2


def reference_policy_expected_value(prior, trials, cap, cost, actions):
    """Brute-force policies using full observation sequences and latent worlds.

    This deliberately evaluates every fixed-length noise path, even after the
    policy stops; the unconsumed suffix marginalizes to one. This contrasts
    with the normalized posterior Bellman recurrence in the module.
    """
    expected = Q(0)
    for (q, w_q), theta, observations in product(prior, (0, 1), product((0, 1), repeat=cap)):
        w = w_q/2
        for z in observations:
            w *= q if z == theta else (1-q)
        depth = 0
        while depth < cap and actions.get(tuple(observations[:depth]), False):
            depth += 1
        predict_equal = reference_prediction(prior, tuple(observations[:depth]))
        assert predict_equal is not None
        fresh_correct = (q if theta == 0 else 1-q) if predict_equal else (
            (1-q) if theta == 0 else q)
        expected += w*(trials*(fresh_correct-Q(1, 2))-cost*depth)
    return expected


@pytest.mark.parametrize("prior", (DEFAULT_PRIOR, ALT_PRIOR, ((Q(3, 4), Q(1)),)))
@pytest.mark.parametrize("observations", ((), (0,), (1,), (0,0), (0,1), (1,0), (1,1), (1,0,1)))
def test_joint_posteriors_agree_with_latent_world_enumeration(prior, observations):
    weights, evidence = reference_mass(prior, observations)
    if evidence == 0:
        with pytest.raises(ValueError, match="probability zero"):
            state(prior, observations.count(0), observations.count(1))
        return
    learned = state(prior, observations.count(0), observations.count(1))
    for q, prob in learned["q_posterior"]:
        expected = sum((weights[q, theta] for theta in (0, 1)), Q(0))/evidence
        assert prob == expected
    p0 = sum((w*(q if theta == 0 else 1-q)
              for (q, theta), w in weights.items()), Q(0))/evidence
    assert learned["next_zero_probability"] == p0
    assert learned["fresh_accuracy"] == max(p0, 1-p0)
    assert learned["predict_flip"] == (p0 < Q(1, 2))
    assert learned["oracle_gap"] >= 0


@pytest.mark.parametrize("prior", (DEFAULT_PRIOR, ALT_PRIOR, ((Q(1, 2),Q(1, 2)),(Q(3, 4),Q(1, 2)))))
def test_one_label_carries_zero_reliability_information(prior):
    assert one_label_posterior_invariant(prior)
    assert state(prior, 0, 0)["q_posterior"] == prior


@pytest.mark.parametrize("q", (Q(1, 2), Q(2, 3), Q(3, 4), Q(1)))
def test_pair_agreement_from_independent_noises(q):
    exhaustive = sum((Q(1, 2)*
                      (q if z0 == theta else 1-q)*
                      (q if z1 == theta else 1-q)
                      for theta, z0, z1 in product((0, 1), repeat=3) if z0 == z1), Q(0))
    assert exhaustive == agreement_probability(q)


def test_two_labels_are_necessary_for_reliability_identification():
    assert state(DEFAULT_PRIOR, 1, 0)["q_posterior"] == DEFAULT_PRIOR
    assert after_pairs(DEFAULT_PRIOR, 1, 0) == (
        (Q(1, 2), Q(1, 3)), (Q(1), Q(2, 3)))
    assert after_pairs(DEFAULT_PRIOR, 0, 1) == (
        (Q(1, 2), Q(1)),)
    assert state(DEFAULT_PRIOR, 1, 1)["q_posterior"][-1][1] == 0


@pytest.mark.parametrize("trials", (0, 1, 2, 5, 12))
@pytest.mark.parametrize("cost", (Q(0), Q(1, 16), Q(1, 4), Q(1)))
@pytest.mark.parametrize("prior", (DEFAULT_PRIOR, ALT_PRIOR))
def test_bellman_matches_complete_binary_policy_enumeration(trials, cost, prior):
    cap = 2
    root = solve_epochs(prior, (trials,), (cap,), (cost,))
    candidates = []
    for b_root, b0, b1 in product((False, True), repeat=3):
        policy = {(): b_root, (0,): b0, (1,): b1}
        candidates.append(reference_policy_expected_value(prior, trials, cap, cost, policy))
    assert root["value_over_chance"] == max(candidates)
    assert root["value_identity"]
    assert root["expected_oracle_regret"] >= 0


@pytest.mark.parametrize("m", range(5))
@pytest.mark.parametrize("prior", (DEFAULT_PRIOR, ALT_PRIOR))
def test_fixed_budget_matches_direct_exhaustive_policy(prior, m):
    always_buy = {obs: True for n in range(m) for obs in product((0, 1), repeat=n)}
    expected = reference_policy_expected_value(prior, 7, m, Q(1, 8), always_buy)
    assert expected == fixed_budget_value(prior, 7, m, Q(1, 8))


def test_exploration_value_across_fresh_polarities():
    trials = (0,)+(6,)*12
    caps = (2,)+(1,)*12
    costs = (Q(1),)*13
    r = solve_epochs(DEFAULT_PRIOR, trials, caps, costs)
    assert r["value_over_chance"] == 7
    assert r["first_stop_value"] == 6
    assert r["first_buy_value"] == 7
    assert r["first_action"] == "buy"
    assert r["expected_gold_labels"] == 11
    assert r["expected_heldout_correct"] == 54
    assert r["expected_oracle_correct"] == 54
    assert r["expected_label_cost"] == 11
    assert r["value_identity"]
    # With only one label in the preliminary epoch, q is unlearnable.
    single = solve_epochs(DEFAULT_PRIOR, trials, (1,)+(1,)*12, costs)
    assert single["first_action"] == "stop"
    assert single["value_over_chance"] == 6
    # Removing future episodes also removes the reason to experiment.
    only_audit = solve_epochs(DEFAULT_PRIOR, (0,), (2,), (Q(1),))
    assert only_audit["first_action"] == "stop"
    assert only_audit["value_over_chance"] == 0


@pytest.mark.parametrize("true_q", (Q(1, 2), Q(1)))
@pytest.mark.parametrize("pairs", (1, 2, 3, 4, 8, 16, 32))
def test_reliability_identification_and_exact_chebyshev(true_q, pairs):
    success = identification_success(DEFAULT_PRIOR, true_q, pairs)
    upper = identification_chebyshev_bound(DEFAULT_PRIOR, true_q, pairs)
    assert 0 <= success <= 1
    assert 1-success <= upper
    if true_q == 1:
        assert success == 1


def test_identification_consistency_and_zero_one_boundaries():
    assert identification_success(DEFAULT_PRIOR, Q(1, 2), 2) == Q(3, 4)
    assert identification_success(DEFAULT_PRIOR, Q(1, 2), 3) == Q(7, 8)
    assert identification_success(DEFAULT_PRIOR, Q(1, 2), 16) > Q(98, 100)
    assert agreement_probability(Q(1, 2)) == Q(1, 2)
    assert agreement_probability(Q(1)) == 1
    assert fixed_budget_value(DEFAULT_PRIOR, 0, 0, Q(1)) == 0


@pytest.mark.parametrize("bad", ((), ((Q(1, 2),Q(1, 4)),),
                                 ((Q(1), Q(1, 2)),(Q(1, 2),Q(1, 2))),
                                 ((Q(1, 4), Q(1)),),
                                 ((Q(3, 4), Q(0)),(Q(1),Q(1))),
                                 ((Q(3, 4), Q(1, 2)),(Q(3, 4),Q(1, 2)))))
def test_invalid_priors_rejected(bad):
    with pytest.raises(ValueError):
        validate_prior(bad)


def test_input_failures_and_impossible_observations():
    with pytest.raises(TypeError):
        validate_prior(((Q(3, 4), 1.0),))
    with pytest.raises(ValueError):
        state(((Q(1), Q(1)),), 1, 1)
    with pytest.raises(ValueError):
        solve_epochs(DEFAULT_PRIOR, (), (), ())
    with pytest.raises(ValueError):
        solve_epochs(DEFAULT_PRIOR, (1, 2), (1,), (Q(1),Q(1)))
    with pytest.raises(ValueError):
        solve_epochs(DEFAULT_PRIOR, (2,), (-1,), (Q(1),))
    with pytest.raises(ValueError):
        solve_epochs(DEFAULT_PRIOR, (2,), (1,), (Q(-1),))
    with pytest.raises(TypeError):
        solve_epochs(DEFAULT_PRIOR, (2,), (1,), (0.1,))
    with pytest.raises(ValueError):
        after_pairs(((Q(1), Q(1)),), 0, 1)
    with pytest.raises(ValueError):
        identification_chebyshev_bound(DEFAULT_PRIOR, Q(1), 0)
    with pytest.raises(ValueError):
        identification_success(DEFAULT_PRIOR, Q(3, 4), 2)
    with pytest.raises(ValueError):
        identification_chebyshev_bound(((Q(3,4),Q(1)),), Q(3,4), 2)


def test_fixture_all_claims_exact():
    r = fixture()
    assert r["all_passed"]
    assert all(r["checks"].values())
    assert len(r["checks"]) >= 14
    assert r["real_agent_evidence"] is False
    assert r["theological_hypothesis_identified"] is False
    assert r["cryptographic_world_identified"] is False
    assert r["lean_formalized"] is False
