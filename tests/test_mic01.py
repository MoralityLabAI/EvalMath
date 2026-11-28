from fractions import Fraction as F
from itertools import permutations
from spiral_ln.mic01 import baseline, check, grade, optimum, pilot, root, task, tighten, walk


def test_certificates():
    for seed in range(128):
        m, b = root(seed)
        p = baseline(m, b)
        gold = optimum(m, b)
        assert check(m, b, p) and check(m, b, gold)
        assert all(gold[i] <= p[i] for i in range(2))
        assert all(gold[i] == b[i] + sum(m[i][j] * gold[j] for j in range(2)) for i in range(2))
        for order in set(permutations([0, 0, 1, 1])):
            out = walk(m, b, order)
            assert all(gold[i] <= out[i] <= p[i] for i in range(2))


def test_boundary():
    m = ((F(0), F(0)), (F(0), F(0)))
    b = (F(1), F(3))
    assert optimum(m, b) == b
    assert walk(m, b, [0, 1]) == b
    assert not check(m, b, (F(0), F(3)))
    assert tighten(m, b, b, 0) == b


def test_pilot():
    p = pilot()
    assert len(p['pilot']) == 64
    assert not p['heldout_sealed'] and not p['units_independent']
    assert p == pilot()


def test_grade():
    for seed in range(64):
        m, b = root(seed)
        gold = optimum(m, b)
        assert grade(seed, [str(x) for x in gold])["valid"]
        assert grade(seed, task(seed)["baseline"])["improved"] is False
        assert not grade(seed, [0.0, 0.0])["valid"]
        assert not grade(seed, ["1/0", "1"])["valid"]
        assert not grade(seed, ["-1", "1"])["valid"]
