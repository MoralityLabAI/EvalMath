"""Exact finite probability kernels shared by RHT-27 and RHT-28.

Rows describe interventions on an explicitly declared, sufficient state. This
module validates finite laws; it cannot establish that a physical system has no
unrecorded state or that a supplied kernel describes that system.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from typing import Iterable

Q = Fraction
Law = tuple[Fraction, ...]


def rational(value: int | str | Fraction) -> Fraction:
    """Parse exact values, rejecting implicit binary floats and Boolean values."""
    if isinstance(value, bool) or not isinstance(value, (int, str, Fraction)):
        raise TypeError("use an integer, rational string, or Fraction")
    return Fraction(value)


def probability(value: int | str | Fraction) -> Fraction:
    result = rational(value)
    if not 0 <= result <= 1:
        raise ValueError("probability must lie in [0, 1]")
    return result


def law(values: Iterable[int | str | Fraction]) -> Law:
    if isinstance(values, (str, bytes)):
        raise TypeError("a law requires a sequence of probabilities")
    result = tuple(probability(value) for value in values)
    if not result or sum(result, Q(0)) != 1:
        raise ValueError("a law must be nonempty and sum exactly to one")
    return result


def _size(size: int) -> int:
    if isinstance(size, bool) or not isinstance(size, int) or size < 1:
        raise ValueError("state-space size must be a positive integer")
    return size


def point_mass(index: int, size: int) -> Law:
    _size(size)
    if isinstance(index, bool) or not isinstance(index, int) or not 0 <= index < size:
        raise ValueError("point-mass index must be inside the state space")
    return tuple(Q(int(i == index)) for i in range(size))


@dataclass(frozen=True)
class Kernel:
    """A nonempty rectangular row-stochastic matrix, normalized exactly."""

    rows: tuple[Law, ...]

    def __post_init__(self) -> None:
        rows = tuple(law(row) for row in self.rows)
        if not rows or len({len(row) for row in rows}) != 1:
            raise ValueError("a kernel needs nonempty equally sized probability rows")
        object.__setattr__(self, "rows", rows)

    @property
    def input_size(self) -> int:
        return len(self.rows)

    @property
    def output_size(self) -> int:
        return len(self.rows[0])


def identity(size: int) -> Kernel:
    _size(size)
    return Kernel(tuple(point_mass(i, size) for i in range(size)))


def apply(mu: Iterable[int | str | Fraction], kernel: Kernel) -> Law:
    initial = law(mu)
    if len(initial) != kernel.input_size:
        raise ValueError("law dimension must match the kernel input space")
    return tuple(
        sum((initial[i] * kernel.rows[i][j] for i in range(kernel.input_size)), Q(0))
        for j in range(kernel.output_size)
    )


def compose(first: Kernel, second: Kernel) -> Kernel:
    """Execute first, then second; rectangular intermediate spaces must agree."""
    if first.output_size != second.input_size:
        raise ValueError("kernel intermediate dimensions must match")
    return Kernel(tuple(apply(row, second) for row in first.rows))


def total_variation(left: Iterable[int | str | Fraction],
                    right: Iterable[int | str | Fraction]) -> Fraction:
    p, q = law(left), law(right)
    if len(p) != len(q):
        raise ValueError("total variation requires a common finite space")
    return sum((abs(a - b) for a, b in zip(p, q)), Q(0)) / 2


def dobrushin(kernel: Kernel) -> Fraction:
    """Exact TV contraction coefficient, including the one-input boundary."""
    return max((total_variation(a, b) for a, b in combinations(kernel.rows, 2)),
               default=Q(0))


def row_distance(left: Kernel, right: Kernel) -> Fraction:
    if (left.input_size, left.output_size) != (right.input_size, right.output_size):
        raise ValueError("row discrepancy requires equally shaped kernels")
    return max(total_variation(a, b) for a, b in zip(left.rows, right.rows))


def expectation(mu: Iterable[int | str | Fraction],
                payoff: Iterable[int | str | Fraction]) -> Fraction:
    distribution = law(mu)
    if isinstance(payoff, (str, bytes)):
        raise TypeError("a payoff requires a sequence of bounded values")
    values = tuple(probability(value) for value in payoff)
    if len(values) != len(distribution):
        raise ValueError("payoff and law must share a finite space")
    return sum((p * value for p, value in zip(distribution, values)), Q(0))
