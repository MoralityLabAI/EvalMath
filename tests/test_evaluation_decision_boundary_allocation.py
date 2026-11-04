"""QI-04 exact decision-boundary and rational information-oracle checks."""
import unittest
from fractions import Fraction as Q
from itertools import product

from spiral_ln.evaluation_decision_boundary_allocation import (
    TV_TOLERANCE, rate_table_from_mask, exact_quotient_radius,
    structured_supports, decision_boundary_family,
    boundary_fractional_certificate, complete_singleton_floor,
)

class DecisionBoundaryTests(unittest.TestCase):
    def test_all_64_boundary_labels_against_direct_minimax(self):
        changed_count = 0
        for mask in range(64):
            world = rate_table_from_mask(mask)
            exact = exact_quotient_radius(world, 1)
            direct = max(
                min(max(abs(row[a]-q) for row in world)
                    for q in (Q(i,20) for i in range(21)))
                for a in range(len(world[0])))
            self.assertEqual(exact, direct)
            mixed = any(len({row[a] for row in world}) == 2 for a in range(2))
            self.assertEqual(exact > TV_TOLERANCE, mixed)
            changed_count += mixed
        self.assertEqual(changed_count,60)

    def test_structured_counterfactuals_are_opposite_label(self):
        family=decision_boundary_family()
        self.assertEqual(family["baseline_tv_optimum"], 0)
        self.assertEqual(family["boundary_masks"], structured_supports())
        self.assertEqual(family["nonboundary_masks"], ())
        self.assertEqual(len(family["alternatives"]),6)
        for alt in family["alternatives"]:
            self.assertEqual(alt["one_step_tv_optimum"],Q(2,5))

    def test_exact_lp_and_rotation(self):
        expected=((Q(1),Q(1,2),Q(1),Q(1,2),Q(1),Q(1,2)),
                  (Q(1,2),Q(1),Q(1,2),Q(1),Q(1,2),Q(1)))
        for rotated,weights in zip((False,True),expected):
            result=boundary_fractional_certificate(rotated)
            self.assertEqual(result["optimal_primal"],weights)
            self.assertEqual(result["fractional_objective"],Q(9,2))
            self.assertEqual(sum(result["optimal_dual"],Q(0)),Q(9,2))
            self.assertGreater(result["kl_evidence_floor"],0)
            masks=result["family"]["boundary_masks"]
            brute=min(
                sum(x,Q(0)) for x in product((Q(0),Q(1,2),Q(1)),repeat=6)
                if all(sum((x[i] for i in range(6) if mask&(1<<i)),Q(0))>=1
                       for mask in masks))
            self.assertEqual(brute,Q(9,2))

    def test_full_candidate_family_requires_uniform(self):
        result=complete_singleton_floor()
        self.assertEqual(len(result["opposite_label_masks"]),60)
        self.assertEqual(result["unrestricted_family_fractional_objective"],6)
        self.assertEqual(result["uniform_primal"],(Q(1),)*6)
        self.assertEqual(result["singleton_dual"],(Q(1),)*6)

    def test_invalid_and_same_label_candidates(self):
        complete_action0=(1<<0)|(1<<2)|(1<<4)
        family=decision_boundary_family((complete_action0,))
        self.assertEqual(family["nonboundary_masks"],(complete_action0,))
        self.assertEqual(family["boundary_masks"],())
        with self.assertRaises(ValueError): rate_table_from_mask(64)
        with self.assertRaises(ValueError): decision_boundary_family((1,1))
        with self.assertRaises(ValueError):
            rate_table_from_mask(0,base=Q(1,2),alternative=Q(1,2))
        with self.assertRaises(ValueError):
            exact_quotient_radius(((Q(1,2),),),0)

if __name__=="__main__":
    unittest.main()
