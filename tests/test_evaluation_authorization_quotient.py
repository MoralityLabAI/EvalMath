"""Exact finite tests for EVAL-AUTH-01, including an independent oracle."""
from __future__ import annotations

from fractions import Fraction as Q
from itertools import product

import pytest

from spiral_ln.evaluation_authorization_quotient import (
    AuthorizationWorld, inspection_value, optimal_observation_policy,
)


def make_worlds(labels, public, audit, masses=None):
    n = len(labels)
    if masses is None:
        masses = [Q(1)] * n
    return [
        AuthorizationWorld(f"w{i}", str(public[i]), str(audit[i]), labels[i], masses[i])
        for i in range(n)
    ]


def brute_min_error(worlds, inspected=False):
    key = lambda x: (x.public, x.audit) if inspected else (x.public,)
    distinct = sorted({key(row) for row in worlds})
    total = sum((row.mass for row in worlds), Q(0))
    errors = []
    for decisions in product((False, True), repeat=len(distinct)):
        policy = dict(zip(distinct, decisions))
        errors.append(sum(
            (row.mass for row in worlds if policy[key(row)] != row.authorized), Q(0)
        ))
    return min(errors) / total


def test_hidden_permission_collision_and_exact_inspection():
    worlds = make_worlds([False, True], [0, 0], [0, 1])
    old = optimal_observation_policy(worlds)
    new = optimal_observation_policy(worlds, inspected=True)
    assert old.error == Q(1, 2)
    assert old.accuracy == Q(1, 2)
    assert old.false_positive_rate == Q(0)
    assert old.true_positive_rate == Q(0)
    assert old.policy == ((("0",), False),)
    assert new.error == Q(0)
    assert new.accuracy == Q(1)
    assert inspection_value(worlds) == Q(1, 2)


def test_weighted_collision_and_tie_handling():
    worlds = make_worlds(
        [False, True], [0, 0], [0, 1], [Q(1), Q(3)]
    )
    old = optimal_observation_policy(worlds)
    assert old.error == Q(1, 4)
    assert old.false_positive_rate == Q(1)
    assert old.true_positive_rate == Q(1)
    assert inspection_value(worlds) == Q(1, 4)


def test_unidentified_denominators_remain_explicit():
    one_class = make_worlds([True], [0], [0])
    result = optimal_observation_policy(one_class)
    assert result.false_positive_rate is None
    assert result.true_positive_rate == Q(1)


@pytest.mark.parametrize("worlds", [
    [],
    make_worlds([True, False], [0, 0], [0, 1], [Q(1), Q(0)]),
    [AuthorizationWorld("duplicate", "o", "a", True),
     AuthorizationWorld("duplicate", "p", "b", False)],
])
def test_invalid_worlds_fail_closed(worlds):
    with pytest.raises(ValueError):
        optimal_observation_policy(worlds)


def test_complete_four_world_oracle_census():
    checks = 0
    for n in range(1, 5):
        for labels in product((False, True), repeat=n):
            for public in product((0, 1), repeat=n):
                for audit in product((0, 1), repeat=n):
                    worlds = make_worlds(labels, public, audit)
                    a = optimal_observation_policy(worlds)
                    b = optimal_observation_policy(worlds, inspected=True)
                    assert a.error == brute_min_error(worlds)
                    assert b.error == brute_min_error(worlds, inspected=True)
                    assert b.error <= a.error
                    assert a.accuracy + a.error == 1
                    checks += 1
    assert checks == sum(8 ** n for n in range(1, 5)) == 4680
