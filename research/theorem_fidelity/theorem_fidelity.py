"""Exact finite semantic witnesses for Unique Games theorem contracts.

These are small arithmetic checks. They do not prove computational hardness.
"""
from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import comb, factorial


@dataclass(frozen=True)
class Edge:
    u: int
    v: int
    relation: tuple[tuple[int, int], ...]


def permutation(relation: tuple[tuple[int, int], ...], q: int) -> bool:
    return (q > 0 and len(relation) == q
            and sorted(a for a, _ in relation) == list(range(q))
            and sorted(b for _, b in relation) == list(range(q)))


def is_f2_translation(relation: tuple[tuple[int, int], ...]) -> bool:
    return permutation(relation, 2) and any(
        all((a ^ shift) == b for a, b in relation) for shift in (0, 1)
    )


def simple_bipartite(vertices: int, edges: tuple[Edge, ...]) -> bool:
    if vertices < 1 or len({(e.u, e.v) for e in edges}) != len(edges):
        return False
    if any(not (0 <= e.u < vertices and 0 <= e.v < vertices) for e in edges):
        return False
    return any(all(sides[e.u] == 0 and sides[e.v] == 1 for e in edges)
               for sides in product((0, 1), repeat=vertices))


def score(labels: tuple[int, ...], edges: tuple[Edge, ...]) -> Fraction:
    if not edges:
        raise ValueError("Unique Games contract requires nonempty edge set")
    return Fraction(sum((labels[e.u], labels[e.v]) in e.relation for e in edges), len(edges))


def optimum(vertices: int, alphabet: int, edges: tuple[Edge, ...]) -> Fraction:
    if vertices < 1 or alphabet < 1 or not edges:
        raise ValueError("positive vertices/alphabet and nonempty edges required")
    if any(e.u not in range(vertices) or e.v not in range(vertices) for e in edges):
        raise ValueError("edge endpoint out of range")
    if any(any(a not in range(alphabet) or b not in range(alphabet)
               for a, b in e.relation) for e in edges):
        raise ValueError("label out of range")
    return max(score(labels, edges)
               for labels in product(range(alphabet), repeat=vertices))


def satisfiable_3cnf(variables: int, clauses: tuple[tuple[int, int, int], ...]) -> bool:
    """Literals use signed one-based indices; repeated literals are permitted."""
    if variables < 1 or any(len(c) != 3 or any(abs(l) not in range(1, variables + 1)
                        for l in c) for c in clauses):
        raise ValueError("invalid 3CNF")
    for assignment in product((False, True), repeat=variables):
        if all(any(assignment[abs(lit) - 1] == (lit > 0) for lit in clause)
               for clause in clauses):
            return True
    return False


def exp_polynomial_certificate(coefficient: int, degree: int) -> dict[str, int]:
    """Construct n with 2^n > C*n^d using the binomial theorem.

    For k=d+1 and n>=2k: binom(n,k)*2^k*k! >= n^k.
    Also 2^n >= binom(n,k). Choosing n > C*2^k*k! proves the bound.
    The code checks integer instances; the universal derivation is documented.
    """
    if coefficient < 1 or degree < 0:
        raise ValueError("coefficient >= 1 and degree >= 0 required")
    k = degree + 1
    scale = (2 ** k) * factorial(k)
    n = max(2 * k, coefficient * scale + 1)
    assert n >= 2 * k and n > coefficient * scale
    assert comb(n, k) * scale >= n ** k
    assert n ** k > coefficient * (n ** degree) * scale
    return {"coefficient": coefficient, "degree": degree, "n": n, "k": k,
            "scale": scale, "choose": comb(n, k)}


def witnesses() -> dict:
    eq = ((0, 0), (1, 1))
    flip = ((0, 1), (1, 0))
    single = (Edge(0, 1, eq),)
    universal = ((0, 0), (0, 1), (1, 0), (1, 1))
    # Inconsistent four-cycle; distinct, bipartite, F2 translation constraints.
    cycle = (Edge(0, 1, eq), Edge(2, 1, eq),
             Edge(2, 3, eq), Edge(0, 3, flip))
    unsat = ((1, 1, 1), (-1, -1, -1))
    return {
        "TF-01": {"weak_existential_score": str(score((0, 1), single)),
                  "actual_optimum": str(optimum(2, 2, single)),
                  "valid_game": simple_bipartite(2, single)},
        "TF-02": {"universal_relation_permutation": permutation(universal, 2),
                  "universal_relation_optimum": str(optimum(2, 2, (Edge(0, 1, universal),)))},
        "TF-03": {"simple_bipartite": simple_bipartite(4, cycle),
                  "all_translations": all(is_f2_translation(e.relation) for e in cycle),
                  "optimum": str(optimum(4, 2, cycle))},
        "TF-04": {"unsat_3cnf": not satisfiable_3cnf(1, unsat),
                  "trivial_language_accepts": True},
        "TF-05": {"alphabet_n2": 2 ** 2, "alphabet_n3": 2 ** 3,
                  "fixed_alphabet_false": (2 ** 2 != 2 ** 3)},
        "TF-06": exp_polynomial_certificate(2, 2),
    }


def validate() -> dict:
    w = witnesses()
    assert w["TF-01"] == {"weak_existential_score": "0", "actual_optimum": "1", "valid_game": True}
    assert w["TF-02"] == {"universal_relation_permutation": False,
                          "universal_relation_optimum": "1"}
    assert w["TF-03"] == {"simple_bipartite": True, "all_translations": True,
                          "optimum": "3/4"}
    assert w["TF-04"] == {"unsat_3cnf": True, "trivial_language_accepts": True}
    assert w["TF-05"]["fixed_alphabet_false"] is True
    assert w["TF-06"]["n"] > 2 * w["TF-06"]["scale"]
    return w


if __name__ == "__main__":
    print(validate())
