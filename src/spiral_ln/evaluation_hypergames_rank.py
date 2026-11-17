"""HG-05: exact multi-goal observation rank, audit costs, finite fibres.

Mathematical reference shared by EvalMath and GPTStoryworld. Classical binary
vectors only. No neural inference, hidden seeds, or quantum measurement claims.
"""
from __future__ import annotations

from collections import defaultdict
from fractions import Fraction as Q
from itertools import combinations


def rank(rows: tuple[int, ...] | list[int], dimension: int) -> int:
    """Exact rank over F_2; integers encode rows, least significant bit x_0."""
    if type(dimension) is not int or dimension < 0:
        raise ValueError("invalid dimension")
    pivots: dict[int, int] = {}
    for r in rows:
        if type(r) is not int or r < 0 or (r >> dimension):
            raise ValueError("row exceeds specified dimension")
        while r:
            pivot = r.bit_length() - 1
            if pivot in pivots:
                r ^= pivots[pivot]
            else:
                pivots[pivot] = r
                break
    return len(pivots)


def deficiency(observation_rows: tuple[int, ...] | list[int],
               target_rows: tuple[int, ...] | list[int], dimension: int) -> int:
    """H(PX|CX) in bits for uniform X, for any finite GF(2) matrices C,P."""
    c = tuple(observation_rows)
    p = tuple(target_rows)
    return rank(c + p, dimension) - rank(c, dimension)


def exact_joint_success(observation_rows, target_rows, dimension: int) -> Q:
    """Best possible probability of guessing the complete target vector."""
    return Q(1, 1 << deficiency(observation_rows, target_rows, dimension))


def independent_fibre_success(observation_rows, target_rows, dimension: int) -> Q:
    """Separate exhaustive oracle, bounded to d <= 10."""
    if type(dimension) is not int or not (1 <= dimension <= 10):
        raise ValueError("independent finite oracle supports 1 <= d <= 10")
    c, p = tuple(observation_rows), tuple(target_rows)
    rank(c + p, dimension)  # also validates all masks
    fibres: dict[tuple[int, ...], dict[tuple[int, ...], int]] = defaultdict(lambda: defaultdict(int))
    for x in range(1 << dimension):
        z = tuple((x & r).bit_count() % 2 for r in c)
        y = tuple((x & r).bit_count() % 2 for r in p)
        fibres[z][y] += 1
    return Q(sum(max(labels.values()) for labels in fibres.values()), 1 << dimension)


def minimum_probe_cost(observation_rows, target_rows, probe_rows,
                       probe_costs, dimension: int) -> dict:
    """Exact weighted spanning audit for <= 14 candidate public probes.

    Returns infeasible when no available probe set covers all goal parities.
    Ties are broken first by lower cost, then lower probe count, then indices.
    """
    c, p, probes = tuple(observation_rows), tuple(target_rows), tuple(probe_rows)
    costs = tuple(probe_costs)
    if len(probes) != len(costs) or len(probes) > 14:
        raise ValueError("at most 14 probes and matching costs required")
    if any(type(w) is not Q or w <= 0 for w in costs):
        raise ValueError("strictly positive exact rational costs required")
    rank(c + p + probes, dimension)
    best = None
    for n in range(len(probes) + 1):
        for idx in combinations(range(len(probes)), n):
            selected = c + tuple(probes[i] for i in idx)
            if deficiency(selected, p, dimension) == 0:
                candidate = (sum((costs[i] for i in idx), Q(0)), n, idx)
                if best is None or candidate < best:
                    best = candidate
    if best is None:
        return {"status": "infeasible", "cost": None, "indices": ()}
    return {"status": "optimal", "cost": best[0], "indices": best[2]}


def ideal_action_values(missing_bits: int, audit_cost_per_bit: Q = Q(1)) -> dict[str, Q]:
    """Declared one-shot decision: submit code, buy perfect semantic audits, abstain.

    Assumes each missing independent target parity can be audited at unit cost
    and all other code bits are exact. This is an *offline decision ceiling*.
    """
    if type(missing_bits) is not int or missing_bits < 0:
        raise ValueError("invalid missing rank")
    if type(audit_cost_per_bit) is not Q or audit_cost_per_bit <= 0:
        raise ValueError("positive rational cost required")
    q = Q(1, 1 << missing_bits)
    return {"submit": 25 * q - 15,
            "semantic_audit_then_submit": Q(10) - audit_cost_per_bit * missing_bits,
            "abstain": Q(0)}


def padding_invariant(rows, targets, dimension: int, padded_dimension: int) -> bool:
    if type(padded_dimension) is not int or padded_dimension < dimension:
        raise ValueError("padding must only add nuisance dimensions")
    return deficiency(rows, targets, dimension) == deficiency(rows, targets, padded_dimension)
