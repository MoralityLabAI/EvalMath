"""Exact stochastic-filtration checks with independent policy and history oracles."""
from fractions import Fraction as Q
from itertools import product
import random
import pytest

from spiral_ln.evaluation_full_filtration import (
    StochasticNull, compress_equivalent_worlds, fixed_optimum,
    fixed_schedule_risk, independent_one_round_oracle,
    noisy_selector_fixture, optimal, peeked_evalue, policy_risk_direct,
)


def test_noisy_selector_early_late_finite_witness():
    for accuracy, expected_early, expected_late in (
        (Q(1, 2), Q(1, 2), Q(1, 2)),
        (Q(3, 4), Q(3, 4), Q(5, 8)),
        (Q(1), Q(1), Q(3, 4)),
    ):
        m = noisy_selector_fixture(accuracy)
        assert optimal(m, 1, "before")["risk"] == expected_early
        assert optimal(m, 1, "after")["risk"] == expected_late
        assert fixed_optimum(m, 1)["risk"] == expected_late
        assert independent_one_round_oracle(m, "before") == expected_early
        assert independent_one_round_oracle(m, "after") == expected_late
        assert optimal(m, 2, "after")["risk"] == expected_early
        assert fixed_optimum(m, 2)["risk"] == expected_early


def test_prepeek_martingale_stopping_counterexample():
    for p, expected in ((Q(0), Q(3, 2)), (Q(1, 4), Q(5, 4)),
                        (Q(1, 2), Q(1)), (Q(3, 4), Q(5, 4)), (Q(1), Q(3, 2))):
        out = peeked_evalue(p)
        assert out["coarse_one_step_expectation"] == Q(1)
        assert out["best_rich_stopping_expectation"] == expected
        assert max(out["all_rich_stopping_values"].values()) == expected
        assert out["one_step_conditional_scale"] == 2 * max(p, 1-p)
    assert peeked_evalue(Q(3, 4))["conditional_factor_expectations"] == (Q(1, 2), Q(3, 2))


def test_random_oneshot_matches_independent_policy_oracle():
    rng = random.Random(2601026)
    for n in range(2, 6):
        for _ in range(24):
            weights = tuple(rng.randrange(1, 6) for _ in range(n))
            events = tuple(tuple(bool(rng.randrange(2)) for _ in range(n)) for _ in range(3))
            queries = tuple(tuple((Q(t), Q(1-t)) for t in [Q(rng.randrange(5), 4)
                                   for _ in range(n)]) for _ in range(2))
            hidden = tuple((Q(rng.randrange(5), 4),) for _ in range(n))
            hidden = tuple((r[0], Q(1) - r[0]) for r in hidden)
            model = StochasticNull(weights, events, queries, hidden)
            values = []
            for timing in ("before", "after"):
                result = optimal(model, 1, timing)
                assert result["risk"] == independent_one_round_oracle(model, timing)
                assert result["risk"] == policy_risk_direct(model, result["policy"])
                values.append(result["risk"])
            assert values[0] >= values[1] >= fixed_optimum(model, 1)["risk"]


def test_two_round_policy_certificate_and_monotonicity():
    rng = random.Random(7412)
    for n in range(2, 5):
        for _ in range(8):
            weights = tuple(rng.randrange(1, 5) for _ in range(n))
            events = tuple(tuple(bool(rng.randrange(2)) for _ in range(n)) for _ in range(2))
            queries = tuple(tuple((Q(t, 4), Q(4-t, 4)) for t in
                                  [rng.randrange(5) for _ in range(n)]) for _ in range(2))
            private = tuple((Q(t, 4), Q(4-t, 4)) for t in [rng.randrange(5) for _ in range(n)])
            m = StochasticNull(weights, events, queries, private)
            early, late = [], []
            for k in range(3):
                b, a = optimal(m, k, "before"), optimal(m, k, "after")
                for item in (a, b):
                    assert item["risk"] == policy_risk_direct(m, item["policy"])
                early.append(b["risk"])
                late.append(a["risk"])
                assert b["risk"] >= a["risk"] >= fixed_optimum(m, k)["risk"]
            assert early == sorted(early) and late == sorted(late)


