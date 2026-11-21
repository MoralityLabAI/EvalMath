"""Pinned source index for RH witness predicates; declarations and textual uses."""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import argparse
import json
import re
import subprocess

from spiral_ln.rh_distillation import anchor_audit, git_blob_sha

BASE = Path(__file__).resolve().parents[2] / "gyms/RHProofDistillation"
PIN = "f150e02623b1e2bbe1f1da8eab5ffee5e930a6a3"
TERMS = ("SizeWindows", "SmallCosts", "GrowthInequalityDataExists",
         "ReducedGrowthInequalityDataExists", "ChainTied", "CoreAtH",
         "RestSize", "Chain2aSizesModelEv", "FamCoreConstantBounds")
DECL = re.compile(r"^\s*(?:(?:private|protected|noncomputable)\s+)*(?:theorem|lemma|def|structure|class|abbrev|instance)\s+([^\s(:]+)")
BOUNDARIES = {t: re.compile(r"(?<![\w'])" + re.escape(t) + r"(?![\w'])") for t in TERMS}


def verify(root: Path, minimum: int = 175187) -> dict:
    head = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    if head != PIN:
        raise ValueError("unexpected upstream commit " + head)
    count = sum(1 for _ in (root / "src").rglob("*.lean"))
    if count < minimum:
        raise ValueError(f"incomplete source: {count}")
    manifest = json.loads((BASE / "anchors.json").read_text())
    anchors = anchor_audit(root, manifest)
    if any(a["status"] != "match" for a in anchors):
        raise ValueError("pinned source anchor differs")
    return {"source_commit": head, "lean_source_files": count, "pinned_anchors": len(anchors)}


def scan(root: Path, limit: int = 300) -> dict:
    if limit < 1:
        raise ValueError("invalid site limit")
    index = {t: {"total": 0, "files": Counter(), "sites": [], "declarations": []} for t in TERMS}
    matching = 0
    for file in sorted((root / "src").rglob("*.lean")):
        raw = file.read_bytes()
        if not any(t.encode() in raw for t in TERMS):
            continue
        matching += 1
        relative = file.relative_to(root).as_posix()
        blob = git_blob_sha(raw)
        current = None
        for line_number, line in enumerate(raw.decode("utf-8").splitlines(), 1):
            match = DECL.match(line)
            if match:
                current = match.group(1)
            for term, pattern in BOUNDARIES.items():
                if not pattern.search(line):
                    continue
                a = index[term]
                a["total"] += 1
                a["files"][relative] += 1
                kind = "declaration" if match and (current == term or current.endswith("." + term)) else "use"
                site = {"path": relative, "line": line_number, "blob": blob,
                        "kind": kind, "nearest_decl": current}
                if kind == "declaration":
                    a["declarations"].append(site)
                if len(a["sites"]) < limit:
                    a["sites"].append(site)
    result = {}
    for term, a in index.items():
        top = sorted(a["files"].items(), key=lambda kv: (-kv[1], kv[0]))
        result[term] = {
            "total_hits": a["total"], "file_count": len(a["files"]),
            "declarations": a["declarations"],
            "top_files": [{"path": p, "hits": v} for p, v in top[:30]],
            "sample_sites": a["sites"], "sample_truncated": len(a["sites"]) < a["total"],
        }
    return {"schema_version": 1, "mode": "pinned_source_symbol_occurrences",
            "proof_term_data": False, "matching_files": matching, "symbols": result,
            "caveat": "Textual sites and nearest declarations are not proof-term dependencies"}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-root", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    root = args.source_root.resolve()
    result = scan(root)
    result["identity"] = verify(root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "identity": result["identity"], "matching_files": result["matching_files"],
        "symbols": {k: {"hits": v["total_hits"], "declarations": len(v["declarations"]),
                        "files": v["file_count"]} for k, v in result["symbols"].items()},
        "proof_term_data": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
