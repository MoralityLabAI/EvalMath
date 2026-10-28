import unittest
from fractions import Fraction as F
from spiral_ln.qwenputer_contract import delta, key, matrix, matmul, overwrite, read, transpose, verify_trace


class QwenputerContractTests(unittest.TestCase):
    def setUp(self):
        self.s = matrix(((2, 3), (5, 7)))

    def test_addressed_overwrite_and_frame(self):
        self.assertEqual(delta(self.s, key(2, 1), (11, 13)), matrix(((2, 3), (11, 13))))

    def test_exact_read(self):
        self.assertEqual(read(self.s, key(2, 0)), (2, 3))

    def test_decay_breaks_frame(self):
        out = delta(self.s, key(2, 1), (11, 13), alpha=F(1, 2))
        self.assertEqual(out[0], (1, F(3, 2)))
        self.assertEqual(out[1], (11, 13))

    def test_partial_write_is_not_overwrite(self):
        self.assertNotEqual(delta(self.s, key(2, 0), (0, 0), beta=F(1, 2)), overwrite(self.s, 0, (0, 0)))

    def test_beta_two_sign_flip(self):
        state = matrix(((1,),))
        for i in range(100):
            state = delta(state, (1,), (0,), beta=2)
            self.assertEqual(state[0][0], (-1) ** (i + 1))

    def test_zero_gate_reads_gated_state(self):
        self.assertEqual(delta(self.s, (1, 0), (11, 13), alpha=0), matrix(((11, 13), (0, 0))))

    def test_rotation_covariance(self):
        u = matrix(((F(3, 5), -F(4, 5)), (F(4, 5), F(3, 5))))
        k = matmul(u, matrix(((1,), (0,))))
        k = tuple(row[0] for row in k)
        rotated = delta(matmul(u, self.s), k, (11, 13))
        self.assertEqual(rotated, matmul(u, overwrite(self.s, 0, (11, 13))))
        self.assertEqual(matmul(transpose(u), matmul(u, self.s)), self.s)

    def test_rotation_without_key_rotation_fails(self):
        u = matrix(((0, -1), (1, 0)))
        self.assertNotEqual(delta(matmul(u, self.s), (1, 0), (11, 13)), matmul(u, overwrite(self.s, 0, (11, 13))))

    def test_trace_and_empty_trace(self):
        out = overwrite(self.s, 1, (11, 13))
        self.assertEqual(verify_trace(self.s, [(1, (11, 13))], [self.s, out]), 1)
        self.assertEqual(verify_trace(self.s, [], [self.s]), 0)

    def test_trace_mutations(self):
        for boundaries in ([], [self.s], [self.s, self.s], [overwrite(self.s, 0, (0, 0)), self.s]):
            with self.subTest(boundaries=boundaries), self.assertRaises(ValueError):
                verify_trace(self.s, [(1, (11, 13))], boundaries)

    def test_visible_alias_is_not_evaluator_sufficiency(self):
        a, b = matrix(((0,), (0,))), matrix(((0,), (1,)))
        self.assertEqual(read(a, (1, 0)), read(b, (1, 0)))
        self.assertNotEqual(read(a, (0, 1)), read(b, (0, 1)))

    def test_strict_scalar_and_address_validation(self):
        for bad in (True, 0.5, float('nan'), float('inf'), '1'):
            with self.subTest(bad=bad), self.assertRaises(TypeError):
                delta(self.s, (1, 0), (bad, 0))
        for address in (-1, 2, True, 0.5):
            with self.subTest(address=address), self.assertRaises((ValueError, TypeError)):
                key(2, address)

    def test_invalid_shapes_and_gates(self):
        for bad in ((), ((),), ((1,), (2, 3))):
            with self.assertRaises(ValueError):
                matrix(bad)
        with self.assertRaises(ValueError):
            delta(self.s, (1,), (1, 2))
        with self.assertRaises(ValueError):
            delta(self.s, (1, 0), (1, 2), beta=3)
        with self.assertRaises(ValueError):
            matmul(self.s, matrix(((1,),)))


if __name__ == '__main__':
    unittest.main()
