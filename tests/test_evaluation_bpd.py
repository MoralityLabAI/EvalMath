"""BPD-01 independent exhaustive optimizer and schedule-fibre audits."""
import itertools
import random
import unittest

from spiral_ln.evaluation_bpd import (
    Probe, adaptive_worst_cost, clock_visibility_floors, coverage,
    exhaustive_batch, fibre_floor, minimum_batch, quotient, refill_witness,
)


class BpdTests(unittest.TestCase):
    def test_branched_adaptive_strict_gain(self):
        # Root separates branches; conditional selectors are disjoint.
        ps = (Probe("root", (0, 0, 1, 1)),
              Probe("left", (0, 1, 0, 0)),
              Probe("right", (0, 0, 0, 1)))
        self.assertEqual(coverage(ps)["separated_pairs"], 6)
        self.assertEqual(minimum_batch(ps), (3, ("root", "left", "right")))
        self.assertEqual(exhaustive_batch(ps), minimum_batch(ps))
        self.assertEqual(adaptive_worst_cost(ps), 2)

    def test_routing_removes_information(self):
        ps = (Probe("root", (0, 0, 1, 1)),
              Probe("left", (0, 1, 0, 0), routed=False),
              Probe("right", (0, 0, 0, 1)))
        self.assertEqual(coverage(ps)["separated_pairs"], 5)
        self.assertEqual(quotient(ps), ((0, 1), (2,), (3,)))
        self.assertIsNone(minimum_batch(ps))
        self.assertIsNone(adaptive_worst_cost(ps))
        self.assertIsNone(exhaustive_batch(ps))

    def test_exhaustive_binary_cases(self):
        checked = 0
        for code in itertools.product(range(8), repeat=3):
            ps = tuple(Probe(f"p{i}", tuple(m >> j & 1 for j in range(3)))
                       for i, m in enumerate(code))
            self.assertEqual(minimum_batch(ps), exhaustive_batch(ps))
            batches = minimum_batch(ps)
            cost = adaptive_worst_cost(ps)
            self.assertEqual(batches is None, cost is None)
            if batches is not None:
                self.assertLessEqual(cost, batches[0])
            checked += 1
        self.assertEqual(checked, 512)

    def test_seeded_weights_multiway(self):
        rng = random.Random(11617)
        for _ in range(96):
            n = rng.randrange(2, 6)
            ps = tuple(Probe(str(i), tuple(rng.randrange(3) for _ in range(n)),
                             rng.randrange(1, 5), rng.choice((True, False, True)))
                       for i in range(rng.randrange(1, 7)))
            self.assertEqual(minimum_batch(ps), exhaustive_batch(ps))
            ans = minimum_batch(ps)
            adaptive = adaptive_worst_cost(ps)
            self.assertEqual(ans is None, adaptive is None)
            if ans is not None:
                self.assertLessEqual(adaptive, ans[0])

    def test_clock_and_visibility_collision(self):
        records = [
            {"case": "g1", "component": "c7", "intervention": "single",
             "state": "s0", "visible": "v0", "pass": 0, "label": 0},
            {"case": "g1", "component": "c7", "intervention": "single",
             "state": "s0", "visible": "v0", "pass": 1, "label": 1},
            {"case": "g1", "component": "c7", "intervention": "single",
             "state": "s1", "visible": "v0", "pass": 2, "label": 1},
        ]
        got = clock_visibility_floors(records)
        self.assertEqual(got["state_only"]["minimum_errors"], 1)
        self.assertEqual(got["state_clock"]["minimum_errors"], 0)
        self.assertEqual(got["visible_only"]["minimum_errors"], 1)
        self.assertEqual(got["visible_only"]["total_weight"], 3)

    def test_weighted_fibre_and_missing_inputs(self):
        rows = [{"s": "x", "label": 0, "weight": 3},
                {"s": "x", "label": 1, "weight": 4},
                {"s": "y", "label": 1, "weight": 2}]
        self.assertEqual(fibre_floor(rows, ("s",))["minimum_errors"], 3)
        with self.assertRaises(ValueError):
            fibre_floor([{"s": "x", "label": 1, "weight": 0}], ("s",))
        with self.assertRaises(ValueError):
            fibre_floor([{"s": "x", "label": True}], ("s",))
        with self.assertRaises(ValueError):
            fibre_floor([{"label": 1}], ("s",))

    def test_early_repair_masks_terminal(self):
        w = refill_witness(4)
        self.assertEqual(w["baseline"], [1, 1, 1, 1])
        self.assertEqual(w["single_cut_final"], [1, 1, 1, 0])
        self.assertEqual(w["persistent_cut_final"], 0)
        self.assertEqual(w["terminal_blind_early_cuts"], 3)
        self.assertEqual(refill_witness(2, 0)["terminal_blind_early_cuts"], 1)
        with self.assertRaises(ValueError):
            refill_witness(1)

    def test_reject_invalid_probe_shapes(self):
        bad = [
            (Probe("same", (0, 1)), Probe("same", (1, 0))),
            (Probe("one", (0,)),),
            (Probe("cost", (0, 1), cost=0),),
            (Probe("bool", (False, True)),),
            (Probe("badroute", (0, 1), routed=1),),
            (Probe("mismatch", (0, 1)), Probe("other", (0, 1, 2))),
        ]
        for ps in bad:
            with self.assertRaises(ValueError):
                coverage(ps)


if __name__ == "__main__":
    unittest.main()
