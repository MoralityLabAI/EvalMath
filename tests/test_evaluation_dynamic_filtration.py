"""Exact checks for private stopping, actor control, revocation chronologies and audit states."""
from fractions import Fraction as Q
from itertools import product
import random
import pytest

from spiral_ln.evaluation_dynamic_filtration import (
    ControlModel, PrivateSignalLaw, SourceModel, actor_value, chronology_safe,
    chronology_worst_case, control_leakage_certificate, doubling_law, doubling_process,
    enumerate_private_stopping_times, fair_bit_sources, is_public_supermartingale,
    leakage_certificate, markov_factor_witnesses, markov_subset_filter,
    martingale_from_terminal, peek_law, per_source_projective_likelihood,
    private_kernel, private_stopping_value, rare_run_law, rare_run_process,
    rare_success_law, revocation_policy_value, sequential_private_value,
    single_source_after_view_value, static_factor_witness,
    static_histories_equivalent, static_subset_posterior, total_variation_value,
    worst_stopped_expectation,
)


def rdist(rng, k, dens=3):
    row = [Q(rng.randint(0, dens)) for _ in range(k)]
    if sum(row) == 0:
        row[rng.randrange(k)] = Q(1)
    s = sum(row)
    return tuple(x / s for x in row)


def random_law(rng, n, alphabet, symbols):
    mass = {}
    for g in product(range(alphabet), repeat=n):
        for h in range(symbols):
            mass[(g, h)] = Q(rng.randint(0, 3))
    if not any(mass.values()):
        mass[((0,) * n, 0)] = Q(1)
    return PrivateSignalLaw((alphabet,) * n, symbols, mass)


def random_martingale(rng, law):
    paths = law.public_paths()
    terminal = {g: Q(rng.randint(0, 4)) for g in paths}
    total = sum(law.prefix_mass(g) * terminal[g] for g in paths)
    if total == 0:
        terminal[paths[0]] = Q(1)
        total = law.prefix_mass(paths[0])
    terminal = {g: v * law.total / total for g, v in terminal.items()}
    return martingale_from_terminal(law, terminal)


# ----- A. private stopping -------------------------------------------------

def test_peek_law_reproduces_pr8_section_four():
    for p, expected in ((Q(0), Q(3, 2)), (Q(1, 4), Q(5, 4)), (Q(1, 2), Q(1)),
                        (Q(3, 4), Q(5, 4)), (Q(1), Q(3, 2))):
        law = peek_law(p)
        process = {(): Q(1), (0,): Q(0), (1,): Q(2)}
        assert is_public_supermartingale(law, process)
        out = worst_stopped_expectation(law, process)
        assert out["value"] == expected
        assert enumerate_private_stopping_times(law, process) == expected
        assert private_stopping_value(law) == expected
        assert total_variation_value(law) == expected
        assert leakage_certificate(law) == 2 * max(p, 1 - p)
        assert out["value"] <= private_stopping_value(law) <= leakage_certificate(law) <= 2


def test_rare_success_approaches_alphabet_bound():
    for eps in (Q(1, 2), Q(1, 10), Q(1, 1000)):
        law = rare_success_law(eps)
        process = {(): Q(1), (0,): Q(0), (1,): 1 / eps}
        assert is_public_supermartingale(law, process)
        assert worst_stopped_expectation(law, process)["value"] == 2 - eps
        assert private_stopping_value(law) == 2 - eps
        assert leakage_certificate(law) == 2


def test_doubling_value_is_one_plus_half_horizon():
    for n in (1, 2, 3, 4):
        law, process = doubling_law(n), doubling_process(n)
        assert is_public_supermartingale(law, process)
        assert worst_stopped_expectation(law, process)["value"] == 1 + Q(n, 2)
        assert private_stopping_value(law) == 1 + Q(n, 2)
        assert leakage_certificate(law) == 2 ** n
        # a digit revealed only after its bit is public is worthless
        assert sequential_private_value(law, process, tuple(range(1, n + 1))) == 1
        assert sequential_private_value(law, process, (0,) * n) == 1 + Q(n, 2)
        if n >= 2:
            # knowing only the first bit in advance
            partial = sequential_private_value(law, process, (0,) + (n + 1,) * (n - 1))
            assert 1 < partial < 1 + Q(n, 2)


