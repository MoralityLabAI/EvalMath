"""Exact finite controls for self-designed evaluation and Fidelity Recursive Complexity.

Every probability and update uses fractions.Fraction.  The trigger auditor
only receives equality queries: O_x(i) = [x == i].  Spectral/coefficient
queries are a distinct, strictly richer observation model studied in
RSITopology/HarmonicConsciousness.  This module neither calls nor trains an AI.

EVIDENCE: elementary algebraic identities (proved in the accompanying note),
finite verified enumeration, and a toy adaptive-design trajectory.  An
exponential query lower bound for this restricted oracle is NOT a universal
FRC theorem about arbitrary RSI systems.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from itertools import product
from typing import Literal, Sequence


def _prob(value: Q, name: str = "probability") -> Q:
    if type(value) is bool or not isinstance(value, (int, Q)):
        raise ValueError(f"{name} must be an exact rational")
    value = Q(value)
    if not 0 <= value <= 1:
        raise ValueError(f"{name} must lie in [0, 1]")
    return value


def _prior(values: Sequence[Q]) -> tuple[Q, ...]:
    if not values:
        raise ValueError("the trigger prior needs at least one candidate")
    p = tuple(_prob(v, "prior mass") for v in values)
    if sum(p) != 1:
        raise ValueError("trigger prior must sum to exactly one")
    return p


def _count(value: int, name: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"{name} must be a non-negative integer")
    return value


def ceil_fraction(value: Q) -> int:
    """Exact mathematical ceiling, including negative fractions."""
    return -(-value.numerator // value.denominator)


def oracle_coverage(prior: Sequence[Q], no_hit_path: Sequence[int]) -> Q:
    """Hit probability for an adaptive deterministic equality-query strategy.

    Until its first hit, every oracle response is 0, so the policy follows a
    fixed no-hit path.  Repeated queries cannot improve its coverage.
    This remains true if the policy adapts to its previous failures.
    """
    p = _prior(prior)
    visited: set[int] = set()
    for i in no_hit_path:
        if type(i) is not int or not 0 <= i < len(p):
            raise ValueError("query index out of bounds")
        visited.add(i)
    return sum((p[i] for i in visited), Q(0))


def optimal_coverage(prior: Sequence[Q], query_budget: int) -> Q:
    """Exact supremum of trigger-hit probability in q equality queries."""
    p = _prior(prior)
    q = _count(query_budget, "query budget")
    return sum(sorted(p, reverse=True)[:q], Q(0))


def min_entropy_effective_support(prior: Sequence[Q]) -> Q:
    """2^H_inf = 1/max_x P(X=x), returned as a rational."""
    p = _prior(prior)
    return 1 / max(p)


def min_entropy_coverage_cap(prior: Sequence[Q], query_budget: int) -> Q:
    p = _prior(prior)
    q = _count(query_budget, "query budget")
    return min(Q(1), q * max(p))


def necessary_queries(prior: Sequence[Q], delta: Q) -> int:
    """Necessary q for a two-sided delta-auditor via min-entropy.

    The auditor must accept a clean oracle with probability >=1-delta and
    reject a trigger oracle with probability >=1-delta *averaged over p*.
    Transcript coupling implies trigger-hit >= 1-2delta, hence q*max(p)
    >= 1-2delta. This is a lower bound, not always sufficient.
    """
    p = _prior(prior)
    d = _prob(delta, "delta")
    requirement = max(Q(0), Q(1) - 2 * d)
    return ceil_fraction(requirement / max(p))


def necessary_queries_by_coverage(prior: Sequence[Q], delta: Q) -> int:
    """Sharper necessary q using the exact sum of q largest prior masses."""
    p = _prior(prior)
    d = _prob(delta, "delta")
    requirement = max(Q(0), Q(1) - 2 * d)
    for q in range(len(p) + 1):
        if optimal_coverage(p, q) >= requirement:
            return q
    raise AssertionError("full enumeration must cover the prior")


def uniform_depth_query_floor(depth: int, delta: Q) -> int:
    """Exact q >= ceil((1-2delta) 2**depth) for uniform 2**depth triggers."""
    d = _count(depth, "depth")
    error = _prob(delta, "delta")
    return ceil_fraction(max(Q(0), 1 - 2 * error) * 2**d)


def fidelity_certificate(judge_reject: Q, false_accept: Q) -> Q:
    """Lower bound on external P from Pr(J=0) and Pr(P=0,J=1).

    Pr(P=0) = Pr(P=0,J=0) + Pr(P=0,J=1) <= reject + false_accept.
    """
    d = _prob(judge_reject, "judge rejection probability")
    e = _prob(false_accept, "false acceptance probability")
    return max(Q(0), Q(1) - d - e)


Policy = Literal["self_confirming", "weakness_seeking", "alternating"]


@dataclass(frozen=True)
class DesignState:
    """Two competing task scores sharing one unit of training capacity."""
    first: Q
    second: Q

    def __post_init__(self) -> None:
        a = _prob(self.first, "first task score")
        b = _prob(self.second, "second task score")
        if a + b != 1:
            raise ValueError("toy task scores must sum to one")
        object.__setattr__(self, "first", a)
        object.__setattr__(self, "second", b)


def choose_self_eval(state: DesignState, policy: Policy, generation: int) -> int:
    """Evaluation design is chosen from current *internal* task scores.

    All policies receive both internal task scores at training time. The
    independent readout of task 1 is never supplied as a selection signal.
    """
    _count(generation, "generation")
    if policy == "self_confirming":
        return 0 if state.first >= state.second else 1
    if policy == "weakness_seeking":
        return 0 if state.first <= state.second else 1
    if policy == "alternating":
        return generation % 2
    raise ValueError(f"unknown evaluation-design policy: {policy}")


def train_on_selected(state: DesignState, chosen: int, fraction: Q) -> DesignState:
    """Move a rational fraction of the unselected task's capacity into the chosen task."""
    eta = _prob(fraction, "training fraction")
    if chosen == 0:
        amount = eta * state.second
        return DesignState(state.first + amount, state.second - amount)
    if chosen == 1:
        amount = eta * state.first
        return DesignState(state.first - amount, state.second + amount)
    raise ValueError("task index must be 0 or 1")


