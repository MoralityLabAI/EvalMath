"""Exact integer-count / terminal-snapshot identification witnesses."""
from fractions import Fraction as Q
import unittest

from spiral_ln.evaluation_reward_carryover_count import (
    MAX_CUES, point_mass, append_cue, after_exposures, joint_persistence,
    collapse_presence, store_after_history, terminal_cue_count,
    terminal_risk, binary_projection_failure, saturating_fixture,
    safe_completion_bounds,
)


class CountCarryoverTests(unittest.TestCase):
    def test_count_transitions_and_clearing(self):
        for n in range(MAX_CUES + 1):
            self.assertEqual(after_exposures(n), point_mass(n))
            self.assertEqual(after_exposures(n, clear_each_boundary=True),
                             point_mass(0))
        self.assertEqual(append_cue(point_mass(MAX_CUES)), point_mass(MAX_CUES))
        with self.assertRaises(ValueError):
            after_exposures(9)

    def test_exact_binomial_count_distribution(self):
        # With no cap binding after two steps and lambda=1/4:
        # P(N=0,1,2)=(9/16,6/16,1/16).
        law = after_exposures(2, write_probability=Q(1, 4))
        self.assertEqual(law[:3], (Q(9, 16), Q(6, 16), Q(1, 16)))
        self.assertEqual(sum(law), 1)
        self.assertEqual(collapse_presence(law), (Q(9, 16), Q(7, 16)))

    def test_same_binary_presence_different_terminal_response(self):
        endpoint = saturating_fixture()
        self.assertEqual(collapse_presence(point_mass(1)),
                         collapse_presence(point_mass(8)))
        self.assertNotEqual(joint_persistence(point_mass(1), endpoint),
                            joint_persistence(point_mass(8), endpoint))
        self.assertTrue(binary_projection_failure(endpoint))
        self.assertFalse(binary_projection_failure(
            {i: Q(i > 0, 2) for i in range(9)}))

    def test_final_snapshot_equivalence_and_transplant(self):
        endpoint = saturating_fixture()
        # Histories differ in execution order, then produce identical store bytes.
        chronological = tuple((f"ep-{i}", "cue") for i in range(1, 9))
        reversed_write = tuple(reversed(chronological))
        original = store_after_history(chronological)
        recipient = store_after_history(reversed_write)
        self.assertEqual(original, recipient)
        self.assertEqual(terminal_cue_count(original), 8)
        self.assertEqual(terminal_risk(original, endpoint),
                         terminal_risk(recipient, endpoint))
        self.assertEqual(terminal_risk({}, endpoint), 0)
        self.assertEqual(terminal_risk({"ep-8": "cue"}, endpoint), Q(1, 8))

    def test_required_task_completion_does_not_imply_policy_compliance(self):
        # Development dose-eight p10/p11: all 256 cases completed the
        # necessary task actions, even when unauthorized actions also occurred.
        self.assertEqual(safe_completion_bounds(256, 0, 256), (0, 0))
        self.assertEqual(safe_completion_bounds(256, 38, 256),
                         (Q(19, 128), Q(19, 128)))
        self.assertEqual(safe_completion_bounds(256, 256, 256), (1, 1))
        # If only marginal completion were known, this intersection could
        # not be uniquely recovered without the case-level joint record.
        self.assertEqual(safe_completion_bounds(256, 38, 128),
                         (0, Q(19, 128)))
        with self.assertRaises(ValueError):
            safe_completion_bounds(256, 300, 256)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            append_cue(point_mass(0), probability=Q(4, 3))
        with self.assertRaises(ValueError):
            point_mass(True)
        with self.assertRaises(ValueError):
            joint_persistence(point_mass(1), {1: Q(1, 2)})


if __name__ == "__main__":
    unittest.main()
