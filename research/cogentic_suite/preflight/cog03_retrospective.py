"""Rebuild COG-03's retrospective calibration diagnostic from published receipts.

The producer did not execute the power planner before training or opening its
readouts. This records that timing. Shuffled carried state is a destructive
sensitivity control. No matched-sham observations were collected, so the planner
must reject its input. The control envelope is computed separately.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

PRODUCER_COMMIT = "c1c903b3f0664ee19838fcba45bd67e24f779aab"
PRODUCER_TREE = "6ab92a50b3c4c527d4be2d84e3de23a4cc6b7f0f"
PRODUCER_SUBDIR = Path("research/cog03_ledger_router")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--producer-root", type=Path, required=True)
    parser.add_argument("--recorded-at", required=True)
    parser.add_argument("--out", type=Path, default=Path(__file__).parent)
    args = parser.parse_args()
    suite_repo = Path(__file__).resolve().parents[3]
    engine = suite_repo / "skills/evalmath-mechinterp-power/scripts/preflight.py"
    spec = importlib.util.spec_from_file_location("power_preflight", engine)
    planner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(planner)

    producer = args.producer_root / PRODUCER_SUBDIR
    registration_path = producer / "results/registration.json"
    episodes_path = producer / "results/episodes.jsonl"
    registration = json.loads(registration_path.read_text())
    episodes = [json.loads(line) for line in episodes_path.read_text().splitlines()]
    assert F(str(registration["minimum_meaningful_effect"])) == F(1, 10)
    assert registration["sealed_readout"] is False
    assert registration["seeds"] == [17, 29]
    seeds = registration["seeds"]
    roots = sorted(registration["roots"]["calibration"])
    assert len(roots) == len(set(roots)) == 64
    calibration = [row for row in episodes if row["split"] == "calibration"]
    indexed = {(row["root_id"], row["seed"], row["arm"]): row for row in calibration}
    expected = {(root, seed, arm) for root in roots for seed in seeds
                for arm in registration["arms"]}
    assert set(indexed) == expected and len(indexed) == len(calibration)
    assert all(type(row["solved"]) is bool for row in calibration)
    assert all(row["budget"] == 24 for row in calibration)

    rows = []
    control_magnitudes = []
    for root in roots:
        primary = [int(indexed[root, seed, "looped"]["solved"])
                   - int(indexed[root, seed, "one_pass"]["solved"])
                   for seed in seeds]
        sensitivity = [int(indexed[root, seed, "looped"]["solved"])
                       - int(indexed[root, seed, "shuffled_history"]["solved"])
                       for seed in seeds]
        rows.append({
            "unit_id": root,
            "paired_effect": str(F(sum(primary), len(seeds))),
            "sham_effects": [],
            "destructive_sensitivity_effects_by_seed": dict(zip(map(str, seeds), map(str, sensitivity))),
            "destructive_sensitivity_root_mean": str(F(sum(sensitivity), len(seeds))),
        })
        control_magnitudes.append(F(max(map(abs, sensitivity))))

    mean_effect = sum((F(row["paired_effect"]) for row in rows), F(0)) / len(rows)
    sensitivity_mean = sum((F(row["destructive_sensitivity_root_mean"]) for row in rows), F(0)) / len(rows)
    assert mean_effect == 0
    assert all(F(row["paired_effect"]) == 0 for row in rows)
    control_bound, control_rank = planner.upper_quantile(control_magnitudes, F(95, 100), F(95, 100))
    timing = "Retrospective: created after training, inspection of all producer readouts, and publication of producer PR 394."
    input_record = {
        "schema_version": 1,
        "experiment_id": "COG-03-retrospective-calibration",
        "recorded_at": args.recorded_at,
        "timing": timing,
        "preflight_executed_before_training_or_readout": False,
        "independent_unit": "source Horn DAG root; checkpoint seeds are repeated observations",
        "alpha": "0.05",
        "scientific_min_effect": "0.10",
        "target_effect": "0.10",
        "measurement_resolution": "1/128",
        "sham_quantile": "0.95",
        "sham_confidence": "0.95",
        "planned_comparisons": 8,
        "producer_comparisons_per_test_split": registration["planned_comparisons"],
        "comparison_family": "Four declared contrasts on each of ordinary_test and ood_test; eight across both readouts.",
        "confirm_units_planned": 64,
        "confirmation_count_status": "Producer nominal root count per readout; every readout has already been exposed.",
        "pilot_from_development_only": True,
        "pilot_split": "calibration",
        "heldout_sealed": False,
        "units_independent": True,
        "independence_scope": "Distinct generated roots, conditional on the two fixed trained checkpoints and the public finite task population.",
        "matched_sham_calibration_present": False,
        "destructive_control": "shuffled_history",
        "destructive_control_role": "destructive sensitivity only; permutation preserves carried-vector norm and four-pass compute",
        "empty_sham_effects_reason": "The producer collected no matched-sham calibration; destructive controls cannot fill that field.",
        "seeds": seeds,
        "pilot": rows,
    }

    # Preserve the planner's real refusal. Its required input must not be filled
    # with destructive controls under a matched-sham label.
    try:
        planner.preflight(input_record)
    except ValueError as exc:
        assert str(exc) == "matched shams required per independent world"
        engine_result = {"status": "input_rejected", "exception": "ValueError", "reason": str(exc)}
    else:
        raise AssertionError("planner unexpectedly accepted absent matched-sham calibration")

    solved = {arm: sum(indexed[root, seed, arm]["solved"] for root in roots for seed in seeds)
              for arm in ("looped", "one_pass", "shuffled_history")}
    output = {
        "schema": "COG03/retrospective-resolution-audit/v1",
        "experiment_id": input_record["experiment_id"],
        "recorded_at": args.recorded_at,
        "timing": timing,
        "decision": "REDESIGN_OR_PILOT_ONLY",
        "causal_gate_open": False,
        "reasons": ["matched_sham_calibration_absent", "heldout_unsealed", "retrospective_planning",
                    "zero_primary_effect_on_all_calibration_roots", "zero_variance_pilot_power_uninformative"],
        "planner_execution": engine_result,
        "unit": input_record["independent_unit"],
        "n_units": len(roots),
        "n_cases": len(roots) * len(seeds),
        "checkpoint_seeds": seeds,
        "primary_contrast": "looped minus independently trained one_pass root completion within 24 verifier calls",
        "physical_dose": "Four tied inner passes with previous-decision state carry; one_pass uses one inner pass and no carry.",
        "scientific_variation_floor": "1/10",
        "scientific_variation_floor_percentage_points": 10,
        "measurement_resolution": "1/128",
        "matched_sham_floor": None,
        "matched_sham_confidence": None,
        "matched_sham_source": None,
        "mechanistic_variation_floor": None,
        "mean_primary_effect": str(mean_effect),
        "primary_root_effect_distribution": dict(Counter(row["paired_effect"] for row in rows)),
        "pilot_root_effect_sigma": 0,
        "estimated_resolvable_effect": None,
        "estimated_roots_for_80_percent_power": None,
        "power_limit": "All 64 primary root effects are zero, while matched-sham variation is unmeasured. Positive-effect power cannot be extrapolated from this pilot.",
        "calibration_solved_cases": solved,
        "destructive_sensitivity_control": {
            "arm": "shuffled_history",
            "role": "destructive sensitivity control",
            "mean_completion_loss": str(sensitivity_mean),
            "mean_completion_loss_percentage_points": float(sensitivity_mean * 100),
            "root_mean_loss_distribution": dict(Counter(row["destructive_sensitivity_root_mean"] for row in rows)),
            "affected_roots": sum(magnitude > 0 for magnitude in control_magnitudes),
            "observed_worst_seed_loss": str(max(control_magnitudes)),
            "envelope_statistic": "maximum absolute seed-specific loss within each independent root",
            "quantile": "19/20",
            "confidence": "19/20",
            "upper_tolerance_bound": str(control_bound) if control_bound is not None else None,
            "order_statistic_rank": control_rank,
            "population_scope": "Conditional on fixed checkpoints and independent generated roots; this measures sensitivity to destructive permutation.",
        },
        "planned_and_actual_comparisons": {
            "producer_declared_per_test_split": 4,
            "test_splits": ["ordinary_test", "ood_test"],
            "family_across_test_splits": 8,
            "producer_inferential_primary_reports": 2,
            "producer_measured_arms_per_root": 8,
            "retrospective_calibration_primary_contrasts": 1,
        },
        "readout_selection_exposure": "calibration, ordinary_test and ood_test had been inspected before this diagnostic; only calibration rows enter this diagnostic; producer checkpoints and architecture remain unchanged",
        "causal_controls": {"reset_history": "destructive memory ablation", "reset_inner": "destructive inner-state ablation", "shuffled_history": "destructive sensitivity control", "matched_sham": "absent"},
        "evidence_class": "power-limited observation on trained tiny models and a synthetic finite Horn corpus",
        "exact_evidence_provenance": "Producer receipts bind every attempt to a finite Horn interpreter. DataGoblin separately compiled all 256 source certificates in Lean 4.35.0. Those checks certify proof validity and source provenance.",
        "further_evidence_needed": "Collect physically matched development shams and an informative primary root contrast, freeze the comparison family, then evaluate new sealed roots after resolution planning.",
    }

    args.out.mkdir(parents=True, exist_ok=True)
    input_path = args.out / "cog03_input.json"
    output_path = args.out / "cog03_output.json"
    write_json(input_path, input_record)
    write_json(output_path, output)
    source_paths = [registration_path, episodes_path, producer / "model.py",
                    producer / "run.py", producer / "analysis/SOURCE.json",
                    producer / "data/SOURCE.json"]
    sources = {
        "schema": "COG03/retrospective-resolution-sources/v1",
        "producer_repository": "MoralityLabAI/LoopedTransformers",
        "producer_published_commit": PRODUCER_COMMIT,
        "producer_tree": PRODUCER_TREE,
        "producer_pull_request": "https://github.com/MoralityLabAI/LoopedTransformers/pull/394",
        "producer_files_sha256": {str(path.relative_to(args.producer_root)): sha256(path) for path in source_paths},
        "planner_path": str(engine.relative_to(suite_repo)),
        "planner_sha256": sha256(engine),
        "builder_sha256": sha256(Path(__file__)),
        "artifacts_sha256": {path.name: sha256(path) for path in (input_path, output_path)},
        "recorded_at": args.recorded_at,
        "reproduction": "python research/cogentic_suite/preflight/cog03_retrospective.py --producer-root ../LoopedTransformers --recorded-at " + args.recorded_at,
    }
    write_json(args.out / "cog03_sources.json", sources)
    print(json.dumps({"decision": output["decision"], "roots": len(roots),
                      "paired_cases": output["n_cases"], "primary_effect": str(mean_effect),
                      "destructive_control_mean_loss": str(sensitivity_mean),
                      "matched_sham_floor": None, "planner": engine_result["status"]}))


if __name__ == "__main__":
    main()
