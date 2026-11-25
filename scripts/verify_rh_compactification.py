"""Recheck curriculum integrity and recorded evidence without running Lean or training.

Fresh native execution is scripts/verify_rh_compactification_native.py. This
fast receipt authenticates the recorded source/target pairs and experiment
scope, and reruns the exact development-preflight calculation.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from spiral_ln.rh_compactification_gym import (
    ALLOWED_AXIOMS, BASE, LEAN_SOURCE, json_text, load_bundle, render, sha256,
)
from spiral_ln.rh_compactification_pack import PACK, load_pack, micro_rows


def read(name: str) -> dict:
    return json.loads((BASE / name).read_text(encoding="utf-8"))


def verify() -> dict:
    curriculum, tasks, teachers = load_bundle()
    pack, public, private = load_pack()
    micro, _ = micro_rows()
    native, adapter, training = read("native_receipt.json"), read("adapter_receipt.json"), read("training_smoke.json")
    observations, pilot, preflight = (read("preflight_" + key + ".json") for key in ("observations", "pilot", "report"))
    module_hash = sha256(LEAN_SOURCE.read_bytes())
    manifest_hash = sha256((PACK / "manifest.json").read_bytes())
    contract_hash = sha256((BASE / "trainer_contract.json").read_bytes())
    checker_hash = sha256((ROOT / "src/spiral_ln/rh_compactification_gym.py").read_bytes())
    assert native["passed"] is True and native["module_source_sha256"] == module_hash
    assert native["environment"]["checker_sha256"] == checker_hash
    assert native["module_theorems"] == len(native["module_axioms"]) == 36
    assert all(set(axioms) <= ALLOWED_AXIOMS for axioms in native["module_axioms"].values())
    assert native["teachers"]["passes"] == native["teachers"]["tasks"] == len(tasks) == 20
    for task, teacher, receipt in zip(tasks, teachers, native["teachers"]["outcomes"], strict=True):
        assert task["id"] == teacher["id"] == receipt["id"]
        assert receipt["label"] == 1 and receipt["closed"] is True and receipt["kernel_ok"] is True
        assert receipt["kernel_calls"] == 1 and set(receipt["axioms"]) <= ALLOWED_AXIOMS
        assert receipt["source_sha256"] == sha256(render(task, teacher["proof"]))
        assert receipt["statement_sha256"] == task["statement_sha256"]
    assert native["candidate_pack"]["matches"] is True
    assert native["candidate_pack"]["candidate_checks"] == 24 and native["candidate_pack"]["trace_checks"] == 12
    by_candidate = {(row["id"], row["candidate"]): row for row in native["candidate_pack"]["rows"]}
    for row, receipt in zip(public, private, strict=True):
        for candidate in row["candidates"]:
            evidence = by_candidate[(row["id"], candidate["id"])]
            assert evidence["matches"] is True
            assert evidence["label"] == receipt["outcomes"][candidate["id"]]["label"]
    assert all(row["rejected"] for row in native["mutation_controls"])
    assert adapter["status"] == "passed" and adapter["truncated_inputs"] == 0
    assert adapter["pack_manifest_sha256"] == manifest_hash and adapter["contract_sha256"] == contract_hash
    assert adapter["goals"] == len(public) == 12 and adapter["families"] == adapter["lineages"] == 1
    assert adapter["candidate_labels"] == {"positive": 12, "negative": 12, "unknown": 0}
    assert training["trainer_contract_sha256"] == contract_hash
    raw = training["raw_upstream_manifest"]
    assert raw["source"]["manifest_sha256"] == manifest_hash
    steps = (BASE / training["train_steps_file"]).read_bytes()
    assert sha256(steps) == raw["train_steps_sha256"]
    assert len(steps.splitlines()) == raw["updates_completed"] == raw["requested_steps"] == 32
    assert training["scientific_eligible"] is False and training["heldout_scored"] is False
    assert training["independent_families"] == raw["train_roots"] == 1
    assert training["protocol_verdict"] == "REDESIGN_OR_PILOT_ONLY"
    assert observations["construction_families"] == 1 and observations["neural_effect_estimate"] is None
    assert observations["certificate_replay_calls"] == 8 and all(observations["checks"].values())
    for relative, digest in observations["source_sha256"].items():
        assert sha256((ROOT / relative).read_bytes()) == digest, relative
    planner_path = ROOT / "skills/evalmath-mechinterp-power/scripts/preflight.py"
    spec = importlib.util.spec_from_file_location("rhcg_preflight", planner_path)
    assert spec is not None and spec.loader is not None
    planner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(planner)
    assert planner.preflight(pilot) == preflight
    assert preflight["decision"] == "REDESIGN_OR_PILOT_ONLY" and preflight["pilot_worlds"] == 1
    assert pilot["heldout_sealed"] is False and pilot["units_independent"] is False
    for filename, expected in observations["frozen_blobs"].items():
        raw_file = (ROOT / "research/rh_pl01" / filename).read_bytes()
        assert hashlib.sha1(b"blob " + str(len(raw_file)).encode() + b"\0" + raw_file).hexdigest() == expected
    paths = {
        "src/spiral_ln/rh_compactification_gym.py", "src/spiral_ln/rh_compactification_pack.py",
        "scripts/verify_rh_compactification.py", "scripts/verify_rh_compactification_native.py",
        "scripts/check_rh_compactification_datagoblin.py", "scripts/prepare_rh_compactification_preflight.py",
        "research/rh_pl01/gym_preflight.mjs", "lean/FeedbackChannel/RHCompactification.lean",
        "tests/test_rh_compactification_gym.py", "tests/test_rh_compactification_pack.py",
    }
    paths.update(observations["source_sha256"])
    for path in BASE.rglob("*"):
        if path.is_file() and (path.suffix in (".json", ".jsonl", ".py", ".in")):
            paths.add(str(path.relative_to(ROOT)))
    return {
        "schema": "EvalMath/rh-compactification-integrity/v1",
        "evidence_class": "source/schema replay with authenticated recorded native and training evidence",
        "native_execution_in_this_command": False, "training_execution_in_this_command": False,
        "source_sha256": {path: sha256((ROOT / path).read_bytes()) for path in sorted(paths)},
        "counts": {"module_theorems": 36, "teacher_tasks": 20, "microsteps": 12, "candidate_labels": 24,
                   "independent_families": 1, "recorded_optimizer_updates": 32},
        "checks": {
            "source_prefixes_and_teachers_match": True, "native_targets_bound_to_source": True,
            "recorded_axioms_allowed": True, "candidate_labels_bound_to_native_sources": True,
            "bounded_goals_and_tactics_fit": True, "upstream_loader_receipts_bound_to_pack": True,
            "training_step_log_and_pack_match": True, "one_public_training_family_preserved": True,
            "preflight_reproduced_as_pilot_only": True, "instrument_sources_current": True,
            "frozen_kernel_and_rh_targets_unchanged": True,
        },
        "evaluation_handoff": {
            "unit": "shared RH recurrence construction family", "n_units": 1,
            "n_cases": 12, "scored_candidate_rows": 24,
            "primary_contrast": "Future recurrent versus one-pass completion, equal verifier-call and token budgets",
            "physical_dose": "Future loop counts 1 versus 4; engineering smoke used ranking depths 1 and 2",
            "scientific_variation_floor": "1/10", "matched_sham_floor": None,
            "matched_sham_source": "Deterministic certificate repeats calibrate the instrument only",
            "planned_comparisons": 2, "actual_effect_comparisons": 0,
            "estimated_resolution_power": None, "readout_selection_exposure": "all current cases public for training",
            "causal_controls": "prospective matched controls required before an effect study",
            "verdict": preflight["decision"],
            "next_evidence": "Independently developed roots, calibrated causal shams and a sealed confirmation readout",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "output/rh_compactification/gym_v1.json")
    args = parser.parse_args()
    receipt = verify()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json_text(receipt), encoding="utf-8")
    print(json.dumps({"checks": len(receipt["checks"]), "sources": len(receipt["source_sha256"]),
                      **receipt["counts"]}, sort_keys=True))


if __name__ == "__main__":
    main()
