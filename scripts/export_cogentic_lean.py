"""Replay trained Horn-router attempts, then compile their complete proofs in Lean.

The emitted theorems quantify over the public atoms, initial facts and Horn
rules. They certify entailment in the supplied synthetic worlds. Every selected
root and model seed remains in the index, including unsuccessful episodes.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from collections.abc import Iterator
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPLAY_SOURCE = ROOT / "src/spiral_ln/cogentic_ledger.py"
REPLAY_SOURCE_SHA256 = hashlib.sha256(REPLAY_SOURCE.read_bytes()).hexdigest()
sys.path.insert(0, str(ROOT / "src"))
from spiral_ln.cogentic_ledger import (
    canonical,
    registry_digest,
    replay_episode,
    sha256,
    validate_world,
)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_rows(path: Path) -> Iterator[dict[str, Any]]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            if line.strip():
                row = json.loads(line)
                if not isinstance(row, dict):
                    raise ValueError(f"{path.name}:{number}: expected an object")
                yield row


def registered_tasks(path: Path) -> list[dict[str, Any]]:
    """Check custody in the full registry before selecting evaluation splits."""
    tasks = list(read_rows(path))
    roots: set[str] = set()
    presentations: set[str] = set()
    worlds: set[str] = set()
    for task in tasks:
        root, task_id, split = task["root_id"], task["task_id"], task["split"]
        if any(not isinstance(value, str) or not value for value in (root, task_id, split)):
            raise ValueError("task identifiers and split must be nonempty strings")
        validate_world(task["world"])
        world_digest = sha256(task["world"])
        if root in roots or task_id in presentations or world_digest in worlds:
            raise ValueError("duplicate root, presentation or world in full registry")
        if task_id != world_digest:
            raise ValueError("task presentation does not commit to its public world")
        if task.get("task_digest") != sha256(
            {key: value for key, value in task.items() if key != "task_digest"}
        ):
            raise ValueError("task digest mismatch")
        if task.get("provenance", {}).get("source_world_sha256") != root:
            raise ValueError("source root custody mismatch")
        roots.add(root)
        presentations.add(task_id)
        worlds.add(world_digest)
    if not tasks:
        raise ValueError("task registry is empty")
    return tasks


def select_episodes(
    tasks: list[dict[str, Any]],
    attempts: Path,
    arm: str,
    splits: list[str],
    budget: int,
    seeds: list[int] | None,
) -> tuple[list[dict[str, Any]], list[int], list[dict[str, Any]], dict[str, int]]:
    registry = {task["root_id"]: task for task in tasks}
    selected = [task for task in tasks if task["split"] in splits]
    if {task["split"] for task in selected} != set(splits):
        raise ValueError("requested split has no registered tasks")
    groups: dict[tuple[int, str], list[dict[str, Any]]] = defaultdict(list)
    observed_seeds: set[int] = set()
    scanned, arm_rows = 0, 0
    for event in read_rows(attempts):
        scanned += 1
        if event.get("arm") != arm:
            continue
        arm_rows += 1
        seed, root = event.get("seed"), event.get("root_id")
        if type(seed) is not int:
            raise ValueError("model seed must be an integer")
        if not isinstance(root, str) or root not in registry:
            raise ValueError("model attempt names an unregistered root")
        task = registry[root]
        if event.get("task_id") != task["task_id"] or event.get("split") != task["split"]:
            raise ValueError("model attempt differs from the root's registered task or split")
        if type(event.get("budget")) is not int or event["budget"] != budget:
            raise ValueError("model attempt differs from the requested verifier budget")
        observed_seeds.add(seed)
        if task["split"] in splits:
            groups[(seed, root)].append(event)
    if not observed_seeds:
        raise ValueError("selected arm has no attempts")
    chosen_seeds = sorted(observed_seeds) if seeds is None else sorted(seeds)
    if len(chosen_seeds) != len(set(chosen_seeds)) or set(chosen_seeds) != observed_seeds:
        raise ValueError("declared seeds must match every observed seed for the selected arm")
    episodes = []
    for seed in chosen_seeds:
        for task in sorted(selected, key=lambda item: (item["split"], item["root_id"])):
            key = (seed, task["root_id"])
            if key not in groups:
                raise ValueError(f"missing selected episode: seed={seed}, root={task['root_id']}")
            events = groups[key]
            result = replay_episode(task, events, budget, check_reported=True)
            if result["stopped_early_unsolved"]:
                raise ValueError("unsolved episode stopped before its declared verifier budget")
            episodes.append({"seed": seed, "task": task, "events": events, "replay": result})
    return episodes, chosen_seeds, selected, {
        "all_attempt_rows_scanned": scanned,
        "selected_arm_rows_scanned": arm_rows,
        "selected_episode_rows": sum(len(episode["events"]) for episode in episodes),
    }


def proof_term(task: dict[str, Any], events: list[dict[str, Any]], name: str) -> str:
    """Construct the proof directly from public rules and available premise terms.

    Call only after replay_episode has accepted the complete episode. This pass
    derives each term from the world; producer flags never select proof steps.
    Atom identifiers are mapped to safe positional Lean names.
    """
    if re.fullmatch(r"cogModel_[0-9a-f]{64}", name) is None:
        raise ValueError("unsafe theorem identifier")
    world = task["world"]
    positions = {atom: index for index, atom in enumerate(world["atoms"])}

    def proposition(atom: int) -> str:
        return f"p{positions[atom]}"

    parameters = ["(" + " ".join(proposition(atom) for atom in world["atoms"]) + " : Prop)"]
    parameters.extend(f"(f{positions[atom]} : {proposition(atom)})" for atom in world["facts"])
    for index, rule in enumerate(world["rules"]):
        implication = " → ".join(proposition(atom) for atom in [*rule["premises"], rule["conclusion"]])
        parameters.append(f"(r{index} : {implication})")
    lines = [f"theorem {name} {' '.join(parameters)} : {proposition(world['goal'])} := by"]
    terms = {atom: f"f{positions[atom]}" for atom in world["facts"]}
    for event in events:
        action = event["action"]
        if type(action) is not int or not 0 <= action < len(world["rules"]):
            continue
        rule = world["rules"][action]
        conclusion = rule["conclusion"]
        if conclusion in terms or any(premise not in terms for premise in rule["premises"]):
            continue
        term_name = f"h{positions[conclusion]}"
        application = " ".join([f"r{action}", *(terms[premise] for premise in rule["premises"])])
        lines.append(f"  have {term_name} : {proposition(conclusion)} := {application}")
        terms[conclusion] = term_name
    if world["goal"] not in terms:
        raise ValueError("trajectory supplies no complete goal proof")
    lines.extend([f"  exact {terms[world['goal']]}", f"#print axioms {name}"])
    return "\n".join(lines) + "\n"


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def export(args: argparse.Namespace) -> dict[str, Any]:
    if args.budget < 0 or not args.arm or len(args.splits) != len(set(args.splits)):
        raise ValueError("require a nonnegative budget, arm and distinct splits")
    input_hashes = {"tasks": file_sha256(args.tasks), "attempts": file_sha256(args.attempts)}
    source_hashes = {
        "scripts/export_cogentic_lean.py": file_sha256(Path(__file__)),
        "src/spiral_ln/cogentic_ledger.py": REPLAY_SOURCE_SHA256,
    }
    tasks = registered_tasks(args.tasks)
    episodes, seeds, selected, scanned = select_episodes(
        tasks, args.attempts, args.arm, args.splits, args.budget, args.seeds
    )
    args.out.mkdir(parents=True, exist_ok=False)
    names: list[str] = []
    terms: list[str] = []
    index = []
    for episode in episodes:
        task, replay = episode["task"], episode["replay"]
        binding = {"arm": args.arm, "seed": episode["seed"], "root_id": task["root_id"],
                   "task_id": task["task_id"], "split": task["split"], "budget": args.budget}
        theorem = None
        if replay["solved"]:
            theorem = "cogModel_" + sha256(binding)
            names.append(theorem)
            terms.append(proof_term(task, episode["events"], theorem))
        index.append({**binding, "theorem": theorem,
                      "events_sha256": sha256(episode["events"]),
                      "replay": replay})
    if not names or len(names) != len(set(names)):
        raise ValueError("expected distinct completed proof declarations")
    proof_path = args.out / "model_proofs.lean"
    proof_path.write_text(
        "import Init\nset_option linter.unusedVariables false\n\n" + "\n".join(terms),
        encoding="utf-8",
    )
    sentinel = args.out / "negative_sentinel.lean"
    sentinel.write_text("import Init\ntheorem cogRejected (P Q : Prop) (h : P) : Q := h\n", encoding="utf-8")
    index_path = args.out / "certificate_index.json"
    write_json(index_path, index)
    executable = args.lean.resolve(strict=True)
    lean_binary_hash = file_sha256(executable)
    version = subprocess.run([str(executable), "--version"], check=True, capture_output=True,
                             text=True, timeout=15).stdout.strip()
    compiled = subprocess.run([str(executable), proof_path.name], check=False, cwd=args.out.resolve(),
                              capture_output=True, text=True, timeout=args.timeout)
    output = compiled.stdout + compiled.stderr
    log = args.out / "lean_stdout.txt"
    log.write_text(output, encoding="utf-8")
    audited = re.findall(r"'(cogModel_[0-9a-f]{64})' does not depend on any axioms", output)
    nonempty_axioms = re.findall(r"'(cogModel_[0-9a-f]{64})' depends on axioms", output)
    rejected = subprocess.run([str(executable), sentinel.name], check=False, cwd=args.out.resolve(),
                              capture_output=True, text=True, timeout=15)
    negative_output = rejected.stdout + rejected.stderr
    negative_log = args.out / "negative_stdout.txt"
    negative_log.write_text(negative_output, encoding="utf-8")
    empty_axioms = Counter(audited) == Counter(names) and not nonempty_axioms
    sentinel_rejected = rejected.returncode != 0 and "type mismatch" in negative_output.lower()
    passed = compiled.returncode == 0 and empty_axioms and sentinel_rejected
    groups = []
    for split in args.splits:
        for seed in seeds:
            rows = [episode for episode in episodes
                    if episode["seed"] == seed and episode["task"]["split"] == split]
            groups.append({"split": split, "seed": seed, "independent_roots": len(rows),
                           "episodes": len(rows), "compiled_complete_proofs": sum(
                               episode["replay"]["solved"] for episode in rows),
                           "recorded_finite_verifier_calls": sum(
                               episode["replay"]["calls"] for episode in rows)})
    # Detect concurrent source/input edits rather than attaching a later hash to
    # code or data that the process did not use.
    for name, expected in source_hashes.items():
        if file_sha256(ROOT / name) != expected:
            raise ValueError(f"source changed during export: {name}")
    for name, path in [("tasks", args.tasks), ("attempts", args.attempts)]:
        if file_sha256(path) != input_hashes[name]:
            raise ValueError(f"input changed during export: {name}")
    if file_sha256(executable) != lean_binary_hash:
        raise ValueError("Lean executable changed during export")
    generated = [proof_path, sentinel, index_path, log, negative_log]
    counts = {key: sum(episode["replay"][key] for episode in episodes)
              for key in ("calls", "accepted", "rejected", "duplicates", "unique_verified_facts",
                          "post_solution_calls")}
    receipt = {
        "schema": "EvalMath/cog08/model-lean/v1",
        "passed": passed,
        "evidence": "native Lean 4 kernel replay of model-produced finite Horn derivations",
        "scope": "Synthetic public Horn worlds; quantified facts and rules are theorem hypotheses.",
        "selection": {"arm": args.arm, "splits": args.splits, "seeds": seeds,
                      "seed_selection": "explicit" if args.seeds is not None else "all seeds observed for the arm",
                      "budget": args.budget, "full_registry_roots": len(tasks),
                      "selected_independent_roots": len(selected), "expected_episodes": len(selected) * len(seeds),
                      "observed_episodes": len(episodes),
                      "full_registry_sha256": registry_digest(tasks),
                      "selected_registry_sha256": registry_digest(selected)},
        "input_files": {name: {"filename": path.name, "sha256": input_hashes[name]}
                        for name, path in [("tasks", args.tasks), ("attempts", args.attempts)]},
        "source_sha256": source_hashes,
        "generated_files": {path.name: {"sha256": file_sha256(path), "bytes": path.stat().st_size}
                            for path in generated},
        "counts": {**scanned, "completed_episodes": len(names),
                   "unsolved_episodes_retained": len(episodes) - len(names),
                   "compiled_axiom_free_theorems": len(audited), **counts},
        "cohorts": groups,
        "cost_accounting": {
            "recorded_finite_policy_verifier_calls": counts["calls"],
            "independent_replay_finite_step_checks": counts["calls"],
            "term_emission_event_visits": sum(len(episode["events"]) for episode in episodes
                                              if episode["replay"]["solved"]),
            "native_proof_compiler_processes": 2,
            "native_positive_batch_processes": 1,
            "native_negative_sentinel_processes": 1,
            "native_version_queries": 1,
            "note": "Model verifier calls are the recorded policy budget. Export validation and native batch compilation are separate costs.",
        },
        "native_lean": {"version": version, "executable_sha256": lean_binary_hash,
                        "positive_exit_code": compiled.returncode,
                        "negative_exit_code": rejected.returncode,
                        "expected_theorems": len(names), "axiom_report_count": len(audited),
                        "all_axiom_lists_empty": empty_axioms,
                        "negative_wrong_term_rejected": sentinel_rejected},
    }
    receipt["receipt_sha256"] = sha256(receipt)
    write_json(args.out / "receipt.json", receipt)
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tasks", type=Path, required=True)
    parser.add_argument("--attempts", type=Path, required=True)
    parser.add_argument("--arm", required=True)
    parser.add_argument("--splits", nargs="+", required=True)
    parser.add_argument("--budget", type=int, required=True)
    parser.add_argument("--seeds", nargs="+", type=int)
    parser.add_argument("--lean", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()
    receipt = export(args)
    print(canonical({"passed": receipt["passed"], "counts": receipt["counts"],
                     "cohorts": receipt["cohorts"], "native_lean": receipt["native_lean"],
                     "receipt_sha256": receipt["receipt_sha256"]}))
    if not receipt["passed"]:
        raise SystemExit("native proof validation failed; inspect saved compiler logs")


if __name__ == "__main__":
    main()
