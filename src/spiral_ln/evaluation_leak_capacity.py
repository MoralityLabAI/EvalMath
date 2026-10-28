"""Capacity-sensitive disclosure for finite category-feedback channels.

All arithmetic is exact.  The two collision-count algorithms deliberately have
separate implementations: bounded integer-kernel enumeration versus grouping
all realizable cell-count vectors by observed margins.

The support contains one tuple of category indices per nonempty joint cell;
sizes gives the corresponding cell capacities.  Each face names a set of
category maps observed *jointly*.  Multiple faces are observed together.
Neither a model nor a grader is evaluated here.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import product
from math import comb, gcd, lcm, prod


def observation_matrix(support, faces, sizes=None):
    """Return sorted cells, aligned capacities and independent 0/1 margin rows.

    This implementation is intentionally separate from leak_topology.margin_rows_k
    so the tests can cross-check construction of the observation matrix.
    """
    raw = tuple(tuple(cell) for cell in support)
    if not raw:
        raise ValueError("support must be nonempty")
    width = len(raw[0])
    if width == 0 or any(len(cell) != width for cell in raw):
        raise ValueError("cells must have the same positive number of coordinates")
    if any(any(type(label) is not int or label < 0 for label in cell) for cell in raw):
        raise ValueError("cell labels must be nonnegative integers")
    if sizes is None:
        sizes = (1,) * len(raw)
    sizes = tuple(sizes)
    if len(sizes) != len(raw) or any(type(s) is not int or s < 1 for s in sizes):
        raise ValueError("capacities must be positive integers aligned with cells")
    pairs = sorted(zip(raw, sizes))
    cells = tuple(cell for cell, _ in pairs)
    if len(set(cells)) != len(cells):
        raise ValueError("joint cells must be distinct")
    capacities = tuple(size for _, size in pairs)
    faces = tuple(tuple(face) for face in faces)
    if any(len(set(face)) != len(face) or any(type(j) is not int or j < 0 or j >= width
                                             for j in face) for face in faces):
        raise ValueError("each face must have distinct, in-range category indices")
    rows = []
    for face in faces:
        groups = sorted({tuple(cell[j] for j in face) for cell in cells})
        for group in groups:
            rows.append(tuple(int(tuple(cell[j] for j in face) == group) for cell in cells))
    return cells, capacities, tuple(rows)


def positive_bounded_moves(rows, sizes):
    """Enumerate one of each pair {z,-z} of nonzero integral kernel moves.

    The first nonzero entry must be positive.  Exact suffix feasibility bounds
    prune partial vectors whose remaining coordinates cannot cancel a margin.
    This algorithm is exponential and intended for small declared supports.
    """
    sizes = tuple(sizes)
    n = len(sizes)
    if any(type(s) is not int or s < 1 for s in sizes):
        raise ValueError("capacities must be positive integers")
    rows = tuple(tuple(row) for row in rows)
    if any(len(row) != n or any(type(v) is not int for v in row) for row in rows):
        raise ValueError("rows must be integer vectors matching capacities")
    suffix = [[0] * (n + 1) for _ in rows]
    for r, row in enumerate(rows):
        for i in range(n - 1, -1, -1):
            suffix[r][i] = suffix[r][i + 1] + abs(row[i]) * sizes[i]
    partial = [0] * n
    balances = [0] * len(rows)

    def search(i, seen_positive):
        if i == n:
            if seen_positive and all(value == 0 for value in balances):
                yield tuple(partial)
            return
        for value in range(-sizes[i], sizes[i] + 1):
            if not seen_positive and value < 0:
                continue
            possible = True
            for r, row in enumerate(rows):
                balances[r] += row[i] * value
                if abs(balances[r]) > suffix[r][i + 1]:
                    possible = False
            partial[i] = value
            if possible:
                yield from search(i + 1, seen_positive or value > 0)
            for r, row in enumerate(rows):
                balances[r] -= row[i] * value
        partial[i] = 0

    yield from search(0, False)


def sparse_kernel_certificate(support, faces):
    """A primitive exact integer kernel vector supported on at most rank+1 cells.

    Returns None precisely when the rational kernel is zero.  The vector is
    obtained by setting one free RREF coordinate to one and clearing
    denominators, so it serves as a finite capacity upper-bound witness.
    """
    cells, _, rows = observation_matrix(support, faces)
    n = len(cells)
    reduced = [[Fraction(v) for v in row] for row in rows]
    pivots = []
    next_row = 0
    for column in range(n):
        pivot = next((j for j in range(next_row, len(reduced))
                      if reduced[j][column] != 0), None)
        if pivot is None:
            continue
        reduced[next_row], reduced[pivot] = reduced[pivot], reduced[next_row]
        scale = reduced[next_row][column]
        reduced[next_row] = [v / scale for v in reduced[next_row]]
        for j in range(len(reduced)):
            if j != next_row and reduced[j][column] != 0:
                factor = reduced[j][column]
                reduced[j] = [a - factor * b for a, b in
                              zip(reduced[j], reduced[next_row])]
        pivots.append(column)
        next_row += 1
        if next_row == len(reduced):
            break
    free = next((j for j in range(n) if j not in pivots), None)
    if free is None:
        return None
    rational = [Fraction(0) for _ in range(n)]
    rational[free] = Fraction(1)
    for i, column in enumerate(pivots):
        rational[column] = -reduced[i][free]
    denominator = lcm(*(v.denominator for v in rational))
    integers = [int(v * denominator) for v in rational]
    common = gcd(*integers)
    vector = tuple(v // common for v in integers)
    if next(v for v in vector if v != 0) < 0:
        vector = tuple(-v for v in vector)
    assert sum(v != 0 for v in vector) <= len(pivots) + 1
    assert all(sum(a * b for a, b in zip(row, vector)) == 0 for row in rows)
    return vector


def bounded_witness(support, faces, sizes=None):
    """First exact pair of distinct feasible count tables, or None."""
    cells, capacities, rows = observation_matrix(support, faces, sizes)
    move = next(positive_bounded_moves(rows, capacities), None)
    if move is None:
        return None
    a = tuple(max(value, 0) for value in move)
    b = tuple(max(-value, 0) for value in move)
    assert a != b and all(sum(v * x for v, x in zip(row, move)) == 0 for row in rows)
    return {"cells": cells, "move": move, "first_counts": a, "second_counts": b}


def collision_counts_lattice(support, faces, sizes=None):
    """Exact ordered record-pair collisions for joint and observed margins.

    Uniform independent item bits.  If z is the difference of cell counts of
    two records, it contributes prod_c C(2*s_c, s_c+z_c) ordered record pairs.
    The zero vector is joint-cell agreement.  Symmetry doubles each positive
    bounded move.  Probabilities have denominator 4**sum(sizes).
    """
    cells, capacities, rows = observation_matrix(support, faces, sizes)
    joint = prod(comb(2 * s, s) for s in capacities)
    extra = 0
    move_count = 0
    first_move = None
    for move in positive_bounded_moves(rows, capacities):
        if first_move is None:
            first_move = move
        move_count += 1
        extra += 2 * prod(comb(2 * s, s + z) for s, z in zip(capacities, move))
    observed = joint + extra
    denominator = 4 ** sum(capacities)
    return {
        "cells": cells, "sizes": capacities, "integer_move_pairs": move_count,
        "first_move": first_move, "joint_record_pairs": joint,
        "observed_record_pairs": observed,
        "joint_collision_probability": Fraction(joint, denominator),
        "observed_collision_probability": Fraction(observed, denominator),
        "collision_ratio": Fraction(observed, joint),
        "strict": extra > 0,
    }


def collision_counts_direct(support, faces, sizes=None):
    """Independent oracle: group count vectors with binomial multiplicity."""
    cells, capacities, rows = observation_matrix(support, faces, sizes)
    masses = {}
    joint = 0
    for counts in product(*(range(s + 1) for s in capacities)):
        weight = prod(comb(s, x) for s, x in zip(capacities, counts))
        margins = tuple(sum(a * x for a, x in zip(row, counts)) for row in rows)
        masses[margins] = masses.get(margins, 0) + weight
        joint += weight * weight
    return joint, sum(m * m for m in masses.values())


def critical_uniform_capacity(support, faces, max_capacity):
    """Minimal common capacity that admits a nonzero move, if at most max_capacity.

    None means no witness *within the searched capacities*, not rank zero.
    """
    if type(max_capacity) is not int or max_capacity < 1:
        raise ValueError("max_capacity must be a positive integer")
    for size in range(1, max_capacity + 1):
        if bounded_witness(support, faces, (size,) * len(support)) is not None:
            return size
    return None
