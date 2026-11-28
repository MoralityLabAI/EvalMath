"""Synthetic examples exercise data custody, never a trained-model finding."""

import unittest

try:
    from research.inkling_loop_monitorability.depth_matrix import audit
except ModuleNotFoundError:
    from depth_matrix import audit


def rows():
    data = []
    for depth in (1, 3, 5):
        for case, root, result in (("a", "r1", depth >= 3),
                                  ("b", "r1", False),
                                  ("c", "r2", True),
                                  ("d", "r2", depth >= 5)):
            data.append({
                "case_id": case, "root_id": root, "family": "pointer",
                "depth": depth, "verified": result, "model_sha": "sha-checkpoint",
                "cache_mode": "unshared", "split": "calibration",
                "reasoning_tokens": 100 - depth,
                "total_tokens": 150 - depth,
                "wall_ms": 10.0 * depth, "joules": None,
            })
    return data


class DepthMatrixTest(unittest.TestCase):
    def test_paired_roots_and_comparison(self):
        report, fsi = audit(rows(), baseline_depth=1, candidate_depth=3)
        self.assertEqual(report["source_roots"], 2)
        self.assertEqual(report["case_count"], 4)
        self.assertAlmostEqual(report["root_macro_paired_effect"], 0.25)
        self.assertEqual(fsi["planned_comparisons"], 2)
        self.assertFalse(fsi["sealed_readout"])
        self.assertFalse(fsi["hypothesis_preregistered"])
        self.assertEqual({c["cluster_id"] for c in fsi["cases"]}, {"r1", "r2"})
        self.assertEqual(report["per_depth"][0]["verified_correct"], 1)
        self.assertEqual(report["per_depth"][1]["verified_correct"], 2)

    def test_incomplete_matrix_rejected(self):
        with self.assertRaisesRegex(ValueError, "incomplete"):
            audit(rows()[:-1], baseline_depth=1, candidate_depth=3)

    def test_sealed_and_duplicate_rejected(self):
        forbidden = rows()
        forbidden[0]["split"] = "ood_test"
        with self.assertRaisesRegex(ValueError, "reserved"):
            audit(forbidden, baseline_depth=1, candidate_depth=3)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            audit(rows() + [rows()[0]], baseline_depth=1, candidate_depth=3)

    def test_model_changes_rejected(self):
        bad = rows()
        bad[-1]["model_sha"] = "different"
        with self.assertRaisesRegex(ValueError, "model_sha"):
            audit(bad, baseline_depth=1, candidate_depth=3)


if __name__ == "__main__":
    unittest.main()
