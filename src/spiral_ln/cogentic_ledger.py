"""COG-08: independently replay finite Horn traces and account for proof progress.

All exact values concern the supplied finite worlds. The verifier in this file
has no dependency on the producer's checker. Statistical reporting uses roots
as clusters, including runs that submitted zero attempts.
"""
from __future__ import annotations

import copy
import hashlib
import json
from collections import defaultdict
from collections.abc import Iterable, Mapping
from fractions import Fraction
from typing import Any

SCHEMA = "EvalMath/cog08/v1"


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False)


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def registry_digest(tasks: Iterable[Mapping[str, Any]]) -> str:
    records = [{"root_id": t["root_id"], "task_id": t["task_id"],
                "split": t["split"], "world_sha256": sha256(t["world"])} for t in tasks]
    return sha256(sorted(records, key=lambda r: (r["root_id"], r["task_id"], r["split"])))


def validate_world(world: Mapping[str, Any]) -> None:
    if set(world) != {"atoms", "facts", "rules", "goal"}:
        raise ValueError("world has unexpected fields")
    atoms = world["atoms"]
    if (not isinstance(atoms, list) or not atoms or len(atoms) > 4096
            or any(type(a) is not int for a in atoms)
            or len(set(atoms)) != len(atoms)):
        raise ValueError("invalid atom domain")
    domain = set(atoms)
    facts = world["facts"]
    if (not isinstance(facts, list) or any(type(a) is not int for a in facts)
            or len(facts) != len(set(facts)) or not set(facts) <= domain
            or type(world["goal"]) is not int or world["goal"] not in domain):
        raise ValueError("invalid facts or goal")
    if not isinstance(world["rules"], list) or len(world["rules"]) > 8192:
        raise ValueError("invalid rules")
    for rule in world["rules"]:
        if not isinstance(rule, dict) or set(rule) != {"premises", "conclusion"}:
            raise ValueError("invalid rule record")
        premises = rule["premises"]
        if (not isinstance(premises, list) or any(type(x) is not int for x in premises)
                or len(premises) != len(set(premises)) or not set(premises) <= domain
                or type(rule["conclusion"]) is not int or rule["conclusion"] not in domain):
            raise ValueError("invalid implication")


def goal_ancestors(world: Mapping[str, Any]) -> set[int]:
    """Backward syntactic dependency closure, including alternative rule paths."""
    needed = {world["goal"]}
    while True:
        larger = needed | {p for r in world["rules"] if r["conclusion"] in needed
                           for p in r["premises"]}
        if larger == needed:
            return needed
        needed = larger


def step(world: Mapping[str, Any], known: set[int], action: object) -> dict[str, Any]:
    """One charged verifier call, including rejections and repeated facts."""
    after = set(known)
    result = {"accepted": False, "code": "invalid_action", "new_fact": None,
              "verifier_calls": 1}
    if type(action) is int and 0 <= action < len(world["rules"]):
        rule = world["rules"][action]
        if all(p in known for p in rule["premises"]):
            conclusion = rule["conclusion"]
            result["accepted"] = True
            result["code"] = "duplicate_lemma" if conclusion in known else "proved_lemma"
            if conclusion not in known:
                result["new_fact"] = conclusion
            after.add(conclusion)
        else:
            result["code"] = "missing_premise"
    result["next_known"] = sorted(after)
    result["solved"] = world["goal"] in after
    return result


def _ratio(numerator: int, denominator: int) -> str | None:
    return str(Fraction(numerator, denominator)) if denominator else None


