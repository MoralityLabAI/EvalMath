"""Authenticate the additive numerator gym and its recorded native/trainer evidence.

This command checks source identities and recorded outcomes. Fresh Lean replay
is scripts/verify_rh_numerator_native.py; model training is a separate command.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import importlib.util
import json
import math
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from spiral_ln import rh_numerator_gym as gym


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def verify() -> dict:
    structure = gym.structural_receipt()
    curriculum, tasks, teachers = gym.load_bundle()
    pack, public, private = gym.load_pack()
    native = read(gym.BASE / "native_receipt.json")
    adapter = read(gym.BASE / "adapter_receipt.json")
    training = read(gym.BASE / "training_smoke.json")
    names = [task["qualified_name"] for task in tasks]
    manifest_hash = gym.sha256((gym.BASE / "pack/manifest.json").read_bytes())
    contract_path = gym.prior.BASE / "trainer_contract.json"
    contract = read(contract_path)
    contract_hash = gym.sha256(contract_path.read_bytes())
    prior_adapter_path = gym.prior.BASE / "adapter_receipt.json"
    prior_adapter = read(prior_adapter_path)

    assert native["schema"] == "EvalMath/rh-numerator-native-suite/v1"
    assert native["evidence_class"] == "native Lean proof and engineering checks"
    assert native["independent_families"] == 1 and native["training_steps"] == 0
    assert native["heldout_scored"] is False and native["neural_effect_claim"] is False
    assert native["passed"] is True and native["environment"] == pack["environment"]
    assert native["environment"]["toolchain_matches"] is True
    assert native["environment"]["expected_version"] == gym.prior.EXPECTED_LEAN == "4.34.1"
    version = re.search(r"\bversion (\d+\.\d+\.\d+)(?=[,\s)])", native["environment"]["lean_version"])
    assert version is not None and version.group(1) == "4.34.1"
    assert native["module_theorems"] == len(tasks) == len(native["module_axioms"]) == 8
    assert set(native["module_axioms"]) == set(names)
    assert all(set(axioms) <= gym.prior.ALLOWED_AXIOMS for axioms in native["module_axioms"].values())
    dependency, source = gym.sources()
    audited = gym.inline_source(dependency, source) + "\n" + "".join("#print axioms " + name + "\n" for name in names)
    assert native["module_audit_source_sha256"] == gym.sha256(audited)
    expected_native_sources = gym.source_hashes()
    native_script = ROOT / "scripts/verify_rh_numerator_native.py"
    expected_native_sources[str(native_script.relative_to(ROOT))] = gym.sha256(native_script.read_bytes())
    assert native["sources_sha256"] == expected_native_sources
    assert native["teachers"]["passes"] == native["teachers"]["tasks"] == len(tasks)
    for task, teacher, result in zip(tasks, teachers, native["teachers"]["outcomes"], strict=True):
        assert task["id"] == teacher["id"] == result["id"]
        assert type(result["label"]) is int and result["label"] == 1
        assert result["closed"] is True and result["kernel_ok"] is True
        assert type(result["kernel_calls"]) is int and result["kernel_calls"] == 1
        assert set(result["axioms"]) <= gym.prior.ALLOWED_AXIOMS
        full = gym.render(task, teacher["proof"])
        assert result["status"] == "accepted" and type(result["returncode"]) is int and result["returncode"] == 0
        assert result["verifier"] == pack["environment"]["backend"]
        assert result["source_sha256"] == gym.sha256(full)
        assert result["charged_source_bytes"] == len(full.encode("utf-8"))
        assert result["statement_sha256"] == task["statement_sha256"]
    replay = native["candidate_pack"]
    assert replay["matches"] is True and replay["goals"] == replay["trace_checks"] == len(public) == 6
    assert replay["candidate_checks"] == len(replay["rows"]) == 12
    assert (replay["positive"], replay["negative"], replay["unknown"]) == (6, 6, 0)
    evidence = {(row["id"], row["candidate"]): row for row in replay["rows"]}
    assert len(evidence) == replay["candidate_checks"]
    for row, receipt in zip(public, private, strict=True):
        for candidate in row["candidates"]:
            outcome = evidence[(row["id"], candidate["id"])]
            recorded = receipt["outcomes"][candidate["id"]]
            assert outcome["matches"] is True
            assert type(outcome["label"]) is int and outcome["label"] == recorded["label"]
            assert outcome["status"] == recorded["status"] and outcome["axioms"] == recorded["axioms"]
            if outcome["label"] == 1:
                assert outcome["status"] == "accepted" and set(outcome["axioms"]) <= gym.prior.ALLOWED_AXIOMS
    controls = native["mutation_controls"]
    assert {row["mutation"] for row in controls} == {
        "invalid_equality", "admission", "self_reference", "future_reference",
        "zero_branch_shift", "successor_denominator_index",
    }
    assert len(controls) == 6 and all(row["rejected"] is True for row in controls)
    surface_controls = {"admission", "self_reference", "future_reference"}
    for row in controls:
        calls = 0 if row["mutation"] in surface_controls else 1
        assert type(row["kernel_calls"]) is int and row["kernel_calls"] == calls
        assert row["status"] in ({"rejected_by_surface"} if calls == 0 else {"rejected_by_lean", "rejected_axioms"})
    shifted_zero, shifted_successor = deepcopy(tasks[0]), deepcopy(tasks[1])
    shifted_zero["context"] = shifted_zero["context"].replace("(y = 0 ∧ b = a) ∨", "(y = 0 ∧ b = a + 1) ∨", 1)
    shifted_successor["statement"] = shifted_successor["statement"].replace("(den x)", "(den (x + 1))", 1)
    semantic_hashes = {
        "zero_branch_shift": gym.sha256(gym.render(shifted_zero, teachers[0]["proof"])),
        "successor_denominator_index": gym.sha256(gym.render(shifted_successor, teachers[1]["proof"])),
    }
    for row in controls:
        if row["mutation"] in semantic_hashes:
            assert row["mutated_source_sha256"] == semantic_hashes[row["mutation"]]
    assert native["native_proof_compilations"] == 1 + len(tasks) + 12 + 6 + sum(row["kernel_calls"] for row in controls)

    assert adapter["schema"] == "evalmath.rh_compactification.datagoblin_adapter_check.v1"
    assert adapter["verification_scope"] == "pinned loader execution over previously generated Lean receipts"
    assert adapter["upstream_evidence_class"] == "lean_kernel_receipt_replay"
    assert adapter["status"] == "passed" and adapter["truncated_inputs"] == 0
    assert adapter["sources"] == prior_adapter["sources"]
    assert adapter["loaders_executed"] == [pin["entrypoint"] for pin in contract["sources"].values()]
    assert adapter["split"] == "train" and adapter["model_max_bytes"] == gym.MAX_BYTES
    assert adapter["lean_processes_executed"] == adapter["training_steps"] == 0
    assert adapter["mixed_pretrain_ready"] is False
    assert adapter["pack_manifest_sha256"] == manifest_hash and adapter["contract_sha256"] == contract_hash
    assert adapter["goals"] == adapter["usable_goals"] == len(public)
    assert adapter["families"] == adapter["lineages"] == 1
    assert adapter["candidate_labels"] == {"positive": 6, "negative": 6, "unknown": 0}
    assert adapter["goal_bytes_max"] == structure["goal_bytes_max"] <= gym.MAX_BYTES
    assert adapter["candidate_bytes_max"] == structure["candidate_bytes_max"] <= gym.MAX_BYTES
    assert adapter["heldout_evaluation"] is False and adapter["scientific_effect_claim"] is False
    for key, pin in contract["sources"].items():
        assert adapter["sources"][key]["commit"] == pin["commit"]
        assert adapter["sources"][key]["verified_files"] == len(pin["files"])
        assert set(adapter["sources"][key]["file_sha256"]) == set(pin["files"])
    raw = training["raw_upstream_manifest"]
    assert training["schema"] == "EvalMath/rh-numerator-training-smoke/v1"
    assert training["evidence_class"] == "engineering smoke test using the pinned upstream PPT trainer"
    trainer_pin = contract["sources"]["looped_transformers"]
    assert training["tooling_source"] == {key: trainer_pin[key] for key in ("repository", "commit")}
    assert raw["schema"] == "ppt_gym.train.v1" and raw["source"]["split"] == "train"
    assert raw["source"]["evidence_class"] == "lean_kernel_receipt_replay"
    assert raw["model"] == {"plan": "a", "width": 32, "heads": 4, "slots": 8,
                           "max_bytes": 384, "mlp_ratio": 2, "parameter_count": 25571}
    assert training["trainer_contract_sha256"] == contract_hash
    assert raw["source"]["manifest_sha256"] == manifest_hash
    assert raw["source"]["source_evidence_sha256"] == pack["source_evidence_sha256"]
    assert raw["source"]["environment"] == pack["environment"]
    assert raw["source"]["rows"] == raw["source"]["loaded"] == training["training_cases"] == len(public)
    steps_path = gym.BASE / training["train_steps_file"]
    assert steps_path.parent == gym.BASE and steps_path.name == "training_steps.jsonl"
    steps = steps_path.read_bytes()
    assert gym.sha256(steps) == raw["train_steps_sha256"]
    assert len(steps.splitlines()) == raw["updates_completed"] == raw["requested_steps"] == 32
    logs = [json.loads(line) for line in steps.splitlines()]
    assert [row["step"] for row in logs] == list(range(1, 33))
    assert {row["root"] for row in logs} <= {row["id"] for row in public}
    assert {row["depth"] for row in logs} <= {1, 2}
    assert all(type(row["step"]) is int and type(row["depth"]) is int
               and type(row["loss"]) in (int, float) and math.isfinite(row["loss"]) for row in logs)
    assert training["observed_distinct_cases"] == len({row["root"] for row in logs}) == 6
    assert training["observed_depths"] == sorted({row["depth"] for row in logs}) == [1, 2]
    assert training["runtime"] == {"python": "3.12.14", "torch": "2.5.1+cpu", "device": "cpu",
                                   "threads": 1, "seed": 17}
    assert type(raw["training_seconds"]) in (int, float)
    assert math.isfinite(raw["training_seconds"]) and raw["training_seconds"] >= 0
    assert training["scientific_eligible"] is False and training["heldout_scored"] is False
    assert training["neural_effect_claim"] is False and training["independent_families"] == raw["train_roots"] == 1
    assert training["candidate_count"] == 12 and training["protocol_verdict"] == "REDESIGN_OR_PILOT_ONLY"

    pilot_path = gym.prior.BASE / "preflight_pilot.json"
    preflight_path = gym.prior.BASE / "preflight_report.json"
    pilot, preflight = read(pilot_path), read(preflight_path)
    planner_path = ROOT / "skills/evalmath-mechinterp-power/scripts/preflight.py"
    spec = importlib.util.spec_from_file_location("rhnum_preflight", planner_path)
    assert spec is not None and spec.loader is not None
    planner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(planner)
    assert planner.preflight(pilot) == preflight
    assert preflight["decision"] == "REDESIGN_OR_PILOT_ONLY" and preflight["pilot_worlds"] == 1
    assert curriculum["family"] == gym.prior.FAMILY and curriculum["independent_families"] == 1
    assert curriculum["confirmation"] == {"status": "unallocated", "scored": False}

    paths = set(expected_native_sources)
    paths.update(str(path.relative_to(ROOT)) for path in gym.BASE.rglob("*")
                 if path.is_file() and "__pycache__" not in path.parts)
    paths.update({str(Path(__file__).resolve().relative_to(ROOT)), "tests/test_rh_numerator_gym.py",
                  "scripts/check_rh_compactification_datagoblin.py", str(contract_path.relative_to(ROOT)),
                  str(prior_adapter_path.relative_to(ROOT)),
                  str(pilot_path.relative_to(ROOT)), str(preflight_path.relative_to(ROOT)), str(planner_path.relative_to(ROOT))})
    return {
        "schema": "EvalMath/rh-numerator-integrity/v1",
        "evidence_class": "source/schema replay with authenticated recorded native and training evidence",
        "native_execution_in_this_command": False, "training_execution_in_this_command": False,
        "source_sha256": {path: gym.sha256((ROOT / path).read_bytes()) for path in sorted(paths)},
        "counts": {"module_theorems": 8, "teacher_tasks": 8, "microsteps": 6, "candidate_labels": 12,
                   "native_mutation_controls": len(controls), "independent_families": 1,
                   "recorded_optimizer_updates": 32},
        "checks": {"source_prefixes_and_teachers_match": True, "native_sources_and_axioms_match": True,
                   "candidate_labels_bound_to_native_sources": True, "bounded_inputs_fit": True,
                   "semantic_and_proof_controls_rejected": True, "pinned_loader_evidence_bound_to_pack": True,
                   "training_step_log_and_pack_match": True, "one_public_training_family_preserved": True,
                   "preflight_reproduced_as_pilot_only": True},
        "evaluation_handoff": {
            "unit": "shared RH recurrence construction family", "n_units": 1, "n_cases": 6,
            "scored_candidate_rows": 12,
            "primary_contrast": "Future recurrent versus one-pass proof completion with matched verifier-call and token budgets",
            "physical_dose": "Future loop counts 1 versus 4; engineering smoke used depths 1 and 2",
            "scientific_variation_floor": "1/10", "matched_sham_floor": None,
            "matched_sham_source": "The earlier deterministic certificate repeats calibrate the instrument",
            "planned_comparisons": 2, "actual_effect_comparisons": 0, "estimated_resolution_power": None,
            "readout_selection_exposure": "All extension cases are public training material in the existing family",
            "causal_controls": "A future effect study requires prospective matched causal controls",
            "verdict": preflight["decision"],
            "next_evidence": "Independent source families, calibrated shams and a sealed confirmation readout",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "output/rh_numerator/gym_v1.json")
    args = parser.parse_args()
    receipt = verify()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(gym.json_text(receipt), encoding="utf-8")
    print(json.dumps({"checks": len(receipt["checks"]), "sources": len(receipt["source_sha256"]),
                      **receipt["counts"]}, sort_keys=True))


if __name__ == "__main__":
    main()