def test_rare_run_law_is_sharp_for_alphabet_bound():
    for n in (1, 2, 3):
        for eps in (Q(1, 2), Q(1, 10)):
            law, process = rare_run_law(eps, n), rare_run_process(eps, n)
            assert is_public_supermartingale(law, process)
            assert law.private_symbols == n + 1
            value = worst_stopped_expectation(law, process)["value"]
            assert value == n * (1 - eps) + 1
            assert private_stopping_value(law) == value
            assert leakage_certificate(law) == n + 1


def test_random_laws_bound_chain_and_brute_force():
    rng = random.Random(2610271)
    for _ in range(60):
        n, alphabet, symbols = rng.choice((1, 2)), rng.choice((2, 3)), rng.choice((2, 3))
        law = random_law(rng, n, alphabet, symbols)
        value, cert = private_stopping_value(law), leakage_certificate(law)
        assert 1 <= value <= cert <= symbols
        if n == 1:
            assert value == total_variation_value(law)
        for _ in range(4):
            process = random_martingale(rng, law)
            assert is_public_supermartingale(law, process)
            w = worst_stopped_expectation(law, process)["value"]
            assert w <= value
            if n == 1 or (alphabet == 2 and symbols == 2):
                assert w == enumerate_private_stopping_times(law, process)
            assert sequential_private_value(law, process, (0,) * 2) == w
            assert sequential_private_value(law, process, (n + 1,) * 2) <= 1


def test_value_one_iff_independent():
    law = PrivateSignalLaw((2,), 2, {((0,), 0): 1, ((0,), 1): 1, ((1,), 0): 2, ((1,), 1): 2})
    assert private_stopping_value(law) == 1 == leakage_certificate(law)
    law = PrivateSignalLaw((2,), 2, {((0,), 0): 1, ((0,), 1): 1, ((1,), 0): 2, ((1,), 1): 1})
    assert private_stopping_value(law) > 1


def test_law_validation():
    with pytest.raises(ValueError):
        PrivateSignalLaw((2,), 2, {((0,), 0): 0.5})
    with pytest.raises(ValueError):
        PrivateSignalLaw((2,), 2, {((2,), 0): 1})
    with pytest.raises(ValueError):
        PrivateSignalLaw((2,), 2, {((0,), 0): 0})


# ----- B. actor control ----------------------------------------------------

def random_control(rng, states, queries, alphabet, static):
    prior = rdist(rng, states)
    transition = tuple(rdist(rng, states) for _ in range(states))
    if static:
        transition = tuple(tuple(Q(int(i == j)) for j in range(states)) for i in range(states))
    kernels = tuple(tuple(rdist(rng, alphabet) for _ in range(states)) for _ in range(queries))
    weights = tuple(rdist(rng, alphabet) for _ in range(queries))
    return prior, transition, kernels, weights


def test_pointwise_factors_immune_to_latent_and_posthoc_private_information():
    rng = random.Random(3)
    for trial in range(16):
        prior, transition, kernels, weights = random_control(rng, 2, 2, 2, trial % 2 == 0)
        ys = list(product(range(2), repeat=2))
        latent = private_kernel(2, kernels, 2, "latent", {s: rdist(rng, 2) for s in range(2)})
        data = private_kernel(2, kernels, 2, "data", {y: rdist(rng, 2) for y in ys})
        for private in (latent, data):
            model = ControlModel(prior, transition, kernels, private, weights)
            assert actor_value(model, 2, "after", "pointwise") <= 1
        assert actor_value(ControlModel(prior, transition, kernels, latent, weights), 2, "before", "pointwise") <= 1


