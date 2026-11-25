"""Additive Lean affine-step curriculum and native checked-candidate pack.

The existing recurrence gym supplies its unchanged verifier and revision loop.
Every new proof receives the complete trusted dependency and the new module's
prefix. Learners need only Lean Init, without a compiled local module cache.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shlex
import textwrap

from spiral_ln import rh_compactification_gym as prior

ROOT = prior.ROOT
BASE = ROOT / "gyms" / "RHNumeratorStep"
LEAN_SOURCE = ROOT / "lean/FeedbackChannel/RHNumeratorStep.lean"
DEPENDENCY = prior.LEAN_SOURCE
NAMESPACE = "FeedbackChannel.RHNumeratorStep"
FAMILY = prior.FAMILY
PACK_SCHEMA = "datagoblin.checked-candidate-pack.v1"
PLACEHOLDER = "__RHGYM_FRAGMENT__"
STATEMENT = "Prove this goal."
MAX_BYTES = 384
TASKS = (
    ("affine_step_zero_iff", "affine_step", "Normalize the identity branch"),
    ("affine_step_succ_iff", "affine_step", "Eliminate successor evaluation witnesses"),
    ("affine_step_iff_graph", "affine_graph", "Identify the deterministic graph"),
    ("affine_step_total", "affine_graph", "Construct an output for each input"),
    ("affine_step_functional", "affine_graph", "Prove uniqueness of the output"),
    ("affine_recurrence_iff", "affine_recurrence", "Normalize the relational recurrence"),
    ("affine_recurrence_exists_unique", "affine_recurrence", "Apply general recursion"),
    ("affine_recurrence_eq_joint_numerator", "affine_recurrence", "Recover the joint numerator"),
)
# Each mutation changes a necessary proof step while preserving the input goal.
MICROS = (
    ("affine_step_zero_iff", "exact h.2", "exact h.1"),
    ("affine_step_succ_iff", "rw [hu, hd]", "rw [hu]"),
    ("affine_step_iff_graph", "affine_step_succ_iff mul add den x a b",
     "affine_step_zero_iff mul add den a b"),
    ("affine_step_total", "⟨affineValue mul add den y a,", "⟨a,"),
    ("affine_step_functional", ".mp hc).symm", ".mp hc)"),
    ("affine_recurrence_iff", ".mp (hf.2 n)", ".mpr (hf.2 n)"),
)
RevisionGym = prior.RevisionGym
sha256 = prior.sha256
json_text = prior.json_text
write_jsonl = prior.write_jsonl
read_jsonl = prior.read_jsonl


def source_hashes() -> dict[str, str]:
    paths = (DEPENDENCY, LEAN_SOURCE, Path(prior.__file__), Path(__file__))
    return {str(path.relative_to(ROOT)): sha256(path.read_bytes()) for path in paths}


def sources() -> tuple[str, str]:
    dependency = DEPENDENCY.read_text(encoding="utf-8")
    source = LEAN_SOURCE.read_text(encoding="utf-8")
    if re.findall(r"^import .+$", dependency, re.M) != ["import Init"]:
        raise ValueError("trusted dependency must remain Init-only")
    if re.findall(r"^import .+$", source, re.M) != ["import FeedbackChannel.RHCompactification"]:
        raise ValueError("extension import contract changed")
    return dependency, source


def inline_source(dependency: str, source: str) -> str:
    return dependency.rstrip() + "\n\n" + source.replace("import FeedbackChannel.RHCompactification\n", "", 1)


def render(task: dict, proof: str) -> str:
    return (task["context"] + task["statement"] + " := by\n"
            + textwrap.indent(proof.strip(), "  ")
            + f"\n\nend {NAMESPACE}\n\n#print axioms {task['qualified_name']}\n")


def extract_tasks() -> tuple[list[dict], list[dict]]:
    dependency, source = sources()
    blocks = list(prior.MARKER.finditer(source))
    names = [block.group(1) for block in blocks]
    if (not blocks or len(names) != len(set(names))
            or source.count("-- RHGYM-BEGIN ") != len(blocks)
            or source.count("-- RHGYM-END ") != len(blocks)):
        raise ValueError("unmatched or duplicate declaration markers")
    by_name = {block.group(1): (index, block) for index, block in enumerate(blocks)}
    theorem_names = re.findall(r"^theorem (\w+)\b", source, re.M)
    if theorem_names != [name for name, _, _ in TASKS]:
        raise ValueError("extension theorem roster differs")
    tasks, teachers = [], []
    for number, (name, stage, title) in enumerate(TASKS, 21):
        index, block = by_name[name]
        declaration = block.group(2)
        start = re.search(r"^theorem " + re.escape(name) + r"\b", declaration, re.M)
        if start is None or ":= by\n" not in declaration[start.start():]:
            raise ValueError("explicit theorem proof boundary missing")
        statement, proof = declaration[start.start():].strip().split(":= by\n", 1)
        statement, proof = statement.rstrip(), textwrap.dedent(proof).strip()
        context = inline_source(dependency, source[:block.start()]).rstrip() + "\n\n"
        task = {
            "id": f"RHCG-{number:03d}", "declaration": name,
            "qualified_name": NAMESPACE + "." + name, "namespace": NAMESPACE,
            "stage": stage, "title": title, "order": number,
            "family": FAMILY, "split": "train", "statement": statement, "context": context,
            "available_declarations": names[:index], "unavailable_declarations": names[index:],
            "source": str(LEAN_SOURCE.relative_to(ROOT)), "source_sha256": sha256(source),
            "dependency": str(DEPENDENCY.relative_to(ROOT)), "dependency_sha256": sha256(dependency),
            "statement_sha256": sha256(statement), "context_sha256": sha256(context),
            "hilbert_stage": "RH-PL-18", "fidelity": "Lean Nat/function analogue; no calculus translation",
        }
        prior.check_proof_surface(task, proof)
        task["reference_source_bytes"] = len(render(task, proof).encode("utf-8"))
        tasks.append(task)
        teachers.append({"id": task["id"], "proof": proof, "proof_sha256": sha256(proof), "split": "train"})
    return tasks, teachers


class NumeratorChecker(prior.LeanChecker):
    """Use the existing native gate with the additive module's source renderer."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.environment["renderer_sha256"] = sha256(Path(__file__).read_bytes())
        self.environment["curriculum"] = "RHNumeratorStep-v1"

    def check(self, task: dict, proof: str) -> dict:
        try:
            prior.check_proof_surface(task, proof)
        except ValueError as exc:
            return {"label": 0, "closed": False, "kernel_ok": False, "kernel_calls": 0,
                    "status": "rejected_by_surface", "axioms": [], "diagnostic": str(exc)}
        return {**self.compile_source(render(task, proof), task["qualified_name"]),
                "proof_sha256": sha256(proof.strip()), "proof_bytes": len(proof.strip().encode("utf-8")),
                "statement_sha256": task["statement_sha256"]}


