"""FSI-01 terminal-decision bound vs the normal-approximation pilot planner.

These are pure CPU regression fixtures. They are not observations from the
sealed confirmation cohort, nor a new empirical calibration.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

mod_path = Path(__file__).with_name("preflight.py")
spec = importlib.util.spec_from_file_location("preflight_rht26_fsi", mod_path)
pf = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(pf)


def manifest(*, target="1/10", floor="1/20", resolution="1/32",
             observations="121/128", comparisons=4, planned=64, opt_in=True):
    return {
        "schema_version": 1,
        "experiment_id": "RHT26-FSI01-CPU-REGRESSION",
        "independent_unit": "independent source-and-target family",
        "alpha": "1/20",
        "scientific_min_effect": floor,
        "target_effect": target,
        "measurement_resolution": resolution,
        "sham_quantile": "19/20",
        "sham_confidence": "19/20",
        "planned_comparisons": comparisons,
        "confirm_units_planned": planned,
        "pilot_from_development_only": True,
        "heldout_sealed": True,
        "units_independent": True,
        "require_final_fsi_gate": opt_in,
        "pilot": [
            {"unit_id": f"synthetic-{i:03d}",
             "paired_effect": observations if i % 2 else "15/16",
             "sham_effects": ["0"]}
            for i in range(64)
        ],
    }


class FSI01PlanningGate(unittest.TestCase):
    def test_rht26_four_comparison_target_not_resolvable_at_64(self):
        out = pf.preflight(manifest())
        gate = out["fsi01_final_effect_floor_resolution"]
        self.assertEqual(gate["minimum_roots_at_target"], 3506)
        self.assertGreater(gate["minimum_effect_for_planned_roots"], 0.42)
        self.assertFalse(gate["target_resolves_floor_at_planned_roots"])
        self.assertIn("fsi01_target_effect_floor_underresolved", out["reasons"])
        # The observed high pilot mean is displayed only as a descriptive sensitivity.
        self.assertGreater(gate["development_only_observed_mean_lower_bound"], 0.05)

    def test_interaction_half_scale_requires_14023_independent_roots(self):
        # Raw interaction support [-2,2]: target=.10/2, floor=.05/2, grid=(1/32)/2.
        out = pf.preflight(manifest(
            target="1/20", floor="1/40", resolution="1/64", observations="1/2"))
        gate = out["fsi01_final_effect_floor_resolution"]
        self.assertEqual(gate["root_effect_support"], "[-1,1]")
        self.assertEqual(gate["minimum_roots_at_target"], 14023)
        self.assertIn("fsi01_target_effect_floor_underresolved", out["reasons"])

    def test_raised_prospective_target_clears_final_rule_resolution(self):
        out = pf.preflight(manifest(target="3/5", observations="3/4"))
        self.assertTrue(out["fsi01_final_effect_floor_resolution"][
            "target_resolves_floor_at_planned_roots"])
        self.assertNotIn("fsi01_target_effect_floor_underresolved", out["reasons"])

    def test_previous_clients_remain_planning_only_by_default(self):
        out = pf.preflight(manifest(opt_in=False))
        self.assertFalse(out["fsi01_rule_required_for_readiness"])
        self.assertFalse(out["fsi01_final_effect_floor_resolution"][
            "target_resolves_floor_at_planned_roots"])
        self.assertNotIn("fsi01_target_effect_floor_underresolved", out["reasons"])

    def test_invalid_opt_in_rejected(self):
        bad = manifest()
        bad["require_final_fsi_gate"] = "true"
        with self.assertRaisesRegex(ValueError, "boolean"):
            pf.preflight(bad)


if __name__ == "__main__":
    unittest.main()
