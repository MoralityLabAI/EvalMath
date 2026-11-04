import random
import unittest
from itertools import product

from spiral_ln.evaluation_metaprune_cover import (
    min_cover_dp, min_cover_bruteforce, adaptive_minimax_depth, validate,
)


class MetaPruneCoverTests(unittest.TestCase):
    def test_covered_and_uncovered(self):
        experiments = (0b0011, 0b1100, 0b0101, 0b1010)
        self.assertEqual(len(min_cover_dp(4, experiments)), 2)
        self.assertEqual(len(min_cover_bruteforce(4, experiments)), 2)
        self.assertEqual(adaptive_minimax_depth(4, experiments), 2)
        for solver in (min_cover_dp, min_cover_bruteforce, adaptive_minimax_depth):
            self.assertIsNone(solver(3, (0b001, 0b010)))

    def test_all_three_alternative_three_experiment_matrices(self):
        count = 0
        for masks in product(range(8), repeat=3):
            dp = min_cover_dp(3, masks)
            direct = min_cover_bruteforce(3, masks)
            adaptive = adaptive_minimax_depth(3, masks)
            self.assertEqual(None if dp is None else len(dp),
                             None if direct is None else len(direct))
            self.assertEqual(adaptive, None if dp is None else len(dp))
            count += 1
        self.assertEqual(count, 512)

    def test_seeded_multi_size_family(self):
        rng = random.Random(20261104)
        count = 0
        for n in range(1, 6):
            for _ in range(25):
                masks = tuple(rng.randrange(1 << n) for _ in range(6))
                dp = min_cover_dp(n, masks)
                direct = min_cover_bruteforce(n, masks)
                adaptive = adaptive_minimax_depth(n, masks)
                self.assertEqual(None if dp is None else len(dp),
                                 None if direct is None else len(direct))
                self.assertEqual(adaptive, None if dp is None else len(dp))
                count += 1
        self.assertEqual(count, 125)

    def test_invalid_masks(self):
        for n, masks in ((0, (1,)), (2, (4,)), (2, (-1,)),
                         (2, (True,))):
            with self.assertRaises(ValueError):
                validate(n, masks)


if __name__ == "__main__":
    unittest.main()