def bundle_manifest(base: Path, tasks: list[dict]) -> dict:
    return {
        "schema": "EvalMath/rh-numerator-curriculum/v1", "language": "Lean 4",
        "expected_lean": prior.EXPECTED_LEAN, "sources_sha256": source_hashes(),
        "tasks": len(tasks), "task_ids": [task["id"] for task in tasks],
        "task_file": "tasks.jsonl", "tasks_sha256": sha256((base / "tasks.jsonl").read_bytes()),
        "teacher_file": "teachers.jsonl", "teachers_sha256": sha256((base / "teachers.jsonl").read_bytes()),
        "family": FAMILY, "independent_families": 1, "splits": {"train": [task["id"] for task in tasks]},
        "confirmation": {"status": "unallocated", "scored": False},
        "scope": "Public RH-PL-18 Nat/function analogue, additive to the existing recurrence family",
        "episode": {"default_attempts": 4, "budget_unit": "submitted candidate attempt",
                    "reward": "unchanged verified-best complete-source-byte potential"},
        "scientific_eligible": False,
    }


def build_bundle(base: Path = BASE) -> dict:
    tasks, teachers = extract_tasks()
    base.mkdir(parents=True, exist_ok=True)
    write_jsonl(base / "tasks.jsonl", tasks)
    write_jsonl(base / "teachers.jsonl", teachers)
    manifest = bundle_manifest(base, tasks)
    (base / "curriculum.json").write_text(json_text(manifest), encoding="utf-8")
    return manifest


def load_bundle(base: Path = BASE) -> tuple[dict, list[dict], list[dict]]:
    manifest = json.loads((base / "curriculum.json").read_text(encoding="utf-8"))
    tasks, teachers = read_jsonl(base / "tasks.jsonl"), read_jsonl(base / "teachers.jsonl")
    expected_tasks, expected_teachers = extract_tasks()
    if tasks != expected_tasks or teachers != expected_teachers:
        raise ValueError("curriculum differs from its source-prefix extraction")
    if manifest != bundle_manifest(base, tasks):
        raise ValueError("curriculum manifest differs from its source and training scope")
    return manifest, tasks, teachers


