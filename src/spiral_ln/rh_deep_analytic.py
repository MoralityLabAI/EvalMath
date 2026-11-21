"""Source-pinned Lean 4.33.1 proof-expression probe for character-balance bottlenecks.

Direct references in elaborated terms are machine evidence about the published
compiled artifact. They are not proof minimization or independent kernel replay.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from spiral_ln.rh_dependency import build_probe, pinned_mirror, run_lean
from spiral_ln.rh_distillation import git_blob_sha
from spiral_ln.rh_full_closure import ImportGraph
from spiral_ln.rh_selective_olean import (
    assure_disk, load_restore_script, restore_subset, selected_rows, verified_manifest,
)

BASE = Path(__file__).resolve().parents[2] / "gyms" / "RHProofDistillation"
SOURCE = "src/Development/AutomorphicArithmetic/DedekindLFunctions/LandauTheorems/ChCore.lean"
IMPORT = "Development.AutomorphicArithmetic.DedekindLFunctions.LandauTheorems.ChCore"
SOURCE_BLOB = "878f5077bc382426c7da988e5a375b85deeaa7de"
TARGETS = {
    "balance_core": {
        "constant": "Deduction.CharacterBalanceMoves.core",
        "source_marker": "lemma core (A0",
    },
    "size_bound": {
        "constant": "Formalism.LFunctionChainParameters.ThickSetMeanBounds.proposition_size_bound",
        "source_marker": "proposition_size_bound",
    },
}


def validate_source(root: Path, manifest: dict) -> dict:
    identity = pinned_mirror(root, manifest)
    raw = (root / SOURCE).read_bytes()
    if git_blob_sha(raw) != SOURCE_BLOB:
        raise ValueError("ChCore source Git blob differs from pinned release")
    body = raw.decode("utf-8")
    if "namespace CharacterBalanceMoves" not in body:
        raise ValueError("CharacterBalanceMoves namespace absent")
    if any(spec["source_marker"] not in body for spec in TARGETS.values()):
        raise ValueError("target theorem source markers absent")
    return {"commit": identity["commit"], "six_anchor_blobs_match": True,
            "ChCore_git_blob": SOURCE_BLOB,
            "ChCore_sha256": hashlib.sha256(raw).hexdigest()}


def compact_summary(result: dict) -> dict:
    roots = {}
    for key, graph in result.get("graphs", {}).items():
        name = TARGETS[key]["constant"]
        items = {n["name"]: n for n in graph["nodes"]}
        node = items[name]
        names = set(node["value_refs"])
        roots[key] = {
            "root": name,
            "root_kind": node["kind"],
            "type_ref_count": len(node["type_refs"]),
            "proof_value_ref_count": len(node["value_refs"]),
            "direct_theorem_refs": sorted(n for n in names if n in items and items[n]["kind"] == "theorem"),
            "visited": graph["scope"]["visited"],
            "truncated": graph["scope"]["truncated"],
            "depth_limited": graph["scope"]["depth_limited"],
            "queued": graph["scope"]["queued"],
        }
    return {"status": result["status"], "proof_term_data": result["proof_term_data"],
            "module_count": result["module_count"],
            "source_commit": result["source"]["commit"],
            "roots": roots}


def run(root: Path, manifest: dict, selected: list[str], *, max_depth: int,
        max_nodes: int, max_modules: int, timeout: int, plan_only: bool) -> dict:
    if not selected or any(k not in TARGETS for k in selected):
        raise ValueError("invalid or empty target selection")
    if max_nodes < 1 or max_depth < 0:
        raise ValueError("invalid proof-reference traversal bounds")
    identity = validate_source(root, manifest)
    module_graph = ImportGraph(root / "src").closure(IMPORT)
    if module_graph["unresolved_internal_imports"]:
        raise ValueError(f"missing source modules: {module_graph['unresolved_internal_imports'][:10]}")
    modules = module_graph["module_set"]
    if not 0 < len(modules) <= max_modules:
        raise ValueError(f"invalid target module closure: {len(modules)}")
    verifier = load_restore_script(root)
    manifest_rows = verified_manifest(verifier)
    rows = selected_rows(manifest_rows, modules)
    receipt = {
        "schema": 1, "source": identity, "source_module": IMPORT,
        "module_count": len(rows), "source_import_edge_sha256": module_graph["edge_stream_sha256"],
        "selected_targets": selected, "proof_term_data": False,
        "compiled_cache": "pinned public Lean 4.33.1 artifacts",
        "trust_boundary": "Published cache verification, not independently rebuilt solution",
    }
    if plan_only:
        receipt["status"] = "source_and_cache_plan_verified"
        return receipt
    assure_disk(root, len(rows), max_modules=max_modules, min_free_gib=7)
    receipt["restore"] = restore_subset(root, rows, verifier, workers=4)
    graphs = {}
    for key in selected:
        target = TARGETS[key]["constant"]
        script = build_probe(
            [IMPORT], [target], depth=max_depth, max_nodes=max_nodes,
            prefixes=["Deduction.", "Formalism."],
        )
        extracted = run_lean(script, root, timeout=timeout)
        root_node = next((n for n in extracted["nodes"] if n["name"] == target), None)
        if root_node is None or root_node["kind"] != "theorem":
            raise ValueError(f"compiled target was not found as theorem: {target}")
        if not root_node["value_refs"]:
            raise ValueError(f"compiled proof value is unexpectedly empty: {target}")
        graphs[key] = extracted
    receipt["graphs"] = graphs
    receipt["proof_term_data"] = True
    receipt["status"] = "source_pinned_compiled_reference_graph"
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--targets", nargs="+", choices=sorted(TARGETS), default=list(TARGETS))
    parser.add_argument("--max-depth", type=int, default=1)
    parser.add_argument("--max-nodes", type=int, default=120)
    parser.add_argument("--max-modules", type=int, default=200)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--plan-only", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--summary", type=Path)
    args = parser.parse_args()
    manifest = json.loads((BASE / "anchors.json").read_text(encoding="utf-8"))
    result = run(args.source_root.resolve(), manifest, args.targets,
                 max_depth=args.max_depth, max_nodes=args.max_nodes,
                 max_modules=args.max_modules, timeout=args.timeout,
                 plan_only=args.plan_only)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    s = compact_summary(result)
    if args.summary:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(json.dumps(s, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(s, sort_keys=True))


if __name__ == "__main__":
    main()
