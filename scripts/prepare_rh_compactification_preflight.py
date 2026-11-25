"""Regenerate the RH gym instrument calibration and its strict preflight.

The four certificates stay grouped as one public construction family. Their
repeatability is instrument evidence; no neural model effect is measured.
The expected planner result is REDESIGN_OR_PILOT_ONLY, and this command preserves
the planner's strict exit status 2 after writing all three artifacts.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "gyms" / "RHCompactification"
NODE_SCRIPT = ROOT / "research" / "rh_pl01" / "gym_preflight.mjs"
PLANNER = ROOT / "skills" / "evalmath-mechinterp-power" / "scripts" / "preflight.py"
UNIT = "rh-prefix-recurrence-family"
EXPECTED_THEOREMS = ["ordered_pair_exists", "ordered_pair_injectivity",
                     "ordered_pair_double_power_bound", "singleton_graph_application"]


def pilot_from_observations(observations: dict) -> dict:
    rows = observations["observations"]
    if ([row["theorem"] for row in rows] != EXPECTED_THEOREMS
            or observations["unit_id"] != UNIT
            or observations["construction_families"] != 1
            or observations["units_independent"] is not False
            or observations["neural_model_run"] is not False
            or observations["neural_effect_estimate"] is not None
            or not all(observations["checks"].values())):
        raise ValueError("instrument calibration identity or scope changed")
    if any(row["first"] != row["repeat"] for row in rows):
        raise ValueError("repeated certificate replay differs")
    delta = Fraction(observations["instrument_paired_completion_delta"])
    if delta != 0:
        raise ValueError("instrument repeatability failed")
    return {
        "alpha": "1/20",
        "confirm_units_planned": 128,
        "experiment_id": "RH-PL-17-Lean-gym-readiness",
        "future_confirmation_count_status": "Planning input only; no confirmation data allocated or opened.",
        "heldout_sealed": False,
        "independent_unit": "the shared RH recurrence construction family (all prerequisite and renamed tasks stay grouped)",
        "measurement_resolution": "1/128",
        "observation_count": len(rows),
        "observations_file": "preflight_observations.json",
        "physical_dose": "Future planned loop counts 1 versus 4; same source context, output-token cap, verifier calls, and checkpoint data exposure.",
        "pilot": [{"paired_effect": str(delta), "sham_effects": [str(delta)], "unit_id": UNIT}],
        "pilot_from_development_only": True,
        "pilot_scope": "Deterministic verifier instrument calibration only: four prerequisite certificates replayed twice with byte-identical results, grouped as one construction family. No neural model was run; these observations cannot estimate a neural loop effect.",
        "planned_comparisons": 2,
        "proposed_primary_contrast": "Paired Lean-certified completion fraction: recurrent policy versus one-pass policy at equal verifier-call budget; second comparison against matched-compute feedforward policy.",
        "readout_selection_exposure": "All present theorem tasks are public training/development material. Fresh external confirmation families have not been generated.",
        "schema_version": 1,
        "scientific_min_effect": "1/10",
        "sham_confidence": "19/20",
        "sham_quantile": "19/20",
        "target_effect": "1/5",
        "units_independent": False,
    }


def prepare(output: Path, node: str = "node") -> int:
    output.mkdir(parents=True, exist_ok=True)
    observations_path = output / "preflight_observations.json"
    pilot_path, report_path = output / "preflight_pilot.json", output / "preflight_report.json"
    measured = subprocess.run([node, str(NODE_SCRIPT), "--output", str(observations_path)],
                              cwd=ROOT, capture_output=True, text=True)
    if measured.returncode:
        raise RuntimeError("certificate calibration failed: " + measured.stderr[-4000:])
    observations = json.loads(observations_path.read_text(encoding="utf-8"))
    pilot = pilot_from_observations(observations)
    pilot_path.write_text(json.dumps(pilot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    planned = subprocess.run([sys.executable, str(PLANNER), "--pilot", str(pilot_path),
                              "--out", str(report_path), "--strict"],
                             cwd=ROOT, capture_output=True, text=True)
    if planned.returncode != 2:
        raise RuntimeError("expected strict preflight status 2; received "
                           + str(planned.returncode) + ": " + planned.stderr[-4000:])
    report = json.loads(report_path.read_text(encoding="utf-8"))
    required_reasons = {"heldout_unsealed", "independence_unverified", "sham_quantile_uncalibrated",
                        "too_few_pilot_worlds", "pilot_effect_not_above_mechanistic_variation_floor",
                        "confirmation_underpowered"}
    if (report["decision"] != "REDESIGN_OR_PILOT_ONLY" or report["pilot_worlds"] != 1
            or report["planned_confirmation_worlds"] != 128 or report["planned_comparisons"] != 2
            or not required_reasons <= set(report["reasons"])):
        raise ValueError("instrument-only pilot no longer preserves the expected closed readiness gate")
    print(json.dumps({"decision": report["decision"], "planner_strict_exit_code": planned.returncode,
                      "observations": len(observations["observations"]), "construction_families": 1,
                      "neural_model_run": False, "neural_effect_estimate": None,
                      "confirmation_allocated": False,
                      "scope": "Instrument calibration reproduced; confirmation readiness remains unestablished.",
                      "files": [str(observations_path), str(pilot_path), str(report_path)]},
                     indent=2, sort_keys=True))
    return planned.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--node", default="node", help="Node executable for certificate regeneration")
    args = parser.parse_args()
    return prepare(args.output_dir.resolve(), args.node)


if __name__ == "__main__":
    raise SystemExit(main())