def verify_teachers(checker: NumeratorChecker, base: Path = BASE) -> dict:
    _, tasks, teachers = load_bundle(base)
    rows = []
    for task, teacher in zip(tasks, teachers, strict=True):
        result = checker.check(task, teacher["proof"])
        result.pop("seconds", None)
        rows.append({"id": task["id"], **result})
    return {"tasks": len(rows), "passes": sum(row["label"] == 1 for row in rows), "outcomes": rows}


def model_input(statement: str, context: str) -> str:
    return f"<STATEMENT> {statement}\n<GOALS> {context}"


def fill_template(template: str, proof: str) -> str:
    needle = "  " + PLACEHOLDER
    if template.count(PLACEHOLDER) != 1 or needle not in template:
        raise ValueError("proof placeholder must occur once at the theorem body")
    return template.replace(needle, textwrap.indent(proof.strip(), "  "))


def micro_specs(base: Path = BASE) -> list[dict]:
    _, tasks, teachers = load_bundle(base)
    table = {task["declaration"]: (task, teacher["proof"])
             for task, teacher in zip(tasks, teachers, strict=True)}
    specs = []
    for name, needle, replacement in MICROS:
        task, gold = table[name]
        if gold.count(needle) != 1:
            raise ValueError("microstep mutation anchor drifted")
        wrong = gold.replace(needle, replacement, 1)
        if max(len(gold.encode("utf-8")), len(wrong.encode("utf-8"))) > MAX_BYTES:
            raise ValueError("microstep proof would be truncated")
        specs.append({"id": "rh_num_micro_" + name, "task": task,
                      "template": render(task, PLACEHOLDER), "gold": gold, "wrong": wrong})
    return specs


def trace_context(checker: NumeratorChecker, spec: dict) -> str:
    target = spec["task"]["qualified_name"]
    source = fill_template(spec["template"], "trace_state\n" + spec["gold"])
    traced = checker.compile_source(source, target)
    if traced["label"] != 1:
        raise ValueError("trace harness did not close: " + spec["id"] + "\n" + traced["diagnostic"])
    context = re.sub(r"'" + re.escape(target) + r"' depends on axioms: \[[^\]]*\]", "",
                     traced["diagnostic"], flags=re.S)
    context = re.sub(r"'" + re.escape(target) + r"' does not depend on any axioms", "", context).strip()
    if "⊢" not in context or len(model_input(STATEMENT, context).encode("utf-8")) > MAX_BYTES:
        raise ValueError("native state is absent or exceeds the encoder budget: " + spec["id"])
    return context


def epoch_for(spec: dict, context: str, environment: dict) -> str:
    return "rhnum_" + sha256(json_text({"id": spec["id"], "environment": environment,
        "template_sha256": sha256(spec["template"]), "statement": STATEMENT, "context": context}))


def public_row(spec: dict, context: str, environment: dict) -> dict:
    epoch = epoch_for(spec, context, environment)
    candidates = [{"id": "c_" + sha256(epoch + "\0" + tactic)[:20],
                   "action": "lean_tactic", "tactic": tactic} for tactic in (spec["gold"], spec["wrong"])]
    candidates.sort(key=lambda item: item["id"])
    task = spec["task"]
    return {"id": spec["id"], "lineage": FAMILY, "family": FAMILY, "epoch": epoch,
            "task": "lean_candidate_proof", "statement": STATEMENT, "context": context,
            "candidates": candidates, "orders": {"compose": [candidate["id"] for candidate in candidates]},
            "retrieved": {"compose": [NAMESPACE + "." + name for name in task["available_declarations"]]},
            "stage": task["stage"], "state_kind": "initial_theorem_goal",
            "source_harness": {"path": "sources/" + spec["id"] + ".lean.in",
                               "sha256": sha256(spec["template"]), "placeholder": PLACEHOLDER,
                               "target": task["qualified_name"]}}


