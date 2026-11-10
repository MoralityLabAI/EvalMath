"""Tests for the exact-rational minimax detection oracle (RHC-04)."""

import random
import time
from fractions import Fraction as F

import pytest

from spiral_ln.evaluation_reward_hacking_bootstrap import finite_witness, optimal_detector
from spiral_ln.evaluation_rhc04_oracle import (
    check_certificate, neyman_pearson, solve_minimax)


def law(rng, n, zero_prob=0.25, top=6):
    while True:
        w = [0 if rng.random() < zero_prob else rng.randint(1, top) for _ in range(n)]
        if sum(w):
            return tuple(F(x, sum(w)) for x in w)


def instance(rng, n, J, zero_prob=0.25):
    alpha = F(rng.randint(0, 8), 8)
    return law(rng, n, zero_prob), [law(rng, n, zero_prob) for _ in range(J)], alpha


def test_agrees_with_vertex_oracle_on_random_small():
    rng = random.Random(1234)
    for _ in range(200):
        n, J = rng.randint(1, 4), rng.randint(1, 3)
        p, qs, alpha = instance(rng, n, J)
        res = solve_minimax(p, qs, alpha)
        assert res["value"] == optimal_detector(p, qs, alpha)["value"]
        assert res["certified"]
    for _ in range(5):  # a few at the n = 5 vertex-oracle limit
        p, qs, alpha = instance(rng, 5, 2)
        assert solve_minimax(p, qs, alpha)["value"] == optimal_detector(p, qs, alpha)["value"]


def test_finite_witness():
    p, qs, alpha = (F(1, 2), F(1, 4), F(1, 4)), [(0, 1, 0), (0, 0, 1)], F(1, 4)
    res = solve_minimax(p, qs, alpha)
    assert res["value"] == F(1, 2) == finite_witness()["oracle"]["value"]
    assert res["certified"] and res["detector"] == (0, F(1, 2), F(1, 2))


def test_strong_duality_certified_larger():
    rng = random.Random(77)
    for _ in range(40):
        n, J = rng.randint(5, 40), rng.randint(1, 6)
        p, qs, alpha = instance(rng, n, J, zero_prob=0.15)
        res = solve_minimax(p, qs, alpha)
        assert res["certified"]
        d = res["dual"]
        assert sum(d["lam"]) == 1 and min(d["lam"]) >= 0 and d["t"] >= 0
        assert d["upper_bound"] == res["value"]
        chk = check_certificate(p, qs, alpha, res["detector"], d["lam"], d["t"])
        assert chk["ok"] and chk["gap"] == 0
        assert res["fpr"] <= alpha and res["fpr"] == sum(a * b for a, b in zip(p, res["detector"]))


def test_check_certificate_rejections():
    p, qs, alpha = (F(1, 2), F(1, 2)), [(F(0), F(1))], F(1, 2)
    res = solve_minimax(p, qs, alpha)
    lam, t = res["dual"]["lam"], res["dual"]["t"]
    det = res["detector"]
    assert check_certificate(p, qs, alpha, det, lam, t)["ok"]
    with pytest.raises(ValueError):
        check_certificate(p, qs, alpha, (F(1), F(1)), lam, t)           # fpr > alpha
    with pytest.raises(ValueError):
        check_certificate(p, qs, alpha, (F(0), F(2)), lam, t)           # f > 1
    with pytest.raises(ValueError):
        check_certificate(p, qs, alpha, (F(-1, 2), F(1)), lam, t)       # f < 0
    with pytest.raises(ValueError):
        check_certificate(p, qs, alpha, det, (F(1, 2),), t)             # lam sum != 1
    with pytest.raises(ValueError):
        check_certificate(p, [(0, 1), (1, 0)], alpha, det, (F(2), F(-1)), t)  # negative lam
    with pytest.raises(ValueError):
        check_certificate(p, qs, alpha, det, lam, F(-1))                # t < 0


def test_degenerate_cases():
    p = (F(1, 2), F(0), F(1, 2))
    qs = [(F(1, 4), F(1, 2), F(1, 4))]
    r0 = solve_minimax(p, qs, F(0))             # alpha = 0: only the p = 0 cell is free
    assert r0["value"] == F(1, 2) and r0["certified"] and r0["fpr"] == 0
    r1 = solve_minimax(p, qs, F(1))             # alpha = 1: detect everything
    assert r1["value"] == 1 and r1["certified"]
    r2 = solve_minimax(p, [p], F(1, 3))         # Q = P: value = alpha
    assert r2["value"] == F(1, 3) and r2["certified"]
    r3 = solve_minimax(p, [p], F(0))            # Q = P, alpha = 0
    assert r3["value"] == 0 and r3["certified"]
    q = (F(1, 3), F(1, 3), F(1, 3))
    r4 = solve_minimax(p, [q, q, q], F(1, 4))   # duplicate attack laws
    assert r4["value"] == solve_minimax(p, [q], F(1, 4))["value"] and r4["certified"]
    assert sum(r4["dual"]["lam"]) == 1
    r5 = solve_minimax((F(1),), [(F(1),)], F(1, 2))  # n = 1
    assert r5["value"] == F(1, 2) and r5["certified"]
    big_rng = random.Random(5)
    t0 = time.time()
    p, qs, alpha = instance(big_rng, 150, 10, zero_prob=0.1)
    res = solve_minimax(p, qs, alpha)
    assert res["certified"]
    assert time.time() - t0 < 60


def test_single_attack_matches_neyman_pearson():
    rng = random.Random(99)
    for _ in range(60):
        n = rng.randint(1, 30)
        p, qs, alpha = instance(rng, n, 1)
        np_res = neyman_pearson(p, qs[0], alpha)
        res = solve_minimax(p, qs, alpha)
        assert res["value"] == np_res["value"] and res["certified"]
        assert sum(a * b for a, b in zip(p, np_res["detector"])) <= alpha


def test_worst_family_below_pooled_attack():
    # Two families on different observations; P has mass on both and a third cell.
    p = (F(1, 2), F(1, 6), F(1, 3))
    q1, q2 = (F(1), F(0), F(0)), (F(0), F(1), F(0))
    alpha = F(1, 2)
    pooled = tuple((a + b) / 2 for a, b in zip(q1, q2))
    worst = solve_minimax(p, [q1, q2], alpha)
    pooled_value = solve_minimax(p, [pooled], alpha)["value"]
    assert worst["value"] == F(3, 4) and worst["certified"]
    assert pooled_value == F(5, 6) == neyman_pearson(p, pooled, alpha)["value"]
    assert worst["value"] < pooled_value
