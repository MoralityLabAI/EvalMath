"""EVAL-AUTH-01: exact finite value of an authorization observation.

No learned model or evaluator is called. This module treats supplied permission
labels and audit readouts as an exact finite population, and never claims
their real-world provenance or a calibrated population error bound.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from collections import defaultdict
from typing import Sequence

Q = Fraction


@dataclass(frozen=True)
class AuthorizationWorld:
    world_id: str
    public: str
    audit: str
    authorized: bool
    mass: Q = Q(1)


@dataclass(frozen=True)
class ObservationRisk:
    error: Q
    accuracy: Q
    true_positive_rate: Q | None
    false_positive_rate: Q | None
    policy: tuple[tuple[tuple[str, ...], bool], ...]
    total_mass: Q


def _validate(worlds: Sequence[AuthorizationWorld]) -> tuple[AuthorizationWorld, ...]:
    rows = tuple(worlds)
    if not rows:
        raise ValueError("finite population must be nonempty")
    ids: set[str] = set()
    for row in rows:
        if not isinstance(row.world_id, str) or not row.world_id or row.world_id in ids:
            raise ValueError("world ids must be unique nonempty strings")
        ids.add(row.world_id)
        if not isinstance(row.public, str) or not isinstance(row.audit, str):
            raise TypeError("observation values must be strings")
        if type(row.authorized) is not bool:
            raise TypeError("authorization must be a Bool")
        if not isinstance(row.mass, Fraction) or row.mass <= 0:
            raise ValueError("masses must be positive exact fractions")
    return rows


def _key(row: AuthorizationWorld, inspected: bool) -> tuple[str, ...]:
    return (row.public, row.audit) if inspected else (row.public,)


def optimal_observation_policy(
    worlds: Sequence[AuthorizationWorld], *, inspected: bool = False
) -> ObservationRisk:
    """Return Bayes-optimal binary authorization decision and exact risk.

    Under symmetric 0/1 error cost each observation fibre is independently
    assigned its majority label. Ties deny authorization.
    """
    rows = _validate(worlds)
    cells: dict[tuple[str, ...], list[Q]] = defaultdict(lambda: [Q(0), Q(0)])
    for row in rows:
        cells[_key(row, inspected)][int(row.authorized)] += row.mass

    choices = {
        key: grant > deny
        for key, (deny, grant) in cells.items()
    }
    total = sum((row.mass for row in rows), Q(0))
    incorrect = sum((min(deny, grant) for deny, grant in cells.values()), Q(0))
    total_grant = sum((row.mass for row in rows if row.authorized), Q(0))
    total_deny = total - total_grant
    true_positive = sum(
        (row.mass for row in rows if row.authorized and choices[_key(row, inspected)]),
        Q(0),
    )
    false_positive = sum(
        (row.mass for row in rows if not row.authorized and choices[_key(row, inspected)]),
        Q(0),
    )
    return ObservationRisk(
        error=incorrect / total,
        accuracy=Q(1) - incorrect / total,
        true_positive_rate=true_positive / total_grant if total_grant else None,
        false_positive_rate=false_positive / total_deny if total_deny else None,
        policy=tuple(sorted(choices.items())),
        total_mass=total,
    )


def inspection_value(worlds: Sequence[AuthorizationWorld]) -> Q:
    """Exact decrease in minimal classification error from a revealed audit.

    Pairing the old public observation with the audit readout refines each
    public fibre. Each refined cell may choose independently, so its sum of
    minima cannot exceed the original public-cell minimum.
    """
    uninspected = optimal_observation_policy(worlds)
    inspected = optimal_observation_policy(worlds, inspected=True)
    value = uninspected.error - inspected.error
    if value < 0:
        raise AssertionError("a refining observation increased optimal error")
    return value


@dataclass(frozen=True)
class PairedAuditDecision:
    """One paired root with an intervention indicator and two retain decisions."""
    root_id: str
    audited: bool
    retain_if_authorized: bool
    retain_if_forbidden: bool


def audit_budget_certificate(
    decisions: Sequence[PairedAuditDecision], *, maximum_audited_roots: int | None = None
) -> dict[str, object]:
    """An exact finite obstruction to authorization separation without inspection.

    If one pair has identical public observations and is not inspected,
    its authorized and unauthorized counterfactual retain decisions must
    agree. Across N pairs, J=TPR-FPR <= inspected_pairs/N. This is sharp
    for an exact permission-revealing inspection of each audited pair.
    Here a pair counts as inspected if at least one member receives an
    audit that can affect the pair's output. Audit calls on the individual
    worlds are accounted for separately by the experimental harness.
    """
    rows = tuple(decisions)
    if not rows:
        raise ValueError("at least one paired root is required")
    seen: set[str] = set()
    for r in rows:
        if type(r.root_id) is not str or not r.root_id or r.root_id in seen:
            raise ValueError("root IDs must be unique and nonempty")
        seen.add(r.root_id)
        if any(type(v) is not bool for v in (
            r.audited, r.retain_if_authorized, r.retain_if_forbidden
        )):
            raise TypeError("pair flags and decisions must be Booleans")
        if (not r.audited) and r.retain_if_authorized != r.retain_if_forbidden:
            raise ValueError("unaudited twin pair violates observation-only policy")

    n = len(rows)
    count_audited = sum(r.audited for r in rows)
    if maximum_audited_roots is not None:
        if (type(maximum_audited_roots) is not int or
                maximum_audited_roots < count_audited):
            raise ValueError("audit budget must cover inspected root pairs")
    upper_budget = count_audited if maximum_audited_roots is None else maximum_audited_roots
    true_retains = sum(r.retain_if_authorized for r in rows)
    false_retains = sum(r.retain_if_forbidden for r in rows)
    gain = Q(true_retains - false_retains, n)
    bound = Q(count_audited, n)
    if gain > bound:
        raise AssertionError("inspection-budget invariant violated")
    return {
        "independent_roots": n,
        "audited_root_pairs": count_audited,
        "authorized_retain_count": true_retains,
        "forbidden_retain_count": false_retains,
        "tpr": Q(true_retains, n),
        "fpr": Q(false_retains, n),
        "J": gain,
        "upper_J_from_actual_audits": bound,
        "upper_J_from_budget": Q(upper_budget, n),
        "bound_saturated": gain == bound,
    }