def build_pack(checker: NumeratorChecker, base: Path = BASE) -> dict:
    specs = micro_specs(base)
    pack = base / "pack"
    (pack / "sources").mkdir(parents=True, exist_ok=True)
    public, private, evidence, files = [], [], [], {}
    for spec in specs:
        context = trace_context(checker, spec)
        row = public_row(spec, context, checker.environment)
        relative = row["source_harness"]["path"]
        (pack / relative).write_text(spec["template"], encoding="utf-8")
        files[relative] = sha256(spec["template"])
        outcomes = {}
        for candidate in row["candidates"]:
            tactic = candidate["tactic"]
            prior.check_proof_surface(spec["task"], tactic)
            result = checker.compile_source(fill_template(spec["template"], tactic), spec["task"]["qualified_name"])
            expected = int(tactic == spec["gold"])
            if result["label"] != expected:
                raise ValueError("native candidate outcome differs: " + spec["id"] + "\n" + result["diagnostic"])
            result.pop("seconds", None)
            outcomes[candidate["id"]] = result
        public.append(row)
        private.append({"id": row["id"], "epoch": row["epoch"], "outcomes": outcomes,
                        "native": {"backend": checker.environment["backend"], "local_context_replayed": True},
                        "retrieval_comparisons": []})
        evidence.append({"id": spec["id"], "context": context, "template_sha256": sha256(spec["template"]),
                         "gold_sha256": sha256(spec["gold"]), "wrong_sha256": sha256(spec["wrong"])})
    trace_evidence = {"schema": "EvalMath/rh-numerator-native-contexts/v1",
                      "sources_sha256": source_hashes(), "rows": evidence}
    (base / "microsteps.json").write_text(json_text(trace_evidence), encoding="utf-8")
    write_jsonl(pack / "train.jsonl", public)
    write_jsonl(pack / "train.receipts.jsonl", private)
    manifest = {
        "schema": PACK_SCHEMA, "splits": {"train": {"goals": len(public), "lineages": 1,
            "public": "train.jsonl", "public_sha256": sha256((pack / "train.jsonl").read_bytes()),
            "receipts": "train.receipts.jsonl", "receipts_sha256": sha256((pack / "train.receipts.jsonl").read_bytes())}},
        "environment": checker.environment, "source_evidence_sha256": sha256((base / "microsteps.json").read_bytes()),
        "sources_sha256": source_hashes(), "source_files_sha256": files,
        "scope": "Public training extension in the existing recurrence family",
        "native_processes_for_export": 3 * len(public), "independent_families": 1,
        "confirmation": {"status": "unallocated", "scored": False},
        "input_cap_utf8_bytes": MAX_BYTES, "candidate_cap_utf8_bytes": MAX_BYTES,
        "scientific_eligible": False, "training_eligible": True,
    }
    (pack / "manifest.json").write_text(json_text(manifest), encoding="utf-8")
    return manifest


