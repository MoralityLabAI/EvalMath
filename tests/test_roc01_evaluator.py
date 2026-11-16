"""ROC-01 EvalMath T1 bridge tests from a publicly pinned MathCan card schema."""
import unittest
from pathlib import Path
import sys

# Repository-wide installed-package pytest excludes the source root.
# Make the public source-only review package importable in that job.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from research.observer_calculus.roc01_evaluator import (
    IDEAL_TABLE, InterventionObservation, identify_types, idealized_example,
    audit_observer_card, MATHCAN_SOURCE
)
from spiral_ln.evaluation_bpd import NO_HYPOTHESIS_FITS


def arm(name,outcomes,*,measured=False,norm=False,routed=True):
    return InterventionObservation(
      name,tuple(outcomes),1,routed,measured,"checkpoint","basis",2,1,norm)


class ROC01EvaluatorTest(unittest.TestCase):
    def test_ideal_five_exemplars_need_three_arms(self):
        out=idealized_example()
        self.assertEqual(out["min_cost"],3)
        self.assertEqual(out["min_arms"],
                         ["dark_to_observed","observed_to_dark","freeze_U"])
        self.assertEqual(out["covered_pairs"],10)
        self.assertFalse(out["causal_identification_ready"])
        self.assertEqual(out["source_mathcan_sha"],MATHCAN_SOURCE)

    def test_unknown_route_remains_missing(self):
        rows=[arm(k,v,routed=k=="ablate_readout")
              for k,v in IDEAL_TABLE.items()]
        out=identify_types(rows)
        self.assertIsNone(out["min_cost"])
        self.assertTrue(out["unresolved_pairs"])
        self.assertFalse(out["causal_identification_ready"])

    def test_no_hypothesis_fits_is_explicit(self):
        rows=[arm(k,v) for k,v in IDEAL_TABLE.items()]
        out=identify_types(rows,{"dark_to_observed":2})
        self.assertEqual(out["realized"],NO_HYPOTHESIS_FITS)

    def test_valid_complete_card_gates(self):
        c={k:0.0 for k in ("A_normalized","B_normalized",
                           "C_normalized","s_causal","task_mse","D_frob","H_trace")}
        c["H_trace"]=1.0
        passed=audit_observer_card(c,random_count=128,
                 distinct_random_bases=128,per_state_rows_public=True,
                 task_only_equal_budget=True,
                 every_intervention_norm_matched=True,
                 output_declared=True)
        self.assertTrue(passed["complete"])
        insufficient=audit_observer_card(c,random_count=8,
                 distinct_random_bases=8,per_state_rows_public=True,
                 task_only_equal_budget=True,
                 every_intervention_norm_matched=True,
                 output_declared=True)
        self.assertFalse(insufficient["complete"])
        self.assertFalse(insufficient["random_rank_valid"])
        missing=audit_observer_card({k:None for k in c},
                 random_count=128,distinct_random_bases=128,
                 per_state_rows_public=True,task_only_equal_budget=True,
                 every_intervention_norm_matched=True,output_declared=True)
        self.assertFalse(missing["complete"])
        self.assertEqual(len(missing["missing_metrics"]),7)
        blank={**c,"B_normalized":""}
        self.assertIn("B_normalized",audit_observer_card(
            blank,random_count=128,distinct_random_bases=128,
            per_state_rows_public=True,task_only_equal_budget=True,
            every_intervention_norm_matched=True,
            output_declared=True)["missing_metrics"])
        self.assertFalse(audit_observer_card(
            c,random_count=128,distinct_random_bases=1,
            per_state_rows_public=True,task_only_equal_budget=True,
            every_intervention_norm_matched=True,output_declared=True)["complete"])
        self.assertFalse(audit_observer_card(
            c,random_count=128,distinct_random_bases=128,
            per_state_rows_public=False,task_only_equal_budget=True,
            every_intervention_norm_matched=True,output_declared=True)["complete"])

    def test_unmeasured_missing_controls_not_promoted(self):
        rows=[arm(k,v,measured=True,norm=True) for k,v in IDEAL_TABLE.items()]
        self.assertTrue(identify_types(rows)["finite_intervention_separation_ready"])
        self.assertFalse(identify_types(rows)["causal_identification_ready"])
        c={k:0.0 for k in ("A_normalized","B_normalized",
                           "C_normalized","s_causal","task_mse","D_frob","H_trace")}
        c["H_trace"]=1.0
        audit=audit_observer_card(
            c,random_count=128,distinct_random_bases=128,
            per_state_rows_public=True,task_only_equal_budget=True,
            every_intervention_norm_matched=True,output_declared=True)
        self.assertTrue(identify_types(rows,card_audit=audit)["causal_identification_ready"])
        changed=rows[:2]+[arm("freeze_U",IDEAL_TABLE["freeze_U"],norm=False,
                              measured=True)]+rows[3:]
        self.assertFalse(identify_types(changed)["causal_identification_ready"])
        with self.assertRaises(ValueError):
            identify_types(rows[:1]+[arm("dark_to_observed",(0,1,0,1,0))])

    def test_disparate_checkpoint_or_clock_rejected(self):
        rows=[arm(k,v) for k,v in IDEAL_TABLE.items()]
        bad=list(rows)
        bad[0]=InterventionObservation(
            bad[0].name,bad[0].outcomes,1,True,False,
            "different","basis",2,1,False)
        with self.assertRaises(ValueError):
            identify_types(bad)

if __name__=="__main__":
    unittest.main()
