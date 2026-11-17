"""EvalMath HG-04: exact GF(2) observer quotient and risk-aware audit values.

Mathematical statements are proved in Hypergames/HG04_QUOTIENT_THEOREMS.md.
This module uses exact rationals and finite reference enumeration only.
"""
from __future__ import annotations
from collections import defaultdict
from fractions import Fraction as F


def rank_gf2(rows: tuple[int, ...], dimension: int) -> int:
    if type(dimension) is not int or dimension < 0:
        raise ValueError("invalid dimension")
    pivots = {}
    for row in rows:
        if type(row) is not int or not 0 <= row < 1 << dimension:
            raise ValueError("invalid GF2 row mask")
        x = row
        while x:
            k = x.bit_length() - 1
            if k in pivots:
                x ^= pivots[k]
            else:
                pivots[k] = x
                break
    return len(pivots)


def uniform_parity_error(rows: tuple[int, ...], target: int, dimension: int) -> F:
    """Optimal 0-1 error for Y=p.X given Z=CX and uniform X in GF(2)^d."""
    if type(target) is not int or not 0 <= target < 1 << dimension:
        raise ValueError("invalid target mask")
    k = rank_gf2(rows, dimension)
    return F(0) if rank_gf2(rows + (target,), dimension) == k else F(1, 2)


def independently_enumerated_error(rows: tuple[int, ...], target: int,
                                   dimension: int) -> F:
    """Independent fibre-majority oracle at d<=10; separate from row reduction."""
    if type(dimension) is not int or not 1 <= dimension <= 10:
        raise ValueError("reference oracle limited to 1..10 dimensions")
    rank_gf2(rows, dimension)
    if type(target) is not int or not 0 <= target < 1 << dimension:
        raise ValueError("invalid target")
    fibres = defaultdict(lambda: [0, 0])
    for x in range(1 << dimension):
        observation = tuple((x & row).bit_count() % 2 for row in rows)
        label = (x & target).bit_count() % 2
        fibres[observation][label] += 1
    return F(sum(min(masses) for masses in fibres.values()), 1 << dimension)


def audited_release_expectation(correct_probability: F) -> F:
    q = F(correct_probability)
    if not 0 <= q <= 1:
        raise ValueError("probability outside [0,1]")
    return 25 * q - 16


def prior_optimal_value(p_hidden_one: F, horizon: int) -> F:
    """Registered HG02: uniform public arithmetic, binary private mode, +/- rewards."""
    p = F(p_hidden_one)
    if not 0 <= p <= 1 or type(horizon) is not int or horizon not in (4, 5):
        raise ValueError("invalid prior or action horizon")
    blind = 25 * max(p, 1-p) - 15
    return max(F(0), blind, F(9) if horizon == 5 else F(0))
