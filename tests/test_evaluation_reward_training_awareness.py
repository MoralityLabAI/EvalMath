"""RHT-20: independent exact-rational controls for simulated-evaluation incentives."""
from fractions import Fraction as Q
from itertools import product
import random

import pytest

from spiral_ln.evaluation_reward_training_awareness import (
    EvaluationCueGame, robust_protection, future_policy_value_delta, sharp_audit_gap,
)


def fixture():
    return EvaluationCueGame(
        ("deployment_cue", "evaluation_cue"),
        (Q(1, 4), Q(3, 4)), (Q(3, 4), Q(1, 4)),
        Q(1, 8), Q(8), Q(1),
    )


def test_posterior_bayes_and_exact_transfer_gap():
    game = fixture()
    assert game.posterior(0) == Q(1, 22)
    assert game.posterior(1) == Q(3, 10)
    assert (game.score(0), game.score(1)) == (-Q(13, 32), Q(17, 32))
    policy = game.bayes_policy()
    assert policy == (False, True)
    assert game.compliance(policy) == (Q(3, 4), Q(1, 4))
    assert game.total_variation() == Q(1, 2)
    assert game.coverage_ratio() == Q(1, 3)
    cert = game.audit_transfer(policy)
    assert cert.guaranteed_deployment_compliance == Q(1, 4)
    assert cert.evaluation_compliance - cert.deployment_compliance == cert.total_variation


def test_identical_cue_laws_and_classical_threshold_with_ties():
    game = EvaluationCueGame(
        ("x", "y"), (Q(3, 4), Q(1, 4)), (Q(3, 4), Q(1, 4)),
        Q(1, 8), Q(8), Q(1),
    )
    assert game.bayes_policy() == (True, True)
    assert game.audit_transfer(game.bayes_policy()).guaranteed_deployment_compliance == 1
    for p in (Q(0), Q(1, 9), Q(1, 8), Q(1, 4), Q(1)):
        single = EvaluationCueGame(("x",), (Q(1),), (Q(1),), p, Q(8), Q(1))
        assert single.score(0) == 9 * p - 1
        assert single.bayes_policy() == (p > Q(1, 9),)


def test_exhaustive_policies_match_optimal_value_and_sharp_tv():
    rng = random.Random(20261111)
    for n in (2, 3, 4):
        for _ in range(50):
            ew = [rng.randrange(5) for i in range(n)]
            rw = [rng.randrange(5) for i in range(n)]
            if not sum(ew):
                ew[0] = 1
            if not sum(rw):
                rw[-1] = 1
            game = EvaluationCueGame(
                tuple(str(i) for i in range(n)),
                tuple(Q(v, sum(ew)) for v in ew),
                tuple(Q(v, sum(rw)) for v in rw),
                Q(rng.randrange(9), 8),
                Q(rng.randrange(1, 10)),
                Q(rng.randrange(1, 10)),
                tuple(Q(rng.randrange(-5, 6), 4) for i in range(n)),
            )
            policies = tuple(product((False, True), repeat=n))
            assert game.policy_value(game.bayes_policy()) == max(
                game.policy_value(pi) for pi in policies
            )
            for pi in policies:
                e, d = game.compliance(pi)
                assert abs(e - d) <= game.total_variation()
            e, d = game.compliance(game.maximum_audit_gap_witness())
            assert e - d == game.total_variation() == sharp_audit_gap(game)


def test_robust_interval_certificate_matches_full_vertex_oracle():
    rng = random.Random(327)
    game = EvaluationCueGame(
        ("a", "b", "c"),
        (Q(1, 3),) * 3,
        (Q(1, 2), Q(1, 3), Q(1, 6)),
        Q(1, 2), Q(2), Q(2),
    )
    for _ in range(60):
        p0, p1 = Q(rng.randrange(5), 8), Q(rng.randrange(5, 9), 8)
        r0 = Q(rng.randrange(1, 5), 2)
        g0 = Q(rng.randrange(1, 5), 2)
        d = tuple((Q(rng.randrange(-3, 2), 3), Q(1)) for _ in range(3))
        cert = robust_protection(
            game, (p0, p1), (r0, r0 + Q(1, 2)),
            (g0, g0 + Q(1, 2)), d,
        )
        brute = min(
            game.score(i, prior=p, protect_reward=r, exploit_gain=g, future_delta=f)
            for i in range(3)
            for p, r, g, f in product(
                (p0, p1), (r0, r0 + Q(1, 2)), (g0, g0 + Q(1, 2)), d[i]
            )
        )
        assert cert.minimum_advantage == brute
        assert cert.forced_protection == (brute > 0)
        assert cert.cues_checked == 3


def test_future_training_kernel_can_reverse_present_choice():
    future = future_policy_value_delta(
        (Q(3, 4), Q(1, 4)), (Q(1, 4), Q(3, 4)),
        (Q(10), Q(0)), Q(1, 2),
    )
    assert future == Q(5, 2)
    basic = fixture()
    good = EvaluationCueGame(
        basic.cues, basic.evaluation, basic.deployment,
        basic.prior, basic.protect_reward, basic.exploit_gain,
        (future, future),
    )
    bad = EvaluationCueGame(
        basic.cues, basic.evaluation, basic.deployment,
        basic.prior, basic.protect_reward, basic.exploit_gain,
        (-future, -future),
    )
    assert good.bayes_policy() == (True, True)
    assert bad.bayes_policy() == (False, False)


def test_purely_deployment_cue_breaks_bargaining():
    game = EvaluationCueGame(
        ("real_only", "eval_only"), (Q(0), Q(1)), (Q(1), Q(0)),
        Q(1, 2), Q(100), Q(1),
    )
    assert game.bayes_policy() == (False, True)
    assert game.coverage_ratio() == 0
    assert game.total_variation() == 1
    assert game.compliance(game.bayes_policy()) == (1, 0)


def test_fail_closed_validation_and_adversarial_tie():
    game = EvaluationCueGame(("x",), (Q(1),), (Q(1),), Q(1, 8), Q(8), Q(1))
    cert = robust_protection(game, (Q(1, 9), Q(1, 4)), (Q(8), Q(8)), (Q(1), Q(1)))
    assert not cert.forced_protection and cert.minimum_advantage == 0
    assert cert.worst_prior == Q(1, 9)
    with pytest.raises(ValueError, match="normalized"):
        EvaluationCueGame(("x",), (Q(1, 2),), (Q(1),), Q(1, 2), Q(2), Q(1))
    with pytest.raises(ValueError, match="exact rational"):
        EvaluationCueGame(("x",), (1.0,), (1,), Q(1, 2), Q(2), Q(1))
    with pytest.raises(ValueError, match="Boolean"):
        game.policy_value((1,))
    with pytest.raises(ValueError, match="prior endpoints"):
        robust_protection(game, (Q(0), Q(2)), (Q(1), Q(2)), (Q(1), Q(2)))
    with pytest.raises(ValueError, match="invalid bounds"):
        robust_protection(game, (Q(1, 2), Q(1, 4)), (Q(1), Q(2)), (Q(1), Q(2)))
    with pytest.raises(ValueError, match="dimensions"):
        future_policy_value_delta((Q(1),), (Q(1, 2), Q(1, 2)), (Q(1),))