def replay_episode(task: Mapping[str, Any], events: Iterable[Mapping[str, Any]],
                   budget: int, *, check_reported: bool = True) -> dict[str, Any]:
    """Replay every attempt from the task's initial facts.

    A supplied verdict never grants credit. The independent result must match
    the producer receipt exactly. Public history is checked before the action.
    """
    if type(budget) is not int or budget < 0:
        raise ValueError("budget must be a nonnegative integer")
    world = task["world"]
    validate_world(world)
    if "task_digest" in task:
        expected = sha256({k: v for k, v in task.items() if k != "task_digest"})
        if task["task_digest"] != expected:
            raise ValueError("task digest mismatch")
    rows = list(events)
    if len(rows) > budget:
        raise ValueError("verifier budget exceeded")
    known = set(world["facts"])
    history: list[dict[str, Any]] = []
    ancestors = goal_ancestors(world)
    fresh: set[int] = set()
    useful: set[int] = set()
    counts = {"accepted": 0, "rejected": 0, "duplicates": 0,
              "irrelevant_new_facts": 0, "post_solution_calls": 0}
    first_solution = 0 if world["goal"] in known else None
    # Each prefix is available for budget-matched progress curves.
    prefixes = [{"calls": 0, "solved": first_solution == 0, "unique_facts": 0,
                 "goal_ancestor_facts": 0}]
    for index, event in enumerate(rows):
        event_step = event.get("step", event.get("visit"))
        if type(event_step) is not int or event_step != index:
            raise ValueError("attempts must form an ordered, zero-based prefix")
        if "root_id" in event and event["root_id"] != task["root_id"]:
            raise ValueError("attempt belongs to another root")
        if "task_id" in event and event["task_id"] != task["task_id"]:
            raise ValueError("attempt belongs to another presentation")
        if "split" in event and event["split"] != task["split"]:
            raise ValueError("attempt split differs from registered task")
        if "budget" in event and event["budget"] != budget:
            raise ValueError("attempt budget differs from registered budget")
        observation = event.get("observation")
        expected_observation = {"world": world, "known": sorted(known), "history": history}
        if canonical(observation) != canonical(expected_observation):
            raise ValueError("public observation differs from independently replayed state")
        if "action" not in event:
            raise ValueError("attempt action missing")
        result = step(world, known, event["action"])
        supplied = event.get("receipt", event.get("verification"))
        if check_reported:
            if not isinstance(supplied, dict):
                raise ValueError("producer receipt missing")
            for key, value in result.items():
                # JSON comparison distinguishes bools from integer atom IDs.
                if key not in supplied or canonical(supplied[key]) != canonical(value):
                    raise ValueError(f"producer receipt mismatch: {key}")
            if "verifier_calls" in event and (type(event["verifier_calls"]) is not int
                                                or event["verifier_calls"] != 1):
                raise ValueError("producer undercounts verifier calls")
            if "cost" in event and (type(event["cost"].get("verifier_calls")) is not int
                                      or event["cost"].get("verifier_calls") != 1):
                raise ValueError("producer cost omits verifier call")
        if first_solution is not None:
            counts["post_solution_calls"] += 1
        if result["accepted"]:
            counts["accepted"] += 1
        else:
            counts["rejected"] += 1
        atom = result["new_fact"]
        if atom is not None:
            fresh.add(atom)
            if atom in ancestors:
                useful.add(atom)
            else:
                counts["irrelevant_new_facts"] += 1
        elif result["accepted"]:
            counts["duplicates"] += 1
        known = set(result["next_known"])
        if first_solution is None and result["solved"]:
            first_solution = index + 1
        history.append({"action": event["action"], **{k: result[k] for k in
                        ("accepted", "code", "new_fact")}})
        prefixes.append({"calls": index + 1, "solved": result["solved"],
                         "unique_facts": len(fresh), "goal_ancestor_facts": len(useful)})
    calls = len(rows)
    return {"root_id": task["root_id"], "task_id": task["task_id"],
            "split": task["split"], "family": task.get("family", "unknown"),
            "world_sha256": sha256(world), "budget": budget, "calls": calls,
            "solved": world["goal"] in known, "first_solution_call": first_solution,
            "unique_verified_facts": len(fresh), "goal_ancestor_verified_facts": len(useful),
            "verified_facts_per_call": _ratio(len(fresh), calls),
            "goal_ancestor_facts_per_call": _ratio(len(useful), calls),
            "unused_budget": budget - calls, "empty_trace": calls == 0,
            "stopped_early_unsolved": calls < budget and world["goal"] not in known,
            "final_known": sorted(known), "prefixes": prefixes, **counts}


