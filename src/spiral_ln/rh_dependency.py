"""Inspect direct theorem/definition constant references from compiled Lean expressions.

Scope: a bounded graph of direct elaborated Expr references, not a minimal
dependency proof. Upstream source identity is verified before execution.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import subprocess
import tempfile

from spiral_ln.rh_distillation import anchor_audit

HERE = Path(__file__).resolve().parents[2] / "gyms" / "RHProofDistillation"
NAME = re.compile(r"^[\w.]+$", re.UNICODE)
RECORD = "RHDEP1\t"
END = "RHDEPEND\t"


def parse_output(stdout: str) -> dict:
    nodes, footer, seen = [], None, set()
    for line in stdout.splitlines():
        if line.startswith(RECORD):
            item = json.loads(line[len(RECORD):])
            name = item["name"]
            if name in seen:
                raise ValueError(f"duplicate constant: {name}")
            if item["kind"] not in {
                "axiom", "definition", "theorem", "opaque", "quotient",
                "inductive", "constructor", "recursor", "missing",
            }:
                raise ValueError(f"unknown declaration type: {item['kind']}")
            if any(not isinstance(x, str) for k in ("type_refs", "value_refs") for x in item[k]):
                raise ValueError(f"invalid refs for {name}")
            seen.add(name)
            nodes.append(item)
        elif line.startswith(END):
            if footer is not None:
                raise ValueError("multiple probe footers")
            footer = json.loads(line[len(END):])
    if footer is None:
        raise ValueError("no completion footer from Lean")
    if len(nodes) != footer["visited"]:
        raise ValueError("visited count disagrees with emitted nodes")
    edges = sorted(
        ({"from": node["name"], "to": dep, "channel": channel}
         for node in nodes for channel, field in
         (("type", "type_refs"), ("value", "value_refs"))
         for dep in node[field]),
        key=lambda e: (e["from"], e["channel"], e["to"]),
    )
    return {
        "mode": "lean_elaborated_direct_constant_refs",
        "proof_term_data": True,
        "nodes": sorted(nodes, key=lambda e: e["name"]),
        "edges": edges,
        "scope": footer,
        "kinds": dict(sorted(Counter(n["kind"] for n in nodes).items())),
    }


def validate_names(names: list[str]) -> None:
    if not names or any(not NAME.fullmatch(n) for n in names):
        raise ValueError("names must be nonempty qualified Lean identifiers")


def build_probe(imports: list[str], roots: list[str], depth: int,
                max_nodes: int, prefixes: list[str], toy: bool = False) -> str:
    validate_names(roots)
    validate_names(imports or ["Lean"])
    if not prefixes or any(not NAME.fullmatch(p) for p in prefixes):
        raise ValueError("safe expansion prefixes required")
    if depth < 0 or max_nodes <= 0:
        raise ValueError("invalid graph bounds")
    probe = (HERE / "lean" / "ProofDependencies.lean").read_text(encoding="utf-8")
    if not probe.startswith("import Lean\n"):
        raise ValueError("probe must start with import Lean")
    header = "\n".join("import " + name for name in sorted(set(["Lean"] + imports)))
    body = probe.split("\n", 1)[1]
    fixtures = ("\nnamespace RHGraphToy\n"
                "theorem upstream : True := True.intro\n"
                "theorem bridge : True := upstream\n"
                "end RHGraphToy\n") if toy else ""
    quoted_roots = ", ".join(chr(96) * 2 + name for name in roots)
    quoted_prefixes = ", ".join(json.dumps(p, ensure_ascii=False) for p in prefixes)
    cmd = ("\nopen Lean Elab Command\nrun_cmd do\n"
           "  let env \u2190 getEnv\n"
           f"  liftIO <| RHDepProbe.emit env #[{quoted_roots}] {depth} {max_nodes} #[{quoted_prefixes}]\n")
    return header + "\n" + body + fixtures + cmd


def run_lean(source: str, cwd: Path, timeout: int) -> dict:
    if not cwd.is_dir():
        raise ValueError(f"Lean workspace missing: {cwd}")
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".lean",
                                     prefix="RHDepProbe_", dir=cwd, delete=False) as f:
        f.write(source)
        path = Path(f.name)
    try:
        proc = subprocess.run(["lake", "env", "lean", path.name], cwd=cwd, text=True,
                              capture_output=True, timeout=timeout, check=False)
    finally:
        path.unlink(missing_ok=True)
    if proc.returncode:
        raise RuntimeError(f"Lean exited {proc.returncode}: {(proc.stdout + proc.stderr)[-2400:]}")
    return parse_output(proc.stdout)


def pinned_mirror(root: Path, manifest: dict) -> dict:
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root,
                         capture_output=True, text=True, check=True).stdout.strip()
    if sha != manifest["mirror_commit"]:
        raise ValueError(f"mirror HEAD mismatch: {sha} vs {manifest['mirror_commit']}")
    audit = anchor_audit(root, manifest)
    if any(x["status"] != "match" for x in audit):
        raise ValueError(f"missing or mutated upstream anchors: {audit}")
    return {"commit": sha, "six_anchors_match": True}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="action", required=True)
    smoke = sub.add_parser("smoke", help="test a direct proof reference with EvalMath Lean")
    smoke.add_argument("--lean-cwd", type=Path, default=Path("lean"))
    smoke.add_argument("--timeout", type=int, default=120)
    smoke.add_argument("--output", type=Path)
    upstream = sub.add_parser("upstream", help="inspect the pinned full upstream proof")
    upstream.add_argument("--source-root", type=Path, required=True)
    upstream.add_argument("--anchors", nargs="+", default=["weighted_bound"])
    upstream.add_argument("--max-depth", type=int, default=2)
    upstream.add_argument("--max-nodes", type=int, default=120)
    upstream.add_argument("--prefixes", nargs="+", default=["UpperTheory.", "Deduction.", "Formalism."])
    upstream.add_argument("--emit-script", type=Path, help="write the Lean script only")
    upstream.add_argument("--output", type=Path)
    upstream.add_argument("--timeout", type=int, default=1800)
    args = ap.parse_args()
    if args.action == "smoke":
        src = build_probe([], ["RHGraphToy.bridge"], 2, 12, ["RHGraphToy."], toy=True)
        result = run_lean(src, args.lean_cwd.resolve(), timeout=args.timeout)
        node = next((n for n in result["nodes"] if n["name"] == "RHGraphToy.bridge"), None)
        if node is None or "RHGraphToy.upstream" not in node["value_refs"]:
            raise RuntimeError(f"missing compiled proof reference: {node}")
        result["smoke_passed"] = True
        result["source_scope"] = "small_local_toy_only"
    else:
        root = args.source_root.resolve()
        manifest = json.loads((HERE / "anchors.json").read_text(encoding="utf-8"))
        receipt = pinned_mirror(root, manifest)
        ids = {a["id"]: a for a in manifest["anchors"]}
        if any(i not in ids for i in args.anchors):
            ap.error(f"unknown anchor: {args.anchors}")
        anchors = [ids[i] for i in args.anchors]
        imports = [a["path"].removeprefix("src/").removesuffix(".lean").replace("/", ".") for a in anchors]
        roots = [a["declaration"] for a in anchors]
        src = build_probe(imports, roots, args.max_depth, args.max_nodes, args.prefixes)
        if args.emit_script:
            args.emit_script.parent.mkdir(parents=True, exist_ok=True)
            args.emit_script.write_text(src, encoding="utf-8")
            result = {"mode": "script_only", "proof_term_data": False,
                      "path": str(args.emit_script), "anchors": roots, "provenance": receipt}
        else:
            result = run_lean(src, root, timeout=args.timeout)
            result["source_scope"] = "pinned_upstream_environment"
            result["anchors"] = roots
            result["provenance"] = receipt
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded)


if __name__ == "__main__":
    main()
