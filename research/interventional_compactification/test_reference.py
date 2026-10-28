import unittest

from reference import (
    commutation_residual,
    copy_y_to_x,
    finite_cover_generalization_bound,
    finite_horizon_bound,
    first_coordinate,
    flip_y,
    identity,
    near_fiber_lower_bound,
    rollout,
)


class CompactificationTests(unittest.TestCase):
    def test_exact_quotient(self):
        # y is a causally irrelevant nuisance under this operation family.
        for h in ((1.0, -5.0), (-2.0, 99.0), (0.0, 0.0)):
            self.assertEqual(
                0.0,
                commutation_residual(
                    h,
                    first_coordinate,
                    lambda x: (0.75 * x[0], x[1] + 9),
                    lambda z: (0.75 * z[0],),
                ),
            )

    def test_observationally_perfect_but_causally_wrong(self):
        # On the baseline diagonal, the abstract transition identity works.
        self.assertEqual(
            0.0,
            commutation_residual((1.0, 1.0), first_coordinate, copy_y_to_x, identity),
        )
        # Post-intervention, the same abstraction misses the effect of y.
        self.assertEqual(
            2.0,
            commutation_residual((1.0, -1.0), first_coordinate, copy_y_to_x, identity),
        )
        error, full, abstract = rollout(
            (1.0, 1.0),
            first_coordinate,
            ["flip_y", "step"],
            {"flip_y": flip_y, "step": copy_y_to_x},
            {"flip_y": identity, "step": identity},
            first_coordinate,
            identity,
        )
        self.assertEqual((-1.0, -1.0), full)
        self.assertEqual((1.0,), abstract)
        self.assertEqual(2.0, error)

    def test_near_fiber_falsifier(self):
        lower = near_fiber_lower_bound(
            ((1.0, 1.0), (1.0, -1.0)),
            first_coordinate,
            copy_y_to_x,
            abstract_lipschitz=1.0,
            max_encoded_distance=0.0,
        )
        self.assertEqual(1.0, lower)

    def test_finite_horizon_bound_tight_for_additive_error(self):
        lam = 0.75
        eps = 0.1
        steps = 8
        full_step = lambda h: (lam * h[0] + eps, h[1])
        abstract_step = lambda z: (lam * z[0],)
        measured, _, _ = rollout(
            (1.0, 0.0),
            first_coordinate,
            ["step"] * steps,
            {"step": full_step},
            {"step": abstract_step},
            first_coordinate,
            identity,
        )
        bound = finite_horizon_bound(steps, eps, 0.0, lam, 1.0)
        self.assertAlmostEqual(measured, bound, places=12)

    def test_statistical_bound(self):
        self.assertGreater(finite_cover_generalization_bound(1000, 0.01, 100, 0.05), 0.0)
        self.assertLess(
            finite_cover_generalization_bound(5000, 0.001, 100, 0.05),
            finite_cover_generalization_bound(500, 0.001, 100, 0.05),
        )
        with self.assertRaises(ValueError):
            finite_cover_generalization_bound(0, 0.01, 3, 0.05)


if __name__ == "__main__":
    unittest.main()
