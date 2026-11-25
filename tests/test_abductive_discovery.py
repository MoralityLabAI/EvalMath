from fractions import Fraction as F
from spiral_ln.evaluation_abductive_discovery import solve, witness, world


def test_bridge():
    a = witness()
    assert solve(a, 0) == (F(1, 2), F(0))
    assert solve(a, 2) == (F(1), F(0))
    assert solve(a, 3, 1) == (F(1), F(0))
    assert solve(a, 3, 2) == solve(a, 3) == (F(1), F(1))


def test_finite_dominance_and_sham():
    for seed in range(4):
        for k in (1, 2):
            a = world(seed, k)
            b = k + 2
            opt = solve(a, b)
            for horizon in (1, 2):
                x = solve(a, b, horizon)
                assert opt[0] + 3 * opt[1] >= x[0] + 3 * x[1]
            # Relabelled prerequisites preserve the optimal objective; tie-broken rates need not agree.
            s = solve(world(seed, k, sham=True), b)
            assert opt[0] + 3 * opt[1] == s[0] + 3 * s[1]
            u = solve(world(seed, k, ungated=True), b)
            assert u[0] + 3 * u[1] >= opt[0] + 3 * opt[1]
