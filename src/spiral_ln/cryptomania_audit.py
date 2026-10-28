"""Auditable, three-valued logical model of Impagliazzo's five worlds.

A recorded research announcement never becomes a theorem input on its own.
An implication A => B permits A=true -> B=true and B=false -> A=false.
Conditional cryptographic routes are evidence paths, not logical implications
from an assumption to the existence or security of a particular primitive.
All arithmetic in the illustrative Bayesian update is exact.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Any, Mapping

WORLD_AXES = ("P_NE_NP", "AVG_HARD", "OWF", "PKE")
WORLD_ORDER = ("Algorithmica", "Heuristica", "Pessiland", "Minicrypt", "Cryptomania")


def validate_manifest(data: dict[str, Any]) -> None:
    """Reject dangling propositions, ill-typed hypotheses and inconsistent worlds."""
    if data.get("schema_version") != "1.0":
        raise ValueError("unsupported manifest schema")
    props = data.get("propositions")
    if not isinstance(props, dict) or not props:
        raise ValueError("nonempty propositions mapping required")
    if not all(isinstance(k, str) and k and isinstance(v, str) and v for k, v in props.items()):
        raise ValueError("invalid proposition")
    if not set(WORLD_AXES).issubset(props):
        raise ValueError("missing five-world axis")
    edges = data.get("implications")
    if not isinstance(edges, list):
        raise ValueError("implications must be a list")
    for edge in edges:
        if not isinstance(edge, list) or len(edge) != 2 or not all(x in props for x in edge):
            raise ValueError(f"invalid implication {edge!r}")
    if len({tuple(e) for e in edges}) != len(edges):
        raise ValueError("duplicate implications")
    worlds = data.get("worlds")
    if not isinstance(worlds, dict) or set(worlds) != set(WORLD_ORDER):
        raise ValueError("exactly five named worlds required")
    for name, flags in worlds.items():
        if not isinstance(flags, dict) or set(flags) != set(WORLD_AXES):
            raise ValueError(f"invalid world projection: {name}")
        if not all(type(v) is bool for v in flags.values()):
            raise ValueError(f"nonboolean world projection: {name}")
        for antecedent, consequent in edges:
            if antecedent in flags and consequent in flags:
                if flags[antecedent] and not flags[consequent]:
                    raise ValueError(f"world violates implication: {name}")
    if len({tuple(w[a] for a in WORLD_AXES) for w in worlds.values()}) != 5:
        raise ValueError("world projections must be distinct")
    scenarios = data.get("scenarios")
    if not isinstance(scenarios, dict) or not scenarios:
        raise ValueError("scenarios mapping required")
    for name, assignments in scenarios.items():
        if not isinstance(assignments, dict):
            raise ValueError(f"invalid scenario {name}")
        for proposition, value in assignments.items():
            if proposition not in props or type(value) is not bool:
                raise ValueError(f"invalid scenario literal {name}/{proposition}")
    routes = data.get("routes")
    if not isinstance(routes, list):
        raise ValueError("routes must be a list")
    ids = set()
    for item in routes:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or item["id"] in ids:
            raise ValueError("missing or duplicate route id")
        ids.add(item["id"])
        if not isinstance(item.get("summary"), str) or not item["summary"]:
            raise ValueError("route lacks explanation")
        alternatives = item.get("premises")
        if not isinstance(alternatives, list) or not alternatives:
            raise ValueError("each claim requires at least one premises route")
        for route in alternatives:
            if not isinstance(route, list) or not route or any(x not in props for x in route):
                raise ValueError("dangling or empty premise route")
    observations = data.get("evidence")
    if not isinstance(observations, list):
        raise ValueError("evidence must be a list")
    obs_ids = set()
    for obs in observations:
        if not isinstance(obs, dict) or not isinstance(obs.get("id"), str) or obs["id"] in obs_ids:
            raise ValueError("missing or duplicate evidence id")
        obs_ids.add(obs["id"])
        if obs.get("proposition") not in props or type(obs.get("proposed_value")) is not bool:
            raise ValueError("invalid evidence proposition or proposed value")
        if not all(isinstance(obs.get(f), str) and obs[f] for f in ("stage", "source", "scope")):
            raise ValueError("evidence lacks review stage, source or scope")


def propagate(data: dict[str, Any], assumed: Mapping[str, bool]) -> tuple[dict[str, bool | None], dict[str, str]]:
    """Compute the least fixed point of Horn implications and contrapositives."""
    validate_manifest(data)
    status: dict[str, bool | None] = dict.fromkeys(data["propositions"])
    why: dict[str, str] = {}

    def place(name: str, value: bool, reason: str) -> bool:
        if name not in status or type(value) is not bool:
            raise ValueError(f"invalid literal {name}={value}")
        old = status[name]
        if old is not None and old != value:
            raise ValueError(f"contradiction for {name}: {why[name]} versus {reason}")
        if old is None:
            status[name] = value
            why[name] = reason
            return True
        return False

    for name, value in sorted(assumed.items()):
        place(name, value, "explicit scenario/world assignment")
    changed = True
    while changed:
        changed = False
        for a, b in sorted(data["implications"]):
            if status[a] is True:
                changed |= place(b, True, f"{a} => {b}; {a} asserted true")
            if status[b] is False:
                changed |= place(a, False, f"{a} => {b}; {b} asserted false")
    return status, why


def compatible_worlds(data: dict[str, Any], assumed: Mapping[str, bool]) -> list[str]:
    """Find world projections consistent with supplied (possibly non-world) facts."""
    result = []
    for world in WORLD_ORDER:
        combined = dict(assumed)
        flags = data["worlds"][world]
        if any(k in combined and combined[k] != value for k, value in flags.items()):
            continue
        combined.update(flags)
        try:
            propagate(data, combined)
        except ValueError:
            continue
        result.append(world)
    return result


def score_routes(data: dict[str, Any], status: Mapping[str, bool | None]) -> dict[str, dict[str, Any]]:
    """Diagnose listed proof routes. A broken premise says nothing about a scheme break."""
    output: dict[str, dict[str, Any]] = {}
    for claim in data["routes"]:
        route_states = []
        for premises in claim["premises"]:
            values = [status[p] for p in premises]
            route_states.append("invalidated" if False in values else
                                "premises_asserted" if all(v is True for v in values) else "open")
        overall = ("premises_asserted" if "premises_asserted" in route_states else
                   "all_listed_routes_invalidated" if all(x == "invalidated" for x in route_states) else
                   "some_routes_invalidated" if "invalidated" in route_states else "open")
        output[claim["id"]] = {"status": overall, "alternative_routes": route_states}
    return output


def bayes_worlds(priors: Mapping[str, Fraction], likelihoods: Mapping[str, Fraction]) -> dict[str, Fraction]:
    """Exact posterior P(world | observed event) with an explicit joint model."""
    if set(priors) != set(WORLD_ORDER) or set(likelihoods) != set(WORLD_ORDER):
        raise ValueError("world-specific priors and likelihoods required")
    if any(type(x) is not Fraction or not 0 <= x <= 1 for x in (*priors.values(), *likelihoods.values())):
        raise ValueError("probabilities must be exact Fractions in [0,1]")
    if sum(priors.values()) != 1:
        raise ValueError("world priors must sum to 1")
    total = sum(priors[w] * likelihoods[w] for w in WORLD_ORDER)
    if total == 0:
        raise ValueError("observed event has zero likelihood")
    return {w: priors[w] * likelihoods[w] / total for w in WORLD_ORDER}


def bayes_example() -> dict[str, Any]:
    """Illustration: unconditional P(ETH)=9/10 with P(ETH|Algorithmica)=0."""
    q = Fraction
    priors = dict(zip(WORLD_ORDER, (q(1, 1000), q(9, 1000), q(40, 1000),
                                    q(150, 1000), q(800, 1000))))
    # Sum_{w != Algorithmica} P(w) * 100/111 = 9/10.
    likelihoods = {w: (q(1) if w == "Algorithmica" else q(11, 111)) for w in WORLD_ORDER}
    post = bayes_worlds(priors, likelihoods)
    assert sum(priors[w] * likelihoods[w] for w in WORLD_ORDER) == q(1, 10)
    assert post["Algorithmica"] / priors["Algorithmica"] == 10
    return {
        "event": "ETH false; assumed, not independently certified by this program",
        "prior_eth": str(q(9, 10)),
        "prior": {w: str(priors[w]) for w in WORLD_ORDER},
        "p_event_given_world": {w: str(likelihoods[w]) for w in WORLD_ORDER},
        "posterior": {w: str(post[w]) for w in WORLD_ORDER},
        "algorithmica_multiplier": "10",
    }


def report(data: dict[str, Any], scenario: str = "unadjudicated") -> dict[str, Any]:
    """Stable machine-readable audit; no observation auto-upgrades a premise."""
    validate_manifest(data)
    if scenario not in data["scenarios"]:
        raise ValueError(f"unknown scenario: {scenario}")
    assumed = data["scenarios"][scenario]
    status, why = propagate(data, assumed)
    return {
        "schema_version": "1.0",
        "scenario": scenario,
        "scenario_literals": assumed,
        "propositions": {k: ("unknown" if v is None else "true" if v else "false")
                         for k, v in sorted(status.items())},
        "inference_reasons": dict(sorted(why.items())),
        "compatible_worlds": compatible_worlds(data, assumed),
        "conditional_routes": score_routes(data, status),
        "bayesian_illustration": bayes_example(),
        "evidence_not_promoted": len(data["evidence"]),
    }
