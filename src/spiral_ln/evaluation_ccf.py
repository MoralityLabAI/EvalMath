"""Finite certificate interfaces with decoder side information (CCF-01)."""
from collections import defaultdict
from fractions import Fraction
from itertools import combinations


def conflict_graph(n, contexts):
    """A context maps feasible state indices to authorization bits."""
    return frozenset((i, j) for c in contexts for i, j in combinations(sorted(c), 2)
                     if c[i] != c[j])


def partitions(n):
    """Canonical restricted-growth strings, exactly one per set partition."""
    def grow(labels):
        if len(labels) == n:
            yield labels
        else:
            for k in range(max(labels, default=-1) + 2):
                yield from grow(labels + (k,))
    yield from grow(())


def optimal_code(n, edges):
    """Minimum number of labels and a proper coloring (finite exact search)."""
    valid = (p for p in partitions(n) if all(p[i] != p[j] for i, j in edges))
    p = min(valid, key=lambda p: (len(set(p)), p))
    return len(set(p)), p


def envelope(contexts, labels):
    """Maximal universally sound and minimal universally complete decoders."""
    cells = defaultdict(list)
    for j, ctx in enumerate(contexts):
        for i, bit in ctx.items():
            cells[j, labels[i]].append(bit)
    return {k: (min(v), max(v)) for k, v in cells.items()}


def risks(contexts, labels, weights=None):
    """Unconditional false-negative (sound) and false-positive (complete) mass."""
    bounds = envelope(contexts, labels)
    fn = fp = total = 0
    for j, ctx in enumerate(contexts):
        for i, bit in ctx.items():
            w = 1 if weights is None else weights[j, i]
            if w < 0:
                raise ValueError("negative mass")
            lo, hi = bounds[j, labels[i]]
            fn += w * (bit - lo)
            fp += w * (hi - bit)
            total += w
    return Fraction(fn, total), Fraction(fp, total)


def edge_contexts(edges):
    return tuple({i: 0, j: 1} for i, j in sorted(edges))