def test_compression_preserves_future_values_exactly():
    rng = random.Random(8433)
    for _ in range(40):
        n = rng.randrange(2, 6)
        model = StochasticNull(
            tuple(rng.randrange(1, 7) for _ in range(n)),
            tuple(tuple(bool(rng.randrange(2)) for _ in range(n)) for _ in range(2)),
            tuple(tuple((Q(t, 4), Q(4-t, 4)) for t in
                        [rng.randrange(5) for _ in range(n)]) for _ in range(2)),
            tuple((Q(t, 4), Q(4-t, 4)) for t in [rng.randrange(5) for _ in range(n)]),
        )
        # Duplicate every world with a fresh positive mass but the same channels.
        duplicated = StochasticNull(
            model.weights + tuple(2 * w for w in model.weights),
            tuple(e + e for e in model.events),
            tuple(q + q for q in model.queries),
            model.private + model.private,
        )
        compressed = compress_equivalent_worlds(duplicated)
        assert len(compressed.weights) <= len(model.weights)
        assert compressed.total == duplicated.total
        for timing in ("before", "after"):
            for k in range(3):
                assert optimal(compressed, k, timing)["risk"] == optimal(duplicated, k, timing)["risk"]


def test_constant_private_and_rare_outcomes():
    m = StochasticNull(
        (1, 2), ((True, False), (False, True)),
        (((Q(1), Q(0)), (Q(0), Q(1))),),
    )
    assert optimal(m, 1, "before")["risk"] == 1
    assert optimal(m, 1, "after")["risk"] == 1
    assert fixed_optimum(m, 0)["risk"] == Q(2, 3)
    assert optimal(m, 0, "after")["risk"] == Q(2, 3)
    assert fixed_schedule_risk(m, (0, 0)) == 1


def test_invalid_input_contracts():
    base = noisy_selector_fixture()
    with pytest.raises(ValueError):
        StochasticNull((1,), ((True,),), (((.5,.5),),))
    with pytest.raises(ValueError):
        StochasticNull((1,), ((True,),), (((Q(1, 4), Q(1, 4)),),))
    with pytest.raises(ValueError):
        StochasticNull((1,), ((True,),), (((Q(1),),),), ((Q(1,2),),))
    with pytest.raises(ValueError):
        StochasticNull((1,), ((True,),), (((Q(1),),),), ((Q(-1), Q(2)),))
    with pytest.raises(ValueError):
        StochasticNull((True,), ((True,),), (((1,),),))
    with pytest.raises(ValueError):
        StochasticNull((1,), ((1,),), (((1,),),))
    with pytest.raises(ValueError):
        StochasticNull((1,), ((True,),), ())
    for k in (-1, 1.2, True):
        with pytest.raises(ValueError):
            optimal(base, k, "before")
        with pytest.raises(ValueError):
            fixed_optimum(base, k)
    with pytest.raises(ValueError):
        optimal(base, 1, "secret-after-last")
    with pytest.raises(ValueError):
        independent_one_round_oracle(base, "secret-before-history")
    for bad in (1.5, True, Q(5,4)):
        with pytest.raises(ValueError):
            noisy_selector_fixture(bad)
        with pytest.raises(ValueError):
            peeked_evalue(bad)


def test_rare_two_event_calibration_and_timing():
    from spiral_ln.evaluation_full_filtration import rare_noisy_selector_fixture
    model = rare_noisy_selector_fixture()
    assert model.total == 40
    assert tuple(Q(sum(w for w, hit in zip(model.weights, e) if hit), model.total)
                 for e in model.events) == (Q(1, 20), Q(1, 20))
    assert optimal(model, 0, "before")["risk"] == Q(1, 20)
    assert optimal(model, 1, "before")["risk"] == Q(3, 40)
    assert optimal(model, 1, "after")["risk"] == Q(1, 16)
    assert fixed_optimum(model, 1)["risk"] == Q(1, 16)
    assert optimal(model, 2, "after")["risk"] == Q(3, 40)
    assert independent_one_round_oracle(model, "before") == Q(3, 40)
    assert independent_one_round_oracle(model, "after") == Q(1, 16)
    for timing in ("before", "after"):
        assert policy_risk_direct(model, optimal(model, 2, timing)["policy"]) == optimal(model, 2, timing)["risk"]
    with pytest.raises(ValueError):
        rare_noisy_selector_fixture(trigger_denominator=1)


def test_embedding_existing_deterministic_query_contract():
    from spiral_ln.evaluation_full_filtration import lift_deterministic_model
    from types import SimpleNamespace
    old = SimpleNamespace(weights=(1, 2, 3),
                          events=((True, False, False), (False, True, True)),
                          queries=((0, 1, 2), (1, 1, 0)))
    model = lift_deterministic_model(old)
    assert optimal(model, 0, "before")["risk"] == Q(5, 6)
    for timing in ("before", "after"):
        assert optimal(model, 1, timing)["risk"] == 1
        assert optimal(model, 1, timing)["risk"] == policy_risk_direct(model, optimal(model, 1, timing)["policy"])
