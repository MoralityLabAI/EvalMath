"""Restore a *small, source-pinned* subset of the RH published Lean cache.

This uses the author's unlicensed source only from a temporary upstream
checkout. Published compiled artifacts are SHA-verified against the
community's pinned manifest, then imported by Lean v4.33.1 for direct
proof-expression references. This is a cache-derived inspection, NOT an
independent full clean build or a proof of RH.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import urllib.request

from spiral_ln.rh_dependency import build_probe, run_lean, pinned_mirror
from spiral_ln.rh_full_closure import ImportGraph, module_name

BASE = Path(__file__).resolve().parents[2] / "gyms" / "RHProofDistillation"
CACHE_URL = ("https://rh-cache.taucetiproject.org/bootstrap/"
             "e50d09817ad81469f737e8f637561e6ccf86c670/modules.jsonl.gz")
MANIFEST_SHA256 = "292caa386a620d935cfc736b56fcceaab9fe7073086693b62e899c1ee4725f04"
REPOSITORY = "leanprover-community/riemann-hypothesis"
MAP_FORMAT = "2026-03-17"


def load_restore_script(root: Path):
    script = root / "scripts" / "restore-cache.py"
    if not script.is_file():
        raise ValueError("missing original community cache verifier")
    spec = importlib.util.spec_from_file_location("rh_community_cache_restorer", script)
    if spec is None or spec.loader is None:
        raise ValueError("could not load community cache verifier")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if module.MANIFEST_SHA256 != MANIFEST_SHA256 or module.URL != CACHE_URL:
        raise ValueError("cache verifier manifest identity changed")
    return module


def verified_manifest(restorer, *, raw: bytes | None = None) -> list[list[str]]:
    if raw is None:
        request = urllib.request.Request(CACHE_URL, headers={"User-Agent": "EvalMath-RH-Distillation/1.0"})
        with urllib.request.urlopen(request, timeout=90) as response:
            raw = response.read(64 * 1024 * 1024 + 1)
    if len(raw) > 64 * 1024 * 1024:
        raise ValueError("pinned cache manifest exceeded 64 MiB limit")
    if hashlib.sha256(raw).hexdigest() != MANIFEST_SHA256:
        raise ValueError("pinned manifest SHA256 mismatch")
    return restorer.manifest_rows(raw)


def selected_rows(rows: list[list[str]], modules: set[str]) -> list[list[str]]:
    found: dict[str, list[str]] = {}
    for row in rows:
        name = row[0]
        if name in modules:
            if name in found:
                raise ValueError(f"duplicate pinned artifact for {name}")
            found[name] = row
    missing = sorted(modules - set(found))
    if missing:
        raise ValueError(f"missing compiled upstream modules: {missing[:12]}")
    return [found[name] for name in sorted(modules)]


def cache_map(rows: list[list[str]]) -> str:
    """Stock Lake mapping file for the exact selected input/artifact pairs."""
    lines = [json.dumps(MAP_FORMAT)]
    lines.extend(json.dumps([entry[1], entry[2]], separators=(",", ":")) for entry in rows)
    return "\n".join(lines) + "\n"


def assure_disk(root: Path, count: int, max_modules: int, min_free_gib: int) -> int:
    if count == 0 or count > max_modules:
        raise ValueError(f"subset size {count} exceeds allowed 1..{max_modules}")
    free = shutil.disk_usage(root).free
    if free < min_free_gib * 1024**3:
        raise ValueError(f"only {free} bytes free; required {min_free_gib} GiB")
    return free


def restore_subset(root: Path, rows: list[list[str]], restorer, *, workers: int = 4) -> dict:
    """Fetch and verify ONLY requested cache artifacts, then stock-leantar extract."""
    cache = root / ".lake" / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    free_before = assure_disk(root, len(rows), max_modules=600, min_free_gib=7)
    mapping = root / ".lake" / "rh-subset-outputs.jsonl"
    mapping.write_text(cache_map(rows), encoding="utf-8")
    env = os.environ.copy()
    for key in list(env):
        if key.startswith(("AWS_", "CLOUDFLARE_", "CF_")) or key in ("LAKE_CACHE_KEY", "GITHUB_TOKEN", "GH_TOKEN"):
            env.pop(key)
    env.update(LAKE_CONFIG=str(root / "lakefile.toml"), LAKE_CACHE_DIR=str(cache),
               LAKE_ARTIFACT_CACHE="true", LAKE_RESTORE_ARTIFACTS="true",
               ELAN_TOOLCHAIN="leanprover/lean4:v4.33.1", LEAN_ABORT_ON_PANIC="1")
    subprocess.run(["lake", "-q", "cache", "get", str(mapping),
                    "--repo", REPOSITORY], cwd=root, env=env,
                   check=True, timeout=1200)
    jobs = restorer.restore_jobs(root, cache, rows)
    for job in jobs:
        for base in job["base"]:
            Path(base).mkdir(parents=True, exist_ok=True)
    env["RUST_MIN_STACK"] = str(max(int(env.get("RUST_MIN_STACK", "0")), 8388608))
    lean = Path(subprocess.check_output(["elan", "which", "lean"], cwd=root,
                                        env=env, text=True).strip())
    subprocess.run([str(lean.with_name("leantar")), "--jobs", str(workers),
                    "-f", "-x", "-j", "-"], input=json.dumps(jobs),
                   cwd=root, env=env, text=True, check=True, timeout=900)
    free_after = shutil.disk_usage(root).free
    return {"modules_restored": len(rows), "free_before": free_before,
            "free_after": free_after, "manifest_sha256": MANIFEST_SHA256,
            "artifacts_hash_checked": len(rows), "cache_source": CACHE_URL}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--anchors", nargs="+", default=["analytic_window", "weighted_bound"])
    parser.add_argument("--max-modules", type=int, default=600)
    parser.add_argument("--max-depth", type=int, default=2)
    parser.add_argument("--max-nodes", type=int, default=120)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--plan-only", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.source_root.resolve()
    manifest = json.loads((BASE / "anchors.json").read_text(encoding="utf-8"))
    identity = pinned_mirror(root, manifest)
    ids = {a["id"]: a for a in manifest["anchors"]}
    if any(key not in ids for key in args.anchors):
        parser.error(f"unknown anchor: {args.anchors}")
    anchors = [ids[key] for key in args.anchors]
    graph = ImportGraph(root / "src")
    modules = set()
    closures = {}
    for anchor in anchors:
        module = module_name(anchor["path"])
        result = graph.closure(module)
        if result["unresolved_internal_imports"]:
            raise ValueError(f"source closure missing internal imports: {result['unresolved_internal_imports'][:10]}")
        modules.update(result["module_set"])
        closures[anchor["id"]] = {"module": module, "closure_modules": result["modules"],
                                  "edge_stream_sha256": result["edge_stream_sha256"]}
    # Cache material is read only after confirming that the target slice is bounded.
    if not modules or len(modules) > args.max_modules:
        raise ValueError(f"union of source modules {len(modules)} > cap {args.max_modules}")
    restorer = load_restore_script(root)
    all_rows = verified_manifest(restorer)
    rows = selected_rows(all_rows, modules)
    receipt = {
        "schema": 1, "source_commit": identity["commit"],
        "source_anchors_matched": identity["six_anchors_match"],
        "source_closures": closures,
        "required_modules": len(rows),
        "cache_manifest_sha256": MANIFEST_SHA256,
        "published_cache_verifier": "original upstream scripts/restore-cache.py",
        "proof_term_data": False,
        "environment": "upstream Lean 4.33.1 compiled cache",
        "verification_scope": "published-cache bytes; independent rebuild out of scope",
    }
    if args.plan_only:
        receipt["status"] = "validated_cache_plan"
    else:
        assure_disk(root, len(rows), args.max_modules, min_free_gib=7)
        receipt["restore"] = restore_subset(root, rows, restorer, workers=args.workers)
        dependencies = {}
        for anchor in anchors:
            import_module = module_name(anchor["path"])
            src = build_probe([import_module], [anchor["declaration"]],
                              depth=args.max_depth, max_nodes=args.max_nodes,
                              prefixes=["UpperTheory.", "Deduction.", "Formalism."])
            result = run_lean(src, root, timeout=args.timeout)
            proof_root = next((n for n in result["nodes"] if n["name"] == anchor["declaration"]), None)
            if proof_root is None or proof_root["kind"] == "missing":
                raise RuntimeError(f"source-pinned theorem not present in compiled env: {anchor['declaration']}")
            result["source_anchor"] = anchor["id"]
            dependencies[anchor["id"]] = result
        receipt["proofs"] = dependencies
        receipt["proof_term_data"] = True
        receipt["status"] = "source_pinned_compiled_proof_expression"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    print(json.dumps({"status": receipt["status"], "source_commit": receipt["source_commit"],
                      "required_modules": receipt["required_modules"],
                      "proof_term_data": receipt["proof_term_data"],
                      "roots": {k: v["source_closures"] if False else v["closure_modules"]
                                for k, v in closures.items()} if False else
                               {k: v["closure_modules"] for k, v in closures.items()}},
                     sort_keys=True))


if __name__ == "__main__":
    main()