def evaluate(tasks: list[dict[str, Any]], events: list[dict[str, Any]],
             protocol: Mapping[str, Any]) -> dict[str, Any]:
    """Account for the complete registered root x seed x arm product."""
    if protocol.get("schema_version") != 1:
        raise ValueError("unsupported protocol")
    arms, seeds, splits = protocol["arms"], protocol["seeds"], protocol["splits"]
    if (not arms or any(not isinstance(x, str) or not x for x in arms)
            or len(arms) != len(set(arms)) or not seeds
            or any(type(x) is not int for x in seeds) or len(seeds) != len(set(seeds))
            or not splits or len(splits) != len(set(splits))):
        raise ValueError("protocol requires unique arms, seeds and splits")
    budget = protocol["budget"]
    expected_registry = protocol.get("expected_registry_sha256")
    observed_registry = registry_digest(tasks)
    if expected_registry is not None and expected_registry != observed_registry:
        raise ValueError("task registry differs from protocol commitment")
    registered: dict[str, dict[str, Any]] = {}
    all_roots, presentations, worlds = set(), set(), set()
    for task in tasks:
        root, task_id = task["root_id"], task["task_id"]
        if not isinstance(root, str) or not root or not isinstance(task_id, str) or not task_id:
            raise ValueError("root and presentation identifiers must be nonempty strings")
        validate_world(task["world"])
        world_digest = sha256(task["world"])
        if root in all_roots:
            raise ValueError("duplicate root in full task registry")
        if task_id in presentations or world_digest in worlds:
            raise ValueError("aliased presentation or identical world across roots")
        all_roots.add(root)
        presentations.add(task_id)
        worlds.add(world_digest)
        if task["split"] not in splits:
            continue
        registered[root] = task
    if not registered or set(splits) != {t["split"] for t in registered.values()}:
        raise ValueError("requested split has no registered tasks")
    if "expected_root_counts" in protocol:
        observed_counts = {s: sum(t["split"] == s for t in registered.values()) for s in splits}
        if protocol["expected_root_counts"] != observed_counts:
            raise ValueError("root counts differ from protocol commitment")
    groups: dict[tuple[str, int, str], list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        key = (event.get("arm"), event.get("seed"), event.get("root_id"))
        if (key[0] not in arms or type(key[1]) is not int
                or key[1] not in seeds or key[2] not in registered):
            raise ValueError("unregistered run or root in attempts")
        groups[key].append(event)
    episodes = []
    for arm in arms:
        for seed in seeds:
            for root, task in sorted(registered.items()):
                score = replay_episode(task, groups.get((arm, seed, root), []), budget)
                score.update(arm=arm, seed=seed)
                episodes.append(score)
    summaries = []
    for split in splits:
        for arm in arms:
            selected = [r for r in episodes if r["arm"] == arm and r["split"] == split]
            roots = {r["root_id"] for r in selected}
            calls = sum(r["calls"] for r in selected)
            solved = sum(r["solved"] for r in selected)
            unique = sum(r["unique_verified_facts"] for r in selected)
            relevant = sum(r["goal_ancestor_verified_facts"] for r in selected)
            missing_runs = sum(r["empty_trace"] and not r["solved"] for r in selected)
            early_runs = sum(r["stopped_early_unsolved"] for r in selected)
            complete_cost = missing_runs == 0 and early_runs == 0
            # Average seed-specific indicators within root, then across roots.
            success = sum((Fraction(sum(r["solved"] for r in selected if r["root_id"] == root),
                                    len(seeds)) for root in roots), Fraction(0)) / len(roots)
            curve = []
            for cap in range(budget + 1):
                n_solved = sum(r["first_solution_call"] is not None
                               and r["first_solution_call"] <= cap for r in selected)
                curve.append({"budget": cap, "solved": n_solved,
                              "solve_fraction": str(Fraction(n_solved, len(selected)))})
            summaries.append({"arm": arm, "split": split, "independent_roots": len(roots),
                              "seed_runs": len(selected), "model_seeds": len(seeds),
                              "solved_runs": solved, "solve_fraction_exact": str(success),
                              "verifier_calls": calls, "unique_verified_facts": unique,
                              "goal_ancestor_verified_facts": relevant,
                              "completed_runs_per_call": _ratio(solved, calls) if complete_cost else None,
                              "completed_runs_per_allocated_call": _ratio(solved, len(selected) * budget),
                              "goal_ancestor_facts_per_call": _ratio(relevant, calls) if complete_cost else None,
                              "raw_acceptance_fraction": (_ratio(sum(r["accepted"] for r in selected), calls)
                                                          if complete_cost else None),
                              "rejected_calls": sum(r["rejected"] for r in selected),
                              "duplicate_calls": sum(r["duplicates"] for r in selected),
                              "irrelevant_new_facts": sum(r["irrelevant_new_facts"] for r in selected),
                              "missing_runs": missing_runs, "early_unsolved_runs": early_runs,
                              "complete_trace_coverage": missing_runs == 0,
                              "cost_accounting_complete": complete_cost,
                              "solve_curve": curve})
    return {"schema": SCHEMA, "evidence": "independently_replayed_finite_synthetic_worlds",
            "protocol_sha256": sha256(protocol), "tasks_sha256": sha256(tasks),
            "registry_sha256": observed_registry, "registry_bound": expected_registry is not None,
            "events_sha256": sha256(events), "episodes": episodes, "summary": summaries,
            "scope": "Goal ancestry measures syntactic progress in the registered worlds. "
                     "Seed repeats share task roots. This replay checks discrete proof steps; "
                     "a native Lean replay has a separate receipt."}


def paired_manifest(report: Mapping[str, Any], candidate: str, baseline: str,
                    split: str, *, comparisons: int) -> dict[str, Any]:
    """Build FSI-01 input with honest exploratory exposure flags."""
    rows = [r for r in report["episodes"] if r["split"] == split]
    by_key = {(r["arm"], r["seed"], r["root_id"]): r for r in rows}
    keys = sorted((r["seed"], r["root_id"]) for r in rows if r["arm"] == candidate)
    if not keys:
        raise ValueError("candidate has no evaluation cases")
    cases = []
    for seed, root in keys:
        if (baseline, seed, root) not in by_key:
            raise ValueError("missing paired baseline")
        cases.append({"case_id": f"{root}:{seed}", "cluster_id": root,
                      "candidate": int(by_key[(candidate, seed, root)]["solved"]),
                      "baseline": int(by_key[(baseline, seed, root)]["solved"])})
    return {"schema_version": 1, "experiment_id": f"COG08:{candidate}:{baseline}:{split}",
            "target_population": "public synthetic Horn roots from COG02",
            "evaluation_mode": "sampled", "alpha": "1/20", "minimum_effect": "1/20",
            "planned_comparisons": comparisons, "min_independent_clusters": 20,
            "hypothesis_preregistered": False, "sealed_readout": False,
            "clusters_independent": True, "exchangeable_pair_labels": False,
            "resample_seed": 20261126, "bootstrap_resamples": 2048,
            "signflip_simulations": 4096, "cases": cases}


def fixture() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Finite adversarial accounting witness with a distraction and a duplicate."""
    world = {"atoms": list(range(5)), "facts": [0], "goal": 3,
             "rules": [{"premises": [0], "conclusion": 1},
                       {"premises": [1], "conclusion": 2},
                       {"premises": [2], "conclusion": 3},
                       {"premises": [0], "conclusion": 4}]}
    task = {"root_id": "accounting-witness", "task_id": "accounting-witness",
            "split": "development", "family": "chain_with_distraction", "world": world}
    rows, known, history = [], set(world["facts"]), []
    for index, action in enumerate([2, 3, 3, 0, 1, 2]):
        obs = {"world": copy.deepcopy(world), "known": sorted(known),
               "history": copy.deepcopy(history)}
        result = step(world, known, action)
        rows.append({"step": index, "observation": obs, "action": action,
                     "receipt": result, "verifier_calls": 1})
        known = set(result["next_known"])
        history.append({"action": action, **{k: result[k] for k in
                        ("accepted", "code", "new_fact")}})
    return task, rows
