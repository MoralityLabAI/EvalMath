"""Finite translation-game probes for four proposed game-space conjectures.

Only small exact finite identities are certified here. Spectral comparisons
use floating eigenvalues; a small census is never evidence for asymptotics.
Translations use xor in F_2^s and count nonzero VECTOR residuals per edge.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations, product
from math import factorial

import numpy as np

from spiral_ln.unique_games_topology import (
    Edge, TranslationGame, cycle_signature, normalized_shifts,
    optimum_by_labels, minimum_bad_edges,
)


def signed_laplacian_gap(game: TranslationGame, character: int) -> float:
    """Bottom of normalized signed Laplacian, loopless graphs with no isolates.

    Character chi_y(x)=(-1)^popcount(y & x) for nonzero y in F_2^s.
    L=I-D^(-1/2) A_chi D^(-1/2), with each edge occurrence counted.
    """
    n = game.vertices
    if character <= 0 or character >= game.alphabet_size:
        raise ValueError("character must be nontrivial and within alphabet")
    degrees = np.zeros(n, dtype=float)
    adjacency = np.zeros((n, n), dtype=float)
    for e in game.edges:
        if e.u == e.v:
            raise ValueError("spectral probe requires a loopless multigraph")
        degrees[e.u] += 1
        degrees[e.v] += 1
        sign = -1.0 if (character & e.shift).bit_count() % 2 else 1.0
        adjacency[e.u, e.v] += sign
        adjacency[e.v, e.u] += sign
    if not np.all(degrees):
        raise ValueError("spectral probe requires positive vertex degrees")
    inv = 1 / np.sqrt(degrees)
    lap = np.eye(n) - inv[:, None] * adjacency * inv[None, :]
    return max(0.0, float(np.linalg.eigvalsh(lap)[0]))


def mean_twisted_gap(game: TranslationGame) -> float:
    return float(np.mean([signed_laplacian_gap(game, ch)
                          for ch in range(1, game.alphabet_size)]))


def spectral_cosystolic_probe(game: TranslationGame) -> dict:
    phi = float(1 - optimum_by_labels(game)[0])
    lam = mean_twisted_gap(game)
    sharp_upper = game.alphabet_size / (game.alphabet_size - 1) * phi
    return {"cosystolic_fraction": phi, "twisted_gap_mean": lam,
            "ratio": lam / phi if phi else None,
            "alphabet_upper_bound": sharp_upper,
            "upper_bound_verified": lam <= sharp_upper + 1e-9}


def _is_simple_cycle(game: TranslationGame, indices: tuple[int, ...]) -> bool:
    """Loop, pair of parallel edges, or connected 2-regular edge subgraph."""
    if not indices:
        return False
    degree: dict[int, int] = {}
    adj: dict[int, set[int]] = {}
    for i in indices:
        e = game.edges[i]
        degree[e.u] = degree.get(e.u, 0) + 1
        degree[e.v] = degree.get(e.v, 0) + 1
        adj.setdefault(e.u, set()).add(e.v)
        adj.setdefault(e.v, set()).add(e.u)
    if any(d != 2 for d in degree.values()):
        return False
    start = next(iter(degree))
    reached = {start}
    stack = [start]
    while stack:
        for nbr in adj[stack.pop()]:
            if nbr not in reached:
                reached.add(nbr)
                stack.append(nbr)
    return len(reached) == len(degree)


def first_frustrated_cycles(game: TranslationGame) -> tuple[int | None, int]:
    """Shortest obstructed edge-cycle length and number of its edge sets."""
    for length in range(1, len(game.edges) + 1):
        count = 0
        for indices in combinations(range(len(game.edges)), length):
            if _is_simple_cycle(game, indices):
                hol = 0
                for i in indices:
                    hol ^= game.edges[i].shift
                count += hol != 0
        if count:
            return length, count
    return None, 0


def ground_moment(game: TranslationGame, power: int) -> Fraction:
    """Normalized trace of (I-|E|^-1 sum P_e)^power, exact rationals."""
    if power < 0:
        raise ValueError("nonnegative integer power required")
    m = len(game.edges)
    total = Fraction(0)
    for a in product(range(game.alphabet_size), repeat=game.vertices):
        sat = sum(a[e.u] ^ a[e.v] == e.shift for e in game.edges)
        energy = Fraction(m - sat, m) if m else Fraction(0)
        total += energy ** power
    return total / game.alphabet_size ** game.vertices


def moment_obstruction_probe(game: TranslationGame) -> dict:
    """First non-flat moment and closed coefficient from shortest cycles."""
    flat = TranslationGame(game.vertices, game.bits, tuple(
        Edge(e.u, e.v, 0) for e in game.edges))
    length, count = first_frustrated_cycles(game)
    if length is None:
        return {"first_frustrated_length": None, "coefficient": "0",
                "matching_through": len(game.edges),
                "all_matching": all(ground_moment(game, j) == ground_moment(flat, j)
                                    for j in range(len(game.edges) + 1))}
    diffs = [ground_moment(game, j) - ground_moment(flat, j)
             for j in range(length + 1)]
    predicted = Fraction((-1) ** (length + 1) * factorial(length) * count,
                         len(game.edges) ** length *
                         game.alphabet_size ** (length - 1))
    return {"first_frustrated_length": length, "cycle_count": count,
            "coefficient": str(predicted), "measured": str(diffs[-1]),
            "low_moments_equal": all(d == 0 for d in diffs[:-1]),
            "first_coefficient_equal": diffs[-1] == predicted}


def anf_degree(truth_table: tuple[int, ...]) -> int:
    """Algebraic normal form degree of a Boolean function, -1 for zero."""
    n = len(truth_table)
    if not n or n & (n - 1) or any(x not in (0, 1) for x in truth_table):
        raise ValueError("truth table needs a power-of-two number of bits")
    coeffs = list(truth_table)
    for bit in range(n.bit_length() - 1):
        for i in range(n):
            if i & (1 << bit):
                coeffs[i] ^= coeffs[i ^ (1 << bit)]
    return max((i.bit_count() for i, value in enumerate(coeffs) if value),
               default=-1)


def latent_stability(q: tuple[int, ...], noise: tuple[tuple[int, int], ...]) -> Fraction:
    """For C(k,u)=k xor q(u), average change under independent noise.

    Noise entries (delta_k, delta_u) are equally likely, including repeats.
    """
    if not noise:
        raise ValueError("need a nonempty noise law")
    if any(k not in (0, 1) or not 0 <= u < len(q) for k, u in noise):
        raise ValueError("noise element outside F_2 x F_2^r")
    if anf_degree(q) < -1:
        raise AssertionError
    return Fraction(sum(k ^ q[x] ^ q[x ^ u]
                        for k, u in noise for x in range(len(q))),
                    len(noise) * len(q))


def degree_probe_min_detection(
        qbits: int, noise: tuple[tuple[int, int], ...], degree: int
) -> tuple[Fraction, tuple[int, ...]]:
    """All F(k,u)=k xor f(u) with ANF degree(f)<=degree.

    Constant term omitted because it cannot change perturbation sensitivity.
    This is a rank-one restriction-to-K probe family, not a full rank-r family.
    """
    if qbits < 1 or qbits > 3 or degree < 0:
        raise ValueError("bounded exhaustive probe supports 1..3 latent bits")
    n = 1 << qbits
    if not noise or any(k not in (0, 1) or not 0 <= u < n for k, u in noise):
        raise ValueError("noise element outside ambient group")
    monomials = [mask for mask in range(1, n) if mask.bit_count() <= degree]
    best = Fraction(2)
    best_terms: tuple[int, ...] = ()
    for flags in product((0, 1), repeat=len(monomials)):
        selected = tuple(mask for mask, flag in zip(monomials, flags) if flag)
        values = tuple(sum((x & mask) == mask for mask in selected) % 2
                       for x in range(n))
        detection = latent_stability(values, noise)
        if detection < best:
            best, best_terms = detection, selected
    return best, best_terms


def _connected_potentials(game: TranslationGame) -> tuple[tuple[int, ...], frozenset[int]]:
    adj: list[list[tuple[int, int, int]]] = [[] for _ in range(game.vertices)]
    for i, e in enumerate(game.edges):
        adj[e.u].append((e.v, e.shift, i))
        adj[e.v].append((e.u, e.shift, i))
    pot: list[int | None] = [None] * game.vertices
    pot[0] = 0
    tree: set[int] = set()
    stack = [0]
    for u in stack:
        for v, c, i in adj[u]:
            if pot[v] is None:
                pot[v] = int(pot[u]) ^ c
                stack.append(v)
                tree.add(i)
    if any(p is None for p in pot):
        raise ValueError("covering experiment requires connected base graph")
    return tuple(int(p) for p in pot), frozenset(tree)


def holonomy_image(game: TranslationGame) -> tuple[int, ...]:
    """Subgroup of K generated by fundamental-cycle holonomies."""
    _connected_potentials(game)
    span = {0}
    for _, h in cycle_signature(game):
        span |= {x ^ h for x in tuple(span)}
    return tuple(sorted(span))


def regular_holonomy_cover(game: TranslationGame) -> tuple[TranslationGame, tuple[int, ...]]:
    """Connected regular cover of degree |image Hol| with exact labeling."""
    p, _ = _connected_potentials(game)
    fiber = holonomy_image(game)
    idx = {a: i for i, a in enumerate(fiber)}
    d = len(fiber)
    lifted = []
    for e in game.edges:
        residue = p[e.u] ^ e.shift ^ p[e.v]
        for h in fiber:
            lifted.append(Edge(e.u * d + idx[h],
                               e.v * d + idx[h ^ residue], e.shift))
    labels = tuple(p[v] ^ h for v in range(game.vertices) for h in fiber)
    return TranslationGame(game.vertices * d, game.bits, tuple(lifted)), labels


def double_covers(game: TranslationGame) -> tuple[TranslationGame, ...]:
    """Gauge-normalized connected two-sheet covers, one per nonzero chord toggle.

    Tree-edge permutations are identity; each chord chooses swap or identity.
    This enumerates all connected degree-two covers up to fiber gauge.
    """
    _, tree = _connected_potentials(game)
    chords = [i for i in range(len(game.edges)) if i not in tree]
    out = []
    for mask in range(1, 1 << len(chords)):
        selected = {chords[j] for j in range(len(chords)) if mask & (1 << j)}
        edges = tuple(Edge(e.u * 2 + i, e.v * 2 + (i ^ int(k in selected)), e.shift)
                      for k, e in enumerate(game.edges) for i in (0, 1))
        out.append(TranslationGame(game.vertices * 2, game.bits, edges))
    return tuple(out)


def minimal_double_cover_frustration(game: TranslationGame) -> Fraction | None:
    covers = double_covers(game)
    if not covers:
        return None
    return min(Fraction(minimum_bad_edges(lift)[0], len(lift.edges))
               for lift in covers)


def edited_holonomy_degree(game: TranslationGame, max_edits: int) -> int:
    """Small exact oracle r_edit_{max_edits/m}; one vector symbol per edge."""
    if not 0 <= max_edits <= len(game.edges):
        raise ValueError("edit budget outside edge occurrences")
    best = len(holonomy_image(game))
    for k in range(1, max_edits + 1):
        for positions in combinations(range(len(game.edges)), k):
            for corrections in product(range(1, game.alphabet_size), repeat=k):
                shifts = [e.shift for e in game.edges]
                for i, change in zip(positions, corrections):
                    shifts[i] ^= change
                updated = TranslationGame(game.vertices, game.bits, tuple(
                    Edge(e.u, e.v, s) for e, s in zip(game.edges, shifts)))
                best = min(best, len(holonomy_image(updated)))
    return best
