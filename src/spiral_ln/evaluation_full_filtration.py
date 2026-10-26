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
