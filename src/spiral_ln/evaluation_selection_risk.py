"""Exact post-feedback selection risk and finite continuation-sufficient audit states.

The statistical model is deliberately finite: each null world has positive
integer mass, tests are Boolean false-authorization events, and deterministic
queries reveal integer-valued functions of the world. The engine computes
*worst-case post-query selection risk*, not a claim of deployed safety.

The automata routines give exact finite-state continuation equivalence under
explicit declared events. They prove nothing about hidden, unlogged peeking.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import combinations_with_replacement, product


@dataclass(frozen=True)
class NullModel:
    """Worlds are distinguished by index; every mass is a positive integer."""

    weights: tuple[int, ...]
    events: tuple[tuple[bool, ...], ...]
    queries: tuple[tuple[int, ...], ...]

    def __post_init__(self):
        n = len(self.weights)
        if (n < 1 or any(type(w) is not int or w < 1 for w in self.weights)
                or not self.events or any(len(ev) != n or any(type(x) is not bool for x in ev)
                                          for ev in self.events)
                or not self.queries or any(len(q) != n or any(type(x) is not int for x in q)
                                           for q in self.queries)):
            raise ValueError("positive world masses, Boolean event rows and integer query rows required")

    @property
    def total(self) -> int:
        return sum(self.weights)

    def marginals(self) -> tuple[Fraction, ...]:
        return tuple(Fraction(sum(w for w, hit in zip(self.weights, ev) if hit), self.total)
                     for ev in self.events)


def selection_mass(model: NullModel, worlds: tuple[int, ...]) -> int:
    """Unnormalised optimum if an actor must choose one event right now."""
    if not worlds:
        return 0
    return max(sum(model.weights[i] for i in worlds if ev[i]) for ev in model.events)


def no_feedback_risk(model: NullModel) -> Fraction:
    return Fraction(selection_mass(model, tuple(range(len(model.weights)))), model.total)


def full_information_risk(model: NullModel) -> Fraction:
    return Fraction(sum(w for i, w in enumerate(model.weights)
                        if any(ev[i] for ev in model.events)), model.total)


def _check_query(model: NullModel, index: int) -> None:
    if type(index) is not int or not 0 <= index < len(model.queries):
        raise ValueError("invalid query index")


def _split(model: NullModel, worlds: tuple[int, ...], query: int):
    _check_query(model, query)
    groups: dict[int, list[int]] = {}
    for i in worlds:
        groups.setdefault(model.queries[query][i], []).append(i)
    return tuple((answer, tuple(indices)) for answer, indices in sorted(groups.items()))


def one_step_profile(model: NullModel, query: int) -> tuple[tuple[int, tuple[int, ...]], ...]:
    """Joint masses of (query response, each individual false-positive event)."""
    return tuple((a, tuple(sum(model.weights[i] for i in worlds if ev[i])
                           for ev in model.events))
                 for a, worlds in _split(model, tuple(range(len(model.weights))), query))


@dataclass(frozen=True)
class QueryNode:
    query: int | None = None
    branches: tuple[tuple[int, 'QueryNode'], ...] = ()


def transcript(model: NullModel, node: QueryNode, world: int) -> tuple[tuple[int, int], ...]:
    if type(world) is not int or not 0 <= world < len(model.weights):
        raise ValueError("invalid world")
    path = []
    while node.query is not None:
        _check_query(model, node.query)
        answer = model.queries[node.query][world]
        children = dict(node.branches)
        if len(children) != len(node.branches) or answer not in children:
            raise ValueError("query node lacks unique reachable response branch")
        path.append((node.query, answer))
        node = children[answer]
    if node.branches:
        raise ValueError("terminal nodes must be empty")
    return tuple(path)


def policy_fibres(model: NullModel, node: QueryNode) -> dict[tuple, tuple[int, ...]]:
    groups: dict[tuple, list[int]] = {}
    for world in range(len(model.weights)):
        groups.setdefault(transcript(model, node, world), []).append(world)
    return {key: tuple(values) for key, values in sorted(groups.items())}


def risk_for_fibres(model: NullModel, fibres) -> Fraction:
    sets = tuple(tuple(group) for group in fibres)
    if sorted(i for group in sets for i in group) != list(range(len(model.weights))):
        raise ValueError("fibres must partition all null worlds once")
    return Fraction(sum(selection_mass(model, group) for group in sets), model.total)


def policy_risk(model: NullModel, node: QueryNode) -> Fraction:
    return risk_for_fibres(model, policy_fibres(model, node).values())


def fixed_fibres(model: NullModel, schedule) -> tuple[tuple[int, ...], ...]:
    schedule = tuple(schedule)
    for q in schedule:
        _check_query(model, q)
    groups: dict[tuple[int, ...], list[int]] = {}
    for i in range(len(model.weights)):
        key = tuple(model.queries[q][i] for q in schedule)
        groups.setdefault(key, []).append(i)
    return tuple(tuple(v) for _, v in sorted(groups.items()))


def fixed_optimum(model: NullModel, budget: int):
    """Exhaustively search fixed query schedules of at most budget queries."""
    if type(budget) is not int or budget < 0:
        raise ValueError("budget must be a nonnegative integer")
    best = no_feedback_risk(model)
    choice = ()
    checked = 1
    for size in range(1, budget + 1):
        for schedule in combinations_with_replacement(range(len(model.queries)), size):
            risk = risk_for_fibres(model, fixed_fibres(model, schedule))
            checked += 1
            if risk > best:
                best, choice = risk, schedule
    return {"risk": best, "schedule": choice, "schedules_checked": checked}


def adaptive_optimum(model: NullModel, budget: int):
    """Exactly maximize post-feedback event selection risk over query trees."""
    if type(budget) is not int or budget < 0:
        raise ValueError("budget must be a nonnegative integer")

    @lru_cache(None)
    def solve(worlds: tuple[int, ...], depth: int):
        best = selection_mass(model, worlds)
        tree = QueryNode()
        if depth:
            for q in range(len(model.queries)):
                groups = _split(model, worlds, q)
                if len(groups) == 1:
                    continue
                subtrees = [(answer, solve(part, depth - 1)) for answer, part in groups]
                risk = sum(result[0] for _, result in subtrees)
                if risk > best:
                    best = risk
                    tree = QueryNode(q, tuple((answer, result[1]) for answer, result in subtrees))
        return best, tree

    mass, tree = solve(tuple(range(len(model.weights))), budget)
    assert policy_risk(model, tree) == Fraction(mass, model.total)
    return {"risk": Fraction(mass, model.total), "mass": mass,
            "tree": tree, "subproblems": solve.cache_info().currsize}


def exhaustive_two_round_optimum(model: NullModel):
    """Independent small-case oracle, by enumerating whole first/second query plans.

    For each first query, enumerate every mapping from its possible responses
    to {stop, query_0, ..., query_m}. Each final leaf selects the test with
    the highest event mass. No dynamic-programming cache is used.
    """
    best = no_feedback_risk(model)
    for first in range(len(model.queries)):
        parents = _split(model, tuple(range(len(model.weights))), first)
        options = range(-1, len(model.queries))
        for plan in product(options, repeat=len(parents)):
            mass = 0
            for (_, group), second in zip(parents, plan):
                if second == -1:
                    mass += selection_mass(model, group)
                else:
                    mass += sum(selection_mass(model, child)
                                for _, child in _split(model, group, second))
            best = max(best, Fraction(mass, model.total))
    return best



def contingency_histogram(model: NullModel) -> tuple[tuple[tuple[int, ...], tuple[bool, ...], int], ...]:
    """Exact joint masses of every possible query answer and event outcome.

    This joint histogram is continuation-sufficient for arbitrary finite
    deterministic query policies from the fixed bank, with a fixed family
    of false-positive events. In particular, marginal event probabilities
    alone do *not* have this property.
    """
    groups: dict[tuple, int] = {}
    for i, weight in enumerate(model.weights):
        query_answers = tuple(query[i] for query in model.queries)
        event_hits = tuple(event[i] for event in model.events)
        key = (query_answers, event_hits)
        groups[key] = groups.get(key, 0) + weight
    return tuple((q, e, groups[q, e]) for q, e in sorted(groups))


def compress_contingency(model: NullModel) -> NullModel:
    """Quotient a finite null into continuation-equivalent response/event types."""
    histogram = contingency_histogram(model)
    return NullModel(
        tuple(mass for _, _, mass in histogram),
        tuple(tuple(hit[j] for _, hit, _ in histogram) for j in range(len(model.events))),
        tuple(tuple(responses[j] for responses, _, _ in histogram)
              for j in range(len(model.queries))),
    )


def dependent_five_percent_models() -> tuple[NullModel, NullModel]:
    """Same two nominal 5% event rates, different post-query selection risks.

    The query returns whether event A occurred. The common-shock model has
    (A,B)=(0,0) with weight 19 and (1,1) with weight 1. The disjoint model
    has (0,0) with weight 18, (1,0) with 1, and (0,1) with 1.
    """
    shared = NullModel((19, 1), ((False, True), (False, True)), ((0, 1),))
    disjoint = NullModel((18, 1, 1),
                         ((False, True, False), (False, False, True)),
                         ((0, 1, 0),))
    return shared, disjoint


def hidden_prepeek_risk(candidate_count: int, per_test_alpha: Fraction) -> Fraction:
    """Independent calibrated events, full advance peeking, choose one success.

    This is a *complete exposure* toy. Merely signing the chosen test after
    observing all candidates cannot reduce this actual selection risk.
    """
    if (type(candidate_count) is not int or candidate_count < 1
            or not isinstance(per_test_alpha, Fraction)
            or not 0 <= per_test_alpha <= 1):
        raise ValueError("positive candidate count and rational error probability required")
    return 1 - (1 - per_test_alpha) ** candidate_count


@dataclass(frozen=True)
class AuditMachine:
    """Complete deterministic Moore machine for a declared procedural contract."""
    events: tuple[str, ...]
    outputs: tuple[tuple[str, ...], ...]
    transitions: tuple[tuple[int, ...], ...]

    def __post_init__(self):
        n = len(self.outputs)
        if (n < 1 or len(self.events) < 1 or len(set(self.events)) != len(self.events)
                or len(self.transitions) != n
                or any(len(row) != len(self.events) for row in self.transitions)
                or any(type(v) is not int or not 0 <= v < n
                       for row in self.transitions for v in row)
                or any(not isinstance(out, tuple) or any(type(v) is not str for v in out)
                       for out in self.outputs)):
            raise ValueError("complete finite audit automaton required")


def partition_refinement(machine: AuditMachine) -> tuple[tuple[int, ...], ...]:
    """Exact continuation-equivalence classes for *all* finite future events.

    Start with equal current outputs. Split classes whenever transitions go
    into different prior classes. On a finite machine this terminates in the
    coarsest right-invariant equivalence respecting the output.
    """
    n = len(machine.outputs)
    labels = [0] * n
    while True:
        signatures = tuple((machine.outputs[s],
                            tuple(labels[next_s] for next_s in machine.transitions[s]))
                           for s in range(n))
        table: dict[tuple, int] = {}
        nxt = []
        for signature in signatures:
            if signature not in table:
                table[signature] = len(table)
            nxt.append(table[signature])
        if nxt == labels:
            break
        labels = nxt
    return tuple(tuple(s for s in range(n) if labels[s] == c)
                 for c in range(len(set(labels))))


def distinguish(machine: AuditMachine, left: int, right: int):
    """Shortest distinguishing continuation, or None if equivalent.

    A suffix is a tuple of event names; an empty suffix distinguishes states
    whose current outputs already differ. Breadth-first search is independent
    of the refinement implementation.
    """
    n = len(machine.outputs)
    if any(type(s) is not int or not 0 <= s < n for s in (left, right)):
        raise ValueError("unknown audit state")
    if machine.outputs[left] != machine.outputs[right]:
        return ()
    queue = deque([(left, right, ())])
    seen = {(left, right)}
    while queue:
        a, b, prefix = queue.popleft()
        for i, event in enumerate(machine.events):
            a1, b1 = machine.transitions[a][i], machine.transitions[b][i]
            suffix = prefix + (event,)
            if machine.outputs[a1] != machine.outputs[b1]:
                return suffix
            if (a1, b1) not in seen:
                seen.add((a1, b1))
                queue.append((a1, b1, suffix))
    return None


def run_events(machine: AuditMachine, start: int, events) -> tuple[int, tuple[str, ...]]:
    if type(start) is not int or not 0 <= start < len(machine.outputs):
        raise ValueError("unknown starting state")
    state = start
    for event in events:
        if event not in machine.events:
            raise ValueError("unknown event")
        state = machine.transitions[state][machine.events.index(event)]
    return state, machine.outputs[state]


def root_and_amendment_machine(roots: int) -> AuditMachine:
    """Finite audit contract: active roots and whether a rule was amended after viewing.

    States: (root bitmap, phase), phase in {pre-view, viewed, post-view-amended}.
    The output contains GO iff some root remains; procedural status is
    'eligible' for phases 0/1 and 'exploratory' for phase 2.
    Events GRANT_i and REVOKE_i set/clear roots idempotently. VIEW updates
    phase 0 to 1; AMEND updates phase 1 to 2. A pre-view amendment retains
    eligibility. Chronology is an explicit *recording assumption*.
    """
    if type(roots) is not int or not 1 <= roots <= 12:
        raise ValueError("roots must be an integer from 1 to 12")
    events = tuple(f"GRANT_{i}" for i in range(roots)) + \
             tuple(f"REVOKE_{i}" for i in range(roots)) + ("VIEW", "AMEND")
    outputs, transitions = [], []
    for mask in range(1 << roots):
        for phase in range(3):
            outputs.append(("GO" if mask else "STOP",
                            "exploratory" if phase == 2 else "eligible"))
            row = []
            for i in range(roots):
                row.append(3 * (mask | (1 << i)) + phase)
            for i in range(roots):
                row.append(3 * (mask & ~(1 << i)) + phase)
            row.append(3 * mask + (1 if phase == 0 else phase))
            row.append(3 * mask + (2 if phase == 1 else phase))
            transitions.append(tuple(row))
    return AuditMachine(events, tuple(outputs), tuple(transitions))


def state_bits(class_count: int) -> int:
    if type(class_count) is not int or class_count < 1:
        raise ValueError("class_count must be positive")
    return (class_count - 1).bit_length()
