"""Boundary, independent-oracle, and corrupted-receipt tests for MIC-17."""
from copy import deepcopy
import unittest

import audit17 as audit
import mic17 as experiment
import mic16_reference as ref

assert_raises = unittest.TestCase().assertRaises


def homogeneous_problem():
    return ref.Problem(entries=((0, 0, 0),) * 3,
                       supports=(1, 2, 4, 3, 5, 6, 7),
                       reward=(0, 0, 0, 60, 60, 60, 90),
                       weights=(1, 2, 3, 4, 1, 2, 3, 4),
                       catalog=tuple(((True, 1),) * 8 for _ in range(7)))


def test_partition_dp_matches_all_partitions_and_capacity_boundaries():
    # Reward comes from choosing one of two classes of worlds. Two labels can
    # preserve all 40 points; one label can preserve only 20.
    values = [10 * max((mask & 5).bit_count(), (mask & 10).bit_count()) for mask in range(16)]
    brute = audit.partition_optima(values)
    dp = experiment.best_partitions(values, max_codes=4)
    assert len(audit.all_partitions(4)) == 15
    assert len(audit.all_partitions(8)) == 4140
    assert brute[1:] == [20, 40, 40, 40]
    assert [dp[k][0] for k in range(1, 5)] == brute[1:]
    assert dp[2][1] == (5, 10)
    assert all(value == 7 and cells == (1,) for value, cells in experiment.best_partitions([0, 7]).values())
    with assert_raises(AssertionError):
        experiment.best_partitions([0])
    with assert_raises(AssertionError):
        experiment.best_partitions([0, 1, 2])


def test_identical_catalog_worlds_need_one_code_with_nonuniform_prior():
    d = homogeneous_problem()
    independent, _ = audit.independent_oracle(d)
    p = ref.Planner(d)
    values = [0]
    for mask in range(1, 256):
        value = independent(frozenset(), audit.worlds_from_mask(mask), 2)
        assert value == p.choice(0, mask, 2, 2)[0]
        assert value == 150 * sum(d.weights[w] for w in audit.worlds_from_mask(mask))
        values.append(value)
    optimal = experiment.best_partitions(values)
    assert all(result == (3000, (255,)) for result in optimal.values())
    p.choice.cache_clear()


def test_redundant_probe_remains_an_optimal_first_action_with_slack():
    d = homogeneous_problem()
    p = ref.Planner(d)
    values = [0] * 256
    for mask in (1, 2, 3):
        values[mask] = p.choice(0, mask, 5, 5)[0]
    probe = p.actions.index(("probe", 0))
    assert p.transitions(0, 1, 5, probe) == ()
    assert experiment.raw_transitions(p, 0, 1, 5, probe)
    reported = experiment.first_action_alias(p, values, 5, 0, 1)
    assert probe in reported["optimal_first_actions"]["0"]
    assert probe in reported["optimal_first_actions"]["1"]
    assert reported["common_first_value"] == reported["full_value"]
    independent = audit.independent_oracle(d)
    full, common, belief, action_values = audit.pair_alias_values(d, (0, 1), 5, independent)
    assert full == common == belief == 810
    assert action_values[probe] == common
    empty = experiment.first_action_alias(p, [0] * 256, 0, 0, 1)
    assert empty["optimal_first_actions"] == {"0": [-1], "1": [-1]}
    p.choice.cache_clear()


def test_weighted_conflict_has_exact_common_action_loss():
    d = homogeneous_problem()
    catalog = [[(False, 1)] * 8 for _ in range(7)]
    catalog[3][0] = (True, 1)
    catalog[4][1] = (True, 1)
    d = ref.Problem(d.entries, d.supports, d.reward, (1, 3, 1, 1, 1, 1, 1, 1),
                    tuple(tuple(row) for row in catalog))
    p = ref.Planner(d)
    values = [0] * 256
    for mask in (1, 2, 3):
        values[mask] = p.choice(0, mask, 1, 1)[0]
    reported = experiment.first_action_alias(p, values, 1, 0, 1)
    independent = audit.independent_oracle(d)
    assert audit.pair_alias_values(d, (0, 1), 1, independent)[:3] == (240, 180, 180)
    assert reported["full_value"] - reported["common_first_value"] == 60
    assert reported["optimal_first_actions"] == {"0": [10], "1": [11]}
    assert reported["shares_primary_window_1"] and reported["shares_primary_window_2"]
    p.choice.cache_clear()


def test_handoff_replay_rejects_tampered_memory_reward_cost_and_posterior():
    d = homogeneous_problem()
    p = ref.Planner(d)
    independent = audit.independent_oracle(d)
    histories = experiment.prefix_histories(p)
    assert audit.check_prefix(histories, 12) == 48
    receipt = experiment.rollout(p, 0, 5, 255)
    assert audit.check_receipt(d, 0, 5, [255], receipt, independent) == 270
    corruptions = []
    bad = deepcopy(receipt)
    bad["initial_mask"] = 1
    corruptions.append(bad)
    bad = deepcopy(receipt)
    bad["reward"] += 1
    corruptions.append(bad)
    bad = deepcopy(receipt)
    bad["path"][0][2][1] += 1
    corruptions.append(bad)
    bad = deepcopy(receipt)
    bad["path"][0][4] = 1
    corruptions.append(bad)
    for bad in corruptions:
        with assert_raises(AssertionError):
            audit.check_receipt(d, 0, 5, [255], bad, independent)
    with assert_raises(AssertionError):
        audit.validate_partition([255, 1])
    bad_histories = deepcopy(histories)
    bad_histories[0][0][2][2] = 1
    with assert_raises(AssertionError):
        audit.check_prefix(bad_histories, 12)
    p.choice.cache_clear()


def test_fresh_fixture_full_independent_audit():
    # This seed is outside both the pilot and registered development sweep.
    row = experiment.evaluate_root("mixed", 17099)
    checked = audit.audit_root(row)
    assert checked["verified_mask_values"] == 255
    assert checked["enumerated_partitions"] == 4140
    assert checked["verified_trajectories"] == 48
    assert checked["pair_alias_checks"] == 28


def load_tests(loader, tests, pattern):
    """Keep the test suite runnable with Python's standard library alone."""
    return unittest.TestSuite(unittest.FunctionTestCase(test) for name, test in globals().items()
                              if name.startswith("test_") and callable(test))


if __name__ == "__main__":
    unittest.main()

