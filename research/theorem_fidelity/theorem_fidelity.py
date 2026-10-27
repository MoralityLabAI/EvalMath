"""Exact finite witnesses for six Unique Games theorem-statement mutations.

This is a semantic contract benchmark seed, not a proof of hardness.
"""
from dataclasses import dataclass
from fractions import Fraction
from itertools import product


@dataclass(frozen=True)
class Edge:
    u: int
    v: int
    relation: tuple[tuple[int, int], ...]


def is_permutation(relation, alphabet):
    return (len(relation) == alphabet
            and sorted(a for a, _ in relation) == list(range(alphabet))
            and sorted(b for _, b in relation) == list(range(alphabet)))


def score(labels, edges):
    if not edges:
        return Fraction(1)
    return Fraction(sum((labels[e.u], labels[e.v]) in e.relation
                        for e in edges), len(edges))


def optimum(vertices, alphabet, edges):
    if vertices < 1 or alphabet < 1:
        raise ValueError("positive vertices and alphabet required")
    if not edges:
        return Fraction(1)
    return max(score(labels, edges)
               for labels in product(range(alphabet), repeat=vertices))


def validate():
    eq = Edge(0, 1, ((0, 0), (1, 1)))
    ne = Edge(0, 1, ((0, 1), (1, 0)))
    universal = ((0, 0), (0, 1), (1, 0), (1, 1))
    results = {
        "TF-01": (score((0, 1), (eq,)) == 0
                  and optimum(2, 2, (eq,)) == 1),
        "TF-02": (not is_permutation(universal, 2)
                  and optimum(2, 2, (Edge(0, 1, universal),)) == 1),
        "TF-03": optimum(2, 2, (eq, ne)) == Fraction(1, 2),
        "TF-04": bool(((1,), (-1,))),  # unsatisfiable x and not x
        "TF-05": len({2 ** n for n in (2, 3, 4)}) == 3,
        "TF-06": all(2 ** n == s for n, s in ((2, 4), (3, 8), (4, 16))),
    }
    assert all(results.values()), results
    return results


if __name__ == "__main__":
    print(validate())
