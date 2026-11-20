"""Independent event-oracle and contract checks for RHT-27."""
from fractions import Fraction as Q
from itertools import product
import unittest

from spiral_ln.evaluation_finite_kernels import (
    Kernel, apply, dobrushin, identity, total_variation,
)
from spiral_ln.evaluation_noninterference import (
    EvaluationInterface, PermittedSimulator, permitted_learning_fixture,
    reset_order_fixture, unsafe_permitted_feedback_fixture,
)


def event_distance(p, q):
    """Enumerate every event, without calling the implementation's TV helper."""
    return max(abs(sum((a - b) * included
                       for a, b, included in zip(p, q, event)))
               for event in product((0, 1), repeat=len(p)))


class NoninterferenceTests(unittest.TestCase):
    def test_rational_intervention_census_against_all_events(self):
        grid = tuple(Q(i, 4) for i in range(5))
        checked = 0
        for probabilities in product(grid, repeat=4):
            left = Kernel(tuple((1 - p, p) for p in probabilities[:2]))
            right = Kernel(tuple((1 - p, p) for p in probabilities[2:]))
            interface = EvaluationInterface(("a", "b"), ("score", "score"), (left, right))
            expected = max(event_distance(p, q) for p, q in zip(left.rows, right.rows))
            audit = interface.audit()
            self.assertEqual(audit.epsilon, expected)
            witness = audit.witness
            self.assertIsNotNone(witness)
            p, q = left.rows[witness.initial_state], right.rows[witness.initial_state]
            self.assertEqual(sum(p[i] - q[i] for i in witness.event), expected)
            self.assertEqual(interface.residual(interface.permitted_simulator()), expected)
            mixture = interface.permitted_simulator({"score": (Q(1, 2), Q(1, 2))})
            self.assertEqual(interface.residual(mixture), expected / 2)
            if expected == 0:
                self.assertEqual(interface.residual(interface.factorization()), 0)
            else:
                with self.assertRaises(ValueError):
                    interface.factorization()
            checked += 1
        self.assertEqual(checked, 625)

    def test_postprocessing_uses_one_common_channel(self):
        interface = EvaluationInterface(
            ("plain", "hook"), ("score:0", "score:0"),
            (Kernel(((1, 0), (Q(1, 4), Q(3, 4)))),
             Kernel(((Q(1, 4), Q(3, 4)), (0, 1)))),
        )
        before = interface.audit().epsilon
        for a, b in product((Q(0), Q(1, 3), Q(1, 2), Q(1)), repeat=2):
            channel = Kernel(((1 - a, a), (1 - b, b)))
            self.assertLessEqual(interface.postprocess(channel).audit().epsilon,
                                 dobrushin(channel) * before)
        self.assertEqual(interface.postprocess(identity(2)), interface)
        with self.assertRaises(ValueError):
            interface.postprocess(identity(3))

    def test_three_output_witness_can_require_multiple_event_atoms(self):
        left = Kernel(((Q(1, 2), Q(1, 3), Q(1, 6)),))
        right = Kernel(((Q(1, 3), Q(1, 6), Q(1, 2)),))
        interface = EvaluationInterface(("a", "b"), ("z", "z"), (left, right))
        audit = interface.audit()
        self.assertEqual(audit.epsilon, event_distance(left.rows[0], right.rows[0]))
        self.assertEqual((audit.epsilon, audit.witness.event), (Q(1, 3), (0, 1)))
        merged = interface.postprocess(Kernel(((1, 0), (1, 0), (0, 1))))
        self.assertEqual(merged.audit().epsilon, Q(1, 3))
        self.assertEqual(interface.postprocess(Kernel(((1,), (1,), (1,)))).audit().epsilon, 0)

    def test_transcript_specific_continuations_can_reintroduce_influence(self):
        before = EvaluationInterface(("a", "b"), ("z", "z"), (Kernel(((1,),)),) * 2)
        safe_continuation, unsafe_continuation = Kernel(((1, 0),)), Kernel(((0, 1),))
        # The continuation can see a second copy of the transcript. Its two
        # kernels therefore differ, which violates the common-channel premise.
        after = EvaluationInterface(("a", "b"), ("z", "z"),
                                    (safe_continuation, unsafe_continuation))
        self.assertEqual((before.audit().epsilon, after.audit().epsilon), (0, 1))

    def test_each_state_is_checked_even_when_nominal_start_is_safe(self):
        safe_at_start = Kernel(((1, 0), (0, 1)))
        poison_hidden_state = Kernel(((1, 0), (1, 0)))
        interface = EvaluationInterface(("a", "b"), ("score", "score"),
                                        (safe_at_start, poison_hidden_state))
        self.assertEqual(total_variation(apply((1, 0), safe_at_start),
                                         apply((1, 0), poison_hidden_state)), 0)
        self.assertEqual(interface.audit().epsilon, 1)
        self.assertEqual(interface.audit().witness.initial_state, 1)

    def test_feedback_coverage_and_singleton_vacuity(self):
        identity_map = EvaluationInterface(("a", "b"), ("a", "b"),
                                          (Kernel(((1, 0),)), Kernel(((0, 1),))))
        audit = identity_map.audit()
        self.assertEqual(audit.epsilon, 0)
        self.assertIsNone(audit.witness)
        self.assertTrue(audit.identity_feedback_vacuous)
        self.assertEqual((audit.coverage, audit.row_comparisons), (0, 0))
        partial = EvaluationInterface(("a", "b", "c"), ("z", "z", "c"),
                                      (identity(2),) * 3)
        audit = partial.audit()
        self.assertEqual((audit.coverage, audit.nontrivial_fibres), (Q(2, 3), 1))
        self.assertEqual((audit.transcript_pairs, audit.row_comparisons), (1, 2))
        self.assertFalse(audit.identity_feedback_vacuous)
        self.assertEqual(EvaluationInterface(("only",), ("z",),
                                             (Kernel(((1,),)),)).audit().epsilon, 0)

    def test_factorization_keeps_permitted_learning(self):
        interface = permitted_learning_fixture()
        simulator = interface.factorization()
        self.assertEqual(interface.audit().coverage, 1)
        self.assertEqual(interface.residual(simulator), 0)
        self.assertEqual(apply((1, 0), simulator.kernel("score:1")), (0, 1))
        self.assertEqual(apply((1, 0), simulator.kernel("score:0")), (1, 0))

    def test_zero_diameter_can_allow_certain_unsafe_action(self):
        interface = unsafe_permitted_feedback_fixture()
        result = interface.risk_certificate(interface.factorization(), (0, 1))
        self.assertEqual((result.residual, result.reference_risk,
                          result.actual_risk, result.risk_bound), (0, 1, 1, 1))

    def test_reference_risk_plus_residual_is_sharp(self):
        interface = EvaluationInterface(("a", "b"), ("score", "score"),
                                        (Kernel(((Q(7, 8), Q(1, 8)),)),
                                         Kernel(((Q(5, 8), Q(3, 8)),))))
        result = interface.risk_certificate(interface.permitted_simulator(), (0, 1))
        self.assertEqual((result.reference_risk, result.residual,
                          result.actual_risk, result.risk_bound),
                         (Q(1, 8), Q(1, 4), Q(3, 8), Q(3, 8)))
        with self.assertRaises(ValueError):
            interface.risk_certificate(interface.permitted_simulator(), (0, 2))

    def test_reset_order_and_readout_can_hide_a_retained_policy(self):
        late, early, artifact = reset_order_fixture()
        self.assertEqual(late.audit().epsilon, 1)
        self.assertEqual(early.audit().epsilon, 0)
        self.assertEqual(late.postprocess(artifact).audit().epsilon, 0)
        self.assertEqual(apply((1, 0, 0, 0), late.kernels[0]), (1, 0, 0, 0))
        self.assertEqual(apply((1, 0, 0, 0), late.kernels[1]), (0, 1, 0, 0))
        self.assertEqual(apply((0, 1, 0, 0), early.kernels[1]), (0, 1, 0, 0))

    def test_observational_conditioning_is_a_different_question(self):
        # Uniform U; observed transcript E=U and action A=U. Intervening on E
        # leaves U unchanged. The state U is held fixed in the two kernels.
        interface = EvaluationInterface(("E0", "E1"), ("same", "same"),
                                        (identity(2), identity(2)))
        observational_joint = {(0, 0): Q(1, 2), (1, 1): Q(1, 2)}
        observed = tuple(tuple(observational_joint.get((e, a), Q(0)) / Q(1, 2)
                               for a in range(2)) for e in range(2))
        self.assertEqual(event_distance(*observed), 1)
        self.assertEqual(interface.audit().epsilon, 0)

    def test_mixture_is_fibre_local_and_normalized(self):
        interface = permitted_learning_fixture()
        for weights in ({}, {"score:0": (1, 0), "score:1": (1, 0), "extra": (1,)},
                        {"score:0": (1,), "score:1": (1, 0)},
                        {"score:0": (1, 1), "score:1": (1, 0)}):
            with self.assertRaises(ValueError):
                interface.permitted_simulator(weights)
        with self.assertRaises(TypeError):
            interface.permitted_simulator({"score:0": (0.5, 0.5), "score:1": (1, 0)})
        with self.assertRaises(ValueError):
            interface.residual(PermittedSimulator(("different",), (identity(2),)))
        with self.assertRaises(ValueError):
            interface.residual(PermittedSimulator(("score:0", "score:1"),
                                                 (identity(3), identity(3))))

    def test_constructor_rejects_ambiguous_or_misaligned_tables(self):
        for transcripts, feedback, kernels in (
            ((), (), ()),
            (("a", "a"), ("z", "z"), (identity(2), identity(2))),
            ("a", ("z",), (identity(2),)),
            (("a",), ("",), (identity(2),)),
            (("a",), ("z", "z"), (identity(2),)),
            (("a",), ("z",), ()),
            (("a",), ("z",), (None,)),
            (("a", "b"), ("z", "z"), (identity(2), identity(3))),
        ):
            with self.assertRaises(ValueError):
                EvaluationInterface(transcripts, feedback, kernels)
        with self.assertRaises(ValueError):
            PermittedSimulator(("z", "z"), (identity(2), identity(2)))
        with self.assertRaises(ValueError):
            permitted_learning_fixture().factorization().kernel("unknown")


if __name__ == "__main__":
    unittest.main()
