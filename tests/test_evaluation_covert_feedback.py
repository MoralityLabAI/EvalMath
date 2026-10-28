"""Exact covert-channel risk fixtures and independent full-label oracle."""
from fractions import Fraction as Q
import random

import pytest

from spiral_ln.evaluation_selection_risk import (
    NullModel, QueryNode, dependent_five_percent_models,
    adaptive_optimum, full_information_risk, policy_fibres,
)
from spiral_ln.evaluation_covert_feedback import (
    best_event_cover, brute_force_covert_risk, covert_risk,
    covert_tree_risk, covert_witness_labels, independent_boolean_null,
    validate_fibres,
)


def test_same_marginal_events_different_covert_risks():
    shared, disjoint = dependent_five_percent_models()
    assert covert_risk(shared, 1)["risk"] == Q(1, 20)
    assert covert_risk(shared, 2)["risk"] == Q(1, 20)
    assert covert_risk(disjoint, 1)["risk"] == Q(1, 20)
    assert covert_risk(disjoint, 2)["risk"] == Q(1, 10)
    assert covert_witness_labels(disjoint, 2)["covered_mass"] == 2


def test_three_iid_five_percent_events_with_public_and_covert_bits():
    model = independent_boolean_null(3)
    assert model.total == 8000
    assert model.marginals() == (Q(1, 20),) * 3
    assert covert_risk(model, 1)["risk"] == Q(1, 20)
    assert covert_risk(model, 2)["risk"] == Q(39, 400)
    assert covert_risk(model, 3)["risk"] == Q(1141, 8000)
    seen_first_event = (tuple(i for i in range(8) if not model.events[0][i]),
                        tuple(i for i in range(8) if model.events[0][i]))
    assert covert_risk(model, 1, seen_first_event)["risk"] == Q(39, 400)
    assert covert_risk(model, 2, seen_first_event)["risk"] == Q(1141, 8000)
    assert covert_risk(model, 3, seen_first_event)["risk"] == Q(1141, 8000)


def test_exact_one_bit_factor_bound_sharp_with_disjoint_events():
    model = NullModel((17, 1, 1, 1),
                      ((False, True, False, False),
                       (False, False, True, False),
                       (False, False, False, True)),
                      ((0, 1, 0, 0),))
    assert covert_risk(model, 1)["risk"] == Q(1, 20)
    assert covert_risk(model, 2)["risk"] == Q(1, 10)
    assert covert_risk(model, 3)["risk"] == Q(3, 20)
    assert covert_risk(model, 2)["risk"] == 2 * covert_risk(model, 1)["risk"]
    assert covert_risk(model, 9)["risk"] == full_information_risk(model)


def test_tree_public_policy_can_combine_with_hidden_messages():
    model = independent_boolean_null(3)
    # Event 0 revealed publicly, events 1 and 2 chosen through one hidden bit.
    leaf = QueryNode()
    tree = QueryNode(1, ((0, leaf), (1, leaf)))
    assert covert_tree_risk(model, tree, 1)["risk"] == Q(39, 400)
    assert covert_tree_risk(model, tree, 2)["risk"] == Q(1141, 8000)
    assert covert_tree_risk(model, tree, 2)["public_fibres"] == tuple(policy_fibres(model, tree).values())


def test_covering_choice_attainable_by_covert_label_assignment():
    model = independent_boolean_null(3)
    for public in (None, ((0, 1, 2, 3), (4, 5, 6, 7))):
        for messages in range(1, 5):
            report = covert_witness_labels(model, messages, public)
            assert report["risk"] == Q(report["covered_mass"], model.total)
            assert all(len(events) <= messages for events in report["selected_event_sets"])
            assert all(all(0 <= label < len(events) for _, label in rows)
                       for events, rows in zip(report["selected_event_sets"], report["covert_world_labels"]))
            assert report["public_risk"] <= report["risk"] <= report["full_information_risk"]


def test_independent_brute_force_hidden_assignments_random_small():
    rng = random.Random(20261026)
    for n in range(2, 7):
        for _ in range(14):
            model = NullModel(tuple(rng.randrange(1, 9) for _ in range(n)),
                              tuple(tuple(bool(rng.randrange(2)) for _ in range(n)) for _ in range(3)),
                              (tuple(rng.randrange(3) for _ in range(n)),))
            for messages in (1, 2):
                exact = covert_risk(model, messages)["risk"]
                brute = brute_force_covert_risk(model, messages)
                assert exact == brute
                assert Q(0) <= exact <= Q(1)
            by_query = (tuple(i for i in range(n) if model.queries[0][i] == 0),
                        tuple(i for i in range(n) if model.queries[0][i] != 0))
            if all(by_query) and len(set(model.queries[0])) == 2:
                assert covert_risk(model, 2, by_query)["risk"] == brute_force_covert_risk(model, 2, by_query)


