"""HG-08 exact GF(2) intervention semantics, support certificates and query bounds.

Public synthetic parity functions only. Exact, deterministic and independent of
any fitted neural model. All integers are coordinate-set bit masks.
"""
from __future__ import annotations

from fractions import Fraction
from math import comb

from spiral_ln.evaluation_hypergames_rank import deficiency


def _valid(mask: int, dimension: int) -> bool:
    return type(mask) is int and 0 <= mask < (1 << dimension)


def parity(mask: int, state: int, dimension: int) -> int:
    if type(dimension) is not int or dimension < 1 or not _valid(mask, dimension) or not _valid(state, dimension):
        raise ValueError('invalid GF2 state, dimension, or mask')
    return (mask & state).bit_count() & 1


def causal_difference(goal_rows: tuple[int, ...], flip_mask: int, dimension: int) -> tuple[int, ...]:
    if type(dimension) is not int or dimension < 1 or not _valid(flip_mask, dimension):
        raise ValueError('invalid intervention')
    if not goal_rows or any(not _valid(r, dimension) for r in goal_rows):
        raise ValueError('invalid goal matrix')
    return tuple((r & flip_mask).bit_count() & 1 for r in goal_rows)


def direct_difference(goal_rows: tuple[int, ...], baseline: int, flip_mask: int, dimension: int) -> tuple[int, ...]:
    return tuple(parity(row, baseline ^ flip_mask, dimension) ^ parity(row, baseline, dimension)
                 for row in goal_rows)


def peel_known(raw_delta: tuple[int, ...], subset_mask: int,
               certified: tuple[frozenset[int], ...], dimension: int) -> tuple[int, ...]:
    if len(raw_delta) != len(certified) or not _valid(subset_mask, dimension):
        raise ValueError('invalid peeling input')
    if any(type(v) is not int or v not in (0, 1) for v in raw_delta):
        raise ValueError('invalid parity value')
    answer = []
    for r, known in zip(raw_delta, certified):
        if any(type(i) is not int or i < 0 or i >= dimension for i in known):
            raise ValueError('invalid certified indices')
        parity_of_known = sum((subset_mask >> i) & 1 for i in known) & 1
        answer.append(r ^ parity_of_known)
    return tuple(answer)


def support_certified(witnesses: dict[int, tuple[int, ...]],
                      dimension: int, target_count: int, support_width: int) -> bool:
    """Validate singleton outcomes from an intervention transcript.

    `witnesses[i]` is a k-output parity response to exactly e_i.
    This proves a *support* when all target rows have declared weight s.
    """
    if (type(dimension) is not int or dimension < 1 or
            type(target_count) is not int or target_count < 1 or
            type(support_width) is not int or support_width < 1):
        raise ValueError('invalid certificate contract')
    counts = [0] * target_count
    for coordinate, result in witnesses.items():
        if type(coordinate) is not int or coordinate < 0 or coordinate >= dimension:
            raise ValueError('invalid certificate coordinate')
        if len(result) != target_count or any(type(v) is not int or v not in (0, 1) for v in result):
            raise ValueError('invalid singleton witness')
        for j, val in enumerate(result):
            counts[j] += val
    return counts == [support_width] * target_count


def information_lower_bound(dimension: int, support_width: int) -> int:
    """Minimum worst-case binary oracle queries for one uniform sparse support."""
    if (type(dimension) is not int or type(support_width) is not int or
            dimension < 1 or not 0 <= support_width <= dimension):
        raise ValueError('invalid uniform sparse prior')
    possibilities = comb(dimension, support_width)
    return (possibilities - 1).bit_length()


def ideal_joint_code_success(observed_query_masks: tuple[int, ...],
                             goal_rows: tuple[int, ...], dimension: int) -> Fraction:
    """Information ceiling for independent *uniform unrestricted* goal masks.

    This ceiling is not an exact sparse-posterior calculation.
    """
    h = deficiency(observed_query_masks, goal_rows, dimension)
    return Fraction(1, 1 << h)


def forced_release_utility(success_probability: Fraction) -> Fraction:
    if type(success_probability) is not Fraction or not 0 <= success_probability <= 1:
        raise ValueError('expected an exact probability')
    return 25 * success_probability - 15
