"""Independent regression checks for the pinned-contract source signatures."""
import unittest
from upstream_contract import SIGNATURES, blob_sha, check_model


class UpstreamContractTests(unittest.TestCase):
    def test_sha(self):
        self.assertEqual(blob_sha(b"hello"), "b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0")

    def test_mutation_detection(self):
        model = "\n".join((
            "soundness : ∀ input, ¬BinaryLanguage.language input →\n    ∀ labeling, (countSatisfied labeling",
            "completeness : ∀ input, BinaryLanguage.language input →\n    ∃ labeling, 1 - ε ≤",
            "computation : Turing.TM2ComputableInPolyTime (id : List Bool → List Bool)\n    Complexity.gameBits construct",
            "structure BinaryGapReduction (ε δ : ℝ) where\n  alphabet : Nat\n  alphabetAtLeastTwo : 2 ≤ alphabet",
        ))
        self.assertTrue(all(check_model(model)[key] for key in
                            ("soundness_forall", "completeness_exists", "polynomial_time", "fixed_alphabet")))
        mutated = model.replace("∀ labeling, (countSatisfied", "∃ labeling, (countSatisfied")
        self.assertFalse(check_model(mutated)["soundness_forall"])
        mutated = model.replace("Turing.TM2ComputableInPolyTime", "Computable")
        self.assertFalse(check_model(mutated)["polynomial_time"])
        mutated = model.replace("alphabetAtLeastTwo", "alphabetAtLeastOne")
        self.assertFalse(check_model(mutated)["fixed_alphabet"])

    def test_all_signatures_are_unique(self):
        self.assertEqual(len(SIGNATURES), len(set(SIGNATURES)))
        self.assertGreaterEqual(len(SIGNATURES), 10)


if __name__ == "__main__":
    unittest.main()
