"""Finite-domain counterexamples and exact grader gates for RH-05."""
from fractions import Fraction

import pytest

from spiral_ln.rh_count_to_find import (
    Instance, audit, combinatorial_first_hit_bound,
    exact_first_hit_distribution, grade_queries, make_instances,
    uniform_without_replacement_expectation,
)


def test_count_constant_search_cost_changes():
    p = 17
    early = Instance(p, 1, 0, 0, "early").verify_by_enumeration()
    late = Instance(p, 1, 0, p - 1, "late").verify_by_enumeration()
    assert early["solution_count"] == late["solution_count"] == p
    assert early["first_lexicographic_query"] == 1
    assert late["first_lexicographic_query"] == p * p - p + 1
    assert late["first_lexicographic_query"] == combinatorial_first_hit_bound(p*p, p)


def test_exact_distribution_and_mean():
    N, M = 9, 3
    dist = exact_first_hit_distribution(N, M)
    assert sum(dist) == 1
    assert sum(Fraction(t + 1) * prob for t, prob in enumerate(dist)) == (
        uniform_without_replacement_expectation(N, M))
    assert uniform_without_replacement_expectation(289, 17) == Fraction(145, 9)


def test_constructive_witnesses_and_all_domains():
    for case in make_instances("dev"):
        checked = case.verify_by_enumeration()
        assert checked["solution_count"] == case.p
        assert case.accepts(*case.construct())
        assert checked["first_lexicographic_query"] <= case.p**2-case.p+1


def test_grading_verifies_finite_points():
    case = Instance(17, 1, 0, 16, "late")
    assert grade_queries(case, [[0, 0], [16, 0]]) == (
        {"solved": True, "first_hit_queries": 2})
    assert grade_queries(case, [[0, 0]])["solved"] is False
    with pytest.raises(ValueError):
        grade_queries(case, [[17, 0]])
    with pytest.raises(ValueError):
        grade_queries(case, [[True, 0]])


def test_receipt_exposes_evidence_boundary():
    receipt = audit("dev")
    assert receipt["independent_units"] == 2
    assert receipt["cases"] == 8
    assert receipt["model_intervention"] is None
    assert receipt["power"] == "not applicable to finite arithmetic truth checks"
    assert len(receipt["source_sha256"]) == 64
