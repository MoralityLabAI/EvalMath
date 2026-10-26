"""Exact finite adaptive evaluation disclosure, with an independent one-hot interval law.

A deterministic policy is a rooted response tree. Each query returns a subset
sum of a *fixed* hidden count table. The next query is selected by previous
answers; queries are visible in the transcript. All weights and probabilities
are exact rational numbers. No model, judge or training loop is executed.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from functools import lru_cache
from itertools import combinations_with_replacement, product
from math import comb, prod


@dataclass(frozen=True)
class FinitePrior:
    """Positive integer masses for distinct feasible cell-count tables."""

    capacities: tuple[int, ...]
    states: tuple[tuple[int, ...], ...]
    weights: tuple[int, ...]

    def __post_init__(self):
        n = len(self.capacities)
        if (not n or any(type(s) is not int or s < 1 for s in self.capacities)
                or not self.states or len(self.states) != len(self.weights)
                or len(set(self.states)) != len(self.states)
                or any(type(w) is not int or w < 1 for w in self.weights)
                or any(len(x) != n or any(type(v) is not int or v < 0 or v > s
                                              for v, s in zip(x, self.capacities))
                       for x in self.states)):
            raise ValueError("invalid positive finite prior on feasible cell tables")

    @property
    def total(self) -> int:
        return sum(self.weights)


def fair_bit_prior(capacities: tuple[int, ...]) -> FinitePrior:
    """Independent fair item bits; P(cell counts) proportional to binomial weights."""
    capacities = tuple(capacities)
    if not capacities or any(type(s) is not int or s < 1 for s in capacities):
        raise ValueError("positive cell capacities required")
    states = tuple(product(*(range(s + 1) for s in capacities)))
    weights = tuple(prod(comb(s, x) for s, x in zip(capacities, state)) for state in states)
    result = FinitePrior(capacities, states, weights)
    assert result.total == 2 ** sum(capacities)
    return result


def one_hot_prior(n: int) -> FinitePrior:
    """Exactly one marked cell among n, uniformly chosen (a conditional prior)."""
    if type(n) is not int or n < 1:
        raise ValueError("n must be positive")
    return FinitePrior((1,) * n, tuple(tuple(int(i == j) for i in range(n))
                                          for j in range(n)), (1,) * n)


def interval_bank(n: int) -> tuple[tuple[int, ...], ...]:
    if type(n) is not int or n < 1:
        raise ValueError("n must be positive")
    return tuple(tuple(int(a <= i < b) for i in range(n))
                 for a in range(n) for b in range(a + 1, n + 1))


def validate_queries(prior: FinitePrior, queries) -> tuple[tuple[int, ...], ...]:
    queries = tuple(tuple(q) for q in queries)
    if (not queries or any(len(q) != len(prior.capacities)
                           or any(type(a) is not int or a not in (0, 1) for a in q)
                           for q in queries)):
        raise ValueError("query bank must contain binary subset-sum row vectors")
    return queries


@dataclass(frozen=True)
class Node:
    """One query index with exhaustive reachable answer branches; None terminates."""
    query: int | None = None
    branches: tuple[tuple[int, Node], ...] = ()


def dot(q, state) -> int:
    return sum(a * b for a, b in zip(q, state))


def transcript(state, tree: Node, queries) -> tuple[tuple[int, int], ...]:
    path = []
    node = tree
    while node.query is not None:
        if type(node.query) is not int or not 0 <= node.query < len(queries):
            raise ValueError("policy references an invalid query")
        response = dot(queries[node.query], state)
        children = dict(node.branches)
        if len(children) != len(node.branches) or response not in children:
            raise ValueError("policy has duplicate or missing response branches")
        path.append((node.query, response))
        node = children[response]
    if node.branches:
        raise ValueError("terminal node cannot contain children")
    return tuple(path)


def partition(prior: FinitePrior, queries, tree: Node) -> dict[tuple, tuple[int, ...]]:
    queries = validate_queries(prior, queries)
    grouped: dict[tuple, list[int]] = {}
    for i, state in enumerate(prior.states):
        grouped.setdefault(transcript(state, tree, queries), []).append(i)
    return {path: tuple(indices) for path, indices in sorted(grouped.items())}


def transcript_profile(prior: FinitePrior, queries, tree: Node) -> dict[str, object]:
    """Exact posterior collision and Bayes count-table reconstruction statistics."""
    leaves = partition(prior, queries, tree)
    masses = tuple(sum(prior.weights[i] for i in group) for group in leaves.values())
    total = prior.total
    observed_pairs = sum(m * m for m in masses)
    joint_pairs = sum(w * w for w in prior.weights)
    return {
        "leaves": len(leaves),
        "observed_collision_probability": Q(observed_pairs, total * total),
        "joint_collision_probability": Q(joint_pairs, total * total),
        "collision_ratio": Q(observed_pairs, joint_pairs),
        "bayes_success": Q(sum(max(prior.weights[i] for i in group)
                               for group in leaves.values()), total),
        "strict": any(len(group) > 1 for group in leaves.values()),
        "maximum_depth": max(len(path) for path in leaves),
    }


def direct_bit_profile(capacities, queries, tree: Node) -> dict[str, object]:
    """Independent oracle: enumerate binary records rather than binomial cell tables."""
    prior = fair_bit_prior(tuple(capacities))
    queries = validate_queries(prior, queries)
    n = sum(prior.capacities)
    grouped: dict[tuple, int] = {}
    joint: dict[tuple, int] = {}
    by_leaf_counts: dict[tuple, dict[tuple, int]] = {}
    for record in product((0, 1), repeat=n):
        cells, cursor = [], 0
        for size in prior.capacities:
            cells.append(sum(record[cursor: cursor + size]))
            cursor += size
        cells = tuple(cells)
        path = transcript(cells, tree, queries)
        grouped[path] = grouped.get(path, 0) + 1
        joint[cells] = joint.get(cells, 0) + 1
        bucket = by_leaf_counts.setdefault(path, {})
        bucket[cells] = bucket.get(cells, 0) + 1
    return {
        "leaves": len(grouped),
        "observed_collision_probability": Q(sum(v * v for v in grouped.values()), 4 ** n),
        "joint_collision_probability": Q(sum(v * v for v in joint.values()), 4 ** n),
        "collision_ratio": Q(sum(v * v for v in grouped.values()),
                             sum(v * v for v in joint.values())),
        "bayes_success": Q(sum(max(bucket.values()) for bucket in by_leaf_counts.values()), 2 ** n),
        "strict": any(len(bucket) > 1 for bucket in by_leaf_counts.values()),
        "maximum_depth": max(len(path) for path in grouped),
    }


def prefix_collision_sequence(prior: FinitePrior, queries, tree: Node) -> tuple[Q, ...]:
    """Exact probability of matching transcripts through each observation depth.

    The reduction at each stage equals twice the cross-products of child
    masses within every parent. Early termination leaves an unchanged mass.
    """
    leaves = partition(prior, queries, tree)
    max_depth = max(map(len, leaves), default=0)
    sequence = []
    for depth in range(max_depth + 1):
        masses: dict[tuple, int] = {}
        for path, indices in leaves.items():
            prefix = path[:depth]
            masses[prefix] = masses.get(prefix, 0) + sum(prior.weights[i] for i in indices)
        sequence.append(Q(sum(v * v for v in masses.values()), prior.total ** 2))
    assert all(sequence[i + 1] <= sequence[i] for i in range(len(sequence) - 1))
    return tuple(sequence)


def reachable_alphabet_bound(prior: FinitePrior, queries, tree: Node) -> dict[str, object]:
    """Compute exact reachable leaf count and product of max conditional alphabet sizes."""
    leaves = partition(prior, queries, tree)
    max_depth = max(map(len, leaves), default=0)
    factors = []
    for depth in range(max_depth):
        extensions: dict[tuple, set[tuple]] = {}
        for path in leaves:
            extensions.setdefault(path[:depth], set()).add(path[:depth + 1])
        factors.append(max(map(len, extensions.values())))
    bound = prod(factors)
    assert len(leaves) <= bound
    return {"reachable_leaves": len(leaves), "alphabet_factors": tuple(factors),
            "product_bound": bound}


def leaf_fibres(prior: FinitePrior, queries, tree: Node) -> dict[tuple, tuple[tuple[int, ...], ...]]:
    """Identify each leaf as a set of feasible count tables for its path equations.

    The identities use the *declared support* of the prior. For a full box
    prior, each leaf is {x: 0 <= x <= capacities, A_path x = answers}.
    """
    queries = validate_queries(prior, queries)
    leaves = partition(prior, queries, tree)
    result = {}
    for path, indices in leaves.items():
        solution = tuple(state for state in prior.states if all(
            dot(queries[query], state) == value for query, value in path))
        assert solution == tuple(prior.states[i] for i in indices)
        result[path] = solution
    return result


def prefix_refinement(prior: FinitePrior, queries, tree: Node) -> bool:
    """Every full transcript class is contained in its depth-t prefix class."""
    leaves = partition(prior, queries, tree)
    for t in range(max(map(len, leaves), default=0) + 1):
        for full_path, indices in leaves.items():
            prefix = full_path[:t]
            for index in indices:
                if transcript(prior.states[index], tree, queries)[:t] != prefix:
                    return False
    return True


def adaptive_optimum(prior: FinitePrior, queries, budget: int):
    """Exact optimal Bayes-success decision tree with <= budget subset queries.

    At a leaf the maximum unnormalized success mass is the largest prior
    weight in that leaf. Dynamic programming uses only feasible posterior
    state subsets, and records one deterministic optimum.
    """
    queries = validate_queries(prior, queries)
    if type(budget) is not int or budget < 0:
        raise ValueError("nonnegative integer budget required")

    @lru_cache(None)
    def split(indices: tuple[int, ...], query: int):
        groups: dict[int, list[int]] = {}
        for i in indices:
            groups.setdefault(dot(queries[query], prior.states[i]), []).append(i)
        return tuple((answer, tuple(part)) for answer, part in sorted(groups.items()))

    @lru_cache(None)
    def solve(indices: tuple[int, ...], steps: int):
        best = max(prior.weights[i] for i in indices)
        winning = Node()
        if steps == 0 or len(indices) == 1:
            return best, winning
        for qi in range(len(queries)):
            groups = split(indices, qi)
            if len(groups) == 1:
                continue
            children = tuple((answer, solve(part, steps - 1)) for answer, part in groups)
            score = sum(result[0] for _, result in children)
            if score > best:
                best = score
                winning = Node(qi, tuple((answer, result[1]) for answer, result in children))
        return best, winning

    mass, tree = solve(tuple(range(len(prior.states))), budget)
    assert transcript_profile(prior, queries, tree)["bayes_success"] == Q(mass, prior.total)
    return {"bayes_success": Q(mass, prior.total), "mass": mass,
            "tree": tree, "states_visited": solve.cache_info().currsize}


def fixed_optimum(prior: FinitePrior, queries, budget: int):
    """Enumerate fixed schedules, including repeated queries, with an exact Bayes objective."""
    queries = validate_queries(prior, queries)
    if type(budget) is not int or budget < 0:
        raise ValueError("nonnegative integer budget required")
    best, schedule, evaluated = 0, (), 0
    for selected in combinations_with_replacement(range(len(queries)), budget):
        classes: dict[tuple[int, ...], int] = {}
        for i, state in enumerate(prior.states):
            responses = tuple(dot(queries[q], state) for q in selected)
            classes[responses] = max(classes.get(responses, 0), prior.weights[i])
        score = sum(classes.values())
        evaluated += 1
        if score > best:
            best, schedule = score, selected
    return {"bayes_success": Q(best, prior.total), "mass": best,
            "schedule": schedule, "schedules_checked": evaluated}


def fixed_tree(prior: FinitePrior, queries, schedule) -> Node:
    """Compile a fixed query sequence to a reachable, explicit decision tree."""
    queries = validate_queries(prior, queries)
    schedule = tuple(schedule)
    if any(type(q) is not int or not 0 <= q < len(queries) for q in schedule):
        raise ValueError("schedule contains an invalid query index")

    def build(states, depth):
        if depth == len(schedule):
            return Node()
        qi = schedule[depth]
        groups: dict[int, list[tuple[int, ...]]] = {}
        for x in states:
            groups.setdefault(dot(queries[qi], x), []).append(x)
        return Node(qi, tuple((answer, build(group, depth + 1))
                              for answer, group in sorted(groups.items())))

    return build(prior.states, 0)


def one_hot_interval_law(n: int, budget: int):
    """Exact optimal number of identified one-hot locations (algebraic theorem)."""
    if type(n) is not int or n < 1 or type(budget) is not int or budget < 0:
        raise ValueError("n>=1 and budget>=0 must be integers")
    return {"adaptive": min(n, 2 ** budget),
            "fixed": min(n, 2 * budget) if budget else 1}


def tree_as_data(node: Node):
    if node.query is None:
        return None
    return {"query": node.query, "branches": {str(a): tree_as_data(child)
                                               for a, child in node.branches}}
