"""Fresh Lean replay of the module, teacher curriculum and bounded candidate pack."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shlex
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spiral_ln.rh_compactification_gym import (
    ALLOWED_AXIOMS, BASE, LEAN_SOURCE, NAMESPACE, LeanChecker,
    json_text, load_bundle, parse_axioms, sha256, verify_teachers,
)
from spiral_ln.rh_compactification_pack import PACK, replay_pack


def run(checker: LeanChecker) -> dict:
    source = LEAN_SOURCE.read_text(encoding="utf-8")
    names = [NAMESPACE + "." + name for name in re.findall(r"^theorem (\w+)\b", source, re.M)]
    audit_source = source + "\n" + "".join("#print axioms " + name + "\n" for name in names)
    module = checker.compile_source(audit_source, names[0])
    if module["label"] != 1:
        raise ValueError("full module did not compile: " + module["diagnostic"])
    axioms = {name: parse_axioms(module["diagnostic"], name) for name in names}
    if any(value is None or not set(value) <= ALLOWED_AXIOMS for value in axioms.values()):
        raise ValueError("module theorem axiom audit incomplete or disallowed")
    teachers = verify_teachers(checker)
    for row in teachers["outcomes"]:
        row.pop("seconds", None)
    pack = replay_pack(checker)
    _, tasks, _ = load_bundle()
    controls = []
    for label, proof in [("invalid_equality", "rfl"), ("admission", "sorry"),
                         ("self_reference", "exact " + tasks[0]["declaration"])]:
        result = checker.check(tasks[0], proof)
        controls.append({"mutation": label, "rejected": result["label"] == 0,
                         "status": result["status"], "kernel_calls": result["kernel_calls"]})
    ok = teachers["passes"] == teachers["tasks"] and pack["matches"] and all(row["rejected"] for row in controls)
    return {"schema": "EvalMath/rh-compactification-native-suite/v1", "passed": ok,
            "environment": checker.environment, "module_source_sha256": sha256(source),
            "module_theorems": len(names), "module_axioms": axioms,
            "teachers": teachers, "candidate_pack": pack, "mutation_controls": controls,
            "evidence_class": "native Lean proof and engineering checks", "independent_families": 1,
            "heldout_scored": False, "neural_effect_claim": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lean-cmd", default="lake env lean")
    parser.add_argument("--lean-cwd", type=Path, default=ROOT / "lean")
    parser.add_argument("--allow-toolchain-mismatch", action="store_true")
    parser.add_argument("--output", type=Path, default=BASE / "native_receipt.json")
    args = parser.parse_args()
    checker = LeanChecker(shlex.split(args.lean_cmd), args.lean_cwd, allow_version_mismatch=args.allow_toolchain_mismatch)
    result = run(checker)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json_text(result), encoding="utf-8")
    print(json.dumps({"passed": result["passed"], "lean_version": checker.version,
                     "module_theorems": result["module_theorems"], "teacher_passes": result["teachers"]["passes"],
                     "candidate_checks": result["candidate_pack"]["candidate_checks"],
                     "trace_checks": result["candidate_pack"]["trace_checks"],
                     "candidate_matches": result["candidate_pack"]["matches"],
                     "controls_rejected": sum(row["rejected"] for row in result["mutation_controls"])}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
