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
         "RestSize", "Chain2aSizesModelEv", "FamCoreConstantBounds",
    "SizesAt", "PlacesAt", "adm5", "adm6", "adm7",
    "FamilyPropTwoSix", "FamilyCharacterSumBounds", "SizesFe", "TOPF",
    "proposition_eleven_two_at_scale", "proposition_eleven_two_along_family",
    "proposition_eleven_two_small_epsilon", "ChainCore")
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
    result["gates"] = audit_gate_sources(root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "identity": result["identity"], "matching_files": result["matching_files"],
        "symbols": {k: {"hits": v["total_hits"], "declarations": len(v["declarations"]),
                        "files": v["file_count"]} for k, v in result["symbols"].items()},
        "proof_term_data": False,
    }, sort_keys=True))



# Source-observed witness transitions. No theorem proof terms are re-exported.
GATE_FILES = {
    "family": ("src/Formalism/SharpRestriction/GlobalSchurBounds/RamificationTwoAndConjugationAtQAndD.lean",
               "1c1495ef81c77fa96f3c1a70106c1da9e24c0c5d"),
    "cost": ("src/Development/AutomorphicArithmetic/ConductorsKronecker/CostPropositionBasicBound.lean",
             "99e6384355aea45f0b5fe4726b4154444e7e82e1"),
    "split": ("src/Formalism/SizeWindowBrackets/ChainSlopeWindows/PChain.lean",
              "57559bc6dedbabbac7365c9f31fbbab09164edca"),
}
GATE_CHECKS = {
    "windows": ("family", ("SizesAt D s", "PlacesAt D s", "ThickSetMeanBounds.SizeWindows")),
    "smallCosts": ("family", ("SizesAt D s", "LargeX s.x", "ThickSetMeanBounds.SmallCosts")),
    "proposition_eleven_two_at_scale": ("family", (
        "adm5 D s", "adm6 D s", "adm7 D s", "SizesAt D s", "PlacesAt D s",
        "ThickSetMeanBounds.SmallCosts", "ThickSetMeanBounds.SizeWindows",
        "cost_proposition_at_scale")),
    "proposition_eleven_two_along_family": ("family", (
        "adm5", "adm6", "SizesAt", "PlacesAt", "adm7",
        "proposition_eleven_two_at_scale")),
    "proposition_eleven_two_small_epsilon": ("family", (
        "FamilyPropTwoSix", "FamilyCharacterSumBounds", "SizesFe", "TOPF")),
    "cost_proposition_at_scale": ("cost", (
        "GrowthInequalityHypotheses", "SmallCosts", "SizeWindows",
        "proposition_size_bound", "card_mul_delta_le_err")),
    "size_windows_split": ("split", ("SizeWindows", "RestSize")),
}


def audit_gate_sources(root: Path) -> dict:
    sources, file_ids = {}, {}
    for key, (name, expected_sha) in GATE_FILES.items():
        raw = (root / name).read_bytes()
        if git_blob_sha(raw) != expected_sha:
            raise ValueError("upstream gate source blob mismatch: " + name)
        sources[key] = raw.decode("utf-8")
        file_ids[key] = {"path": name, "git_blob": expected_sha}
    sites = {}
    for name, (file_key, needles) in GATE_CHECKS.items():
        text = sources[file_key]
        marker = "theorem " + name + " "
        start = text.find(marker)
        if start < 0:
            raise ValueError("upstream theorem missing: " + name)
        stop = text.find("\ntheorem ", start + len(marker))
        body = text[start:stop if stop >= 0 else len(text)]
        absent = [needle for needle in needles if needle not in body]
        if absent:
            raise ValueError(f"upstream theorem {name} missing markers: {absent}")
        sites[name] = {"path": file_ids[file_key]["path"],
                       "git_blob": file_ids[file_key]["git_blob"],
                       "start_line": text[:start].count("\n") + 1,
                       "observed_text_calls": list(needles)}
    return {"mode": "pinned_source_text_calls_only", "proof_term_data": False,
            "files": file_ids, "gates": sites}

if __name__ == "__main__":
    main()
