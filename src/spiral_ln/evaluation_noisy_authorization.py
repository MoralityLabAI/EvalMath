"""EVAL-AUTH-03: exact Bayes value of a binary, noisy authorization audit.

All probability arithmetic is Fraction-exact. The modeled authorization prior,
audit sensitivity and audit false-positive rate are assumptions about a finite
synthetic channel, not independently authenticated properties of an issuer.

For independent tasks, and a fixed rule for interpreting audit reports, sorting
their known expected risk reductions is optimal for a nonadaptive fixed-budget
audit schedule. A private shared latent variable or outcome-dependent costs
requires an extended state space and a new analysis.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from typing import Sequence

Q = Fraction


def _prob(value: Q, field: str) -> Q:
    if not isinstance(value, Fraction) or not Q(0) <= value <= Q(1):
        raise ValueError(f"{field} must be an exact Fraction in [0,1]")
    return value


@dataclass(frozen=True)
class AuditChannel:
    prior: Q
    sensitivity: Q
    false_positive: Q

    def __post_init__(self) -> None:
        _prob(self.prior, "prior")
        _prob(self.sensitivity, "sensitivity")
        _prob(self.false_positive, "false_positive")


def public_error(channel: AuditChannel) -> Q:
    """Optimal symmetric binary-error risk without reading the audit."""
    return min(channel.prior, Q(1) - channel.prior)


def audited_error(channel: AuditChannel) -> Q:
    """Optimal risk when a binary audit outcome is observed before action.

    The two terms are the smaller joint mass of (authorization, report)
    for report=true and report=false. Marginalizing the report gives the
    uninspected risk, so this expression can never exceed public_error.
    """
    p, t, f = channel.prior, channel.sensitivity, channel.false_positive
    yes = min(p * t, (Q(1) - p) * f)
    no = min(p * (Q(1) - t), (Q(1) - p) * (Q(1) - f))
    return yes + no


def audit_value(channel: AuditChannel) -> Q:
    value = public_error(channel) - audited_error(channel)
    if value < 0:
        raise AssertionError("Bayes value of information must be nonnegative")
    return value


def decide_public(estimated: AuditChannel) -> bool:
    """Grant authorization only on a strictly greater posterior."""
    return estimated.prior > Q(1, 2)


def decide_after_report(estimated: AuditChannel, *, report: bool) -> bool:
    """Conditional Bayes action using the fitted audit model.

    Compares unnormalized joint masses, avoiding a division at zero-support
    reports. Ties deny permission.
    """
    p, t, f = estimated.prior, estimated.sensitivity, estimated.false_positive
    if report:
        positive = p * t
        negative = (Q(1) - p) * f
    else:
        positive = p * (Q(1) - t)
        negative = (Q(1) - p) * (Q(1) - f)
    return positive > negative


def expected_error_under_rule(
    true_channel: AuditChannel,
    estimated_channel: AuditChannel,
    *, inspect: bool,
) -> Q:
    """Evaluate a frozen classifier against the true finite channel.

    The true channel determines risk only; the decision rule sees estimated
    probabilities and a report if and only if inspect=True.
    """
    p, t, f = true_channel.prior, true_channel.sensitivity, true_channel.false_positive
    if not inspect:
        return (Q(1) - p) if decide_public(estimated_channel) else p

    incorrect = Q(0)
    for report in (False, True):
        chooses_grant = decide_after_report(estimated_channel, report=report)
        authorized_mass = p * (t if report else Q(1) - t)
        forbidden_mass = (Q(1) - p) * (f if report else Q(1) - f)
        incorrect += forbidden_mass if chooses_grant else authorized_mass
    return incorrect


def rule_audit_value(
    true_channel: AuditChannel, estimated_channel: AuditChannel,
) -> Q:
    """Signed value of *a fixed fitted decision rule*.

    Unlike Bayes value, the value here may be negative when fitted
    probabilities are wrong.
    """
    return expected_error_under_rule(
        true_channel, estimated_channel, inspect=False
    ) - expected_error_under_rule(
        true_channel, estimated_channel, inspect=True
    )


@dataclass(frozen=True)
class AuditCandidate:
    case_id: str
    value: Q

    def __post_init__(self) -> None:
        if not isinstance(self.case_id, str) or not self.case_id:
            raise ValueError("case ID required")
        if not isinstance(self.value, Fraction):
            raise TypeError("expected risk reduction must be exact Fraction")


def optimal_fixed_budget(
    candidates: Sequence[AuditCandidate], budget: int,
) -> tuple[AuditCandidate, ...]:
    """Choose exactly B public candidates by value, then stable case ID.

    This is an optimal nonadaptive schedule when expected per-case risk
    reductions add. It does not choose based on the withheld audit report.
    """
    rows = tuple(candidates)
    if type(budget) is not int or not 0 <= budget <= len(rows):
        raise ValueError("budget must be an integer between zero and case count")
    if len({row.case_id for row in rows}) != len(rows):
        raise ValueError("duplicate case ID")
    return tuple(sorted(rows, key=lambda x: (-x.value, x.case_id))[:budget])


def audit_budget_frontier(candidates: Sequence[AuditCandidate]) -> tuple[Q, ...]:
    """Maximum additive expected gain after exactly 0..N inspections."""
    rows = tuple(candidates)
    ranked = optimal_fixed_budget(rows, len(rows))
    result = [Q(0)]
    total = Q(0)
    for candidate in ranked:
        total += candidate.value
        result.append(total)
    return tuple(result)


def brute_force_budget_gain(candidates: Sequence[AuditCandidate], budget: int) -> Q:
    """Independent small-domain enumeration for verifying the sorting law."""
    rows = tuple(candidates)
    if type(budget) is not int or not 0 <= budget <= len(rows):
        raise ValueError("invalid fixed budget")
    if len({row.case_id for row in rows}) != len(rows):
        raise ValueError("duplicate case ID")
    return max(
        (sum((item.value for item in selected), Q(0))
         for selected in combinations(rows, budget)),
        default=Q(0),
    )


# EVAL-AUTH-04: explicit asymmetric authorization error costs.

def _positive_cost(value: Q, field: str) -> Q:
    if not isinstance(value, Fraction) or value <= 0:
        raise ValueError(f"{field} must be a positive exact Fraction")
    return value


def weighted_public_error(
    channel: AuditChannel, *, false_grant_cost: Q, missed_grant_cost: Q = Q(1),
) -> Q:
    """Bayes error when false authorization and missed authorization differ."""
    c_fp = _positive_cost(false_grant_cost, "false_grant_cost")
    c_fn = _positive_cost(missed_grant_cost, "missed_grant_cost")
    p = channel.prior
    return min(c_fn * p, c_fp * (Q(1) - p))


def weighted_audited_error(
    channel: AuditChannel, *, false_grant_cost: Q, missed_grant_cost: Q = Q(1),
) -> Q:
    """Minimum weighted risk after a finite noisy report is observed."""
    c_fp = _positive_cost(false_grant_cost, "false_grant_cost")
    c_fn = _positive_cost(missed_grant_cost, "missed_grant_cost")
    p, t, f = channel.prior, channel.sensitivity, channel.false_positive
    yes = min(c_fn * p * t, c_fp * (Q(1) - p) * f)
    no = min(c_fn * p * (Q(1) - t), c_fp * (Q(1) - p) * (Q(1) - f))
    return yes + no


def weighted_audit_value(
    channel: AuditChannel, *, false_grant_cost: Q, missed_grant_cost: Q = Q(1),
) -> Q:
    value = weighted_public_error(
        channel, false_grant_cost=false_grant_cost,
        missed_grant_cost=missed_grant_cost,
    ) - weighted_audited_error(
        channel, false_grant_cost=false_grant_cost,
        missed_grant_cost=missed_grant_cost,
    )
    if value < 0:
        raise AssertionError("Bayes value of information must be nonnegative")
    return value


def weighted_decide_public(
    estimated: AuditChannel, *, false_grant_cost: Q, missed_grant_cost: Q = Q(1),
) -> bool:
    c_fp = _positive_cost(false_grant_cost, "false_grant_cost")
    c_fn = _positive_cost(missed_grant_cost, "missed_grant_cost")
    return c_fn * estimated.prior > c_fp * (Q(1) - estimated.prior)


def weighted_decide_after_report(
    estimated: AuditChannel, *, report: bool,
    false_grant_cost: Q, missed_grant_cost: Q = Q(1),
) -> bool:
    c_fp = _positive_cost(false_grant_cost, "false_grant_cost")
    c_fn = _positive_cost(missed_grant_cost, "missed_grant_cost")
    p,t,f=estimated.prior,estimated.sensitivity,estimated.false_positive
    allowed_mass = p * (t if report else Q(1) - t)
    forbidden_mass = (Q(1) - p) * (f if report else Q(1) - f)
    return c_fn * allowed_mass > c_fp * forbidden_mass


def weighted_expected_error_under_rule(
    true_channel: AuditChannel, estimated_channel: AuditChannel,
    *, inspect: bool, false_grant_cost: Q, missed_grant_cost: Q = Q(1),
) -> Q:
    """Weighted true loss of a frozen, potentially miscalibrated controller."""
    c_fp = _positive_cost(false_grant_cost, "false_grant_cost")
    c_fn = _positive_cost(missed_grant_cost, "missed_grant_cost")
    p,t,f=true_channel.prior,true_channel.sensitivity,true_channel.false_positive
    if not inspect:
        return c_fp*(Q(1)-p) if weighted_decide_public(
            estimated_channel,false_grant_cost=c_fp,missed_grant_cost=c_fn
        ) else c_fn*p
    total=Q(0)
    for report in (False,True):
        allowed_mass = p*(t if report else Q(1)-t)
        forbidden_mass = (Q(1)-p)*(f if report else Q(1)-f)
        chosen = weighted_decide_after_report(
            estimated_channel,report=report,
            false_grant_cost=c_fp,missed_grant_cost=c_fn,
        )
        total += c_fp*forbidden_mass if chosen else c_fn*allowed_mass
    return total


def weighted_rule_audit_value(
    true_channel: AuditChannel, estimated_channel: AuditChannel,
    *, false_grant_cost: Q, missed_grant_cost: Q = Q(1),
) -> Q:
    return weighted_expected_error_under_rule(
        true_channel,estimated_channel,inspect=False,
        false_grant_cost=false_grant_cost,missed_grant_cost=missed_grant_cost,
    ) - weighted_expected_error_under_rule(
        true_channel,estimated_channel,inspect=True,
        false_grant_cost=false_grant_cost,missed_grant_cost=missed_grant_cost,
    )
