"""Independent exact HG-05 theorem checks and boundary controls."""
import random
import unittest
from fractions import Fraction as Q
from itertools import product
from spiral_ln.evaluation_hypergames_rank import (
    rank, deficiency, exact_joint_success, independent_fibre_success,
    minimum_probe_cost, ideal_action_values, padding_invariant,
)


class HG05RankTheorems(unittest.TestCase):
    def test_fibre_matches_rank_for_all_small_matrix_patterns(self):
        comparisons = 0
        for d in range(1, 5):
            masks = range(1 << d)
            for c in product(masks, repeat=2):
                for p in product(masks, repeat=2):
                    self.assertEqual(exact_joint_success(c, p, d),
                                     independent_fibre_success(c, p, d))
                    comparisons += 1
        self.assertEqual(comparisons, sum(1 << (4*d) for d in range(1, 5)))

    def test_random_larger_finite_oracle(self):
        rng = random.Random(20261117)
        for d in (5, 6, 8, 10):
            for _ in range(25):
                c = tuple(rng.randrange(1 << d) for __ in range(3))
                p = tuple(rng.randrange(1 << d) for __ in range(3))
                self.assertEqual(independent_fibre_success(c, p, d),
                                 exact_joint_success(c, p, d))

    def test_independent_disjoint_goals(self):
        for d, k in ((140, 1), (140, 16), (512, 16), (1024, 16)):
            goals = tuple((1 << (6*i)) | (1 << (6*i+1)) for i in range(k))
            self.assertEqual(rank(goals, d), k)
            self.assertEqual(deficiency([], goals, d), k)
            self.assertEqual(exact_joint_success([], goals, d), Q(1, 1 << k))
            self.assertEqual(deficiency(goals[:k//2], goals, d), k-k//2)

    def test_adding_observations_never_increases_deficiency(self):
        p = (1, 2, 4, 8)
        self.assertEqual([deficiency(p[:i], p, 4) for i in range(5)], [4, 3, 2, 1, 0])

    def test_padding(self):
        self.assertTrue(padding_invariant((3, 5), (9, 10), 7, 1024))
        with self.assertRaises(ValueError):
            padding_invariant((1,), (2,), 4, 3)

    def test_probes_needed_equals_missing_rank_for_unit_goal_rows(self):
        p = (1, 2, 4, 8, 16)
        for seen in range(6):
            result = minimum_probe_cost(p[:seen], p, p, (Q(1),)*5, 5)
            self.assertEqual(result['cost'], Q(5-seen))

    def test_weighted_audits_joint_probe_advantage(self):
        # A cheap probe for a missing parity can replace the expensive direct probe.
        result = minimum_probe_cost((1,), (1, 2), (2, 3), (Q(5), Q(1)), 2)
        self.assertEqual(result['indices'], (1,))
        self.assertEqual(result['cost'], Q(1))

    def test_infeasible_spanning(self):
        self.assertEqual(minimum_probe_cost((1,), (2,), (1,), (Q(1),), 2)['status'], 'infeasible')

    def test_rank_belief_thresholds(self):
        self.assertEqual(ideal_action_values(0)['submit'], Q(10))
        self.assertEqual(ideal_action_values(1)['submit'], Q(-5, 2))
        self.assertEqual(ideal_action_values(1)['semantic_audit_then_submit'], Q(9))
        self.assertEqual(ideal_action_values(16)['semantic_audit_then_submit'], Q(-6))

    def test_strict_fail_closed(self):
        bad = (([1 << 5], (), 4), ([True], (), 4), ([-1], (), 4))
        for c, p, d in bad:
            with self.assertRaises(ValueError):
                deficiency(c, p, d)
        with self.assertRaises(ValueError):
            independent_fibre_success((), (), 11)
        with self.assertRaises(ValueError):
            minimum_probe_cost((), (1,), (1,), (1,), 2)
        with self.assertRaises(ValueError):
            ideal_action_values(True)


if __name__ == '__main__':
    unittest.main()
