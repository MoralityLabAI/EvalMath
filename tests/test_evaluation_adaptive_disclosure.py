"""Cross-checked exact-adaptive disclosure and one-hot interval theorems."""
from fractions import Fraction as Q
from itertools import combinations, product

import pytest

from spiral_ln.evaluation_adaptive_disclosure import (
    FinitePrior, Node, adaptive_optimum, direct_bit_profile, fair_bit_prior,
    fixed_optimum, fixed_tree, interval_bank, leaf_fibres, one_hot_interval_law,
    one_hot_prior, partition, prefix_collision_sequence, prefix_refinement,
    reachable_alphabet_bound, transcript, transcript_profile, tree_as_data,
    validate_queries,
)


def test_fair_priors_and_direct_record_oracle():
    for capacities in ((1,), (1, 1), (2, 1), (1, 2, 1), (2, 2)):
        prior = fair_bit_prior(capacities)
        bank = interval_bank(len(capacities))
        for schedule in ((), (0,), (len(bank) - 1,),
                         (0, len(bank) - 1), (1 if len(bank) > 1 else 0, 0)):
            tree = fixed_tree(prior, bank, schedule)
            assert transcript_profile(prior, bank, tree) == direct_bit_profile(capacities, bank, tree)
            assert prefix_refinement(prior, bank, tree)
            assert len(leaf_fibres(prior, bank, tree)) == transcript_profile(prior, bank, tree)["leaves"]
            seq = prefix_collision_sequence(prior, bank, tree)
            assert seq[0] == 1 and seq[-1] == transcript_profile(prior, bank, tree)["observed_collision_probability"]
            report = reachable_alphabet_bound(prior, bank, tree)
            assert report["reachable_leaves"] <= report["product_bound"]


def test_leaf_equations_need_path_answers_as_well_as_kernel():
    prior = fair_bit_prior((1, 1))
    bank = ((1, 1),)
    tree = fixed_tree(prior, bank, (0,))
    leaves = leaf_fibres(prior, bank, tree)
    assert leaves[((0, 0),)] == ((0, 0),)
    assert set(leaves[((0, 1),)]) == {(0, 1), (1, 0)}
    assert leaves[((0, 2),)] == ((1, 1),)
    assert transcript_profile(prior, bank, tree)["strict"]


def test_all_8_location_interval_optima_and_certified_gap():
    prior, queries = one_hot_prior(8), interval_bank(8)
    a, f = adaptive_optimum(prior, queries, 3), fixed_optimum(prior, queries, 3)
    assert a["mass"] == 8 and f["mass"] == 6
    assert f["schedules_checked"] == 8436
    assert a["bayes_success"] == Q(1) and f["bayes_success"] == Q(3, 4)
    assert one_hot_interval_law(8, 3) == {"adaptive": 8, "fixed": 6}
    assert transcript_profile(prior, queries, a["tree"])["leaves"] == 8
    assert prefix_collision_sequence(prior, queries, a["tree"]) == (Q(1), Q(1, 2), Q(1, 4), Q(1, 8))
    assert reachable_alphabet_bound(prior, queries, a["tree"])["product_bound"] == 8
    assert transcript_profile(prior, queries, fixed_tree(prior, queries, f["schedule"]))["leaves"] == 6
    assert tree_as_data(a["tree"]) is not None


def test_unrestricted_subset_queries_remove_the_interval_gap():
    # Three fixed, non-contiguous bit-position queries encode all eight locations.
    prior = one_hot_prior(8)
    code_queries = tuple(tuple((i >> bit) & 1 for i in range(8)) for bit in range(3))
    profile = transcript_profile(prior, code_queries, fixed_tree(prior, code_queries, (0, 1, 2)))
    assert profile["leaves"] == 8 and profile["bayes_success"] == 1
    assert profile["joint_collision_probability"] == Q(1, 8)


def test_arbitrary_positive_integer_prior_weights():
    prior = FinitePrior((1, 1), ((0, 0), (0, 1), (1, 0), (1, 1)), (1, 2, 3, 7))
    bank = ((1, 0), (0, 1))
    adaptive = adaptive_optimum(prior, bank, 1)
    fixed = fixed_optimum(prior, bank, 1)
    assert adaptive["bayes_success"] == fixed["bayes_success"] == Q(10, 13)
    assert transcript_profile(prior, bank, adaptive["tree"])["bayes_success"] == Q(10, 13)


def test_law_exhaustively_against_both_optimizers():
    for n, k in ((1, 0), (1, 2), (2, 1), (3, 1), (3, 2), (4, 2),
                 (5, 2), (5, 3), (6, 2), (6, 3), (7, 3), (8, 3)):
        prior, queries = one_hot_prior(n), interval_bank(n)
        law = one_hot_interval_law(n, k)
        assert adaptive_optimum(prior, queries, k)["mass"] == law["adaptive"]
        assert fixed_optimum(prior, queries, k)["mass"] == law["fixed"]


