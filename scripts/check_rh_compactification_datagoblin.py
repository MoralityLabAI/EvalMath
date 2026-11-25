#!/usr/bin/env python3
"""Load a training-only RH microstep pack with both pinned upstream loaders.

Supply existing source checkouts or exact source snapshots. This command has no
network client and runs no trainer or Lean process. Each imported upstream file
is checked against its Git blob ID before the existing loader code executes.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any


REPOSITORY = Path(__file__).resolve().parents[1]
CONTRACT = REPOSITORY / "gyms/RHCompactification/trainer_contract.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_sources(root: Path, source: dict[str, Any]) -> dict[str, Any]:
    """Authenticate a full checkout or a minimal, unmodified source snapshot."""
    checked = {}
    for relative, expected in source["files"].items():
        path = (root / relative).resolve()
        if not path.is_relative_to(root):
            raise ValueError(f"upstream source escapes its root: {relative}")
        data = path.read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        if blob != expected:
            raise ValueError(f"upstream source differs from the pin: {relative}")
        checked[relative] = hashlib.sha256(data).hexdigest()
    return {
        "repository": source["repository"],
        "commit": source["commit"],
        "entrypoint": source["entrypoint"],
        "verified_files": len(checked),
        "file_sha256": checked,
    }


def import_datagoblin(root: Path):
    """Import the real package, including its normal package initializers."""
    if any(name == "datagoblin" or name.startswith("datagoblin.") for name in sys.modules):
        raise ValueError("run this verifier in a fresh Python process")
    sys.path.insert(0, str(root / "src"))
    module = importlib.import_module("datagoblin.training_gym.rlt_pretrain_data")
    expected = root / "src/datagoblin/training_gym/rlt_pretrain_data.py"
    if Path(module.__file__).resolve() != expected:
        raise ValueError("imported DataGoblin loader came from another source root")
    return module


def import_ppt(root: Path):
    """Import the unchanged loader directly; its API has no Torch dependency."""
    path = root / "research/lean_cgrt_hrm400/ppt_gym/data.py"
    name = "_evalmath_pinned_ppt_data"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError("unable to load pinned PPT data module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def bounded_public_row(row: dict[str, Any], max_bytes: int) -> tuple[int, int]:
    for key in ("id", "lineage", "family", "epoch", "statement", "context"):
        if not isinstance(row.get(key), str) or not row[key]:
            raise ValueError(f"public {key} must be a nonempty string")
    candidates = row["candidates"]
    ids = {candidate["id"] for candidate in candidates}
    order = row.get("orders", {}).get("compose")
    hits = row.get("retrieved", {}).get("compose")
    if (
        not isinstance(order, list) or not order
        or not all(isinstance(item, str) for item in order)
        or len(order) != len(set(order)) or not set(order) <= ids
    ):
        raise ValueError("orders.compose must list distinct, present candidate IDs")
    if not isinstance(hits, list) or not all(isinstance(item, str) and item for item in hits):
        raise ValueError("retrieved.compose must list string lemma names")
    goal = f"<STATEMENT> {row['statement']}\n<GOALS> {row['context']}"
    goal_bytes = len(goal.encode("utf-8"))
    if goal_bytes > max_bytes:
        raise ValueError(f"PPT would truncate goal {row['id']}: {goal_bytes} > {max_bytes} bytes")
    longest = 0
    for candidate in candidates:
        if not isinstance(candidate.get("id"), str) or not candidate["id"]:
            raise ValueError("candidate ID must be a nonempty string")
        tactic = candidate.get("tactic")
        if not isinstance(tactic, str) or not tactic:
            raise ValueError("candidate tactic must be a nonempty string")
        size = len(tactic.encode("utf-8"))
        if size > max_bytes:
            raise ValueError(f"PPT would truncate candidate {candidate['id']}: {size} > {max_bytes} bytes")
        longest = max(longest, size)
    return goal_bytes, longest


def check(pack: Path, datagoblin_root: Path, looped_root: Path) -> dict[str, Any]:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    manifest_path = pack / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != contract["pack_schema"]:
        raise ValueError("unexpected checked-candidate schema")
    if set(manifest.get("splits", {})) != {"train"}:
        raise ValueError("this adapter accepts exactly the public train split")
    declared = manifest["splits"]["train"]["goals"]
    if type(declared) is not int or not 1 <= declared <= 20000:
        raise ValueError("train goal count must be an integer in 1..20000")
    provenance = {
        "datagoblin": verify_sources(datagoblin_root, contract["sources"]["datagoblin"]),
        "looped_transformers": verify_sources(looped_root, contract["sources"]["looped_transformers"]),
    }
    dg = import_datagoblin(datagoblin_root)
    ppt = import_ppt(looped_root)
    rows = list(dg.lean_rows(pack, manifest, "train"))
    # Load every row. A smaller upstream max_cases would skip receipt checks.
    cases, ppt_metadata = ppt.load_checked_pack(pack, "train", max_cases=declared)
    if len(rows) != declared or len(cases) != declared:
        raise ValueError("upstream loader omitted a declared training goal")
    labels = {"positive": 0, "negative": 0, "unknown": 0}
    max_goal = max_tactic = 0
    usable = 0
    for (public, private), case in zip(rows, cases, strict=True):
        if public["id"] != case.root:
            raise ValueError("upstream loaders disagree on row identity")
        goal_bytes, tactic_bytes = bounded_public_row(public, contract["model"]["max_bytes"])
        max_goal, max_tactic = max(max_goal, goal_bytes), max(max_tactic, tactic_bytes)
        usable += any(label >= 0 for label in case.labels)
        for label in case.labels:
            labels[{1: "positive", 0: "negative", -1: "unknown"}[label]] += 1
        expected = tuple(
            -1 if private["outcomes"][item["id"]]["label"] is None
            else private["outcomes"][item["id"]]["label"]
            for item in public["candidates"]
        )
        if case.labels != expected:
            raise ValueError("upstream loaders disagree on candidate labels")
    if not usable:
        raise ValueError("training needs at least one definitive candidate outcome")
    return {
        "schema": "evalmath.rh_compactification.datagoblin_adapter_check.v1",
        "status": "passed",
        "contract_sha256": sha256(CONTRACT),
        "pack_manifest_sha256": sha256(manifest_path),
        "sources": provenance,
        "loaders_executed": [
            "datagoblin.training_gym.rlt_pretrain_data.lean_rows",
            "ppt_gym.data.load_checked_pack",
        ],
        "split": "train",
        "goals": len(cases),
        "lineages": len({case.lineage for case in cases}),
        "families": len({case.family for case in cases}),
        "usable_goals": usable,
        "candidate_labels": labels,
        "goal_bytes_max": max_goal,
        "candidate_bytes_max": max_tactic,
        "model_max_bytes": contract["model"]["max_bytes"],
        "truncated_inputs": 0,
        "upstream_evidence_class": ppt_metadata["evidence_class"],
        "verification_scope": "pinned loader execution over previously generated Lean receipts",
        "lean_processes_executed": 0,
        "training_steps": 0,
        "heldout_evaluation": False,
        "mixed_pretrain_ready": False,
        "scientific_effect_claim": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", type=Path, required=True)
    parser.add_argument("--datagoblin-root", type=Path, required=True)
    parser.add_argument("--looped-transformers-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, help="Optional JSON receipt path")
    args = parser.parse_args()
    try:
        result = check(
            args.pack.resolve(), args.datagoblin_root.resolve(),
            args.looped_transformers_root.resolve(),
        )
    except (OSError, ValueError, KeyError, TypeError, ImportError) as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 1
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
