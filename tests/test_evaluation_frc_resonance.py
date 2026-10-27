"""Independent exact checks, including arbitrary no-hit adaptive query paths."""
from fractions import Fraction as Q
from itertools import product
import pytest

from spiral_ln.evaluation_frc_resonance import (
    DesignState, choose_self_eval, design_trajectory, fidelity_certificate,
    min_entropy_coverage_cap, min_entropy_effective_support,
    necessary_queries, necessary_queries_by_coverage,
    optimal_coverage, oracle_coverage, train_on_selected,
    uniform_depth_query_floor, uniform_depth_query_floor_sharp,
    sharp_coverage_threshold, optimal_randomized_power,
    necessary_queries_sharp, necessary_queries_by_coverage_sharp,
    verify, weakness_external_floor,
)


def test_exact_nonuniform_optimal_coverage_by_exhaustion():
    prior = (Q(1, 2), Q(1, 4), Q(1, 8), Q(1, 8))
    for budget in range(5):
        brute = max(oracle_coverage(prior, path)
                    for path in product(range(4), repeat=budget))
        assert brute == optimal_coverage(prior, budget)
        assert brute <= min_entropy_coverage_cap(prior, budget)
    assert min_entropy_effective_support(prior) == Q(2)


def test_every_adaptive_deterministic_strategy_has_no_hit_path():
    # With an equality oracle, the only pre-hit response sequence is (0,...,0).
    # For all possible adaptive no-hit branches, coverage is bounded by top-q.
    prior = tuple(Q(v, 10) for v in (1, 2, 3, 4))
    for budget in (0, 1, 2, 3):
        assert all(oracle_coverage(prior, path) <= optimal_coverage(prior, budget)
                   for path in product(range(4), repeat=budget))


def test_randomized_policy_is_convex_combination_of_deterministic_paths():
    prior = tuple(Q(v, 10) for v in (1, 2, 3, 4))
    paths = tuple(product(range(4), repeat=2))
    weight = Q(1, len(paths))
    randomized = sum((weight * oracle_coverage(prior, path) for path in paths), Q(0))
    assert randomized <= optimal_coverage(prior, 2)


def test_min_entropy_bound_can_be_strictly_weaker():
    prior = (Q(1, 2), Q(1, 4), Q(1, 8), Q(1, 8))
    assert necessary_queries(prior, Q(1, 10)) == 2
    assert necessary_queries_by_coverage(prior, Q(1, 10)) == 3
    assert optimal_coverage(prior, 2) == Q(3, 4) < Q(4, 5)


@pytest.mark.parametrize("depth", range(10))
def test_uniform_depth_formula_agrees_with_materialized_prior(depth):
    prior = (Q(1, 2**depth),) * (2**depth)
    for delta in (Q(0), Q(1, 10), Q(1, 4), Q(1, 2), Q(3, 4)):
        assert uniform_depth_query_floor(depth, delta) == necessary_queries(prior, delta)


def test_recursive_exponent_has_exact_geometric_floor():
    # For delta=1/10, q_k >= (4/5) * 2^k, hence ln(1+q_k)/k >=
    # ln(4/5)/k + ln(2) for k>0. The latter lower bound tends to ln(2).
    assert all(Q(uniform_depth_query_floor(k, Q(1, 10)), 2**k) >= Q(4, 5)
               for k in range(1, 22))


def test_fidelity_partition_identity_on_all_binary_joint_distributions():
    # Joint law for (P_fail,J_reject). P_fail probability is two of the cells.
    for a, b, c in product(range(8), repeat=3):
        if a + b + c > 7:
            continue
        d = 7 - a - b - c
        fail_and_reject = Q(a, 7)
        fail_and_accept = Q(b, 7)
        pass_and_reject = Q(c, 7)
        pass_and_accept = Q(d, 7)
        external_fidelity = pass_and_reject + pass_and_accept
        judge_reject = fail_and_reject + pass_and_reject
        assert external_fidelity >= fidelity_certificate(judge_reject, fail_and_accept)


def test_fidelity_bound_attains_equality_without_false_rejection_of_good():
    assert fidelity_certificate(Q(1, 5), Q(1, 10)) == Q(7, 10)


def test_false_resonance_exact_trajectory_and_external_collapse():
    p = design_trajectory("self_confirming", 32)
    assert p["final"].second == Q(9, 20) * Q(3, 4)**32
    assert p["final"].first > Q(999, 1000)
    assert all(row["eval_design_task"] == 0 for row in p["records"])
    assert all(row["predicted_gain"] == row["observed_gain"] for row in p["records"])


def test_weakness_selection_floor_holds_over_many_rational_parameters():
    for numerator in range(1, 20):
        initial = DesignState(Q(numerator, 20), Q(20-numerator, 20))
        for eta in (Q(0), Q(1, 10), Q(1, 4), Q(1, 2), Q(1)):
            result = design_trajectory("weakness_seeking", 18, initial=initial, rate=eta)
            floor = weakness_external_floor(initial, eta)
            assert all(row["external_property_task_1"] >= floor for row in result["records"])


def test_training_preserves_capacity_and_predicted_gain():
    for a in (Q(0), Q(1, 4), Q(1, 2), Q(3, 4), Q(1)):
        state = DesignState(a, 1-a)
        for eta in (Q(0), Q(1, 3), Q(1)):
            for j in (0, 1):
                nxt = train_on_selected(state, j, eta)
                assert nxt.first + nxt.second == 1
                assert (nxt.first if j==0 else nxt.second) >= (state.first if j==0 else state.second)


