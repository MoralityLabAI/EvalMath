"""Produce actual Lean microsteps that fit the native 384-byte PPT ranker.

Each model row contains the complete output of one successful ``trace_state``.
The source template is a prefix of the public Lean development with one proof
fragment hole. All remaining teacher proof text is public training material.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile


REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / "lean/FeedbackChannel/RHCompactification.lean"
HERE = Path(__file__).resolve().parent
PLACEHOLDER = "__RHGYM_FRAGMENT__"
NAMESPACE = "FeedbackChannel.RHCompactification"
STATEMENT = "Prove this goal."
INPUT_CAP = 384


def _spec(target, stage, old, replacement, gold, wrong, retrieved):
    return dict(target=target, stage=stage, old=old, replacement=replacement,
                gold=gold, wrong=wrong, retrieved=retrieved)


SPECS = [
    _spec("extend_before", "prefix", "  simp [extend, hne]",
          "  clear hi\n  " + PLACEHOLDER,
          "simp [extend, hne]", "rfl", ["extend"]),
    _spec("prefix_restrict", "prefix", "  exact hf.2 i (Nat.lt_of_lt_of_le hi hmn)",
          "  " + PLACEHOLDER,
          "exact hf.2 i (Nat.lt_of_lt_of_le hi hmn)", "exact hf.2 i hi", ["IsPrefix"]),
    _spec("prefix_extend", "prefix",
          "      rw [extend_at_new, extend_before f n n (step n (f n)) (Nat.le_refl n)]",
          "      clear hf seed\n      " + PLACEHOLDER,
          "rw [extend_at_new, extend_before f n n (step n (f n)) (Nat.le_refl n)]",
          "rw [extend_at_new]", ["extend_at_new", "extend_before"]),
    _spec("prefix_graph_overlap", "overlap",
          "  exact ha.2.trans ((prefix_agreement hf hg i ha.1 hb.1).trans hb.2.symm)",
          "  have hab : f i = g i := prefix_agreement hf hg i ha.1 hb.1\n"
          "  have ha' : a = f i := ha.2\n"
          "  have hb' : b = g i := hb.2\n"
          "  clear hf hg ha hb step seed n m\n  " + PLACEHOLDER,
          "exact ha'.trans (hab.trans hb'.symm)",
          "exact ha'.trans (hab.trans hb')", ["prefix_agreement"]),
    _spec("glue_agrees", "glue",
          "  exact prefix_agreement (family i).property (family n).property i (Nat.le_refl i) hi",
          "  " + PLACEHOLDER,
          "exact prefix_agreement (family i).property (family n).property i (Nat.le_refl i) hi",
          "exact (family n).property.1", ["prefix_agreement"]),
    _spec("glued_graph_iff", "glue",
          "    exact hn.2.trans (glue_agrees family n i hn.1).symm",
          "    " + PLACEHOLDER,
          "exact hn.2.trans (glue_agrees family n i hn.1).symm",
          "exact hn.2", ["glue_agrees"]),
    _spec("glue_succ", "glue",
          "    _ = step n (glue family n) :=\n"
          "      congrArg (step n) (glue_agrees family (n + 1) n (Nat.le_succ n)).symm",
          "    _ = step n (glue family n) := by\n      " + PLACEHOLDER,
          "exact congrArg (step n) (glue_agrees family (n + 1) n (Nat.le_succ n)).symm",
          "exact congrArg (step n) (glue_agrees family (n + 1) n (Nat.le_succ n))",
          ["glue_agrees"]),
    _spec("denominator_unique", "denominator",
          "  exact recurrence_unique ⟨h0, hs⟩ (orbit_recurrence (fun n value => mul (n + 1) value) seed)",
          "  " + PLACEHOLDER,
          "exact recurrence_unique ⟨h0, hs⟩ (orbit_recurrence (fun n value => mul (n + 1) value) seed)",
          "exact recurrence_unique (orbit_recurrence (fun n value => mul (n + 1) value) seed) ⟨h0, hs⟩",
          ["recurrence_unique", "orbit_recurrence"]),
    _spec("denominator_step_to_exact", "denominator",
          "  exact ⟨n + 1, f (n + 1), n + 1, f n, f (n + 1), rfl, rfl, rfl, rfl, hs n, rfl⟩",
          "  refine ⟨n + 1, f (n + 1), n + 1, f n, f (n + 1), rfl, rfl, rfl, rfl, ?_, rfl⟩\n"
          "  " + PLACEHOLDER,
          "exact hs n", "exact (hs n).symm", ["ExactDenominatorStep"]),
    _spec("denominator_exact_to_step", "denominator",
          "    _ = mul (n + 1) (f n) := by rw [hl, hb]",
          "    _ = mul (n + 1) (f n) := by\n"
          "      clear h hk ha hc hac k a c\n      " + PLACEHOLDER,
          "rw [hl, hb]", "rw [hl]", ["ExactDenominatorStep"]),
    _spec("denominator_exact_unique", "denominator",
          "  exact denominator_unique h0 (denominator_exact_to_step hs)",
          "  " + PLACEHOLDER,
          "exact denominator_unique h0 (denominator_exact_to_step hs)",
          "exact denominator_unique h0 hs", ["denominator_unique", "denominator_exact_to_step"]),
    _spec("joint_unique", "joint",
          "  exact recurrence_unique ⟨h0, hs⟩ (orbit_recurrence (jointStep mul add) (numSeed, denSeed))",
          "  " + PLACEHOLDER,
          "exact recurrence_unique ⟨h0, hs⟩ (orbit_recurrence (jointStep mul add) (numSeed, denSeed))",
          "exact recurrence_unique (orbit_recurrence (jointStep mul add) (numSeed, denSeed)) ⟨h0, hs⟩",
          ["recurrence_unique", "orbit_recurrence"]),
]


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def model_input(statement: str, context: str) -> str:
    return f"<STATEMENT> {statement}\n<GOALS> {context}"


def build_template(spec: dict, source: str) -> str:
    target = spec["target"]
    pattern = re.compile(r"^-- RHGYM-BEGIN " + re.escape(target) + r"\n(.*?)"
                         r"^-- RHGYM-END " + re.escape(target) + r"\n", re.M | re.S)
    match = pattern.search(source)
    if match is None:
        raise ValueError(f"missing declaration {target}")
    block = match.group(0)
    if block.count(spec["old"]) != 1:
        raise ValueError(f"fragment source drift: {target}")
    block = block.replace(spec["old"], spec["replacement"])
    template = source[:match.start()] + block + f"\nend {NAMESPACE}\n"
    if template.count(PLACEHOLDER) != 1:
        raise ValueError("expected one fragment hole")
    return template


def fill_template(template: str, fragment: str) -> str:
    match = re.search(r"^( *)" + PLACEHOLDER + r"$", template, re.M)
    if match is None:
        raise ValueError("fragment placeholder must occupy its own line")
    indent = match.group(1)
    replacement = "\n".join(indent + line if line else "" for line in fragment.splitlines())
    return template[:match.start()] + replacement + template[match.end():]


def lean_check(exe: str, source: str, path: Path) -> dict:
    path.write_text(source, encoding="utf-8")
    result = subprocess.run([exe, str(path)], text=True, capture_output=True, timeout=60)
    return {"returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr,
            "source_sha256": sha256(source)}


def build_rows(lean: str, *, output: Path, workers: int = 4) -> dict:
    source = SOURCE.read_text(encoding="utf-8")
    source_dir = output.parent / "microstep_sources"
    source_dir.mkdir(parents=True, exist_ok=True)
    version = subprocess.check_output([lean, "--version"], text=True).strip()
    with tempfile.TemporaryDirectory(prefix="rh-microsteps-") as temp:
        temp_dir = Path(temp)

        def produce(spec):
            target = spec["target"]
            task_id = "rh_micro_" + target
            template = build_template(spec, source)
            gold_source = fill_template(template, spec["gold"])
            wrong_source = fill_template(template, spec["wrong"])
            trace_source = fill_template(template, "trace_state\n" + spec["gold"])
            traced = lean_check(lean, trace_source, temp_dir / (target + "_trace.lean"))
            gold = lean_check(lean, gold_source, temp_dir / (target + "_gold.lean"))
            wrong = lean_check(lean, wrong_source, temp_dir / (target + "_wrong.lean"))
            if traced["returncode"] or gold["returncode"] or not wrong["returncode"]:
                raise ValueError(json.dumps({"target": target, "trace": traced,
                                            "gold": gold, "wrong": wrong}, indent=2))
            if traced["stderr"] or gold["stdout"] or gold["stderr"]:
                raise ValueError(f"unexpected Lean diagnostics for {target}")
            context = traced["stdout"].strip()
            if "⊢" not in context:
                raise ValueError(f"missing actual goal for {target}")
            input_bytes = len(model_input(STATEMENT, context).encode("utf-8"))
            if input_bytes > INPUT_CAP:
                raise ValueError(json.dumps({"target": target, "input_bytes": input_bytes,
                                            "actual_trace_state": context}, indent=2))
            candidates = []
            for key, expected, checked in [("gold", True, gold), ("wrong", False, wrong)]:
                fragment = spec[key]
                size = len(fragment.encode("utf-8"))
                if size > INPUT_CAP:
                    raise ValueError(f"candidate too long: {target}/{key}")
                candidates.append({"id": task_id + "_" + key, "action": "lean_tactic",
                                   "text": fragment, "bytes_utf8": size,
                                   "expected_accept": expected,
                                   "lean_returncode": checked["returncode"],
                                   "full_source_sha256": checked["source_sha256"]})
            template_path = source_dir / (task_id + ".lean.in")
            template_path.write_text(template, encoding="utf-8")
            return {"id": task_id, "task_id": task_id, "task_type": "lean_candidate_proof",
                    "root_id": "rh_compactification_recurrence_v1", "split": "train",
                    "stage": spec["stage"], "target_theorem": NAMESPACE + "." + target,
                    "statement": STATEMENT, "context": context,
                    "context_origin": "Lean trace_state from successful full theorem harness",
                    "ranker_input_bytes_utf8": input_bytes, "ranker_input_cap_bytes": INPUT_CAP,
                    "fragment_placeholder": PLACEHOLDER,
                    "source_template_path": str(template_path.relative_to(REPO)),
                    "source_template_sha256": sha256(template),
                    "trace_source_sha256": traced["source_sha256"],
                    "candidates": candidates,
                    "retrieved": {"compose": [NAMESPACE + "." + name for name in spec["retrieved"]]},
                    "orders": {"compose": [candidates[0]["id"], candidates[1]["id"]]}}

        with ThreadPoolExecutor(max_workers=workers) as pool:
            rows = list(pool.map(produce, SPECS))
    payload = {"schema": "rh_compactification_microsteps_v1", "lean_version": version,
               "module_source": str(SOURCE.relative_to(REPO)), "module_source_sha256": sha256(source),
               "generator_source": str(Path(__file__).relative_to(REPO)),
               "generator_source_sha256": sha256(Path(__file__).read_text(encoding="utf-8")),
               "unit": "shared recurrence development", "n_independent_roots": 1,
               "n_cases": len(rows), "split": "train_only", "model_trained_or_evaluated": False,
               "statement_context_format": "<STATEMENT> {statement}\n<GOALS> {context}",
               "input_cap_bytes_utf8": INPUT_CAP, "candidate_cap_bytes_utf8": INPUT_CAP,
               "gold_full_closure_passed": len(rows), "wrong_full_closure_rejected": len(rows),
               "rows": rows}
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lean", required=True)
    parser.add_argument("--output", type=Path, default=HERE / "microsteps.json")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    payload = build_rows(args.lean, output=args.output, workers=args.workers)
    print(json.dumps({key: payload[key] for key in ["schema", "lean_version", "n_cases",
                     "n_independent_roots", "gold_full_closure_passed", "wrong_full_closure_rejected"]}, indent=2))
    print(json.dumps({row["task_id"]: row["ranker_input_bytes_utf8"] for row in payload["rows"]}, indent=2))


if __name__ == "__main__":
    main()
