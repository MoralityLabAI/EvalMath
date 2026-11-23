"""Finite balanced-gain-graph (random-cluster) partition function.

All computations are exact Fractions. Works on F2^s translation games with
edge occurrences, including loops and parallel edges. Brute force in |E|.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations, product
from math import comb, cos, pi

from spiral_ln.unique_games_topology import TranslationGame


def _balanced_components(game: TranslationGame, subset: tuple[int, ...]):
    """Union-find with xor potentials. Return (balanced, component count)."""
    n = game.vertices
    parent = list(range(n))
    weight = [0] * n  # a[v] xor a[parent[v]]
    rank = [0] * n

    def find(v):
        if parent[v] != v:
            r, delta = find(parent[v])
            weight[v] ^= delta
            parent[v] = r
        return parent[v], weight[v]

    components = n
    for i in subset:
        e = game.edges[i]
        ru, au = find(e.u)
        rv, av = find(e.v)
        if ru == rv:
            if (au ^ av) != e.shift:
                return False, components
            continue
        shift = e.shift ^ au ^ av
        if rank[ru] < rank[rv]:
            parent[ru] = rv
            weight[ru] = shift
        else:
            parent[rv] = ru
            weight[rv] = shift
            if rank[ru] == rank[rv]:
                rank[ru] += 1
        components -= 1
    return True, components


def balanced_subgraph_coefficients(game: TranslationGame):
    """Coefficients [z^j] E_a prod_e(1+z P_e(a)), j=0..m.

    Sum over balanced edge subsets F of z^|F| q^(k(F)-|V|).
    """
    m, q = len(game.edges), game.alphabet_size
    coefficients = [Fraction(0)] * (m + 1)
    for k in range(m + 1):
        for subset in combinations(range(m), k):
            balanced, components = _balanced_components(game, subset)
            if balanced:
                coefficients[k] += Fraction(1, q ** (game.vertices - components))
    return tuple(coefficients)


def flat_subgraph_coefficients(game: TranslationGame):
    """Flat random-cluster polynomial on the same underlying multigraph."""
    from spiral_ln.unique_games_topology import Edge
    flat = TranslationGame(game.vertices, game.bits, tuple(
        Edge(e.u, e.v, 0) for e in game.edges
    ))
    return balanced_subgraph_coefficients(flat)


def direct_partition(game: TranslationGame, z: Fraction | int):
    """Independent oracle: sum over all vertex labelings, exponential in |V|."""
    z = Fraction(z)
    q = game.alphabet_size
    total = Fraction(0)
    for a in product(range(q), repeat=game.vertices):
        term = Fraction(1)
        for e in game.edges:
            if (a[e.u] ^ a[e.v]) == e.shift:
                term *= 1 + z
        total += term
    return total / (q ** game.vertices)


def polynomial_value(coefficients: tuple[Fraction, ...], z: Fraction | int):
    z = Fraction(z)
    return sum((c * z**j for j, c in enumerate(coefficients)), Fraction(0))


def balanced_random_cluster_probability(game: TranslationGame, z: Fraction | int):
    """Exactly Z_c(z)/Z_flat(z), valid for z>=0."""
    z = Fraction(z)
    if z < 0:
        raise ValueError("random-cluster weights require z >= 0")
    good = polynomial_value(balanced_subgraph_coefficients(game), z)
    flat = polynomial_value(flat_subgraph_coefficients(game), z)
    return good / flat


def annealed_coefficients(game: TranslationGame):
    """Expectation over iid uniform edge shifts; exact binomial coefficients."""
    m, q = len(game.edges), game.alphabet_size
    return tuple(Fraction(comb(m, k), q**k) for k in range(m + 1))


def frustrated_cycle_closed_form(length: int, q: int, z: Fraction | int):
    """Exact Z(z) on a cycle with nonzero holonomy, including length 1 and 2."""
    if length < 1 or q < 2:
        raise ValueError("cycle length>=1, alphabet order>=2")
    z = Fraction(z)
    return (1 + z / q)**length - (z / q)**length


def flat_cycle_closed_form(length: int, q: int, z: Fraction | int):
    """Exact Z(z) for flat q-label translation constraints on a cycle."""
    if length < 1 or q < 2:
        raise ValueError("cycle length>=1, alphabet order>=2")
    z = Fraction(z)
    return (1 + z / q)**length + (q - 1) * (z / q)**length


def cycle_spectral_closed_form(length: int, q: int):
    """Character mean lambda_min on cycle with one nonzero holonomy.

    L=I-D^(-1/2) A_chi D^(-1/2), including two parallel edges for length 2.
    For q=2^s, fraction q/(2(q-1)) of nontrivial characters detect holonomy.
    The twisted cycle has antiperiodic Fourier modes (2j+1) pi/length.
    """
    if length < 2 or q < 2 or q & (q - 1):
        raise ValueError("length>=2 and q=2^s")
    return q / (2 * (q - 1)) * (1 - cos(pi / length))
