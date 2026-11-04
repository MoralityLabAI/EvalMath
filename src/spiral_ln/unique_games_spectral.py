"""UG-FID-02: exact finite spectral and curvature witnesses for translation games.

The diagonal mean of local clopen projections has operator norm equal to
the maximum satisfied-edge fraction. A separate syndrome enumerator checks
the minimum-support curvature correction. All values are exact Fractions.

This file contains no algorithm for the upstream 3SAT-to-UG reduction.
Both explicit diagonalization and syndrome enumeration are exponential.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations, product

from spiral_ln.unique_games_topology import (
    Edge, TranslationGame, cycle_signature,
)


def satisfaction_spectrum(game: TranslationGame) -> tuple[Fraction, ...]:
    """Diagonal eigenvalues of |E|^-1 sum_e P_e on l2(K^V)."""
    m = len(game.edges)
    if not m:
        return (Fraction(1),) * game.alphabet_size ** game.vertices
    return tuple(
        Fraction(sum(a[e.v] == (a[e.u] ^ e.shift) for e in game.edges), m)
        for a in product(range(game.alphabet_size), repeat=game.vertices)
    )


def diagonal_operator_norm(game: TranslationGame) -> Fraction:
    """Exact norm: all eigenvalues are nonnegative."""
    return max(satisfaction_spectrum(game))


def frustration_ground_energy(game: TranslationGame) -> Fraction:
    """Least eigenvalue of H = I - average(P_e)."""
    return min(Fraction(1) - val for val in satisfaction_spectrum(game))


def curvature(game: TranslationGame, cochain: tuple[int, ...]) -> tuple[int, ...]:
    """Fundamental-cycle holonomies after replacing all edge shifts.

    The forest is fixed by ordered edge occurrences. For F_2^s, signs vanish.
    Fundamental cycles span the entire graph cycle space over F_2.
    """
    if len(cochain) != len(game.edges):
        raise ValueError("cochain length differs from edge occurrences")
    if any(not 0 <= x < game.alphabet_size for x in cochain):
        raise ValueError("cochain element outside fixed translation alphabet")
    instance = TranslationGame(
        game.vertices, game.bits,
        tuple(Edge(e.u, e.v, shift) for e, shift in zip(game.edges, cochain)),
    )
    return tuple(h for _, h in cycle_signature(instance))


def minimum_curvature_repair(game: TranslationGame) -> tuple[int, tuple[int, ...]]:
    """Independent exhaustive syndrome decoder minimizing nonzero EDGES.

    Finds xi with curvature(xi)=curvature(c). Each nonzero K symbol counts
    as one edge correction, even if multiple bits are set.
    """
    m = len(game.edges)
    target = curvature(game, tuple(e.shift for e in game.edges))
    if target == tuple(0 for _ in target):
        return 0, (0,) * m
    for weight in range(1, m + 1):
        for positions in combinations(range(m), weight):
            for changes in product(range(1, game.alphabet_size), repeat=weight):
                candidate = [0] * m
                for i, shift in zip(positions, changes):
                    candidate[i] = shift
                result = tuple(candidate)
                if curvature(game, result) == target:
                    return weight, result
    raise AssertionError("original cochain is always a valid correction")


def gap_threshold(epsilon: Fraction, delta: Fraction, tau: Fraction) -> Fraction:
    """Threshold separating promised norm bands under +-tau estimation.

    This is a parameter check, NOT proof of the upstream reduction nor an
    efficient matrix representation of the exponentially large diagonal.
    """
    if not (0 < epsilon < Fraction(1, 2)
            and 0 < delta < Fraction(1, 2)
            and 0 <= tau
            and 2 * tau < 1 - epsilon - delta):
        raise ValueError("gap parameters do not provide strict separation")
    return ((1 - epsilon - tau) + (delta + tau)) / 2
