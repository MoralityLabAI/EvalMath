"""Exact integer-count / terminal-snapshot identification witnesses."""
from fractions import Fraction as Q
from itertools import product
from math import comb
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
        # The histories produce equal mappings under this count interface.
        # Byte identity would additionally require a fixed serialization rule.
        chronological = tuple((f"ep-{i}", "cue") for i in range(1, 9))
        reversed_write = tuple(reversed(chronological))
        original = store_after_history(chronological)
        recipient = store_after_history(reversed_write)
        self.assertEqual(original, recipient)
        self.assertNotEqual(tuple(original.items()), tuple(recipient.items()))
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

    def test_every_finite_horizon_matches_exact_binomial_formula(self):
        for h, numerator in product(range(9), range(9)):
            p = Q(numerator, 8)
            expected = tuple(Q(comb(h, k)) * p ** k * (1 - p) ** (h - k)
                             if k <= h else Q(0) for k in range(9))
            self.assertEqual(after_exposures(h, write_probability=p), expected)
            self.assertEqual(after_exposures(h, write_probability=p, clear_each_boundary=True),
                             point_mass(0))

    def test_frechet_extrema_from_independent_binary_assignments(self):
        for n in range(1, 6):
            attained = {}
            for cases in product(range(4), repeat=n):
                clean = sum(case // 2 for case in cases)
                completed = sum(case % 2 for case in cases)
                intersection = sum(case == 3 for case in cases)
                attained.setdefault((clean, completed), set()).add(intersection)
            for counts, intersections in attained.items():
                self.assertEqual(safe_completion_bounds(n, *counts),
                                 (Q(min(intersections), n), Q(max(intersections), n)))

    def test_probabilities_and_flags_validate_at_zero_horizon(self):
        for bad in (0.5, True, False):
            with self.assertRaises(TypeError):
                after_exposures(0, write_probability=bad)
            with self.assertRaises(TypeError):
                append_cue(point_mass(0), probability=bad)
        for bad in (Q(-1, 8), Q(9, 8)):
            with self.assertRaises(ValueError):
                after_exposures(0, write_probability=bad)
        for bad in (0, 1, "false", None):
            with self.assertRaises(ValueError):
                after_exposures(0, clear_each_boundary=bad)

    def test_endpoint_validates_unused_states_and_integer_key_types(self):
        for invalid in (Q(-1, 8), Q(9, 8), True, 0.5):
            endpoint = saturating_fixture()
            endpoint[0] = invalid
            for evaluate in (lambda: binary_projection_failure(endpoint),
                             lambda: terminal_risk({"a": "cue"}, endpoint),
                             lambda: joint_persistence(point_mass(8), endpoint)):
                with self.assertRaises((ValueError, TypeError)):
                    evaluate()
        for replacement in (False, 0.0, "0"):
            endpoint = saturating_fixture()
            del endpoint[0]
            endpoint[replacement] = Q(0)
            with self.assertRaises(ValueError):
                binary_projection_failure(endpoint)
        with self.assertRaises(ValueError):
            terminal_risk({"a": "cue"}, {1: Q(1, 2)})

    def test_terminal_store_validates_keys_and_last_write_semantics(self):
        for key in ("", " ", 0, True, None):
            with self.assertRaises(ValueError):
                terminal_cue_count({key: "cue"})
            with self.assertRaises(ValueError):
                store_after_history(((key, "cue"),))
        self.assertEqual(store_after_history((("a", "cue"), ("a", "sham"))),
                         {"a": "sham"})
        with self.assertRaises(ValueError):
            terminal_cue_count({str(i): "cue" for i in range(9)})


if __name__ == "__main__":
    unittest.main()
