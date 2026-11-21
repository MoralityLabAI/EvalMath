"""Measure complete, source-pinned Lean module import closures.

This is a 175k-file source traversal. A module-import graph is not a graph of
proof-term references. Its purpose is to size selective .olean restoration and
find a concrete shortest module path from Main to core_gm.
"""
from __future__ import annotations

import argparse
from collections import Counter, deque
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Iterable

from spiral_ln.rh_distillation import anchor_audit, parse_imports

ROOT = Path(__file__).resolve().parents[2] / "gyms" / "RHProofDistillation"
MODULE = re.compile(r"^[^\s/]+(?:\.[^\s/]+)*$", re.UNICODE)
INTERNAL = frozenset({
    "Statements", "Main", "Development", "Formalism", "GroundTheory",
    "ReciprocityTheory", "CompanionTheory", "PositivityTheory",
    "Lemmata", "Supplements", "BuildAid", "Challenge",
})


def module_name(path: str) -> str:
    if not path.startswith("src/") or not path.endswith(".lean"):
        raise ValueError(f"invalid source path: {path}")
    return path[len("src/"):-len(".lean")].replace("/", ".")


def module_file(src: Path, module: str) -> Path:
    if not MODULE.fullmatch(module) or any(part in ("", ".", "..") for part in module.split(".")):
        raise ValueError(f"invalid Lean module: {module!r}")
    return src.joinpath(*module.split(".")).with_suffix(".lean")


def verify_full_checkout(root: Path, manifest: dict, minimum: int) -> dict:
    head = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    if head != manifest["mirror_commit"]:
        raise ValueError(f"pinned HEAD mismatch: {head}")
    if minimum < 1:
        raise ValueError("minimum file count must be positive")
    count = sum(1 for _ in (root / "src").rglob("*.lean"))
    if count < minimum:
        raise ValueError(f"source checkout incomplete: {count} .lean files < {minimum}")
    anchors = anchor_audit(root, manifest)
    if any(a["status"] != "match" for a in anchors):
        raise ValueError(f"source anchors differ: {anchors}")
    return {"commit": head, "lean_files_checked_out": count, "anchors_matched": len(anchors)}


class ImportGraph:
    def __init__(self, src: Path) -> None:
        self.src = src
        self.cached: dict[str, tuple[str, ...] | None] = {}
        self.bytes: dict[str, int] = {}

    def imports(self, module: str) -> tuple[str, ...] | None:
        if module not in self.cached:
            f = module_file(self.src, module)
            if f.is_file():
                data = f.read_bytes()
                self.bytes[module] = len(data)
                self.cached[module] = tuple(parse_imports(data.decode("utf-8")))
            else:
                self.cached[module] = None
        return self.cached[module]

    def closure(self, root: str, targets: Iterable[str] = ()) -> dict:
        todo = deque([root])
        visited: set[str] = set()
        queued: set[str] = {root}
        parents: dict[str, str | None] = {root: None}
        external: set[str] = set()
        missing: set[str] = set()
        import_edges = 0
        h = hashlib.sha256()
        families: Counter[str] = Counter()
        while todo:
            mod = todo.popleft()
            if mod in visited:
                continue
            deps = self.imports(mod)
            if deps is None:
                (missing if mod.split(".", 1)[0] in INTERNAL else external).add(mod)
                continue
            visited.add(mod)
            families[mod.split(".", 1)[0]] += 1
            for dep in deps:
                import_edges += 1
                h.update((mod + "\t" + dep + "\n").encode())
                if dep not in queued:
                    queued.add(dep)
                    parents[dep] = mod
                    todo.append(dep)
        paths = {}
        for target in targets:
            if target not in visited:
                paths[target] = None
                continue
            chain = []
            node = target
            while node is not None:
                chain.append(node)
                node = parents[node]
            paths[target] = chain[::-1]
        return {
            "root": root, "modules": len(visited), "import_edges": import_edges,
            "module_source_bytes": sum(self.bytes[m] for m in visited),
            "external_imports": sorted(external),
            "unresolved_internal_imports": sorted(missing),
            "family_counts": dict(sorted(families.items())),
            "edge_stream_sha256": h.hexdigest(),
            "paths": paths,
            "module_set": visited,
        }


def complete_graph(root: Path, manifest: dict, minimum: int, selected: list[str]) -> dict:
    evidence = verify_full_checkout(root, manifest, minimum)
    graph = ImportGraph(root / "src")
    outputs = []
    for name in selected:
        item = graph.closure(name, targets=selected)
        output = {k: v for k, v in item.items() if k != "module_set"}
        outputs.append(output)
    overlap = []
    for i, a in enumerate(selected):
        for b in selected[i + 1:]:
            set_a = graph.closure(a)["module_set"]
            set_b = graph.closure(b)["module_set"]
            overlap.append({"left": a, "right": b, "shared_modules": len(set_a & set_b)})
    return {
        "schema_version": 1,
        "mode": "full_upstream_source_module_import_graph",
        "proof_term_data": False,
        "upstream_source": evidence,
        "distinct_modules_parsed": sum(1 for x in graph.cached.values() if x is not None),
        "roots": outputs,
        "pairwise_overlap": overlap,
        "cache_projection_note": (
            "Source module closure is only a lower-level prerequisite count. "
            "Olean bytes, transitive proof constants, and archive fetch costs "
            "must be measured separately."
        ),
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-root", type=Path, required=True)
    p.add_argument("--manifest", type=Path, default=ROOT / "anchors.json")
    p.add_argument("--roots", nargs="+", default=["weighted_bound", "all_characters", "theta_galois", "analytic_window"])
    p.add_argument("--include-main", action="store_true")
    p.add_argument("--minimum-files", type=int, default=175187)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    ids = {x["id"]: module_name(x["path"]) for x in manifest["anchors"]}
    invalid = [x for x in args.roots if x not in ids]
    if invalid:
        p.error(f"unknown anchor IDs: {invalid}")
    selected = [ids[a] for a in args.roots]
    if args.include_main and "Main" not in selected:
        selected.append("Main")
    if not selected:
        p.error("provide at least one root")
    result = complete_graph(args.source_root.resolve(), manifest, args.minimum_files, selected)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "head": result["upstream_source"]["commit"],
        "files": result["upstream_source"]["lean_files_checked_out"],
        "parsed": result["distinct_modules_parsed"],
        "roots": [{"root": x["root"], "modules": x["modules"],
                   "bytes": x["module_source_bytes"], "imports": x["import_edges"]}
                  for x in result["roots"]],
        "proof_term_data": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
