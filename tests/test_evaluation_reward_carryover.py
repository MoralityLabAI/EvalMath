"""Independent finite-path checks for RHT-26's declared carryover model."""

from fractions import Fraction as Q
from itertools import product
import random

import pytest

from spiral_ln.evaluation_reward_carryover import (
    STATES, ZERO_STATE, IDENTITY, RESET_ARTIFACT, RESET_ALL,
    Kernel, Episode, JointOutcome, CueExperiment, apply, compose, evolve,
    run_episodes, factorial, total_variation, dobrushin, transmission_certificate,
    copied_cues, iid_cues, carryover_fixture, accumulation_fixture, state_law,
)


def deterministic_kernel(next_state):
    return Kernel(tuple(tuple(Q(target == next_state(source)) for target in STATES)
                        for source in STATES))


def normalized(weights):
    total = sum(weights)
    if total == 0:
        weights = [1] + list(weights[1:])
        total = 1
    return tuple(Q(weight, total) for weight in weights)


def independent_paths(initial, episodes, *, keep_artifacts, learn,
                      reset_before_update=False):
    """Expand latent trajectories without matrix composition or state merging."""
    paths = [(state, mass) for state, mass in zip(STATES, initial) if mass]
    for episode in episodes:
        next_paths = []
        for state, mass in paths:
            for intermediate, write_probability in zip(
                STATES, episode.exposure.rows[STATES.index(state)]
            ):
                if not write_probability:
                    continue
                read_state = intermediate
                if not keep_artifacts and reset_before_update:
                    read_state = (0, read_state[1])
                if learn:
                    updates = zip(STATES, episode.update.rows[STATES.index(read_state)])
                else:
                    updates = ((read_state, Q(1)),)
                for following, update_probability in updates:
                    if not update_probability:
                        continue
                    if not keep_artifacts and not reset_before_update:
                        following = (0, following[1])
                    next_paths.append((following, mass * write_probability * update_probability))
        paths = next_paths
    return paths


def independent_state_and_outcomes(paths, endpoint):
    state_mass = [Q(0)] * 4
    outcome_mass = [Q(0)] * 4
    for state, mass in paths:
        index = STATES.index(state)
        state_mass[index] += mass
        for outcome, probability in enumerate(endpoint.rows[index]):
            outcome_mass[outcome] += mass * probability
    return tuple(state_mass), tuple(outcome_mass)


def random_episode(rng):
    writes, updates = [], []
    for memory, policy in STATES:
        write_law = normalized([rng.randrange(5), rng.randrange(5)])
        update_law = normalized([rng.randrange(5), rng.randrange(5)])
        writes.append(tuple(write_law[m] if z == policy else Q(0) for m, z in STATES))
        updates.append(tuple(update_law[z] if m == memory else Q(0) for m, z in STATES))
    return Episode(Kernel(tuple(writes)), Kernel(tuple(updates)))


def test_fixture_exact_factorial_and_selected_denominator_reversal():
    episode, endpoint = carryover_fixture()
    expected = {
        (False, False): (Q(1, 8), Q(1, 4), Q(1, 2)),
        (False, True): (Q(5, 32), Q(9, 32), Q(5, 9)),
        (True, False): (Q(9, 64), Q(5, 16), Q(9, 20)),
        (True, True): (Q(13, 64), Q(11, 32), Q(13, 22)),
    }
    result = factorial(ZERO_STATE, (episode,), endpoint)
    for arm in result.arms:
        joint, pre, conditional = expected[(arm.keep_artifacts, arm.learn)]
        assert arm.outcome.joint_persistence == arm.outcome.post_drift == joint
        assert arm.outcome.pre_drift == pre
        assert arm.outcome.conditional_persistence == conditional
    assert result.interaction == Q(1, 32)
    assert expected[(True, False)][0] > expected[(False, False)][0]
    assert expected[(True, False)][2] < expected[(False, False)][2]


def test_two_exposures_retain_joint_history_and_horizon_zero():
    episode, endpoint = carryover_fixture()
    empty = factorial(ZERO_STATE, (), endpoint)
    assert empty.interaction == 0
    assert all(arm.final_state == ZERO_STATE for arm in empty.arms)
    result = factorial(ZERO_STATE, (episode, episode), endpoint)
    assert tuple(arm.outcome.joint_persistence for arm in result.arms) == (
        Q(1, 8), Q(47, 256), Q(73, 512), Q(133, 512)
    )
    assert result.interaction == Q(15, 256)
    assert result.arms[-1].final_state == (Q(49, 64), Q(1, 32), Q(0), Q(13, 64))