def test_alternating_and_weakness_are_distinct_policy_controls():
    a = design_trajectory("alternating", 11)
    b = design_trajectory("weakness_seeking", 11)
    assert a["final"] != b["final"]
    assert choose_self_eval(DesignState(Q(1, 2), Q(1, 2)), "self_confirming", 0) == 0
    assert choose_self_eval(DesignState(Q(1, 2), Q(1, 2)), "weakness_seeking", 0) == 0


def test_invalid_parameter_and_stronger_information_leaks():
    with pytest.raises(ValueError):
        optimal_coverage((Q(1, 2),), 1)
    with pytest.raises(ValueError):
        oracle_coverage((Q(1),), [2])
    with pytest.raises(ValueError):
        uniform_depth_query_floor(-1, Q(1, 4))
    with pytest.raises(ValueError):
        necessary_queries((Q(1),), Q(-1, 10))
    with pytest.raises(ValueError):
        DesignState(Q(1, 3), Q(1, 3))
    with pytest.raises(ValueError):
        design_trajectory("unknown", 2)
    assert verify()["all_passed"]


def test_sharp_coverage_threshold_boundary_and_nonuniform_query_floor():
    p = (Q(1, 2), Q(1, 4), Q(1, 8), Q(1, 8))
    assert sharp_coverage_threshold(Q(0)) == 1
    assert sharp_coverage_threshold(Q(1, 10)) == Q(8, 9)
    assert sharp_coverage_threshold(Q(1, 4)) == Q(2, 3)
    assert sharp_coverage_threshold(Q(1, 2)) == 0
    assert sharp_coverage_threshold(Q(1)) == 0
    assert necessary_queries_by_coverage_sharp(p, Q(1, 10)) == 4
    assert necessary_queries_sharp(p, Q(1, 10)) == 2
    assert necessary_queries_by_coverage(p, Q(1, 10)) == 3
    for d in (Q(0), Q(1, 10), Q(1, 4), Q(1, 2), Q(3, 4), Q(1)):
        assert necessary_queries_by_coverage_sharp(p, d) >= necessary_queries_by_coverage(p, d)


def test_uniform_exponential_sharp_floor_and_attainable_randomized_witness():
    for k in range(11):
        prior = (Q(1, 2**k),) * 2**k
        for delta in (Q(0), Q(1, 10), Q(1, 4), Q(1, 2), Q(3, 4), Q(1)):
            expected = uniform_depth_query_floor_sharp(k, delta)
            assert expected == necessary_queries_by_coverage_sharp(prior, delta)
            assert expected >= uniform_depth_query_floor(k, delta)
            assert optimal_randomized_power(prior, expected, delta) >= 1-delta
            if expected:
                assert optimal_randomized_power(prior, expected-1, delta) < 1-delta
    assert uniform_depth_query_floor_sharp(8, Q(1, 10)) == 228
    assert uniform_depth_query_floor_sharp(12, Q(1, 10)) == 3641


def _strategies(size, depth):
    """Exhaust all deterministic boolean decision trees for tiny sizes."""
    if depth == 0:
        return (False, True)
    smaller = _strategies(size, depth-1)
    return tuple((i, no, yes) for i in range(size) for no in smaller for yes in smaller)


def _run_strategy(tree, hidden):
    """hidden=None means benign; otherwise equality-oracle trigger index."""
    while isinstance(tree, tuple):
        index, no, yes = tree
        tree = yes if hidden == index else no
    return tree


def test_exhaustive_adaptive_auditors_obey_sharp_seedwise_coupling():
    p = (Q(1, 2), Q(1, 3), Q(1, 6))
    q = 2
    cov = optimal_coverage(p, q)
    trees = _strategies(len(p), q)
    # 2 -> 3*(3*4)^2=432 decision trees, including deliberate false positives.
    assert len(trees) == 432
    for tree in trees:
        benign = Q(int(_run_strategy(tree, None)))
        triggered = sum((px*int(_run_strategy(tree, x)) for x, px in enumerate(p)), Q(0))
        assert triggered <= benign + (1-benign)*cov
    # Every pair of tree seeds is a uniform randomized strategy.
    observed = [(Q(int(_run_strategy(t, None))),
                 sum((px*int(_run_strategy(t, x)) for x, px in enumerate(p)), Q(0)))
                for t in trees]
    for i in range(len(observed)):
        for j in (i, (i+17) % len(observed), (i+131) % len(observed)):
            false_alarm = (observed[i][0] + observed[j][0])/2
            power = (observed[i][1] + observed[j][1])/2
            assert power <= false_alarm + (1-false_alarm)*cov


def test_randomized_achievability_is_exact_under_two_sided_constraints():
    prior = (Q(1, 4),) * 4
    delta = Q(1, 4)
    assert necessary_queries_by_coverage_sharp(prior, delta) == 3
    # One of four independent auditor coins rejects immediately. The other
    # three scan {0,1,2} and reject only on a hit. Uniform-trigger detection:
    reject_given_trigger = []
    for target in range(4):
        seed_outputs = [True] + [target in (0,1,2)]*3
        reject_given_trigger.append(Q(sum(seed_outputs), 4))
    power = sum((px*power_x for px,power_x in zip(prior,reject_given_trigger)),Q(0))
    assert power == Q(13, 16) == optimal_randomized_power(prior, 3, delta)
    assert delta <= delta and power >= 1-delta
    assert optimal_randomized_power(prior, 2, delta) == Q(5, 8) < 1-delta