def test_prepeek_and_calibrated_factors_can_inflate_but_respect_leakage():
    rng = random.Random(5)
    inflated = {"data-before-pointwise": False, "latent-before-calibrated": False}
    for trial in range(16):
        prior, transition, kernels, weights = random_control(rng, 2, 2, 2, trial % 2 == 0)
        ys = list(product(range(2), repeat=2))
        data = private_kernel(2, kernels, 2, "data", {y: rdist(rng, 2) for y in ys})
        latent = private_kernel(2, kernels, 2, "latent", {s: rdist(rng, 2) for s in range(2)})
        for name, private, timing, family in (
                ("data-before-pointwise", data, "before", "pointwise"),
                ("latent-before-calibrated", latent, "before", "calibrated")):
            model = ControlModel(prior, transition, kernels, private, weights)
            value = actor_value(model, 2, timing, family)
            assert value <= control_leakage_certificate(model, 2) <= 4
            inflated[name] |= value > 1
    assert all(inflated.values())


def test_independent_private_noise_never_inflates():
    rng = random.Random(9)
    for trial in range(6):
        prior, transition, kernels, weights = random_control(rng, 2, 2, 2, trial % 2 == 0)
        private = private_kernel(2, kernels, 2, "none", None)
        model = ControlModel(prior, transition, kernels, private, weights)
        for timing in ("before", "after"):
            for family in ("pointwise", "calibrated"):
                assert actor_value(model, 2, timing, family) <= 1
        assert control_leakage_certificate(model, 1) == 1


# ----- C. revocation chronologies -----------------------------------------

def test_fair_bit_revocation_witnesses():
    one, two = fair_bit_sources(1), fair_bit_sources(2)
    assert chronology_worst_case(one, [("VIEW", 0), ("REVOKE", 0)])["value"] == Q(3, 2)
    assert single_source_after_view_value(one) == Q(3, 2)
    assert chronology_worst_case(one, [("REVOKE", 0), ("VIEW", 0)])["value"] == 1
    both_after = [("VIEW", 0), ("VIEW", 1), ("REVOKE", 0), ("REVOKE", 1)]
    assert chronology_worst_case(two, both_after)["value"] == Q(9, 4)
    assert chronology_worst_case(two, [("VIEW", 0), ("REVOKE", 1), ("VIEW", 1)])["value"] == 1
    assert chronology_safe(two, [("VIEW", 0), ("REVOKE", 1), ("VIEW", 1)])
    assert not chronology_safe(two, both_after)
    assert chronology_worst_case(two, [("VIEW", 0), ("REVOKE", 1), ("VIEW", 1), ("REVOKE", 0)])["value"] == Q(3, 2)

    def cyclic(idx, seen):
        values = dict(seen)
        return values[1] == 1 if idx == 2 else values[0] == 1

    def triangular(idx, seen):
        return dict(seen)[0] == 1 if idx == 3 else False

    assert revocation_policy_value(two, both_after, cyclic) == Q(5, 4)
    assert revocation_policy_value(two, both_after, triangular) == 1
    assert revocation_policy_value(two, both_after, lambda i, s: False) == 1


def test_safe_chronologies_never_inflate_and_later_slots_weakly_increase():
    rng = random.Random(11)
    for _ in range(80):
        worlds, sources = rng.choice((1, 2, 3)), rng.choice((1, 2, 3))
        prior = rdist(rng, worlds)
        kernels, factors = [], []
        for _ in range(sources):
            a = rng.choice((2, 3))
            k = tuple(rdist(rng, a) for _ in range(worlds))
            w = rdist(rng, a)
            kernels.append(k)
            factors.append(tuple(w[y] / max(r[y] for r in k) if max(r[y] for r in k) else Q(0)
                                 for y in range(a)))
        model = SourceModel(prior, tuple(kernels), tuple(factors))
        events = [("VIEW", i) for i in range(sources)] + [("REVOKE", i) for i in range(sources)]
        rng.shuffle(events)
        value = chronology_worst_case(model, events)["value"]
        if chronology_safe(model, events):
            assert value <= 1
        # move one revoke slot one place later
        for idx in range(len(events) - 1):
            if events[idx][0] == "REVOKE":
                moved = events[:idx] + [events[idx + 1], events[idx]] + events[idx + 2:]
                assert chronology_worst_case(model, moved)["value"] >= value
                break


