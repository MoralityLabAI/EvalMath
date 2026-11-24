from fractions import Fraction as F
from itertools import combinations, product
from spiral_ln.evaluation_ccf import (
    conflict_graph, edge_contexts, envelope, optimal_code, partitions, risks,
)


def independent_chromatic(n, edges):
    """Labeled assignments with no restricted-growth or partition machinery."""
    for k in range(1, n + 1):
        if any(all(p[i] != p[j] for i, j in edges)
               for p in product(range(k), repeat=n)):
            return k
    raise AssertionError("no coloring")


def test_all_graphs_on_five_vertices():
    pairs = list(combinations(range(5), 2))
    for mask in range(1 << len(pairs)):
        edges = frozenset(e for j, e in enumerate(pairs) if mask >> j & 1)
        contexts = edge_contexts(edges)
        assert conflict_graph(5, contexts) == edges
        k, labels = optimal_code(5, edges)
        assert k == independent_chromatic(5, edges)
        assert all(lo == hi for lo, hi in envelope(contexts, labels).values())


def test_five_cycle_budget():
    edges = frozenset({(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)})
    contexts = edge_contexts(edges)
    assert optimal_code(5, edges)[0] == 3
    assert min(risks(contexts, p) for p in partitions(5) if len(set(p)) <= 2) == (F(1, 10), F(1, 10))


def test_side_information_and_weights():
    contexts = ({0: 0, 1: 1}, {1: 0, 2: 1})
    assert optimal_code(3, conflict_graph(3, contexts))[0] == 2
    weights = {(0, 0): 1, (0, 1): 3, (1, 1): 2, (1, 2): 4}
    assert risks(contexts, (0, 0, 1), weights) == (F(3, 10), F(1, 10))