def test_independent_full_path_enumeration_including_joint_endpoint():
    rng = random.Random(260112)
    for horizon in range(4):
        for _ in range(5):
            initial = normalized([rng.randrange(6) for _ in STATES])
            episodes = tuple(random_episode(rng) for _ in range(horizon))
            endpoint = JointOutcome(tuple(normalized([rng.randrange(5) for _ in range(4)])
                                          for _ in STATES))
            for keep, learn, before in product((False, True), repeat=3):
                paths = independent_paths(initial, episodes, keep_artifacts=keep, learn=learn,
                                          reset_before_update=before)
                expected_state, expected_joint = independent_state_and_outcomes(paths, endpoint)
                actual = run_episodes(initial, episodes, keep_artifacts=keep, learn=learn,
                                      reset_before_update=before)
                report = endpoint.report(actual)
                assert actual == expected_state
                assert report.joint_law == expected_joint
                assert report.pre_drift == expected_joint[2] + expected_joint[3]
                assert report.post_drift == expected_joint[1] + expected_joint[3]
                assert report.joint_persistence == expected_joint[3]
                expected_ratio = expected_joint[3] / report.pre_drift if report.pre_drift else None
                assert report.conditional_persistence == expected_ratio
                assert sum(report.joint_law) == sum(actual) == 1


def test_boundary_order_controls_whether_an_update_reads_the_artifact():
    write_hook = deterministic_kernel(lambda state: (1, state[1]))
    copy_to_policy = deterministic_kernel(lambda state: (state[0], state[0] | state[1]))
    episode = Episode(write_hook, copy_to_policy)
    after = run_episodes(ZERO_STATE, (episode,), keep_artifacts=False, learn=True)
    before = run_episodes(ZERO_STATE, (episode,), keep_artifacts=False, learn=True,
                          reset_before_update=True)
    assert after == (Q(0), Q(1), Q(0), Q(0))
    assert before == ZERO_STATE
    assert compose(write_hook, copy_to_policy, RESET_ARTIFACT).rows != (
        compose(write_hook, RESET_ARTIFACT, copy_to_policy).rows
    )
    assert run_episodes(ZERO_STATE, (episode,), keep_artifacts=False, learn=False) == ZERO_STATE


def test_frozen_policy_preserves_its_initial_value_instead_of_resetting_it():
    episode, _ = carryover_fixture()
    initial = (Q(0), Q(1, 3), Q(0), Q(2, 3))
    final = run_episodes(initial, (episode,) * 4, keep_artifacts=False, learn=False)
    assert final == (Q(0), Q(1), Q(0), Q(0))
    assert apply(final, RESET_ALL) == ZERO_STATE


def test_equal_marginals_do_not_determine_persistence():
    correlated = (Q(1, 2), Q(0), Q(0), Q(1, 2))
    anticorrelated = (Q(0), Q(1, 2), Q(1, 2), Q(0))
    endpoint = JointOutcome(tuple((Q(1 - (m & z)), 0, 0, Q(m & z)) for m, z in STATES))
    for law in (correlated, anticorrelated):
        assert law[2] + law[3] == law[1] + law[3] == Q(1, 2)
    assert endpoint.report(correlated).joint_persistence == Q(1, 2)
    assert endpoint.report(anticorrelated).joint_persistence == 0


def test_complete_reset_erases_history_and_partial_reset_retains_policy():
    left, right = ZERO_STATE, (0, 0, 0, 1)
    assert dobrushin(RESET_ALL) == 0
    assert dobrushin(RESET_ARTIFACT) == dobrushin(IDENTITY) == 1
    assert apply(left, RESET_ALL) == apply(right, RESET_ALL)
    assert apply(left, RESET_ARTIFACT) != apply(right, RESET_ARTIFACT)
    episode, endpoint = carryover_fixture()
    future = episode.kernel(keep_artifacts=True, learn=True)
    certificate = transmission_certificate(left, right, (future, RESET_ALL, future), endpoint)
    assert certificate.initial_tv == 1
    assert certificate.final_tv == certificate.contraction_bound == certificate.outcome_tv == 0
    assert certificate.joint_persistence_gap == certificate.pre_drift_gap == certificate.post_drift_gap == 0


def test_transmission_bound_has_a_sharp_nonzero_rational_witness():
    def soft_reset(probability):
        return Kernel(tuple(tuple((1 - probability) * IDENTITY.rows[i][j]
                                  + probability * RESET_ALL.rows[i][j]
                                  for j in range(4)) for i in range(4)))
    kernels = (soft_reset(Q(1, 4)), soft_reset(Q(1, 2)))
    endpoint = JointOutcome(tuple((1 - z, 0, 0, z) for _, z in STATES))
    result = transmission_certificate(ZERO_STATE, (0, 1, 0, 0), kernels, endpoint)
    assert result.contraction_coefficients == (Q(3, 4), Q(1, 2))
    assert result.contraction_bound == result.final_tv == Q(3, 8)
    assert result.outcome_tv == result.joint_persistence_gap == Q(3, 8)
    assert evolve((0, 1, 0, 0), ()) == state_law((0, 1, 0, 0))
    assert compose().rows == IDENTITY.rows


