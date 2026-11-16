"""SRB-01: exact finite-world systemic-loss and feedback-selection scorer.

Each world is one stipulated coupled-system scenario, with complete counterfactual
node-loss vectors for each named intervention. Masses encode a declared finite
law, not independent empirical replications. Observations define information
fibres; query responses model optional *pre-selection* feedback disclosure.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
import json
from itertools import groupby

from .evaluation_selection_risk import (
    NullModel, adaptive_optimum, fixed_optimum, full_information_risk,
    no_feedback_risk,
)

SCHEMA = "SRB-EvalMath-01"


def rational(value: str | int) -> Fraction:
    """Reject floating point numbers and booleans to preserve exact provenance."""
    if type(value) not in (str, int):
        raise ValueError("exact integer or rational string required")
    try:
        result = Fraction(value)
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        raise ValueError("invalid exact rational") from exc
    if result < 0:
        raise ValueError("nonnegative rational required")
    return result


@dataclass(frozen=True)
class World:
    name: str
    weight: int
    visible: tuple[int, ...]
    queries: tuple[int, ...]
    node_losses: tuple[tuple[Fraction, ...], ...]  # action x node
    claims_safe: tuple[bool, ...]
    selected: int | None


@dataclass(frozen=True)
class Bank:
    nodes: tuple[str, ...]
    actions: tuple[str, ...]
    costs: tuple[Fraction, ...]
    baseline: int
    query_names: tuple[str, ...]
    harm_threshold: Fraction
    tail_alpha: Fraction
    worlds: tuple[World, ...]


def _names(values) -> tuple[str, ...]:
    if (not isinstance(values, list) or not values or
            any(not isinstance(x, str) or not x for x in values) or
            len(set(values)) != len(values)):
        raise ValueError("unique nonempty names required")
    return tuple(values)


def _ints(values, *, length: int | None = None) -> tuple[int, ...]:
    if (not isinstance(values, list) or (length is not None and len(values) != length)
            or any(type(x) is not int or x < 0 for x in values)):
        raise ValueError("nonnegative categorical integer vector required")
    return tuple(values)


def parse_bank(data: dict) -> Bank:
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        raise ValueError(f"expected schema {SCHEMA}")
    nodes = _names(data.get("nodes"))
    specs = data.get("actions")
    if not isinstance(specs, list) or not specs or any(not isinstance(x, dict) for x in specs):
        raise ValueError("nonempty action specifications required")
    actions = _names([x.get("name") for x in specs])
    costs = tuple(rational(x.get("cost")) for x in specs)
    baseline = data.get("baseline")
    if baseline not in actions:
        raise ValueError("baseline must name an action")
    raw_queries = data.get("query_names", [])
    query_names = _names(raw_queries) if raw_queries else ()
    if not isinstance(raw_queries, list):
        raise ValueError("query_names must be a list")
    harm_threshold = rational(data.get("harm_threshold"))
    tail_alpha = rational(data.get("tail_alpha"))
    if tail_alpha >= 1:
        raise ValueError("tail_alpha must be in [0,1)")
    rows = data.get("worlds")
    if not isinstance(rows, list) or not rows:
        raise ValueError("nonempty world bank required")
    worlds = []
    ids = set()
    visibility_length = None
    for x in rows:
        if not isinstance(x, dict) or not isinstance(x.get("id"), str) or not x["id"] or x["id"] in ids:
            raise ValueError("unique world id required")
        ids.add(x["id"])
        weight = x.get("mass")
        if type(weight) is not int or weight <= 0:
            raise ValueError("positive integer scenario mass required")
        visible = _ints(x.get("visible"))
        if visibility_length is None:
            visibility_length = len(visible)
        if len(visible) != visibility_length:
            raise ValueError("visible signature dimensions must match")
        queries = _ints(x.get("queries", []), length=len(query_names))
        outcomes = x.get("outcomes")
        if not isinstance(outcomes, dict) or set(outcomes) != set(actions):
            raise ValueError("every action must have a counterfactual outcome")
        loss_vectors, claims = [], []
        for action in actions:
            outcome = outcomes[action]
            if not isinstance(outcome, dict):
                raise ValueError("invalid outcome")
            entries = outcome.get("node_loss")
            if not isinstance(entries, list) or len(entries) != len(nodes):
                raise ValueError("node_loss vector must cover all nodes")
            loss_vectors.append(tuple(rational(v) for v in entries))
            claim = outcome.get("claimed_safe")
            if type(claim) is not bool:
                raise ValueError("claimed_safe requires a Boolean grader report")
            claims.append(claim)
        selected = x.get("selected")
        if selected is not None and selected not in actions:
            raise ValueError("selected action must be registered")
        worlds.append(World(x["id"], weight, visible, queries,
                            tuple(loss_vectors), tuple(claims),
                            actions.index(selected) if selected is not None else None))
    if any(w.selected is None for w in worlds) and any(w.selected is not None for w in worlds):
        raise ValueError("selected policy must be recorded for every world or none")
    return Bank(nodes, actions, costs, actions.index(baseline), query_names,
                harm_threshold, tail_alpha, tuple(worlds))


def load_bank(path: str | Path) -> Bank:
    return parse_bank(json.loads(Path(path).read_text(encoding="utf-8")))


def harm(world: World, action: int) -> Fraction:
    return sum(world.node_losses[action], Fraction(0))


def total_loss(bank: Bank, world: World, action: int) -> Fraction:
    return harm(world, action) + bank.costs[action]


def expected_loss(bank: Bank, choices: tuple[int, ...]) -> Fraction:
    if len(choices) != len(bank.worlds) or any(type(a) is not int or not 0 <= a < len(bank.actions) for a in choices):
        raise ValueError("one registered action per world required")
    total = sum(w.weight for w in bank.worlds)
    return sum((w.weight * total_loss(bank, w, a)
                for w, a in zip(bank.worlds, choices)), Fraction(0)) / total


def optimal_observable(bank: Bank, extra_query: int | None = None) -> tuple[int, ...]:
    """Minimum exact expected loss of policies constant on each visible fibre."""
    if extra_query is not None and (type(extra_query) is not int or not 0 <= extra_query < len(bank.query_names)):
        raise ValueError("unknown disclosure query")
    fibres: dict[tuple[int, ...], list[int]] = {}
    for i, w in enumerate(bank.worlds):
        key = w.visible + ((w.queries[extra_query],) if extra_query is not None else ())
        fibres.setdefault(key, []).append(i)
    choices = [0] * len(bank.worlds)
    for ids in fibres.values():
        best = min(range(len(bank.actions)),
                   key=lambda a: sum((bank.worlds[i].weight * total_loss(bank, bank.worlds[i], a)
                                      for i in ids), Fraction(0)))
        for i in ids:
            choices[i] = best
    return tuple(choices)


def weighted_cvar(values: tuple[tuple[Fraction, int], ...], alpha: Fraction) -> Fraction:
    """Upper-tail CVaR for a discrete weighted loss law with exact mass slicing."""
    if (not values or not 0 <= alpha < 1 or
            any(type(w) is not int or w < 1 or not isinstance(v, Fraction) or v < 0
                for v, w in values)):
        raise ValueError("nonempty nonnegative exact losses, positive masses, alpha in [0,1)")
    total = sum(w for _, w in values)
    remaining = (1 - alpha) * total
    tail_sum = Fraction(0)
    for loss, weight in sorted(values, reverse=True):
        taken = min(remaining, weight)
        tail_sum += taken * loss
        remaining -= taken
        if remaining == 0:
            break
    return tail_sum / ((1 - alpha) * total)


def _tail(bank: Bank, choices: tuple[int, ...]) -> Fraction:
    return weighted_cvar(tuple((harm(w, a), w.weight)
                               for w, a in zip(bank.worlds, choices)), bank.tail_alpha)


def binary_collision_floor(bank: Bank) -> Fraction:
    """For exactly two actions, the visible-oracle gap as opposing advantage masses."""
    if len(bank.actions) != 2:
        raise ValueError("binary certificate requires exactly two actions")
    fibres: dict[tuple[int, ...], list[World]] = {}
    for w in bank.worlds:
        fibres.setdefault(w.visible, []).append(w)
    gap = Fraction(0)
    for worlds in fibres.values():
        positive = sum((w.weight * max(total_loss(bank, w, 0) - total_loss(bank, w, 1), 0)
                        for w in worlds), Fraction(0))
        negative = sum((w.weight * max(total_loss(bank, w, 1) - total_loss(bank, w, 0), 0)
                        for w in worlds), Fraction(0))
        gap += min(positive, negative)
    return gap / sum(w.weight for w in bank.worlds)


def _selection(bank: Bank) -> dict:
    model = NullModel(
        weights=tuple(w.weight for w in bank.worlds),
        events=tuple(tuple(w.claims_safe[a] and harm(w, a) >= bank.harm_threshold
                           for w in bank.worlds) for a in range(len(bank.actions))),
        queries=tuple(tuple(w.queries[q] for w in bank.worlds)
                      for q in range(len(bank.query_names))) or (tuple(0 for _ in bank.worlds),),
    )
    return {
        "no_disclosure": no_feedback_risk(model),
        "one_query_optimum": fixed_optimum(model, 1)["risk"],
        "two_adaptive_queries": adaptive_optimum(model, 2)["risk"],
        "full_disclosure": full_information_risk(model),
    }


def score(bank: Bank) -> dict:
    n = len(bank.worlds)
    actions = range(len(bank.actions))
    no_info_action = min(actions,
                         key=lambda a: expected_loss(bank, (a,) * n))
    no_info = (no_info_action,) * n
    visible = optimal_observable(bank)
    oracle = tuple(min(actions, key=lambda a: total_loss(bank, w, a))
                   for w in bank.worlds)
    result = {
        "scenario_count": n,
        "total_mass": sum(w.weight for w in bank.worlds),
        "fixed_action": bank.actions[no_info_action],
        "fixed_loss": expected_loss(bank, no_info),
        "observable_loss": expected_loss(bank, visible),
        "oracle_loss": expected_loss(bank, oracle),
        "visibility_value": expected_loss(bank, no_info) - expected_loss(bank, visible),
        "unobservable_regret": expected_loss(bank, visible) - expected_loss(bank, oracle),
        "baseline_loss": expected_loss(bank, (bank.baseline,) * n),
        "baseline_harm_cvar": _tail(bank, (bank.baseline,) * n),
        "observable_harm_cvar": _tail(bank, visible),
        "query_disclosure_loss": {q: expected_loss(bank, optimal_observable(bank, i))
                                  for i, q in enumerate(bank.query_names)},
        "false_authorization_selection": _selection(bank),
        "binary_collision_certificate": binary_collision_floor(bank) if len(bank.actions) == 2 else None,
    }
    if bank.worlds[0].selected is not None:
        chosen = tuple(w.selected for w in bank.worlds)
        result["trace_replay_loss"] = expected_loss(bank, chosen)
        result["trace_replay_harm_cvar"] = _tail(bank, chosen)
        result["trace_replay_false_authorization"] = Fraction(
            sum(w.weight for w, a in zip(bank.worlds, chosen)
                if w.claims_safe[a] and harm(w, a) >= bank.harm_threshold),
            result["total_mass"],
        )
    return result


def json_exact(value):
    """Stable exact serialization, no rounded floats or implicit conversions."""
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {k: json_exact(v) for k, v in value.items()}
    if isinstance(value, tuple):
        return [json_exact(v) for v in value]
    return value
