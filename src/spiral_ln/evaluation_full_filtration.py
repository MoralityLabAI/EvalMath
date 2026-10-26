"""Exact finite stochastic feedback with private signals before or after each query.

A fixed latent world is drawn once under the null. Conditional on that world,
private signals on different rounds and query outputs on different rounds are
independent, with predeclared finite rational kernels. No Bayesian superiority,
physical acquisition guarantee, or deployed e-process validity is asserted.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from functools import lru_cache
from itertools import product


def _distribution(row):
    if not isinstance(row, (tuple, list)) or not row:
        raise ValueError("a probability row must be nonempty")
    if any(type(x) not in (int, Q) for x in row):
        raise ValueError("probabilities must be rational, never floats or booleans")
    result = tuple(Q(x) for x in row)
    if any(x < 0 for x in result) or sum(result) != 1:
        raise ValueError("probabilities must be nonnegative and sum to one")
    return result


@dataclass(frozen=True)
class StochasticNull:
    weights: tuple[int, ...]
    events: tuple[tuple[bool, ...], ...]
    queries: tuple[tuple[tuple[Q, ...], ...], ...]
    private: tuple[tuple[Q, ...], ...] = ()

    def __post_init__(self):
        n = len(self.weights)
        if (not n or any(type(w) is not int or w <= 0 for w in self.weights)
                or not self.events or any(len(e) != n or any(type(v) is not bool for v in e)
                                          for e in self.events)
                or not self.queries or any(len(q) != n for q in self.queries)):
            raise ValueError("positive world masses, Boolean events and nonempty query bank required")
        qbank = []
        for q in self.queries:
            rows = tuple(_distribution(row) for row in q)
            if any(len(row) != len(rows[0]) for row in rows):
                raise ValueError("each query must have a fixed answer alphabet")
            qbank.append(rows)
        if self.private:
            if len(self.private) != n:
                raise ValueError("private channel must have one row per world")
            priv = tuple(_distribution(row) for row in self.private)
            if any(len(row) != len(priv[0]) for row in priv):
                raise ValueError("private channel must have one output alphabet")
        else:
            priv = tuple((Q(1),) for _ in range(n))
        object.__setattr__(self, "queries", tuple(qbank))
        object.__setattr__(self, "private", priv)

    @property
    def total(self):
        return sum(self.weights)

    @property
    def private_symbols(self):
        return len(self.private[0])


def _event_mass(model, mass):
    values = tuple(sum(m for m, flag in zip(mass, event) if flag)
                   for event in model.events)
    best = max(values)
    return best, values.index(best)


def _update(mass, kernel, symbol):
    return tuple(m * row[symbol] for m, row in zip(mass, kernel))


def optimal(model: StochasticNull, budget: int, timing: str):
    """Bayes-optimal false-selection risk for the complete actor information.

    timing='before': private H then chosen public Q then Y, on every round.
    timing='after': chosen Q then Y then private H, on every round.
    A query outcome or private signal may affect the next query and final test.
    A stopped policy receives no further private signals. Zero-mass outcomes
    are omitted from the certificate. Rounds are independent conditional W.
    """
    if type(budget) is not int or budget < 0 or timing not in ("before", "after"):
        raise ValueError("budget must be a nonnegative integer; timing before/after")

    @lru_cache(None)
    def solve(mass: tuple[Q, ...], left: int):
        terminal_mass, terminal_test = _event_mass(model, mass)
        terminal = ("test", terminal_test)
        if left == 0 or not any(mass):
            return terminal_mass, terminal
        if timing == "before":
            total = Q(0)
            branches = []
            for h in range(model.private_symbols):
                current = _update(mass, model.private, h)
                if not any(current):
                    continue
                value, action = _event_mass(model, current)[0], ("test", _event_mass(model, current)[1])
                for qid, kernel in enumerate(model.queries):
                    score = Q(0)
                    replies = []
                    for y in range(len(kernel[0])):
                        updated = _update(current, kernel, y)
                        if any(updated):
                            child_value, child = solve(updated, left - 1)
                            score += child_value
                            replies.append((y, child))
                    if score > value:
                        value, action = score, ("query", qid, tuple(replies))
                total += value
                branches.append((h, action))
            return total, ("private", tuple(branches))
        best, action = terminal_mass, terminal
        for qid, kernel in enumerate(model.queries):
            value = Q(0)
            replies = []
            for y in range(len(kernel[0])):
                after_query = _update(mass, kernel, y)
                if not any(after_query):
                    continue
                after_private = []
                for h in range(model.private_symbols):
                    updated = _update(after_query, model.private, h)
                    if any(updated):
                        score, child = solve(updated, left - 1)
                        value += score
                        after_private.append((h, child))
                replies.append((y, ("private", tuple(after_private))))
            if value > best:
                best, action = value, ("query", qid, tuple(replies))
        return best, action

    raw, tree = solve(tuple(Q(w) for w in model.weights), budget)
    return {"risk": raw / model.total, "weighted_risk": raw,
            "policy": tree, "posterior_states": solve.cache_info().currsize}


def policy_risk_direct(model: StochasticNull, policy) -> Q:
    """Separate policy evaluator: sum probability of each world/outcome path.

    This checks policy certificates via path enumeration instead of the DP's
    posterior-caching recurrence.
    """
    def walk(world, node, probability):
        typ = node[0]
        if typ == "test":
            return probability if model.events[node[1]][world] else Q(0)
        if typ == "private":
            return sum((walk(world, subtree, probability * model.private[world][h])
                        for h, subtree in node[1]), Q(0))
        if typ == "query":
            kernel = model.queries[node[1]][world]
            return sum((walk(world, subtree, probability * kernel[y])
                        for y, subtree in node[2]), Q(0))
        raise ValueError("malformed policy node")

    return sum((Q(w) * walk(i, policy, Q(1))
                for i, w in enumerate(model.weights)), Q(0)) / model.total


def fixed_schedule_risk(model: StochasticNull, schedule) -> Q:
    """Terminal Bayes value for predetermined queries with all H,Y revealed.

    Signal timing becomes irrelevant once query choices are fixed, because all
    kernel draws are conditionally independent given the world. Allows repeats.
    """
    schedule = tuple(schedule)
    if any(type(q) is not int or q < 0 or q >= len(model.queries) for q in schedule):
        raise ValueError("invalid query schedule")
    histories = [tuple(Q(w) for w in model.weights)]
    for q in schedule:
        next_histories = []
        for current in histories:
            for h in range(model.private_symbols):
                for y in range(len(model.queries[q][0])):
                    updated = tuple(current[i] * model.private[i][h] * model.queries[q][i][y]
                                    for i in range(len(current)))
                    if any(updated):
                        next_histories.append(updated)
        histories = next_histories
    return sum((_event_mass(model, mass)[0] for mass in histories), Q(0)) / model.total


def fixed_optimum(model: StochasticNull, budget: int) -> dict:
    if type(budget) is not int or budget < 0:
        raise ValueError("budget must be nonnegative")
    best, schedule, count = fixed_schedule_risk(model, ()), (), 1
    for length in range(1, budget + 1):
        for chosen in product(range(len(model.queries)), repeat=length):
            current = fixed_schedule_risk(model, chosen)
            count += 1
            if current > best:
                best, schedule = current, chosen
    return {"risk": best, "schedule": schedule, "schedules_checked": count}


def independent_one_round_oracle(model: StochasticNull, timing: str) -> Q:
    """Enumerate query allocations to hidden symbols and every possible answer.

    Uses raw world and outcome sums, then independently chooses the best event
    at the leaf. Small finite models only. No call to optimal or fixed_optimum.
    """
    if timing not in ("before", "after"):
        raise ValueError("invalid timing")
    def payoff(q, hidden):
        score = Q(0)
        for y in range(len(model.queries[q][0])):
            choices = [sum((Q(w) * model.private[i][hidden] *
                            model.queries[q][i][y] for i, w in enumerate(model.weights)
                            if event[i]), Q(0)) for event in model.events]
            score += max(choices)
        return score

    base = max(sum((Q(w) for i, w in enumerate(model.weights) if event[i]), Q(0))
               for event in model.events)
    if timing == "before":
        best = base
        for plan in product(range(-1, len(model.queries)), repeat=model.private_symbols):
            value = Q(0)
            for h, q in enumerate(plan):
                if q < 0:
                    value += max(sum((Q(w) * model.private[i][h]
                                      for i, w in enumerate(model.weights) if event[i]), Q(0))
                                 for event in model.events)
                else:
                    value += payoff(q, h)
            best = max(best, value)
        return best / model.total
    best = base
    for q in range(len(model.queries)):
        value = sum(payoff(q, h) for h in range(model.private_symbols))
        best = max(best, value)
    return best / model.total


def compress_equivalent_worlds(model: StochasticNull):
    """Sum weights of worlds with identical event and all channel likelihoods.

    Exact for every future policy in this fixed i.i.d.-conditional-on-world
    channel family. The grouping is independent of any particular policy.
    """
    index = {}
    weights = []
    events = [[] for _ in model.events]
    queries = [[] for _ in model.queries]
    private = []
    for i, w in enumerate(model.weights):
        key = (tuple(e[i] for e in model.events), model.private[i],
               tuple(q[i] for q in model.queries))
        if key in index:
            weights[index[key]] += w
            continue
        index[key] = len(weights)
        weights.append(w)
        for j, e in enumerate(model.events):
            events[j].append(e[i])
        for j, q in enumerate(model.queries):
            queries[j].append(q[i])
        private.append(model.private[i])
    return StochasticNull(tuple(weights), tuple(tuple(e) for e in events),
                          tuple(tuple(q) for q in queries), tuple(private))


def noisy_selector_fixture(accuracy=Q(3, 4)):
