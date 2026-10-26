"""Regenerate the exact dynamic-filtration validity receipt, with source hashes."""
from __future__ import annotations

import argparse
import json
import random
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
from pathlib import Path

from spiral_ln.evaluation_dynamic_filtration import (
    ControlModel, PrivateSignalLaw, SourceModel, actor_value, chronology_safe,
    chronology_worst_case, control_leakage_certificate, doubling_law, doubling_process,
    enumerate_private_stopping_times, fair_bit_sources, is_public_supermartingale,
    leakage_certificate, markov_factor_witnesses, martingale_from_terminal, peek_law,
    per_source_projective_likelihood, private_kernel, private_stopping_value,
    rare_run_law, rare_run_process, rare_success_law, revocation_policy_value,
    sequential_private_value, single_source_after_view_value, static_factor_witness,
    static_histories_equivalent, total_variation_value, worst_stopped_expectation,
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


def product_law(rng, n, alphabet, symbols):
    """Public path independent of the private symbol: value must be exactly one."""
    pub = {g: Q(rng.randint(0, 3)) for g in product(range(alphabet), repeat=n)}
    if not any(pub.values()):
        pub[(0,) * n] = Q(1)
    priv = rdist(rng, symbols)
    return PrivateSignalLaw((alphabet,) * n, symbols,
                            {(g, h): m * priv[h] for g, m in pub.items() for h in range(symbols)})


def random_martingale(rng, law):
    paths = law.public_paths()
    terminal = {g: Q(rng.randint(0, 4)) for g in paths}
    total = sum(law.prefix_mass(g) * terminal[g] for g in paths)
    if total == 0:
        terminal[paths[0]] = Q(1)
        total = law.prefix_mass(paths[0])
    return martingale_from_terminal(law, {g: v * law.total / total for g, v in terminal.items()})


def extreme_point_supremum(law):
    best = Q(0)
    for g0 in law.public_paths():
        terminal = {g: (law.total / law.prefix_mass(g0) if g == g0 else Q(0)) for g in law.public_paths()}
        best = max(best, worst_stopped_expectation(law, martingale_from_terminal(law, terminal))["value"])
    return best


def verify():
    checks = {}

    # --- A1. PR #8 Section 4 law reproduced and bounded ---------------------------------
    process = {(): Q(1), (0,): Q(0), (1,): Q(2)}
    peek = {p: worst_stopped_expectation(peek_law(p), process)["value"]
            for p in (Q(0), Q(1, 4), Q(1, 2), Q(3, 4), Q(1))}
    checks["peek_law_stopped_values"] = peek == {Q(0): Q(3, 2), Q(1, 4): Q(5, 4), Q(1, 2): Q(1),
                                                 Q(3, 4): Q(5, 4), Q(1): Q(3, 2)}
    checks["peek_law_closed_form_and_leakage"] = all(
        private_stopping_value(peek_law(p)) == Q(1, 2) + max(p, 1 - p)
        and total_variation_value(peek_law(p)) == Q(1, 2) + max(p, 1 - p)
        and leakage_certificate(peek_law(p)) == 2 * max(p, 1 - p)
        and enumerate_private_stopping_times(peek_law(p), process) == peek[p]
        for p in peek)
    checks["peek_three_quarters_value_below_leakage"] = (
        private_stopping_value(peek_law(Q(3, 4))) == Q(5, 4) < leakage_certificate(peek_law(Q(3, 4))) == Q(3, 2))

    # --- A2. sharpness families ---------------------------------------------------------
    checks["rare_success_two_minus_epsilon"] = all(
        worst_stopped_expectation(rare_success_law(e), {(): Q(1), (0,): Q(0), (1,): 1 / e})["value"]
        == 2 - e == private_stopping_value(rare_success_law(e))
        and leakage_certificate(rare_success_law(e)) == 2
        for e in (Q(1, 2), Q(1, 10), Q(1, 100), Q(1, 10 ** 6)))
    doubling = {}
    for n in range(1, 6):
        law, proc = doubling_law(n), doubling_process(n)
        doubling[n] = (is_public_supermartingale(law, proc),
                       worst_stopped_expectation(law, proc)["value"], private_stopping_value(law),
                       leakage_certificate(law), sequential_private_value(law, proc, tuple(range(1, n + 1))))
    checks["doubling_one_plus_half_horizon_n_1_to_5"] = all(
        v == (True, 1 + Q(n, 2), 1 + Q(n, 2), Q(2 ** n), Q(1)) for n, v in doubling.items())
    rare_run = {}
    for n in range(1, 5):
        for e in (Q(1, 2), Q(1, 10), Q(1, 1000)):
            law, proc = rare_run_law(e, n), rare_run_process(e, n)
            rare_run[(n, e)] = (worst_stopped_expectation(law, proc)["value"],
                                private_stopping_value(law), leakage_certificate(law), law.private_symbols)
    checks["rare_run_alphabet_bound_sharp_n_1_to_4"] = all(
        v == (n * (1 - e) + 1, n * (1 - e) + 1, Q(n + 1), n + 1) for (n, e), v in rare_run.items())

    # --- A3. random laws: closed form, bound chain, brute force, sequential arrival --------
    rng = random.Random(26102701)
    law_cases = []
    chain = extreme = brute = tv = seq = True
    brute_count = 0
    for _ in range(200):
        n, alphabet, symbols = rng.choice((1, 2, 3)), rng.choice((2, 3)), rng.choice((2, 3))
        if n == 3 and alphabet == 3:
            alphabet = 2
        law = random_law(rng, n, alphabet, symbols)
        value, cert = private_stopping_value(law), leakage_certificate(law)
        chain &= Q(1) <= value <= cert <= symbols
        extreme &= extreme_point_supremum(law) == value
        if n == 1:
            tv &= total_variation_value(law) == value
        for _ in range(3):
            proc = random_martingale(rng, law)
            w = worst_stopped_expectation(law, proc)["value"]
            chain &= is_public_supermartingale(law, proc) and w <= value
            nodes = sum(len(law.prefixes(t)) for t in range(n)) * symbols
            if nodes <= 18:
                brute &= enumerate_private_stopping_times(law, proc) == w
                brute_count += 1
            seq &= sequential_private_value(law, proc, (0, 0)) == w
            seq &= sequential_private_value(law, proc, (n + 1, n + 1)) <= 1
            late = sequential_private_value(law, proc, (1, 1))
            seq &= Q(1) - Q(0) <= late <= w  # digits revealed at time 1: between no information and full
        law_cases.append((n, alphabet, symbols, str(value), str(cert)))
    checks["200_random_laws_bound_chain_1_V_leakage_L"] = chain
    checks["200_random_laws_extreme_points_attain_closed_form"] = extreme
    checks["random_laws_one_step_total_variation_form"] = tv
    checks["random_laws_brute_force_stopping_times"] = brute and brute_count >= 150
    checks["random_laws_sequential_arrival_monotone"] = seq
    rng = random.Random(991)
    indep = True
    for _ in range(60):
        law = product_law(rng, rng.choice((1, 2)), rng.choice((2, 3)), rng.choice((2, 3)))
        indep &= private_stopping_value(law) == 1 == leakage_certificate(law)
    checks["60_independent_private_symbols_value_one"] = indep

    # --- B. actor control with a latent Markov state -------------------------------------
    rng = random.Random(1203)
    immune = bounded = noise = True
    inflated = {"pointwise/data/before": 0, "calibrated/latent/before": 0, "calibrated/latent/after": 0,
                "calibrated/data/after": 0}
    control_cases = []
    for trial in range(24):
        states, queries, alphabet = 2, 2, 2
        prior = rdist(rng, states)
        transition = tuple(rdist(rng, states) for _ in range(states))
        if trial % 2 == 0:
            transition = tuple(tuple(Q(int(i == j)) for j in range(states)) for i in range(states))
        kernels = tuple(tuple(rdist(rng, alphabet) for _ in range(states)) for _ in range(queries))
        weights = tuple(rdist(rng, alphabet) for _ in range(queries))
        ys = list(product(range(alphabet), repeat=queries))
        privates = {
            "none": private_kernel(states, kernels, 2, "none", None),
            "latent": private_kernel(states, kernels, 2, "latent", {s: rdist(rng, 2) for s in range(states)}),
            "data": private_kernel(states, kernels, 2, "data", {y: rdist(rng, 2) for y in ys}),
        }
        row = {}
        for mode, private in privates.items():
            model = ControlModel(prior, transition, kernels, private, weights)
            cert = control_leakage_certificate(model, 2)
            for timing in ("before", "after"):
                for family in ("pointwise", "calibrated"):
                    v = actor_value(model, 2, timing, family)
                    row[f"{family}/{mode}/{timing}"] = str(v)
                    bounded &= v <= cert <= 4
                    if mode == "none":
                        noise &= v <= 1 and cert == 1
                    if family == "pointwise" and (mode == "latent" or timing == "after"):
                        immune &= v <= 1
                    key = f"{family}/{mode}/{timing}"
                    if key in inflated:
                        inflated[key] += v > 1
        control_cases.append(row)
    checks["24_control_models_pointwise_immune_latent_or_posthoc"] = immune
    checks["24_control_models_leakage_certificate_bounds_all_values"] = bounded
    checks["24_control_models_independent_noise_worthless"] = noise
    checks["control_inflation_witnessed_in_each_vulnerable_class"] = all(c > 0 for c in inflated.values())

    # --- C. revocation chronologies ------------------------------------------------------
    one, two = fair_bit_sources(1), fair_bit_sources(2)
    both_after = [("VIEW", 0), ("VIEW", 1), ("REVOKE", 0), ("REVOKE", 1)]

    def cyclic(idx, seen):
        values = dict(seen)
        return values[1] == 1 if idx == 2 else values[0] == 1

    checks["fair_bit_revocation_witnesses"] = (
        chronology_worst_case(one, [("VIEW", 0), ("REVOKE", 0)])["value"] == Q(3, 2)
        == single_source_after_view_value(one)
        and chronology_worst_case(one, [("REVOKE", 0), ("VIEW", 0)])["value"] == 1
        and chronology_worst_case(two, both_after)["value"] == Q(9, 4)
        and chronology_worst_case(two, [("VIEW", 0), ("REVOKE", 1), ("VIEW", 1)])["value"] == 1
        and chronology_worst_case(two, [("VIEW", 0), ("REVOKE", 1), ("VIEW", 1), ("REVOKE", 0)])["value"] == Q(3, 2)
        and revocation_policy_value(two, both_after, cyclic) == Q(5, 4)
        and revocation_policy_value(two, both_after, lambda i, s: False) == 1)
    rng = random.Random(4417)
    safe_ok = mono = closed = True
    chron_cases = []
    for _ in range(150):
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
        safe = chronology_safe(model, events)
        safe_ok &= (not safe) or value <= 1
        for idx in range(len(events) - 1):
            if events[idx][0] == "REVOKE":
                moved = events[:idx] + [events[idx + 1], events[idx]] + events[idx + 2:]
                mono &= chronology_worst_case(model, moved)["value"] >= value
        single = SourceModel(prior, (kernels[0],), (factors[0],))
        closed &= (chronology_worst_case(single, [("VIEW", 0), ("REVOKE", 0)])["value"]
                   == single_source_after_view_value(single))
        chron_cases.append((worlds, sources, tuple(f"{e}{i}" for e, i in events), safe, str(value)))
    checks["150_chronologies_safe_implies_no_inflation"] = safe_ok
    checks["150_chronologies_later_slot_weakly_increases"] = mono
    checks["150_single_source_closed_form_E_max_F_1"] = closed

    # --- D. audit states -----------------------------------------------------------------
    w = static_factor_witness()
    checks["static_pooled_equal_leave_one_out_differ"] = (
        w[frozenset({0, 1})][0] == w[frozenset({0, 1})][1]
        and w[frozenset({0})][0] != w[frozenset({0})][1] and w[frozenset({1})][0] != w[frozenset({1})][1])
    rng = random.Random(777)
    iff = True
    equivalent_count = 0
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
        iff &= lhs == rhs
        equivalent_count += lhs
    checks["300_static_equivalence_iff_per_source_projective_likelihoods"] = iff and equivalent_count >= 20
    m = markov_factor_witnesses()
    checks["markov_two_source_subset_filters_irredundant"] = (
        m["pooled"][frozenset({0})][0] == m["pooled"][frozenset({0})][1]
        and m["pooled"][frozenset({1})][0] == m["pooled"][frozenset({1})][1]
        and m["pooled"][frozenset({0, 1})] == ((Q(21, 26), Q(5, 26)), (Q(5, 6), Q(1, 6)))
        and m["single"][frozenset({0, 1})][0] == m["single"][frozenset({0, 1})][1]
        and m["single"][frozenset({1})][0] == m["single"][frozenset({1})][1]
        and m["single"][frozenset({0})] == ((Q(1, 6), Q(5, 6)), (Q(5, 26), Q(21, 26))))

    fingerprint = sha256(json.dumps((law_cases, control_cases, chron_cases),
                                    separators=(",", ":")).encode("utf-8")).hexdigest()
    return {
        "all_passed": all(checks.values()), "checks": checks,
        "random_private_signal_laws": 200, "brute_force_stopping_comparisons": brute_count,
        "control_models": 24, "revocation_chronologies": 150, "static_equivalence_pairs": 300,
        "case_sha256": fingerprint,
        "fixture": {
            "peek_values": {str(p): str(v) for p, v in peek.items()},
            "doubling": {str(n): [str(x) for x in v[1:]] for n, v in doubling.items()},
            "rare_run": {f"{n},{e}": [str(x) for x in v] for (n, e), v in rare_run.items()},
            "control_inflation_counts": inflated,
            "fair_bits": {"one_after_view": "3/2", "two_both_after": "9/4", "two_cyclic_cross_policy": "5/4",
                          "two_triangular": "1"},
            "markov_witnesses": {name: {",".join(str(i) for i in sorted(sub)): [[str(x) for x in v] for v in pair]
                                       for sub, pair in table.items()} for name, table in m.items()},
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    files = (
        "src/spiral_ln/evaluation_dynamic_filtration.py",
        "tests/test_evaluation_dynamic_filtration.py",
        "scripts/verify_evaluation_dynamic_filtration.py",
    )
    report = {"schema_version": "0.1",
              "generated_at_utc": datetime.now(timezone.utc).isoformat(),
              **verify(),
              "source_sha256": {name: sha256((root / name).read_bytes()).hexdigest()
                                for name in files}}
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(rendered)
    else:
        print(rendered, end="")
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
