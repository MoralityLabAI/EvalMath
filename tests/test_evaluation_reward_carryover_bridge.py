"""CPU-only exact checks for the eight-root RHT-26 empirical bridge."""
import unittest
from fractions import Fraction as Q

from spiral_ln.evaluation_reward_carryover_bridge import (
    JointCounts, complete_pilot_fixture, factorial_contrasts,
    hoeffding_floor_planning, independent_write_threshold,
    selected_denominator_decomposition,
)


class RHT26BridgeTests(unittest.TestCase):
    def test_exact_four_arm_joint_contrasts(self):
        arms=complete_pilot_fixture()
        self.assertEqual(factorial_contrasts(arms), {
            "artifact_frozen":Q(121,128),
            "learning_clean":Q(0),
            "combined":Q(11,64),
            "interaction":Q(-99,128),
            "update_given_artifact":Q(-99,128),
        })
        self.assertEqual(arms["p11"].before,Q(218,256))
        self.assertEqual(arms["p11"].persistence_given_before,Q(44,218))
        self.assertEqual(arms["p11"].recovered_given_before,Q(174,218))
        self.assertIsNone(arms["p01"].persistence_given_before)

    def test_selected_denominator_decomposition(self):
        arms=complete_pilot_fixture()
        before,survival,total=selected_denominator_decomposition(arms["p10"],arms["p11"])
        self.assertEqual(before,Q(-2299,16384))
        self.assertEqual(survival,Q(-10373,16384))
        self.assertEqual(total,Q(-99,128))

    def test_threshold_model_exact_and_monotone(self):
        for q in (Q(0),Q(1,4),Q(3,4),Q(1)):
            for threshold in (1,2,3,8):
                values=[independent_write_threshold(t,threshold,q) for t in range(10)]
                self.assertEqual(values,sorted(values))
                self.assertTrue(all(0 <= v <= 1 for v in values))
        self.assertEqual(independent_write_threshold(2,2,Q(3,4)),Q(9,16))
        self.assertEqual(independent_write_threshold(0,1,Q(1)),Q(0))

    def test_fsi01_root_bound_is_separate_from_normal_power(self):
        params=dict(floor=Q(1,20),comparisons=4,alpha=Q(1,20),confirm_roots=64)
        weak=hoeffding_floor_planning(target=Q(1,10),**params)
        self.assertEqual(weak["min_roots_if_observed_mean_equals_target"],3506)
        strong=hoeffding_floor_planning(target=Q(121,128),**params)
        self.assertEqual(strong["min_roots_if_observed_mean_equals_target"],11)
        combined=hoeffding_floor_planning(target=Q(11,64),**params)
        self.assertEqual(combined["min_roots_if_observed_mean_equals_target"],591)
        negative_interaction=hoeffding_floor_planning(
            target=Q(99,256), floor=Q(1,40),comparisons=4,
            alpha=Q(1,20),confirm_roots=64)
        self.assertEqual(negative_interaction["min_roots_if_observed_mean_equals_target"],67)

    def test_validation_and_undefined_conditionals(self):
        for args in ((0,0,0,0),(-1,0,0,1),(1,0,False,0)):
            with self.assertRaises(ValueError):JointCounts(*args)
        with self.assertRaises(ValueError):
            factorial_contrasts({"p10":JointCounts(1,0,0,0)})
        with self.assertRaises(ValueError):
            selected_denominator_decomposition(JointCounts(1,0,0,0),JointCounts(0,0,0,1))
        with self.assertRaises(ValueError):
            independent_write_threshold(2,2,Q(2))
        with self.assertRaises(ValueError):
            hoeffding_floor_planning(target=Q(1,20),floor=Q(1,10),
                                     comparisons=4,alpha=Q(1,20))


if __name__ == "__main__":
    unittest.main()
