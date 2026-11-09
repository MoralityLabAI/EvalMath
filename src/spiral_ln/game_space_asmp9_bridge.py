"""UGCS-03: ASMP-9 exact gauge-access bridge for F2^s translation games.

Fundamental-cycle queries identify the algebraic connection modulo vertex
gauge. They do not certify an optimal/low-frustration representative.
Exact oracles below are exponential when enumerating assignments or gauge
classes; the cycle basis itself is computed by spanning forests.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import product

from spiral_ln.unique_games_topology import (
    Edge, TranslationGame, betti_one, cycle_signature, normalized_shifts,
)


def _check_shared_graph(a: TranslationGame, b: TranslationGame) -> None:
    if a.vertices != b.vertices or a.bits != b.bits or tuple(
        (e.u, e.v) for e in a.edges
    ) != tuple((e.u, e.v) for e in b.edges):
        raise ValueError("gauge comparison requires identical ordered edge graph and alphabet")


def connected_components(game: TranslationGame) -> int:
    adj: list[list[int]] = [[] for _ in range(game.vertices)]
    for edge in game.edges:
        adj[edge.u].append(edge.v)
        adj[edge.v].append(edge.u)
    seen: set[int] = set()
    count = 0
    for v in range(game.vertices):
        if v in seen:
            continue
        count += 1
        seen.add(v)
        todo = [v]
        for u in todo:
            for w in adj[u]:
                if w not in seen:
                    seen.add(w)
                    todo.append(w)
    return count


def gauge_witness(a: TranslationGame, b: TranslationGame) -> tuple[int, ...] | None:
    """Solve b_e=a_e+p(u)+p(v) over F2^s; returns one vertex gauge or None."""
    _check_shared_graph(a, b)
    adj: list[list[tuple[int, int]]] = [[] for _ in range(a.vertices)]
    for e, f in zip(a.edges, b.edges):
        delta = e.shift ^ f.shift
        adj[e.u].append((e.v, delta))
        adj[e.v].append((e.u, delta))
    potentials: list[int | None] = [None] * a.vertices
    for root in range(a.vertices):
        if potentials[root] is not None:
            continue
        potentials[root] = 0
        queue = [root]
        for u in queue:
            for v, delta in adj[u]:
                expected = int(potentials[u]) ^ delta
                if potentials[v] is None:
                    potentials[v] = expected
                    queue.append(v)
                elif potentials[v] != expected:
                    return None
    return tuple(int(p) for p in potentials)


def quotient_coordinates(game: TranslationGame) -> tuple[int, ...]:
    """Exact ASMP-9 analogue: K-valued fundamental cycle-return measurements."""
    return tuple(h for _, h in cycle_signature(game))


def quotient_size_and_orbit_size(game: TranslationGame) -> tuple[int, int]:
    """For K=F2^s, |C1/im d|=q^beta1, |im d|=q^(|V|-components)."""
    q = game.alphabet_size
    return q ** betti_one(game), q ** (game.vertices - connected_components(game))


def canonical_connection(game: TranslationGame) -> TranslationGame:
    """Tree edge shifts vanish, chord shifts contain all quotient coordinates."""
    return TranslationGame(game.vertices, game.bits, tuple(
        Edge(e.u, e.v, s) for e, s in zip(game.edges, normalized_shifts(game))
    ))


def partial_cycle_access_counterexample(
    graph: TranslationGame, queried_chords: tuple[int, ...]
) -> tuple[TranslationGame, TranslationGame]:
    """Flat versus frustrated, indistinguishable under registered partial queries.

    Only fundamental-cycle coordinates are admitted as measurements.
    For any proper subset of fundamental chords, changing an unqueried
    chord leaves all queried cycle values zero but creates nonzero holonomy.
    """
    chord_ids = tuple(i for i, _ in cycle_signature(graph))
    if len(set(queried_chords)) != len(queried_chords) or any(
        i not in chord_ids for i in queried_chords
    ):
        raise ValueError("query identifiers must be distinct fundamental chords")
    unqueried = next((i for i in chord_ids if i not in queried_chords), None)
    if unqueried is None:
        raise ValueError("requires at least one unqueried independent cycle")
    flat = TranslationGame(graph.vertices, graph.bits, tuple(
        Edge(e.u, e.v, 0) for e in graph.edges
    ))
    frustrated = TranslationGame(graph.vertices, graph.bits, tuple(
        Edge(e.u, e.v, 1 if i == unqueried else 0)
        for i, e in enumerate(graph.edges)
    ))
    assert dict(cycle_signature(flat)).keys() == dict(cycle_signature(frustrated)).keys()
    assert all(dict(cycle_signature(flat))[i] ==
               dict(cycle_signature(frustrated))[i] for i in queried_chords)
    return flat, frustrated


def satisfaction_pattern_law(
    game: TranslationGame, queried_edges: tuple[int, ...]
) -> dict[tuple[bool, ...], Fraction]:
    """Exact joint law of queried clopen projections under uniform labelings."""
    if len(set(queried_edges)) != len(queried_edges) or any(
        i < 0 or i >= len(game.edges) for i in queried_edges
    ):
        raise ValueError("edge queries must be distinct valid occurrences")
    q = game.alphabet_size
    counts: Counter[tuple[bool, ...]] = Counter()
    for labels in product(range(q), repeat=game.vertices):
        pat = tuple(
            labels[game.edges[i].v] == (labels[game.edges[i].u] ^ game.edges[i].shift)
            for i in queried_edges
        )
        counts[pat] += 1
    denom = q ** game.vertices
    return {p: Fraction(count, denom) for p, count in counts.items()}


def maxcut_count(vertices: int, undirected_edges: tuple[tuple[int, int], ...]) -> int:
    """Small independent MaxCut oracle; shows F2 all-ones game = MaxCut."""
    return max((sum(bits[u] != bits[v] for u, v in undirected_edges)
                for bits in product((0, 1), repeat=vertices)), default=0)
