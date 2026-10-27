"""Finite, exact semantic witnesses for Unique Games statement mutations.

Only finite witnesses are certified here. Runtime and alphabet growth cases
illustrate quantifier dependencies and require separate asymptotic reasoning.
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
    return (len(relation) == alphabet and
            sorted(a for a, _ in relation) == list(range(alphabet)) and
            sorted(b for _, b in relation) == list(range(alphabet)))

def score(labels, edges):
    if not edges:
        return Fraction(1)
    return Fraction(sum((labels[e.u], labels[e.v]) in e.relation for e in edges), len(edges))

def optimum(vertices, alphabet, edges):
    if vertices < 1 or alphabet < 1:
        raise ValueError("positive vertices and alphabet required")
    if not edges:
        return Fraction(1)
    return max(score(labels, edges) for labels in product(range(alphabet), repeat=vertices))

def unsatisfiable_unit_cnf(clauses):
    return not any(all(any((assignment[abs(lit) - 1] if lit > 0
                           else not assignment[abs(lit) - 1]) for lit in clause)
                       for clause in clauses)
                   for assignment in product((False, True), repeat=1))

def validate():
    eq = Edge(0, 1, ((0, 0), (1, 1)))
    ne = Edge(0, 1, ((0, 1), (1, 0)))
    universal = ((0, 0), (0, 1), (1, 0), (1, 1))
    assert score((0, 1), (eq,)) == 0 and optimum(2, 2, (eq,)) == 1
    assert not is_permutation(universal, 2)
    assert optimum(2, 2, (eq, ne)) == Fraction(1, 2)
    assert unsatisfiable_unit_cnf(((1,), (-1,)))
    assert len({2**n for n in (2, 3, 4)}) == 3
    assert all(2**n == v for n, v in ((2, 4), (3, 8), (4, 16)))
    return {"TF-01": "finite witness", "TF-02": "finite witness",
            "TF-03": "finite witness", "TF-04": "propositional witness",
            "TF-05": "asymptotic contract illustration",
            "TF-06": "asymptotic contract illustration"}

if __name__ == "__main__":
    print(validate())
