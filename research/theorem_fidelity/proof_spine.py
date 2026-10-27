"""Pin and inspect the *source-level* proof spine of OAI Unique Games.

This protects a selected set of declarations/imports against drift and simple
text spoofing. It does not check Lean elaboration, dependencies beyond these
paths, theorem correctness, or the complete axiom footprint.
"""
import argparse
import json
import re
from pathlib import Path
from urllib.request import urlopen

from upstream_contract import blob_sha, source_without_noncode

ROOT = Path(__file__).resolve().parent
BASE = "lean/OAI/Computability/UniqueGames/"

# Each anchor matches executable source after line/block comments and strings
# have been masked. Exact blob pins prevent silently changing these witnesses.
ANCHORS = {
    "Theorem.lean": (
        r"\btheorem\s+theorem11\s*\(",
        r"\btheorem\s+exists_binaryGapReduction\s*\(",
        r"ParameterSelection\.exists_outerParameters\s+ε\s+δ\s+hε\s+hδ",
        r"Decoder\.MatrixGap\.exists_parameters\s+P\.pStar\s+P\.pStar_pos",
        r"FromMatrixGap\.reduction\s+P\s+M",
        r"Theorem\.exists_binaryGapReduction\s+ε\s+δ\s+hε\s+hεhalf\s+hδ\s+hδhalf",
    ),
    "Reduction/FromMatrixGap.lean": (
        r"\bdef\s+reduction\b",
        r"MachineOutputContract\.BinaryGapReduction\s+ε\s+δ\s*:=\s*by",
        r"MachineSingleOrbitBridge\.computableInPolyTime",
        r"Outer\.BinaryParityReduction\.exists_reduction",
    ),
    "Reduction/ParameterSelection.lean": (
        r"\btheorem\s+exists_outerParameters\s*\(",
        r"\bdef\s+pStar\s*:",
    ),
    "Decoding/MatrixGapFromInverseLemmas.lean": (
        r"\btheorem\s+parameters_of_inverse\s*\(",
        r"\btheorem\s+exists_parameters\s*\(",
        r"Gadget\.exists_split_gadget\s+p\s+hp",
        r"parameters_of_inverse\s+Inverse\.ShortcodeTheorem\.inversePrinciple\s+p\s+hp",
    ),
    "Inverse/ShortcodeTheorem.lean": (
        r"\btheorem\s+inversePrinciple\s*:",
        r"ShortcodeFromGrassmann\.inversePrinciple_of_expansion\s+KMSExpansion\.kms_expansion",
    ),
    "Inverse/ShortcodeFromGrassmannLemmas.lean": (
        r"\btheorem\s+inversePrinciple_of_expansion\s*\(",
        r"inversePrinciple_of_expansion_and_chart\s+hKMS\s+chartFiberRetention",
    ),
    "Inverse/KMSAnalyticHybridEnergyLemmas.lean": (
        r"\btheorem\s+kms_expansion\s*:\s*KMS\.ExpansionPrinciple",
        r"\btheorem\s+lifted_fourth_moment_bound\b",
        r"KMSMomentTheorem\.lifted_fourth_moment_bound\s+r\s+ε",
    ),
    "Gadgets/Final.lean": (
        r"\btheorem\s+exists_split_gadget\s*\(",
        r"exists_actual_gadget\s+p\s+hp",
    ),
}

# Direct edges only. Other paths have transitive imports that are outside this
# selected spine; absence from this mapping never constitutes a proof of closure.
EDGES = {
    "Theorem.lean": (
        "Decoding/MatrixGapFromInverseLemmas.lean",
        "Reduction/FromMatrixGap.lean",
    ),
    "Decoding/MatrixGapFromInverseLemmas.lean": (
        "Gadgets/Final.lean",
        "Inverse/ShortcodeTheorem.lean",
    ),
    "Inverse/ShortcodeTheorem.lean": (
        "Inverse/KMSAnalyticHybridEnergyLemmas.lean",
        "Inverse/ShortcodeFromGrassmannLemmas.lean",
    ),
}


