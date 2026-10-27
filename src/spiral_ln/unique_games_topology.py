"""Exact finite topology of F_2^s translation Unique Games.

An oriented constraint (u, v, c) is satisfied when x[v] = x[u] XOR c.
XOR represents vector addition in F_2^s; each edge is one unweighted
constraint even when s > 1. No claim about a general UGC reduction is made.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations, product


@dataclass(frozen=True)
class Edge:
    u: int
    v: int
    shift: int


@dataclass(frozen=True)
class TranslationGame:
    vertices: int
    bits: int
    edges: tuple[Edge, ...]

    def __post_init__(self) -> None:
        if self.vertices < 1 or self.bits < 1:
            raise ValueError("vertices and bits must be positive")
        for edge in self.edges:
            if not (0 <= edge.u < self.vertices and 0 <= edge.v < self.vertices):
                raise ValueError("edge endpoint outside vertex range")
            if not 0 <= edge.shift < (1 << self.bits):
                raise ValueError("edge shift outside F_2^s")

    @property
    def alphabet_size(self) -> int:
        return 1 << self.bits


def _forest(game: TranslationGame, keep: frozenset[int] | None = None):
    """Rooted spanning forest and GF(2)^s potentials of retained edges.

    Returns root potentials, tree edge IDs, component roots and chord residuals.
    Nonzero residuals are precisely the cycle-holonomy obstructions.
    """
    if keep is None:
        keep = frozenset(range(len(game.edges)))
    adjacency: list[list[tuple[int, int, int]]] = [[] for _ in range(game.vertices)]
    for i in sorted(keep):
        e = game.edges[i]
        adjacency[e.u].append((e.v, e.shift, i))
        adjacency[e.v].append((e.u, e.shift, i))
    potentials: list[int | None] = [None] * game.vertices
    tree: set[int] = set()
    roots: list[int] = []
    for root in range(game.vertices):
        if potentials[root] is not None:
            continue
        roots.append(root)
        potentials[root] = 0
        queue = [root]
        for u in queue:
            for v, shift, eid in adjacency[u]:
                if potentials[v] is None:
                    potentials[v] = potentials[u] ^ shift  # type: ignore[operator]
                    tree.add(eid)
                    queue.append(v)
    p = tuple(int(a) for a in potentials)
    chords = tuple((i, p[e.u] ^ e.shift ^ p[e.v])
                   for i, e in enumerate(game.edges) if i in keep and i not in tree)
    return p, frozenset(tree), tuple(roots), chords


def cycle_signature(game: TranslationGame) -> tuple[tuple[int, int], ...]:
    """Canonical fundamental-cycle holonomies, fixed edge order and forest."""
    return _forest(game)[3]


def normalized_shifts(game: TranslationGame) -> tuple[int, ...]:
    """Gauge-normalize all tree edges to zero."""
    potentials, _, _, _ = _forest(game)
    return tuple(potentials[e.u] ^ e.shift ^ potentials[e.v] for e in game.edges)


def betti_one(game: TranslationGame) -> int:
    """Dimension of H^1 of the underlying finite multigraph (loops allowed)."""
    _, tree, _, _ = _forest(game)
    return len(game.edges) - len(tree)


def coboundary_zero(game: TranslationGame) -> bool:
    """The 1-cochain c is a coboundary iff all fundamental holonomies vanish."""
    return all(value == 0 for _, value in cycle_signature(game))


def _satisfied(game: TranslationGame, labels: tuple[int, ...]) -> int:
    return sum(labels[e.v] == (labels[e.u] ^ e.shift) for e in game.edges)


def optimum_by_labels(game: TranslationGame) -> tuple[Fraction, tuple[int, ...]]:
    """Independent exact oracle: enumerate labelings, fix one root per component."""
    _, _, roots, _ = _forest(game)
    free = tuple(v for v in range(game.vertices) if v not in roots)
    best = -1
    best_labels: tuple[int, ...] = ()
    for assignment in product(range(game.alphabet_size), repeat=len(free)):
        labels = [0] * game.vertices
        for v, a in zip(free, assignment):
            labels[v] = a
        count = _satisfied(game, tuple(labels))
        if count > best:
            best, best_labels = count, tuple(labels)
    m = len(game.edges)
    return Fraction(best, m) if m else Fraction(1), best_labels


def minimum_bad_edges(game: TranslationGame) -> tuple[int, tuple[int, ...]]:
    """Independent exact oracle: delete fewest edges to kill all holonomy."""
    m = len(game.edges)
    for deleted_size in range(m + 1):
        for deleted in combinations(range(m), deleted_size):
            retained = frozenset(range(m)).difference(deleted)
            if all(h == 0 for _, h in _forest(game, retained)[3]):
                return deleted_size, deleted
    raise AssertionError("deleting every edge must work")


def cosystolic_value(game: TranslationGame) -> Fraction:
    """Block-Hamming cosystolic norm translated to satisfied-edge fraction."""
    bad, _ = minimum_bad_edges(game)
    return Fraction(len(game.edges) - bad, len(game.edges)) if game.edges else Fraction(1)


def fundamental_cycle_packing_bound(game: TranslationGame) -> int:
    """Edge-disjoint obstructed fundamental cycles lower-bound bad edges."""
    _, tree, _, chords = _forest(game)
    adj: list[list[tuple[int, int]]] = [[] for _ in range(game.vertices)]
    for i in tree:
        e = game.edges[i]
        adj[e.u].append((e.v, i))
        adj[e.v].append((e.u, i))

    def tree_path(u: int, v: int) -> frozenset[int]:
        queue = [(u, frozenset())]
        seen = {u}
        for w, used in queue:
            if w == v:
                return used
            for nxt, eid in adj[w]:
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append((nxt, used | {eid}))
        raise AssertionError("chord endpoints must be connected in the tree")

    cycles = [tree_path(game.edges[i].u, game.edges[i].v) | {i}
              for i, holonomy in chords if holonomy]
    return max((len(packing) for k in range(len(cycles) + 1)
                for packing in combinations(cycles, k)
                if len(set().union(*packing)) == sum(map(len, packing))), default=0)


def _game(n: int, bits: int, pairs: tuple[tuple[int, int], ...], shifts: tuple[int, ...]):
    return TranslationGame(n, bits, tuple(Edge(u, v, c) for (u, v), c in zip(pairs, shifts)))


def finite_census() -> dict:
    """Exhaustive bounded census; all integer/Fraction arithmetic."""
    checks = 0
    c4_pairs = ((0, 2), (0, 3), (1, 2), (1, 3))
    c4_hist: dict[str, int] = {}
    for shifts in product(range(4), repeat=4):
        game = _game(4, 2, c4_pairs, shifts)
        opt, labels = optimum_by_labels(game)
        bad, _ = minimum_bad_edges(game)
        assert opt == Fraction(4 - bad, 4)
        assert coboundary_zero(game) == (bad == 0)
        assert _satisfied(game, labels) == 4 - bad
        assert betti_one(game) == 1
        assert fundamental_cycle_packing_bound(game) <= bad
        key = str(bad)
        c4_hist[key] = c4_hist.get(key, 0) + 1
        checks += 1

    k23_pairs = ((0, 2), (1, 2), (0, 3), (1, 3), (0, 4), (1, 4))
    k23_hist: dict[str, int] = {}
    zero = _game(5, 2, k23_pairs, (0,) * 6)
    _, tree, _, _ = _forest(zero)
    chords = tuple(i for i in range(6) if i not in tree)
    assert len(chords) == 2
    for h1, h2 in product(range(4), repeat=2):
        shifts = tuple((h1 if i == chords[0] else h2 if i == chords[1] else 0)
                       for i in range(6))
        game = _game(5, 2, k23_pairs, shifts)
        val, _ = optimum_by_labels(game)
        bad, _ = minimum_bad_edges(game)
        assert val == Fraction(6 - bad, 6)
        assert fundamental_cycle_packing_bound(game) <= bad
        assert betti_one(game) == 2
        k23_hist[str(bad)] = k23_hist.get(str(bad), 0) + 1
        checks += 1

    all_pairs = tuple(combinations(range(4), 2))
    k4_count = 0
    for flags in product((None, 0, 1), repeat=len(all_pairs)):
        edges = tuple(Edge(u, v, flag) for (u, v), flag in zip(all_pairs, flags)
                      if flag is not None)
        game = TranslationGame(4, 1, edges)
        val, _ = optimum_by_labels(game)
        bad, _ = minimum_bad_edges(game)
        assert val == cosystolic_value(game)
        assert val == (Fraction(len(edges) - bad, len(edges)) if edges else Fraction(1))
        assert (bad == 0) == coboundary_zero(game)
        assert fundamental_cycle_packing_bound(game) <= bad
        assert betti_one(game) == len(cycle_signature(game))
        k4_count += 1
        checks += 1
    return {"checks": checks, "c4_F2_2": c4_hist,
            "k23_F2_2_gauge_classes": k23_hist, "all_signed_simple_K4_subgraphs": k4_count,
            "empty_edges_value": "1", "method": "exhaustive integer enumeration"}
