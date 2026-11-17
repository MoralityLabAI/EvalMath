"""Exact finite tests for EVAL-AUTH-01, including an independent oracle."""
from __future__ import annotations

from fractions import Fraction as Q
from itertools import product

import pytest

from spiral_ln.evaluation_authorization_quotient import (
    AuthorizationWorld, PairedAuditDecision, audit_budget_certificate, inspection_value, optimal_observation_policy,
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


def test_exact_budget_bound_matches_registered_eca01():
    def rows(shared_count, independent_count, arm):
        values = []
        for i in range(independent_count):
            values.append(PairedAuditDecision(f"independent-{i}", arm == "audit_all",
                                            True, arm != "audit_all"))
        for i in range(shared_count):
            values.append(PairedAuditDecision(f"shared-{i}", arm in ("audit_partial", "audit_all"),
                                            arm in ("audit_partial", "audit_all"),
                                            False))
        return values

    legacy = [
        PairedAuditDecision(f"root-{i}", False, True, True)
        for i in range(64)
    ]
    assert audit_budget_certificate(legacy)["J"] == Q(0)
    partial = audit_budget_certificate(rows(28, 36, "audit_partial"), maximum_audited_roots=28)
    assert partial["J"] == Q(7, 16)
    assert partial["audited_root_pairs"] == 28
    assert partial["upper_J_from_actual_audits"] == Q(7, 16)
    assert partial["bound_saturated"]
    full = audit_budget_certificate(rows(28, 36, "audit_all"), maximum_audited_roots=64)
    assert full["J"] == Q(1)
    assert full["bound_saturated"]


def test_pair_budget_all_small_decision_rosters():
    # Two unaudited equal-decision rows, four audited rows.
    choices = [
        (False, False, False),
        (False, True, True),
        (True, False, False),
        (True, False, True),
        (True, True, False),
        (True, True, True),
    ]
    for n in range(1, 5):
        for vector in product(choices, repeat=n):
            rows = [
                PairedAuditDecision(str(i), *item) for i, item in enumerate(vector)
            ]
            report = audit_budget_certificate(rows)
            assert report["J"] <= report["upper_J_from_actual_audits"]
            assert report["J"] == report["tpr"] - report["fpr"]
            assert report["upper_J_from_budget"] <= Q(1)


def test_budget_rejects_public_collision_break_and_overspend():
    with pytest.raises(ValueError, match="observation-only"):
        audit_budget_certificate([PairedAuditDecision("root", False, True, False)])
    with pytest.raises(ValueError, match="budget"):
        audit_budget_certificate([PairedAuditDecision("root", True, True, False)],
                                 maximum_audited_roots=0)
    with pytest.raises(ValueError, match="unique"):
        audit_budget_certificate([
            PairedAuditDecision("r", False, True, True),
            PairedAuditDecision("r", False, False, False),
        ])