def paths_and_pin(pin: dict) -> dict[str, str]:
    if pin.get("repository") != "openai/math":
        raise ValueError("unexpected upstream repository")
    if not re.fullmatch(r"[0-9a-f]{40}", pin.get("commit", "")):
        raise ValueError("expected immutable 40-character upstream commit SHA")
    paths = pin["sources"] | pin["environment"]
    if len(paths) != len(pin["sources"]) + len(pin["environment"]):
        raise ValueError("duplicate source and environment paths")
    if {path.removeprefix(BASE) for path in pin["sources"]} != set(ANCHORS):
        raise ValueError("the pinned proof modules do not match the declared anchors")
    return paths


def active_imports(source: str) -> set[str]:
    """Extract direct module imports from comment/string-stripped Lean text."""
    clean = source_without_noncode(source)
    return set(re.findall(r"(?m)^[ \t]*import[ \t]+([A-Za-z0-9_.]+)[ \t]*$", clean))


def active_placeholders(source: str) -> bool:
    code = source_without_noncode(source)
    return bool(re.search(r"\b(?:sorry|admit)\b", code))


def audit(sources: dict[str, bytes], pin: dict) -> dict:
    paths = paths_and_pin(pin)
    if set(sources) != set(paths):
        raise ValueError("source set differs from pinned source and environment set")
    for path, expected in paths.items():
        if blob_sha(sources[path]) != expected:
            raise ValueError(f"upstream Git blob hash mismatch: {path}")
    if sources["lean/lean-toolchain"].decode().strip() != pin["expected_toolchain"]:
        raise ValueError("upstream Lean toolchain changed")
    lake = json.loads(sources["lean/lake-manifest.json"])
    mathlib = [p for p in lake["packages"] if p.get("name") == "mathlib"]
    if len(mathlib) != 1 or mathlib[0].get("rev") != pin["expected_mathlib"]:
        raise ValueError("upstream Mathlib revision changed")
    checks = 0
    direct_edges = 0
    for short_path, patterns in ANCHORS.items():
        path = BASE + short_path
        source = sources[path].decode("utf-8")
        code = source_without_noncode(source)
        if active_placeholders(source):
            raise ValueError(f"active sorry/admit in selected proof-spine module: {path}")
        for pattern in patterns:
            if not re.search(pattern, code):
                raise ValueError(f"missing active proof-spine declaration/reference: {path}: {pattern}")
            checks += 1
        imports = active_imports(source)
        for dependency in EDGES.get(short_path, ()):
            mod = "OAI.Computability.UniqueGames." + dependency.removesuffix(".lean").replace("/", ".")
            if mod not in imports:
                raise ValueError(f"missing active direct import {mod} in {path}")
            direct_edges += 1
    return {
        "commit": pin["commit"],
        "source_blobs_verified": len(pin["sources"]),
        "build_environment_blobs_verified": len(pin["environment"]),
        "proof_reference_anchors": checks,
        "direct_module_import_edges": direct_edges,
        "selected_source_active_placeholders": 0,
        "scope": "pinned source proof spine; independent Lean compilation remains open",
    }


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--fetch", action="store_true")
    group.add_argument("--snapshot", type=Path)
    args = parser.parse_args()
    pin = json.loads((ROOT / "proof_spine_pin.json").read_text("utf-8"))
    paths = paths_and_pin(pin)
    source = {}
    for path in paths:
        if args.fetch:
            url = f'https://raw.githubusercontent.com/{pin["repository"]}/{pin["commit"]}/{path}'
            with urlopen(url, timeout=35) as stream:
                source[path] = stream.read()
        else:
            source[path] = (args.snapshot / path).read_bytes()
    print(json.dumps(audit(source, pin), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