def test_source_model_rejects_invalid_factors():
    with pytest.raises(ValueError):
        SourceModel((Q(1),), (((Q(1, 2), Q(1, 2)),),), ((Q(1), Q(2)),))
    with pytest.raises(ValueError):
        chronology_worst_case(fair_bit_sources(1), [("VIEW", 0), ("VIEW", 0)])


# ----- D. audit states -----------------------------------------------------

def test_static_pooled_posterior_is_not_revocation_sufficient():
    w = static_factor_witness()
    assert w[frozenset({0, 1})][0] == w[frozenset({0, 1})][1] == (Q(1, 2), Q(1, 2))
    assert w[frozenset({0})][0] != w[frozenset({0})][1]
    assert w[frozenset({1})][0] != w[frozenset({1})][1]


def test_static_equivalence_iff_per_source_projective_likelihoods():
    rng = random.Random(13)
    seen_equivalent = 0
    for _ in range(300):
        worlds, sources = rng.choice((2, 3)), rng.choice((1, 2, 3))
        prior = rdist(rng, worlds)
        kernels = tuple(tuple(rdist(rng, 2) for _ in range(worlds)) for _ in range(sources))
        h1 = tuple((rng.randrange(sources), rng.randrange(2)) for _ in range(rng.randrange(0, 4)))
        h2 = tuple((rng.randrange(sources), rng.randrange(2)) for _ in range(rng.randrange(0, 4)))
        if rng.random() < 0.3:
            h2 = tuple(sorted(h1, key=lambda _: rng.random()))
        lhs = static_histories_equivalent(prior, kernels, h1, h2, range(sources))
        rhs = all(per_source_projective_likelihood(prior, kernels, h1, i)
                  == per_source_projective_likelihood(prior, kernels, h2, i) for i in range(sources))
        assert lhs == rhs
        seen_equivalent += lhs
    assert seen_equivalent > 20


def test_markov_subset_filters_have_no_redundancy_for_two_sources():
    w = markov_factor_witnesses()
    pooled, single = w["pooled"], w["single"]
    assert pooled[frozenset({0})][0] == pooled[frozenset({0})][1]
    assert pooled[frozenset({1})][0] == pooled[frozenset({1})][1]
    assert pooled[frozenset({0, 1})][0] != pooled[frozenset({0, 1})][1]
    assert pooled[frozenset({0, 1})] == ((Q(21, 26), Q(5, 26)), (Q(5, 6), Q(1, 6)))
    assert single[frozenset({0, 1})][0] == single[frozenset({0, 1})][1]
    assert single[frozenset({1})][0] == single[frozenset({1})][1]
    assert single[frozenset({0})] == ((Q(1, 6), Q(5, 6)), (Q(5, 26), Q(21, 26)))


def test_markov_filter_reduces_to_static_posterior_under_identity_transition():
    prior = (Q(1, 3), Q(2, 3))
    identity = ((Q(1), Q(0)), (Q(0), Q(1)))
    kernels = (((Q(1, 4), Q(3, 4)), (Q(2, 3), Q(1, 3))),)
    schedule = (((0, 1),), ((0, 0),))
    assert (markov_subset_filter(prior, identity, kernels, schedule, {0})
            == static_subset_posterior(prior, kernels, ((0, 1), (0, 0)), {0}))
