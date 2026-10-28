"""Tiny exact #CNF benchmark: independent-component factorization versus brute force.

The work metric counts full component assignments examined, excluding parsing,
graph traversal and fixed overhead. This is a toy control of structural reuse,
not an ETH algorithm, cryptanalytic claim or measured wall-clock speedup.
"""
from __future__ import annotations

from random import Random

Clause = tuple[int, ...]
CNF = tuple[Clause, ...]


def validate_cnf(n: int, clauses: CNF) -> None:
    if type(n) is not int or not 0 <= n <= 20:
        raise ValueError("toy benchmark supports 0 <= n <= 20")
    for clause in clauses:
        if not isinstance(clause, tuple) or not clause:
            raise ValueError("nonempty tuple clause required")
        if any(type(lit) is not int or lit == 0 or abs(lit) > n for lit in clause):
            raise ValueError("invalid literal")
        if len({abs(lit) for lit in clause}) != len(clause):
            raise ValueError("one literal per variable per clause required")


def exact_count(n: int, clauses: CNF) -> tuple[int, int]:
    """Count full satisfying assignments by exhaustive independent enumeration."""
    validate_cnf(n, clauses)
    count = 0
    for mask in range(1 << n):
        if all(any(bool(mask & (1 << (abs(lit) - 1))) == (lit > 0)
                   for lit in clause) for clause in clauses):
            count += 1
    return count, 1 << n


def components(n: int, clauses: CNF) -> tuple[tuple[int, ...], ...]:
    """Connected variable components of the clause hypergraph; isolates included."""
    validate_cnf(n, clauses)
    adjacent = [set() for _ in range(n)]
    for clause in clauses:
        vs = [abs(x) - 1 for x in clause]
        for v in vs[1:]:
            adjacent[vs[0]].add(v)
            adjacent[v].add(vs[0])
    seen: set[int] = set()
    blocks = []
    for root in range(n):
        if root in seen:
            continue
        seen.add(root)
        stack = [root]
        block = []
        while stack:
            v = stack.pop()
            block.append(v)
            for w in sorted(adjacent[v]):
                if w not in seen:
                    seen.add(w)
                    stack.append(w)
        blocks.append(tuple(sorted(block)))
    return tuple(blocks)


def factorized_count(n: int, clauses: CNF) -> tuple[int, int, tuple[int, ...]]:
    """Exact product of component counts; returns counts and assignment proxy."""
    blocks = components(n, clauses)
    total, work = 1, 0
    for block in blocks:
        index = {v: i + 1 for i, v in enumerate(block)}
        sub = tuple(tuple((1 if lit > 0 else -1) * index[abs(lit) - 1]
                          for lit in clause)
                    for clause in clauses if abs(clause[0]) - 1 in index)
        partial, visited = exact_count(len(block), sub)
        total *= partial
        work += visited
    return total, work, tuple(len(b) for b in blocks)


def seeded_instance(blocks: int, seed: int, connected: bool) -> tuple[int, CNF]:
    """Seeded fixed-width instances with disconnected and joined control graphs."""
    if type(blocks) is not int or not 1 <= blocks <= 5:
        raise ValueError("blocks must be in [1,5]")
    rng = Random(seed)
    clauses: list[Clause] = []
    for b in range(blocks):
        vs = (3 * b + 1, 3 * b + 2, 3 * b + 3)
        for _ in range(3):
            clauses.append(tuple(rng.choice((-1, 1)) * x for x in vs))
    if connected:
        for b in range(1, blocks):
            clauses.append((3 * b, 3 * b + 1, -(3 * b + 2)))
    return 3 * blocks, tuple(clauses)


def run_toy_suite(seed: int = 20261027) -> list[dict[str, object]]:
    """Reproducible exact-count tests over connected/disconnected controls."""
    rows = []
    for blocks in (2, 3, 4, 5):
        for linked in (False, True):
            n, clauses = seeded_instance(blocks, seed + blocks, linked)
            count, baseline = exact_count(n, clauses)
            factored, work, sizes = factorized_count(n, clauses)
            if factored != count:
                raise AssertionError("factorization changed exact #SAT")
            rows.append({
                "variables": n,
                "linked_control": linked,
                "solutions": count,
                "components": list(sizes),
                "baseline_assignments": baseline,
                "factorized_assignments": work,
                "assignment_proxy_ratio": f"{baseline}/{work}",
                "exactly_equal": True,
            })
    return rows
