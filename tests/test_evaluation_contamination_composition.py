"""Independent finite-path checks and failure witnesses for RHT-28."""
from fractions import Fraction as Q
from itertools import product
import random
import unittest

from spiral_ln.evaluation_finite_kernels import Kernel, identity, point_mass
from spiral_ln.evaluation_contamination_composition import (
    composition_certificate, path_coupling_bound, risk_certificate, trace_law,
    trace_total_variation, unrolled_contributions,
)


def independent_paths(start, kernels):
    sizes = [len(start)] + [len(kernel.rows[0]) for kernel in kernels]
    result = {}
    for path in product(*(range(size) for size in sizes)):
        mass = Q(start[path[0]])
        for time in range(len(kernels)):
            mass *= kernels[time].rows[path[time]][path[time + 1]]
        result[path] = mass
    return result


def independent_tv(left, right):
    return sum((abs(left[key] - right[key]) for key in left), Q(0)) / 2


class CompositionTests(unittest.TestCase):
    def test_zero_horizon_keeps_initial_distance(self):
        p, q = (Q(3, 4), Q(1, 4)), (Q(1, 4), Q(3, 4))
        result = composition_certificate(p, q, (), ())
        self.assertEqual(result.initial_tv, Q(1, 2))
        self.assertEqual(result.final_tv, result.terminal_bound)
        self.assertEqual(result.unrolled_bound, Q(1, 2))
        self.assertEqual(result.initial_contribution, Q(1, 2))
        self.assertEqual(result.injection_contributions, ())
        self.assertEqual(trace_law(p, ()).paths, ((0,), (1,)))
        self.assertEqual(trace_total_variation(p, q, (), ()), Q(1, 2))

    def test_initial_distance_contracts_in_current_state_only(self):
        contraction = Kernel(((1, 0), (Q(1, 2), Q(1, 2))))
        for horizon in range(9):
            result = composition_certificate((1, 0), (0, 1),
                                             (contraction,) * horizon,
                                             (contraction,) * horizon)
            self.assertEqual(result.final_tv, Q(1, 2) ** horizon)
            self.assertEqual(result.terminal_bound, result.final_tv)
            self.assertEqual(result.trace_bound, 1)
            self.assertTrue(all(step.epsilon == 0 for step in result.steps))

    def test_repeated_injection_has_sharp_geometric_bound(self):
        for hazard in (Q(0), Q(1, 4), Q(1)):
            poisoned = Kernel(((1 - hazard, hazard), (0, 1)))
            clean = identity(2)
            for horizon in range(7):
                result = composition_certificate((1, 0), (1, 0),
                                                 (poisoned,) * horizon,
                                                 (clean,) * horizon)
                expected = 1 - (1 - hazard) ** horizon
                self.assertEqual(result.final_tv, expected)
                self.assertEqual(result.terminal_bound, expected)
                self.assertEqual(result.trace_bound, expected)
                self.assertEqual(trace_total_variation((1, 0), (1, 0),
                                                      (poisoned,) * horizon,
                                                      (clean,) * horizon), expected)

    def test_unrolled_formula_preserves_initial_term_and_time_order(self):
        initial, injections = unrolled_contributions(
            Q(1, 2), (Q(1, 4), Q(1, 8), 0), (Q(1, 2), Q(3, 4), Q(1, 3)))
        self.assertEqual(initial, Q(1, 16))
        self.assertEqual(injections, (Q(1, 16), Q(1, 24), 0))
        self.assertEqual(initial + sum(injections), Q(1, 6))
        self.assertEqual(unrolled_contributions(Q(2, 3), (), ()), (Q(2, 3), ()))

    def test_clipping_before_later_contraction_can_strengthen_bound(self):
        same = identity(2)
        swap = Kernel(((0, 1), (1, 0)))
        contraction = Kernel(((1, 0), (Q(1, 2), Q(1, 2))))
        result = composition_certificate((1, 0), (1, 0),
                                         (same, same, contraction),
                                         (swap, swap, contraction))
        self.assertEqual(result.final_tv, 0)
        self.assertEqual(result.recurrence_bound, Q(1, 2))
        self.assertEqual(result.unrolled_bound, 1)
        self.assertEqual(sum(result.injection_contributions), 1)

    def test_either_triangle_orientation_licenses_minimum_delta(self):
        reset = Kernel(((Q(1, 2), Q(1, 2)),) * 2)
        same = identity(2)
        for left, right in ((reset, same), (same, reset)):
            result = composition_certificate((1, 0), (0, 1), (left,), (right,))
            self.assertEqual(result.steps[0].delta, 0)
            self.assertEqual(result.steps[0].epsilon, Q(1, 2))
            self.assertEqual(result.terminal_bound, Q(1, 2))

    def test_state_reset_does_not_erase_earlier_harm(self):
        harm = Kernel(((0, 1),) * 2)
        reset = Kernel(((1, 0),) * 2)
        result = composition_certificate((1, 0), (1, 0), (harm, reset), (reset, reset))
        self.assertEqual(result.final_tv, 0)
        self.assertEqual(result.terminal_bound, 0)
        self.assertEqual(result.trace_bound, 1)
        left, right = trace_law((1, 0), (harm, reset)), trace_law((1, 0), (reset, reset))
        ever_harm_left = sum(mass for path, mass in zip(left.paths, left.probabilities) if 1 in path)
        ever_harm_right = sum(mass for path, mass in zip(right.paths, right.probabilities) if 1 in path)
        self.assertEqual((ever_harm_left, ever_harm_right), (1, 0))
        self.assertEqual(trace_total_variation((1, 0), (1, 0), (harm, reset), (reset, reset)), 1)

    def test_absorbing_ever_harm_flag_preserves_endpoint_evidence(self):
        # States: clean, currently harmful with history, reset with harmful history.
        harm = Kernel(((0, 1, 0),) * 3)
        reset = Kernel(((1, 0, 0), (0, 0, 1), (0, 0, 1)))
        result = composition_certificate((1, 0, 0), (1, 0, 0),
                                         (harm, reset), (reset, reset))
        self.assertEqual(result.final_p, (0, 0, 1))
        self.assertEqual(result.final_q, (1, 0, 0))
        self.assertEqual(result.final_tv, 1)
        risk = risk_certificate(result, (0, 1, 1))
        self.assertEqual(risk.absolute_gap, 1)

    def test_changed_endpoint_oracle_is_a_separate_discrepancy(self):
        result = composition_certificate((1,), (1,), (), ())
        protected = risk_certificate(result, (1,))
        changed = risk_certificate(result, (1,), (0,))
        self.assertEqual(protected.absolute_gap, 0)
        self.assertEqual(protected.actual_risk_upper_bound, 1)
        self.assertEqual(changed.endpoint_discrepancy, 1)
        self.assertEqual(changed.gap_bound, 1)
        self.assertEqual(changed.absolute_gap, 1)

    def test_fractional_loss_and_nonzero_reference_risk(self):
        result = composition_certificate((Q(1, 2), Q(1, 2)), (1, 0), (), ())
        risk = risk_certificate(result, (Q(1, 4), Q(3, 4)))
        self.assertEqual(risk.actual_risk, Q(1, 2))
        self.assertEqual(risk.reference_risk, Q(1, 4))
        self.assertEqual(risk.absolute_gap, Q(1, 4))
        self.assertEqual(risk.actual_risk_upper_bound, Q(3, 4))

    def test_average_row_discrepancy_cannot_replace_uniform_maximum(self):
        same = identity(2)
        reset = Kernel(((1, 0),) * 2)
        result = composition_certificate((0, 1), (0, 1), (same,), (reset,))
        self.assertEqual(result.steps[0].epsilon, 1)
        self.assertEqual(result.final_tv, 1)
        average_over_rows = Q(1, 2)
        self.assertGreater(result.final_tv, average_over_rows)

    def test_varying_state_spaces_and_independent_path_oracle(self):
        rng = random.Random(2801)
        for _ in range(24):
            schedules = []
            for _side in range(2):
                kernels = []
                for source_size, target_size in ((2, 3), (3, 2), (2, 1)):
                    rows = []
                    for _row in range(source_size):
                        weights = [rng.randint(1, 5) for _ in range(target_size)]
                        rows.append(tuple(Q(w, sum(weights)) for w in weights))
                    kernels.append(Kernel(tuple(rows)))
                schedules.append(tuple(kernels))
            p, q = (Q(1, 3), Q(2, 3)), (Q(3, 4), Q(1, 4))
            expected_p, expected_q = independent_paths(p, schedules[0]), independent_paths(q, schedules[1])
            result = composition_certificate(p, q, *schedules)
            observed = trace_law(p, schedules[0])
            self.assertEqual(dict(zip(observed.paths, observed.probabilities)), expected_p)
            actual_path_tv = independent_tv(expected_p, expected_q)
            self.assertEqual(trace_total_variation(p, q, *schedules), actual_path_tv)
            self.assertLessEqual(actual_path_tv, result.trace_bound)
            self.assertEqual(result.final_tv, 0)

    def test_trace_resource_guard_checks_complete_product_before_allocation(self):
        with self.assertRaisesRegex(ValueError, "exceeds max_paths"):
            trace_law((1, 0), (identity(2),) * 20, max_paths=1024)
        self.assertEqual(len(trace_law((1, 0), (identity(2),), max_paths=4).paths), 4)
        for invalid in (True, 0, -1, Q(3, 2), 4.0):
            with self.assertRaises(ValueError):
                trace_law((1,), (), max_paths=invalid)

    def test_schedule_shape_and_exact_input_validation(self):
        with self.assertRaises(ValueError):
            composition_certificate((1, 0), (1,), (), ())
        with self.assertRaises(ValueError):
            composition_certificate((1, 0), (1, 0), (identity(2),), ())
        with self.assertRaises(ValueError):
            composition_certificate((1, 0), (1, 0), (Kernel(((1,), (1,))),), (identity(2),))
        with self.assertRaises(ValueError):
            trace_law((1,), (identity(2),))
        with self.assertRaises(TypeError):
            trace_law((1,), ("reset",))
        with self.assertRaises(ValueError):
            unrolled_contributions(0, (0,), ())
        for invalid in (True, 0.25):
            with self.assertRaises(TypeError):
                path_coupling_bound(invalid, ())
            with self.assertRaises(TypeError):
                unrolled_contributions(0, (invalid,), (0,))
        with self.assertRaises(ValueError):
            path_coupling_bound(0, (Q(3, 2),))
        result = composition_certificate((1,), (1,), (), ())
        with self.assertRaises(ValueError):
            risk_certificate(result, (0, 1))
        with self.assertRaises(ValueError):
            risk_certificate(result, (-1,))
        with self.assertRaises(TypeError):
            risk_certificate(result, (True,))
        with self.assertRaises(TypeError):
            risk_certificate(result, "1")
        with self.assertRaises(TypeError):
            unrolled_contributions(0, "0", (0,))
        with self.assertRaises(TypeError):
            path_coupling_bound(0, "0")


if __name__ == "__main__":
    unittest.main()