def test_explicit_constructive_fixed_schedule_tightness():
    for k in range(1, 5):
        n = 2 * k
        prior, bank = one_hot_prior(n), interval_bank(n)
        query_vectors = tuple(tuple(int(i <= x < i + k) for x in range(n)) for i in range(k))
        schedule = tuple(bank.index(q) for q in query_vectors)
        assert transcript_profile(prior, bank, fixed_tree(prior, bank, schedule))["leaves"] == n
    for n in range(1, 9):
        for k in range(1, 5):
            assert one_hot_interval_law(n, k)["fixed"] <= min(n, 2 * k)
            assert one_hot_interval_law(n, k)["adaptive"] <= min(n, 2 ** k)


def test_branchwise_queries_are_essential_union_full_rank_is_insufficient():
    bank = ((1, 0), (0, 1))
    prior = fair_bit_prior((1, 1))
    terminal = Node()
    tree = Node(0, ((0, Node(1, ((0, terminal), (1, terminal)))),
                    (1, Node(0, ((1, terminal),)))))
    leaves = partition(prior, bank, tree)
    assert len(leaves) == 3
    assert transcript((1, 0), tree, bank) == transcript((1, 1), tree, bank)
    assert transcript((0, 0), tree, bank) != transcript((0, 1), tree, bank)
    assert transcript_profile(prior, bank, tree)["bayes_success"] == Q(3, 4)
    assert prefix_collision_sequence(prior, bank, tree) == (Q(1), Q(1, 2), Q(3, 8))
    assert reachable_alphabet_bound(prior, bank, tree)["reachable_leaves"] == 3


def test_adaptive_optimum_on_full_box_agrees_with_brute_policy_search():
    prior = fair_bit_prior((2, 1, 1))
    bank = interval_bank(3)
    for budget in range(3):
        adaptive = adaptive_optimum(prior, bank, budget)
        fixed = fixed_optimum(prior, bank, budget)
        assert adaptive["bayes_success"] >= fixed["bayes_success"]
        assert transcript_profile(prior, bank, adaptive["tree"])["bayes_success"] == adaptive["bayes_success"]
        assert prefix_refinement(prior, bank, adaptive["tree"])
        assert transcript_profile(prior, bank, adaptive["tree"]) == direct_bit_profile(prior.capacities, bank, adaptive["tree"])


def test_monotonic_conditional_collision_loss_and_budget():
    p, bank = fair_bit_prior((1, 2, 1)), interval_bank(3)
    for budget in range(4):
        tree = adaptive_optimum(p, bank, budget)["tree"]
        cp = prefix_collision_sequence(p, bank, tree)
        assert all(a >= b for a, b in zip(cp, cp[1:]))
        assert sum(a - b for a, b in zip(cp, cp[1:])) == 1 - cp[-1]
        assert reachable_alphabet_bound(p, bank, tree)["reachable_leaves"] <= reachable_alphabet_bound(p, bank, tree)["product_bound"]


@pytest.mark.parametrize("capacities", [(), (0,), (True,), (-1, 2)])
def test_bad_prior(capacities):
    with pytest.raises(ValueError):
        fair_bit_prior(capacities)


def test_malformed_prior_queries_policy_and_budget():
    p = fair_bit_prior((1, 1))
    with pytest.raises(ValueError):
        FinitePrior((1, 1), ((0, 0), (0, 0)), (1, 1))
    with pytest.raises(ValueError):
        FinitePrior((1, 1), ((2, 0),), (1,))
    with pytest.raises(ValueError):
        FinitePrior((1,), ((0,),), (True,))
    for bad in ((), ((1,),), ((0.5, 0),), ((1, -1),), ((1, True),)):
        with pytest.raises(ValueError):
            validate_queries(p, bad)
    for k in (-1, 0.5, True):
        with pytest.raises(ValueError):
            adaptive_optimum(p, ((1, 0),), k)
        with pytest.raises(ValueError):
            fixed_optimum(p, ((1, 0),), k)
    with pytest.raises(ValueError):
        transcript((0, 0), Node(1, ((0, Node()),)), ((1, 0),))
    with pytest.raises(ValueError):
        transcript((0, 0), Node(0, ((1, Node()),)), ((1, 0),))
    with pytest.raises(ValueError):
        transcript((0, 0), Node(None, ((0, Node()),)), ((1, 0),))
    for n in (0, True):
        with pytest.raises(ValueError):
            one_hot_prior(n)
        with pytest.raises(ValueError):
            interval_bank(n)


def test_zero_query_and_constant_channel():
    p = fair_bit_prior((1, 1))
    q = ((0, 0),)
    tree = fixed_tree(p, q, (0, 0))
    profile = transcript_profile(p, q, tree)
    assert profile["leaves"] == 1
    assert profile["observed_collision_probability"] == 1
    assert prefix_collision_sequence(p, q, tree) == (Q(1), Q(1), Q(1))
    assert reachable_alphabet_bound(p, q, tree)["alphabet_factors"] == (1, 1)
    assert one_hot_interval_law(8, 0) == {"adaptive": 1, "fixed": 1}