def test_fibre_validation_and_secret_budget_validation():
    model = independent_boolean_null(2)
    for fibres in ((), ((0, 1),), ((0, 1), (1, 2, 3)), ((0, 1), ()),
                   ((0, True), (1, 2, 3)), ((0, 1), (2, 9))):
        with pytest.raises(ValueError):
            validate_fibres(model, fibres)
    for bad in (0, -1, 2.5, True):
        with pytest.raises(ValueError):
            covert_risk(model, bad)
        with pytest.raises(ValueError):
            brute_force_covert_risk(model, bad)
    with pytest.raises(ValueError):
        brute_force_covert_risk(independent_boolean_null(4), 3)
    with pytest.raises(ValueError):
        independent_boolean_null(0)
    with pytest.raises(ValueError):
        independent_boolean_null(2, denominator=1)


def test_hidden_witness_selection_event_indices_are_exact():
    model = independent_boolean_null(3)
    report = covert_risk(model, 2)
    mass, selected = best_event_cover(model, tuple(range(8)), 2)
    assert report["selected_event_sets"] == (selected,)
    assert mass == report["covered_mass"]
    assert covert_risk(model, 2)["risk"] == 1 - Q(19, 20)**2


def test_minimum_full_exposure_alphabet_matches_set_cover():
    from spiral_ln.evaluation_covert_feedback import minimum_full_exposure_messages
    model = independent_boolean_null(3)
    assert minimum_full_exposure_messages(model)["messages"] == 3
    reveal0 = (tuple(i for i in range(8) if not model.events[0][i]),
               tuple(i for i in range(8) if model.events[0][i]))
    assert minimum_full_exposure_messages(model, reveal0)["messages"] == 2
    shared, disjoint = dependent_five_percent_models()
    assert minimum_full_exposure_messages(shared)["messages"] == 1
    assert minimum_full_exposure_messages(disjoint)["messages"] == 2


def test_joint_adaptive_public_queries_and_terminal_hidden_signal():
    from spiral_ln.evaluation_covert_feedback import adaptive_covert_optimum, fixed_covert_optimum
    iid = independent_boolean_null(3)
    assert adaptive_covert_optimum(iid, 0, 2)["risk"] == Q(39, 400)
    assert adaptive_covert_optimum(iid, 1, 2)["risk"] == Q(1141, 8000)
    assert fixed_covert_optimum(iid, 1, 2)["risk"] == Q(1141, 8000)
    assert adaptive_covert_optimum(iid, 2, 1)["risk"] == Q(1141, 8000)
    assert fixed_covert_optimum(iid, 2, 1)["risk"] == Q(1141, 8000)
    assert adaptive_covert_optimum(iid, 3, 3)["risk"] == Q(1141, 8000)
    for bad in (-1, 1.5, True):
        with pytest.raises(ValueError):
            adaptive_covert_optimum(iid, bad, 2)
        with pytest.raises(ValueError):
            fixed_covert_optimum(iid, bad, 2)


def test_joint_adaptive_dp_matches_independent_full_plan_search():
    from spiral_ln.evaluation_covert_feedback import (
        adaptive_covert_optimum, brute_two_round_covert_optimum, fixed_covert_optimum,
    )
    rng = random.Random(74022)
    for n in range(2, 6):
        for _ in range(10):
            model = NullModel(tuple(rng.randrange(1, 7) for _ in range(n)),
                              tuple(tuple(bool(rng.randrange(2)) for _ in range(n))
                                    for _ in range(3)),
                              tuple(tuple(rng.randrange(2) for _ in range(n))
                                    for _ in range(2)))
            for messages in (1, 2):
                adaptive = adaptive_covert_optimum(model, 2, messages)["risk"]
                fixed = fixed_covert_optimum(model, 2, messages)["risk"]
                assert adaptive == brute_two_round_covert_optimum(model, messages)
                assert fixed <= adaptive <= full_information_risk(model)