def test_joint_outcomes_allow_new_drift_and_undefined_conditional_persistence():
    no_prior_drift = JointOutcome(((Q(1, 4), Q(3, 4), 0, 0),) * 4).report(ZERO_STATE)
    assert no_prior_drift.pre_drift == no_prior_drift.joint_persistence == 0
    assert no_prior_drift.post_drift == Q(3, 4)
    assert no_prior_drift.conditional_persistence is None
    mutually_exclusive = JointOutcome(((0, Q(1, 2), Q(1, 2), 0),) * 4).report(ZERO_STATE)
    assert mutually_exclusive.pre_drift * mutually_exclusive.post_drift == Q(1, 4)
    assert mutually_exclusive.joint_persistence == 0


def test_copied_cues_and_independent_cues_have_different_likelihoods():
    for count in range(1, 7):
        copied = copied_cues(Q(3, 4), Q(1, 4), count)
        fresh = iid_cues(Q(3, 4), Q(1, 4), count)
        ones = "1" * count
        assert copied.posterior(Q(1, 2), copied.transcripts.index(ones)) == Q(3, 4)
        assert fresh.posterior(Q(1, 2), fresh.transcripts.index(ones)) == Q(3**count, 1 + 3**count)
        assert total_variation(copied.evaluation, copied.deployment) == Q(1, 2)
        if count > 1:
            mixed = copied.transcripts.index("0" * (count - 1) + "1")
            assert copied.posterior(Q(1, 2), mixed) is None
    assert iid_cues(Q(3, 4), Q(1, 4), 3).posterior(Q(1, 2), 7) == Q(27, 28)


def test_cue_bayes_martingale_zero_exposures_and_prior_boundaries():
    for make in (copied_cues, iid_cues):
        empty = make(Q(3, 4), Q(1, 4), 0)
        assert empty.transcripts == ("",)
        assert empty.evaluation == empty.deployment == (Q(1),)
        assert empty.posterior(Q(2, 7), 0) == Q(2, 7)
        for e, d, prior in product((Q(0), Q(1, 4), Q(1)), repeat=3):
            experiment = make(e, d, 3)
            average = Q(0)
            for index, (pe, pd) in enumerate(zip(experiment.evaluation, experiment.deployment)):
                probability = prior * pe + (1 - prior) * pd
                posterior = experiment.posterior(prior, index)
                if probability:
                    average += probability * posterior
                else:
                    assert posterior is None
            assert average == prior


def test_accumulation_family_including_certain_and_zero_write_boundaries():
    endpoint = JointOutcome(tuple((1 - m, 0, 0, m) for m, _ in STATES))
    for p in (Q(0), Q(1, 4), Q(1)):
        episode = accumulation_fixture(p)
        for horizon in range(8):
            retained = run_episodes(ZERO_STATE, (episode,) * horizon,
                                    keep_artifacts=True, learn=False)
            erased = run_episodes(ZERO_STATE, (episode,) * horizon,
                                  keep_artifacts=False, learn=False)
            assert endpoint.report(retained).joint_persistence == 1 - (1 - p) ** horizon
            assert endpoint.report(erased).joint_persistence == 0


def test_validation_rejects_bad_stochastic_objects_and_channel_cross_writes():
    for bad_law in ((0, 0, 0, 0), (1, 0, 0), (2, -1, 0, 0), (1.0, 0, 0, 0)):
        with pytest.raises(ValueError):
            state_law(bad_law)
    for constructor in (Kernel, JointOutcome):
        with pytest.raises(ValueError):
            constructor(((1, 0, 0, 0),) * 3)
        with pytest.raises(ValueError):
            constructor(((Q(1, 2), 0, 0, 0),) * 4)
        with pytest.raises(ValueError):
            constructor(((True, 0, 0, 0),) * 4)
    changes_policy = deterministic_kernel(lambda state: (state[0], 1 - state[1]))
    changes_artifact = deterministic_kernel(lambda state: (1 - state[0], state[1]))
    with pytest.raises(ValueError):
        Episode(changes_policy, IDENTITY)
    with pytest.raises(ValueError):
        Episode(IDENTITY, changes_artifact)
    with pytest.raises(ValueError):
        CueExperiment(("same", "same"), (Q(1, 2), Q(1, 2)), (Q(1, 2), Q(1, 2)))
    for make in (copied_cues, iid_cues):
        for count in (-1, True, 1.5, 13):
            with pytest.raises(ValueError):
                make(Q(1, 2), Q(1, 2), count)
    cues = copied_cues(Q(1, 2), Q(1, 2), 1)
    for prior, index in ((Q(-1), 0), (Q(2), 0), (0.5, 0), (Q(1, 2), -1), (Q(1, 2), True)):
        with pytest.raises(ValueError):
            cues.posterior(prior, index)