def load_pack(base: Path = BASE) -> tuple[dict, list[dict], list[dict]]:
    specs = micro_specs(base)
    pack = base / "pack"
    manifest = json.loads((pack / "manifest.json").read_text(encoding="utf-8"))
    if (manifest.get("schema") != PACK_SCHEMA or set(manifest.get("splits", {})) != {"train"}
            or manifest.get("independent_families") != 1 or manifest.get("scientific_eligible") is not False
            or manifest.get("training_eligible") is not True
            or manifest.get("confirmation") != {"status": "unallocated", "scored": False}
            or manifest.get("input_cap_utf8_bytes") != MAX_BYTES
            or manifest.get("candidate_cap_utf8_bytes") != MAX_BYTES
            or manifest.get("native_processes_for_export") != 3 * len(specs)
            or manifest.get("scope") != "Public training extension in the existing recurrence family"
            or manifest.get("sources_sha256") != source_hashes()
            or manifest.get("source_evidence_sha256") != sha256((base / "microsteps.json").read_bytes())):
        raise ValueError("pack source identity or public training scope differs")
    environment = manifest["environment"]
    version = environment.get("lean_version")
    parsed_version = re.search(r"version\s+(\d+\.\d+\.\d+)", version) if isinstance(version, str) else None
    timeout = environment.get("timeout_s")
    digest = environment.get("lean_sha256")
    if (environment.get("checker_sha256") != sha256(Path(prior.__file__).read_bytes())
            or environment.get("renderer_sha256") != sha256(Path(__file__).read_bytes())
            or environment.get("curriculum") != "RHNumeratorStep-v1"
            or environment.get("backend") != "lean4_direct_compile_with_axiom_audit"
            or environment.get("expected_version") != prior.EXPECTED_LEAN
            or parsed_version is None
            or type(environment.get("toolchain_matches")) is not bool
            or environment["toolchain_matches"] != (parsed_version.group(1) == prior.EXPECTED_LEAN)
            or type(timeout) not in (int, float) or not 0 < timeout <= 60
            or environment.get("memory_limit_mib") != 768 or environment.get("max_heartbeats") != 400000
            or not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None):
        raise ValueError("pack verifier sources differ")
    evidence = json.loads((base / "microsteps.json").read_text(encoding="utf-8"))
    if (evidence.get("schema") != "EvalMath/rh-numerator-native-contexts/v1"
            or set(evidence) != {"schema", "sources_sha256", "rows"}
            or evidence.get("sources_sha256") != source_hashes() or len(evidence["rows"]) != len(specs)):
        raise ValueError("native trace evidence differs")
    entry = manifest["splits"]["train"]
    for field in ("public", "receipts"):
        name = entry[field]
        if name != Path(name).name or sha256((pack / name).read_bytes()) != entry[field + "_sha256"]:
            raise ValueError("pack filename or data digest differs")
    public, private = read_jsonl(pack / entry["public"]), read_jsonl(pack / entry["receipts"])
    if len(public) != len(private) or len(public) != len(specs) or entry["goals"] != len(specs) or entry["lineages"] != 1:
        raise ValueError("pack goal count differs")
    expected_files = {}
    for spec, row, receipt, trace in zip(specs, public, private, evidence["rows"], strict=True):
        expected_trace = {"id": spec["id"], "context": trace["context"],
                          "template_sha256": sha256(spec["template"]),
                          "gold_sha256": sha256(spec["gold"]), "wrong_sha256": sha256(spec["wrong"])}
        if trace != expected_trace or row != public_row(spec, trace["context"], environment):
            raise ValueError("public row differs from its source-derived specification")
        if len(model_input(row["statement"], row["context"]).encode("utf-8")) > MAX_BYTES or "⊢" not in row["context"]:
            raise ValueError("local goal would be truncated or is absent")
        harness = row["source_harness"]
        path = pack / harness["path"]
        if path.read_text(encoding="utf-8") != spec["template"]:
            raise ValueError("source harness differs from the target prefix")
        expected_files[harness["path"]] = sha256(spec["template"])
        ids = {candidate["id"] for candidate in row["candidates"]}
        if (receipt["id"] != row["id"] or receipt["epoch"] != row["epoch"]
                or set(receipt["outcomes"]) != ids
                or receipt.get("native") != {"backend": environment["backend"], "local_context_replayed": True}
                or receipt.get("retrieval_comparisons") != []):
            raise ValueError("candidate receipt identity differs")
        for candidate in row["candidates"]:
            result = receipt["outcomes"][candidate["id"]]
            expected_label = int(candidate["tactic"] == spec["gold"])
            label = result.get("label")
            status, returncode = result.get("status"), result.get("returncode")
            axioms, diagnostic = result.get("axioms"), result.get("diagnostic")
            if (result.get("verifier") != environment["backend"]
                    or type(result.get("kernel_calls")) is not int or result["kernel_calls"] != 1
                    or type(returncode) is not int or returncode < 0
                    or not isinstance(axioms, list) or not all(isinstance(axiom, str) for axiom in axioms)
                    or not isinstance(diagnostic, str)
                    or type(result.get("charged_source_bytes")) is not int):
                raise ValueError("native outcome metadata is inconsistent")
            if label == 1:
                coherent = status == "accepted" and returncode == 0
            else:
                coherent = (result.get("closed") is False and result.get("kernel_ok") is False
                    and ((status == "rejected_by_lean" and returncode > 0 and "error:" in diagnostic.lower())
                         or (status == "rejected_axioms"
                             and (bool(set(axioms) - prior.ALLOWED_AXIOMS) or "sorry" in diagnostic.lower()))))
            if not coherent:
                raise ValueError("native outcome status contradicts its label")
            positive = (result.get("closed") is True and result.get("kernel_ok") is True
                        and type(result.get("kernel_calls")) is int and result["kernel_calls"] == 1
                        and isinstance(result.get("axioms"), list)
                        and all(isinstance(axiom, str) and axiom in prior.ALLOWED_AXIOMS for axiom in result["axioms"]))
            full = fill_template(spec["template"], candidate["tactic"])
            if (type(label) is not int or label != expected_label or (label == 1) != positive
                    or result["source_sha256"] != sha256(full)
                    or result["charged_source_bytes"] != len(full.encode("utf-8"))):
                raise ValueError("candidate receipt disagrees with its native source oracle")
    if manifest["source_files_sha256"] != expected_files:
        raise ValueError("registered harness files differ")
    return manifest, public, private


