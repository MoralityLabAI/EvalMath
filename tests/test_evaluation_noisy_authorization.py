"""Independent exact-Fraction oracles for EVAL-AUTH-03."""
from fractions import Fraction as Q
from itertools import product

import pytest

from spiral_ln.evaluation_noisy_authorization import (
    AuditCandidate, AuditChannel, audit_budget_frontier, audit_value,
    audited_error, brute_force_budget_gain, decide_after_report,
    decide_public, expected_error_under_rule, optimal_fixed_budget,
    public_error, rule_audit_value,
)


def test_named_exact_channels_and_bayes_value():
    excellent = AuditChannel(Q(1,2), Q(9,10), Q(1,10))
    weak = AuditChannel(Q(1,2), Q(3,5), Q(2,5))
    rare_good = AuditChannel(Q(1,8), Q(9,10), Q(1,10))
    rare_weak = AuditChannel(Q(1,8), Q(3,5), Q(2,5))
    assert (public_error(excellent), audited_error(excellent),
            audit_value(excellent)) == (Q(1,2), Q(1,10), Q(2,5))
    assert audit_value(weak) == Q(1,10)
    assert audit_value(rare_good) == Q(1,40)
    assert audit_value(rare_weak) == Q(0)


def test_bayes_value_nonnegative_on_complete_fifth_grid():
    grid = [Q(0), Q(1,4), Q(1,2), Q(3,4), Q(1)]
    for p,t,f in product(grid, repeat=3):
        ch = AuditChannel(p,t,f)
        value = audit_value(ch)
        assert value == public_error(ch) - audited_error(ch)
        assert Q(0) <= audited_error(ch) <= public_error(ch) <= Q(1,2)
        assert value <= public_error(ch)
        assert expected_error_under_rule(ch,ch,inspect=False) == public_error(ch)
        assert expected_error_under_rule(ch,ch,inspect=True) == audited_error(ch)


def test_true_channel_noisy_fitted_rule_can_hurt():
    true = AuditChannel(Q(3,5), Q(1,2), Q(1,2))
    overconfident = AuditChannel(Q(3,5), Q(99,100), Q(1,100))
    assert audit_value(true) == Q(0)
    assert decide_public(overconfident) is True
    assert decide_after_report(overconfident, report=True)
    assert not decide_after_report(overconfident, report=False)
    assert expected_error_under_rule(true,overconfident,inspect=False) == Q(2,5)
    assert expected_error_under_rule(true,overconfident,inspect=True) == Q(1,2)
    assert rule_audit_value(true,overconfident) == -Q(1,10)


def test_fixed_budget_matches_independent_subset_census():
    values = (-Q(1,4), Q(0), Q(1,8), Q(2,5))
    for n in range(0, 5):
        for vector in product(values, repeat=n):
            rows = [AuditCandidate(str(i), value) for i,value in enumerate(vector)]
            frontier = audit_budget_frontier(rows)
            assert len(frontier) == n+1
            for budget in range(n+1):
                selected = optimal_fixed_budget(rows,budget)
                value = sum((item.value for item in selected),Q(0))
                assert frontier[budget] == value
                assert value == brute_force_budget_gain(rows,budget)


def test_ties_and_zero_budget_are_stable():
    rows = [
        AuditCandidate("b",Q(1,4)), AuditCandidate("a",Q(1,4)),
        AuditCandidate("c",-Q(1,3))
    ]
    assert [x.case_id for x in optimal_fixed_budget(rows,2)] == ["a","b"]
    assert optimal_fixed_budget(rows,0) == ()
    assert audit_budget_frontier(rows) == (Q(0),Q(1,4),Q(1,2),Q(1,6))


def test_invalid_inputs_fail_closed():
    with pytest.raises(ValueError):
        AuditChannel(Q(11,10),Q(1),Q(0))
    with pytest.raises(ValueError):
        AuditChannel(Q(1,2),Q(-1,10),Q(1,2))
    with pytest.raises(ValueError):
        optimal_fixed_budget([AuditCandidate("a",Q(1))],2)
    with pytest.raises(ValueError):
        optimal_fixed_budget([AuditCandidate("a",Q(1)),AuditCandidate("a",Q(2))],1)
    with pytest.raises(TypeError):
        AuditCandidate("foo",1)
    with pytest.raises(ValueError):
        AuditCandidate("",Q(1))
