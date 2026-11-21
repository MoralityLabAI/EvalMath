"""Source-only, provenance-pinned audit of the RH core_gm proof boundary."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

from spiral_ln.rh_dependency import pinned_mirror
from spiral_ln.rh_distillation import git_blob_sha, parse_imports, walk_imports

BASE = Path(__file__).resolve().parents[2] / "gyms" / "RHProofDistillation"
PREFIX = Path("src/Development/AutomorphicArithmetic")
CORE = PREFIX / "PrimitiveCosets/CoreGm.lean"
PREDICATE = PREFIX / "PrimitiveCosets/CoreAtH.lean"
PREDICATE_SHA = "0ba3621036f19146e7e67fa9c0e8a1c38661a097"
REQUIRED = {
    "log_derivative": "HostAddCharCompatible H ell",
    "x_match": "Dd.x = x",
    "epsilon_match": "Dd.ε = eps",
    "divisorial_slack": "C.eDiv ≤ eD",
    "loss_slack": "C.eLoss ≤ eL",
    "geometric_slack": "C.cHH ≤ cHH",
    "index_coverage": "∀ s ∈ φ.A0, ∃ u, tr u = s",
    "geometric_identification": "IdentU Dd tr",
    "size_data": "SizeData₂ Dd C Xpp",
    "error_window": "ErrWindows Dd C Xpp",
    "bounded_numbers": "BNBoundsU Dd T2",
    "character_size": "SizesA φ.A0 TT T2",
    "thin_scales": "ThinScales (arith H) ell X' θ",
    "cost_windows": "CostWindows x (fPl φ.A)",
    "rest_size": "RestSize eps x",
    "surviving_chars": "∀ s ∈ T2, s ∈ φ.A0",
}
BRIDGES = {
    "PrimitiveCosets/WindowInequalityOfArtinInputs.lean": ["core_gm", "zeroFreeOn_of_tiedWin"],
    "PrimitiveCosets/LevelGmLeOnFamilyScales.lean": ["windowInequality_of_artinInputs", "zeroFreeOn_of_core"],
    "PrimitiveCosets/Imports.lean": ["Deduction.zeroFree_of_rpow_window", "UpperTheory.Comparison₂.level_family"],
    "DedekindLFunctions/LandauTheorems/ZeroFreeOfRpowWindow.lean": ["lemmaL", "windowHyp_of_rpow"],
    "DedekindLFunctions/LandauTheorems/ChCore.lean": ["CharacterBalanceMoves.core", "proposition_size_bound", "derivative_integral_all"],
    "DedekindLFunctions/LandauTheorems/ChTop.lean": ["ch_top_main_eq", "each_unit_bound_statement", "errX5at_le"],
}

def match_name(text: str, name: str) -> bool:
    return re.search(r"(?<![\w'])" + re.escape(name) + r"(?![\w'])", text) is not None

def region(src: str, start: str, stop: str) -> str:
    i = src.find(start)
    if i < 0:
        raise ValueError("missing declaration: " + start)
    j = src.find(stop, i + len(start))
    if j < 0:
        raise ValueError("missing boundary: " + stop)
    return src[i:j]

def verified_file(root: Path, path: Path, expected: str | None = None) -> tuple[str, dict]:
    file = root / path
    if not file.is_file():
        raise ValueError("pinned source missing: " + str(path))
    raw = file.read_bytes()
    blob = git_blob_sha(raw)
    if expected and blob != expected:
        raise ValueError("pinned Git blob differs: " + str(path))
    text = raw.decode("utf-8")
    return text, {"path": str(path), "git_blob": blob,
                  "sha256": hashlib.sha256(raw).hexdigest(),
                  "bytes": len(raw), "imports": parse_imports(text)}

def audit(root: Path, manifest: dict, ledger: dict) -> dict:
    identity = pinned_mirror(root, manifest)
    if ledger["source_commit"] != manifest["mirror_commit"]:
        raise ValueError("ledger and mirror source pins differ")
    if Path(ledger["caller_file"]) != CORE:
        raise ValueError("unexpected source declaration")
    anchor = next(a for a in manifest["anchors"] if a["id"] == "weighted_bound")
    if ledger["caller_blob"] != anchor["blob_sha"]:
        raise ValueError("source ledger disagrees with pinned anchor")
    caller, rec = verified_file(root, CORE, ledger["caller_blob"])
    body = region(caller, "theorem UpperTheory.Comparison₂.core_gm", "\nend")
    records = [rec]
    calls = []
    for dependency in ledger["edges"]:
        path = PREFIX / dependency["source"]
        txt, evidence = verified_file(root, path, dependency["blob"])
        symbol = dependency["callee"].rsplit(".", 1)[-1]
        if not match_name(body, symbol) or not match_name(txt, symbol):
            raise ValueError("missing source proof reference: " + dependency["callee"])
        records.append(evidence)
        calls.append({"from": ledger["caller"], "to": dependency["callee"],
                      "source": str(path), "channel": "source_call",
                      "blob": evidence["git_blob"]})
    definition, predicate_record = verified_file(root, PREDICATE, PREDICATE_SHA)
    records.append(predicate_record)
    contract = region(definition, "def CoreAtH ", "\ndef pcOf ")
    for label, fragment in REQUIRED.items():
        if fragment not in contract:
            raise ValueError("CoreAtH field changed or missing: " + label)
    bridges = []
    for name, needles in BRIDGES.items():
        path = PREFIX / name
        src, item = verified_file(root, path)
        if not all(match_name(src, n) for n in needles):
            raise ValueError("bridge call missing: " + name)
        records.append(item)
        bridges.append({"path": str(path), "sha256": item["sha256"],
                        "calls": needles})
    for item in ledger["downstream"]:
        path = PREFIX / item["source"]
        src, verified = verified_file(root, path, item["blob"])
        if not match_name(src, item["theorem"].rsplit(".", 1)[-1]):
            raise ValueError("downstream declaration missing: " + item["theorem"])
    graph = walk_imports(root / "src",
                         ["Development.AutomorphicArithmetic.PrimitiveCosets.CoreGm"], 120)
    unique = {r["path"]: r for r in records}
    return {
        "schema_version": 1,
        "mode": "pinned_upstream_source_only",
        "proof_term_data": False,
        "compiled_olean_used": False,
        "identity": identity,
        "source_files": [unique[k] for k in sorted(unique)],
        "direct_call_sites": calls,
        "core_at_h_obligations": list(REQUIRED),
        "core_at_h_contract_sha256": hashlib.sha256(contract.encode()).hexdigest(),
        "verified_bridges": bridges,
        "import_graph": {
            "visited_modules": graph["visited_modules"],
            "edges": graph["import_edges"], "truncated": graph["truncated"],
            "unavailable_internal": graph["unresolved_internal_imports"],
            "external": graph["external_imports"],
        },
        "limitations": "Source call graph; missing imports may reflect sparse checkout. No proof-term closure.",
    }

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads((BASE / "anchors.json").read_text())
    ledger = json.loads((BASE / "core_gm_sources.json").read_text())
    receipt = audit(args.source_root.resolve(), manifest, ledger)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"commit": receipt["identity"]["commit"],
                      "files": len(receipt["source_files"]),
                      "direct_calls": len(receipt["direct_call_sites"]),
                      "obligations": len(receipt["core_at_h_obligations"]),
                      "bridges": len(receipt["verified_bridges"]),
                      "imports": receipt["import_graph"]["visited_modules"],
                      "proof_term_data": False}, sort_keys=True))

if __name__ == "__main__":
    main()