def replay_pack(checker: NumeratorChecker, base: Path = BASE) -> dict:
    _, public, private = load_pack(base)
    rows = []
    for spec, row, receipt in zip(micro_specs(base), public, private, strict=True):
        if trace_context(checker, spec) != row["context"]:
            raise ValueError("native local goal differs from the public state")
        for candidate in row["candidates"]:
            result = checker.compile_source(fill_template(spec["template"], candidate["tactic"]), spec["task"]["qualified_name"])
            expected = receipt["outcomes"][candidate["id"]]
            rows.append({"id": row["id"], "candidate": candidate["id"], "label": result["label"],
                         "matches": result["label"] == expected["label"] and result["source_sha256"] == expected["source_sha256"],
                         "status": result["status"], "axioms": result["axioms"]})
    return {"goals": len(public), "candidate_checks": len(rows), "trace_checks": len(public),
            "positive": sum(row["label"] == 1 for row in rows), "negative": sum(row["label"] == 0 for row in rows),
            "unknown": sum(row["label"] is None for row in rows), "matches": all(row["matches"] for row in rows), "rows": rows}


def structural_receipt(base: Path = BASE) -> dict:
    _, tasks, _ = load_bundle(base)
    manifest, public, private = load_pack(base)
    files = [base / name for name in ("curriculum.json", "tasks.jsonl", "teachers.jsonl", "microsteps.json")]
    entry = manifest["splits"]["train"]
    files.extend(base / "pack" / name for name in ("manifest.json", entry["public"], entry["receipts"]))
    files.extend(base / "pack" / name for name in manifest["source_files_sha256"])
    return {"schema": "EvalMath/rh-numerator-structure/v1", "passed": True,
            "sources_sha256": source_hashes(),
            "artifacts_sha256": {str(path.relative_to(base)): sha256(path.read_bytes()) for path in sorted(files) if path.is_file()},
            "tasks": len(tasks), "microsteps": len(public), "candidate_receipts": sum(len(row["outcomes"]) for row in private),
            "goal_bytes_max": max(len(model_input(row["statement"], row["context"]).encode("utf-8")) for row in public),
            "candidate_bytes_max": max(len(candidate["tactic"].encode("utf-8")) for row in public for candidate in row["candidates"]),
            "independent_families": 1, "native_replay_performed": False,
            "training_steps": 0, "heldout_scored": False, "neural_effect_claim": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("build", "check", "verify", "pack-build", "pack-verify", "serve"))
    parser.add_argument("--base", type=Path, default=BASE)
    parser.add_argument("--lean-cmd", default="lake env lean")
    parser.add_argument("--lean-cwd", type=Path, default=ROOT / "lean")
    parser.add_argument("--allow-toolchain-mismatch", action="store_true")
    parser.add_argument("--max-attempts", type=int, default=4)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.action == "build":
        result = build_bundle(args.base)
    elif args.action == "check":
        result = structural_receipt(args.base)
    else:
        checker = NumeratorChecker(shlex.split(args.lean_cmd), args.lean_cwd,
                                   allow_version_mismatch=args.allow_toolchain_mismatch)
        if args.action == "verify":
            result = verify_teachers(checker, args.base)
        elif args.action == "pack-build":
            result = build_pack(checker, args.base)
        elif args.action == "pack-verify":
            result = replay_pack(checker, args.base)
        else:
            import sys
            _, tasks, _ = load_bundle(args.base)
            gym = RevisionGym(tasks, checker.check, args.max_attempts)
            for line in sys.stdin:
                try:
                    request = json.loads(line)
                    if request.get("op") == "reset":
                        result = gym.reset(request["id"])
                    elif request.get("op") == "step":
                        result = gym.step(request["proof"])
                    elif request.get("op") == "close":
                        break
                    else:
                        raise ValueError("op must be reset, step, or close")
                except (ValueError, KeyError, TypeError) as exc:
                    result = {"error": str(exc)}
                print(json.dumps(result, ensure_ascii=False, sort_keys=True), flush=True)
            return 0
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json_text(result), encoding="utf-8")
    print(json_text({key: value for key, value in result.items() if key not in ("outcomes", "rows", "sources_sha256", "artifacts_sha256", "source_files_sha256")}), end="")
    if args.action == "verify" and result["passes"] != result["tasks"]:
        return 1
    if args.action == "pack-verify" and not result["matches"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
