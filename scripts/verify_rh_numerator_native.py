"""Replay every affine-step theorem, teacher, native goal and candidate with Lean."""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import re
import shlex
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spiral_ln import rh_numerator_gym as gym


def run(checker: gym.NumeratorChecker, base: Path = gym.BASE) -> dict:
    dependency, source = gym.sources()
    names = [gym.NAMESPACE + "." + name for name in re.findall(r"^theorem (\w+)\b", source, re.M)]
    audited = gym.inline_source(dependency, source) + "\n" + "".join("#print axioms " + name + "\n" for name in names)
    module = checker.compile_source(audited, names[0])
    axioms = {name: gym.prior.parse_axioms(module["diagnostic"], name) for name in names}
    if module["label"] != 1 or any(value is None or not set(value) <= gym.prior.ALLOWED_AXIOMS for value in axioms.values()):
        raise ValueError("module compilation or theorem axiom audit failed: " + module["diagnostic"])
    teachers = gym.verify_teachers(checker, base)
    pack = gym.replay_pack(checker, base)
    _, tasks, teacher_rows = gym.load_bundle(base)
    controls = []
    for name, proof in (("invalid_equality", "rfl"), ("admission", "sorry"),
                        ("self_reference", "exact " + tasks[0]["declaration"]),
                        ("future_reference", "exact " + tasks[-1]["declaration"])):
        result = checker.check(tasks[0], proof)
        controls.append({"mutation": name, "rejected": result["label"] == 0,
                         "status": result["status"], "kernel_calls": result["kernel_calls"]})
    wrong_zero = deepcopy(tasks[0])
    needle = "(y = 0 ∧ b = a) ∨"
    if wrong_zero["context"].count(needle) != 1:
        raise ValueError("zero-branch mutation anchor drifted")
    wrong_zero["context"] = wrong_zero["context"].replace(needle, "(y = 0 ∧ b = a + 1) ∨", 1)
    wrong_successor = deepcopy(tasks[1])
    if wrong_successor["statement"].count("(den x)") != 1:
        raise ValueError("successor-index mutation anchor drifted")
    wrong_successor["statement"] = wrong_successor["statement"].replace("(den x)", "(den (x + 1))", 1)
    for name, task, teacher in (("zero_branch_shift", wrong_zero, teacher_rows[0]),
                                ("successor_denominator_index", wrong_successor, teacher_rows[1])):
        result = checker.compile_source(gym.render(task, teacher["proof"]), task["qualified_name"])
        controls.append({"mutation": name, "rejected": result["label"] == 0,
                         "status": result["status"], "kernel_calls": result["kernel_calls"],
                         "mutated_source_sha256": result["source_sha256"]})
    passed = teachers["passes"] == len(tasks) and pack["matches"] and all(row["rejected"] for row in controls)
    hashes = gym.source_hashes()
    hashes[str(Path(__file__).resolve().relative_to(ROOT))] = gym.sha256(Path(__file__).read_bytes())
    return {"schema": "EvalMath/rh-numerator-native-suite/v1", "passed": passed,
            "environment": checker.environment, "sources_sha256": hashes,
            "module_theorems": len(names), "module_axioms": axioms,
            "module_audit_source_sha256": module["source_sha256"],
            "teachers": teachers, "candidate_pack": pack, "mutation_controls": controls,
            "native_proof_compilations": 1 + len(tasks) + pack["candidate_checks"] + pack["trace_checks"]
                + sum(row["kernel_calls"] for row in controls),
            "evidence_class": "native Lean proof and engineering checks", "independent_families": 1,
            "training_steps": 0, "heldout_scored": False, "neural_effect_claim": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=gym.BASE)
    parser.add_argument("--lean-cmd", default="lake env lean")
    parser.add_argument("--lean-cwd", type=Path, default=ROOT / "lean")
    parser.add_argument("--allow-toolchain-mismatch", action="store_true")
    parser.add_argument("--output", type=Path, default=gym.BASE / "native_receipt.json")
    args = parser.parse_args()
    checker = gym.NumeratorChecker(shlex.split(args.lean_cmd), args.lean_cwd,
                                   allow_version_mismatch=args.allow_toolchain_mismatch)
    result = run(checker, args.base)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(gym.json_text(result), encoding="utf-8")
    print(json.dumps({"passed": result["passed"], "lean_version": checker.version,
                     "module_theorems": result["module_theorems"], "teachers": result["teachers"]["passes"],
                     "trace_checks": result["candidate_pack"]["trace_checks"],
                     "candidate_checks": result["candidate_pack"]["candidate_checks"],
                     "controls_rejected": sum(row["rejected"] for row in result["mutation_controls"])}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