def design_trajectory(
    policy: Policy, generations: int, *,
    initial: DesignState = DesignState(Q(11, 20), Q(9, 20)),
    rate: Q = Q(1, 4),
) -> dict:
    """Self-designed eval -> score-only feedback -> exact training update.

    Task 1 is the SEALED independent external property. The training agent
    only sees internal scores of its selected task and updates the model.
    Observed training gain is relative to that selected task. For this toy
    mechanism the self-model knows its update law exactly.
    """
    n = _count(generations, "generations")
    eta = _prob(rate, "training rate")
    state = initial
    records = []
    for k in range(n):
        j = choose_self_eval(state, policy, k)
        before = state.first if j == 0 else state.second
        other = state.second if j == 0 else state.first
        predicted_gain = eta * other
        updated = train_on_selected(state, j, eta)
        after = updated.first if j == 0 else updated.second
        records.append({
            "generation": k,
            "eval_design_task": j,
            "training_signal_pre": before,
            "training_signal_post": after,
            "predicted_gain": predicted_gain,
            "observed_gain": after - before,
            "external_property_task_1": updated.second,
        })
        state = updated
    return {
        "policy": policy, "initial": initial, "rate": eta,
        "records": tuple(records), "final": state,
    }


def weakness_external_floor(initial: DesignState, rate: Q) -> Q:
    """Provable all-k floor on task-1 performance for weakness-seeking policy.

    If task 1 is selected, it rises. Otherwise task 0 is weaker and task 1
    is at least 1/2 before the update, so afterwards it is >= (1-eta)/2.
    """
    eta = _prob(rate, "training rate")
    return min(initial.second, (1 - eta) / 2)


def verify() -> dict:
    checks: dict[str, bool] = {}
    p = (Q(1, 2), Q(1, 4), Q(1, 8), Q(1, 8))
    checks["topq_exact_nonuniform"] = optimal_coverage(p, 2) == Q(3, 4)
    checks["minentropy_weaker"] = min_entropy_coverage_cap(p, 2) == 1
    checks["path_duplicates_no_gain"] = oracle_coverage(p, [0, 0, 1]) == Q(3, 4)
    checks["sharper_bound_differs"] = (
        necessary_queries(p, Q(1, 10)) == 2
        and necessary_queries_by_coverage(p, Q(1, 10)) == 3
    )
    checks["uniform_8_delta_point_one"] = uniform_depth_query_floor(8, Q(1, 10)) == 205
    checks["calibration_partition"] = fidelity_certificate(Q(1, 10), Q(1, 20)) == Q(17, 20)
    initial = DesignState(Q(11, 20), Q(9, 20))
    self_path = design_trajectory("self_confirming", 12)
    weak_path = design_trajectory("weakness_seeking", 12)
    checks["self_confirming_exact_closed_form"] = self_path["final"].second == Q(9, 20) * Q(3, 4)**12
    checks["self_confirming_score_rises"] = self_path["final"].first > Q(98, 100)
    floor = weakness_external_floor(initial, Q(1, 4))
    checks["weakness_floor_holds"] = all(x["external_property_task_1"] >= floor for x in weak_path["records"])
    checks["metaprediction_matches_selected"] = all(
        x["observed_gain"] == x["predicted_gain"]
        for path in (self_path, weak_path) for x in path["records"]
    )
    checks["external_gap_detected"] = self_path["final"].second < weak_path["final"].second
    floors = {str(k): uniform_depth_query_floor(k, Q(1, 10)) for k in (2, 4, 8, 12)}
    return {
        "evidence": "finite_verified_example_and_algebraic_identity",
        "model_evaluations": 0,
        "checks": checks,
        "all_passed": all(checks.values()),
        "min_entropy_uniform_audit_floor": floors,
        "two_task": {
            "rate": str(Q(1, 4)),
            "generations": 12,
            "self_confirming_final": [str(self_path["final"].first), str(self_path["final"].second)],
            "weakness_seeking_final": [str(weak_path["final"].first), str(weak_path["final"].second)],
            "weakness_external_global_floor": str(floor),
            "self_confirming_closed_form_external": "9/20 * (3/4)^k",
        },
    }
