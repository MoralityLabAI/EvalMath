"""Regenerate exact full-filtration feedback research receipt, with source hashes."""
from __future__ import annotations

import argparse
import json
import random
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path

from spiral_ln.evaluation_full_filtration import (
    StochasticNull, compress_equivalent_worlds, fixed_optimum,
    independent_one_round_oracle, noisy_selector_fixture, optimal,
    peeked_evalue, policy_risk_direct, rare_noisy_selector_fixture,
)


def verify():
    checks = {}
    witness = noisy_selector_fixture()
    calibrated = rare_noisy_selector_fixture()
    marginals = tuple(Q(sum(w for w, hit in zip(calibrated.weights, event) if hit),
                        calibrated.total) for event in calibrated.events)
    checks["rare_two_tests_individually_five_percent"] = marginals == (Q(1, 20),) * 2
    checks["early_selection_risk_seven_point_five_percent"] = (
        optimal(calibrated, 1, "before")["risk"] == Q(3, 40))
    checks["late_selection_risk_six_point_two_five_percent"] = (
        optimal(calibrated, 1, "after")["risk"] == Q(1, 16))
    checks["late_equals_fixed_one_round"] = (
        fixed_optimum(calibrated, 1)["risk"] == Q(1, 16))
    checks["two_late_rounds_recover_early_value"] = (
        optimal(calibrated, 2, "after")["risk"] == Q(3, 40))
    checks["noisy_one_round_early_vs_late"] = (
        optimal(witness, 1, "before")["risk"] == Q(3, 4)
        and optimal(witness, 1, "after")["risk"] == Q(5, 8))
    checks["direct_noisy_policy_certificate"] = all(
        policy_risk_direct(witness, optimal(witness, k, t)["policy"])
        == optimal(witness, k, t)["risk"] for t in ("before", "after") for k in (0, 1, 2))
    checks["one_round_independent_calibrated_oracle"] = all(
        independent_one_round_oracle(calibrated, t) == optimal(calibrated, 1, t)["risk"]
        for t in ("before", "after"))
    p = peeked_evalue(Q(3, 4))
    checks["coarse_one_step_martingale"] = p["coarse_one_step_expectation"] == Q(1)
    checks["fine_information_stopping_exceeds_one"] = (
        p["best_rich_stopping_expectation"] == Q(5, 4)
        and max(p["all_rich_stopping_values"].values()) == Q(5, 4))
    checks["fine_conditional_factor_fails"] = (
        p["conditional_factor_expectations"] == (Q(1, 2), Q(3, 2)))
    checks["one_step_conditional_scale"] = p["one_step_conditional_scale"] == Q(3, 2)
    checks["fair_peek_is_valid"] = peeked_evalue(Q(1, 2))["best_rich_stopping_expectation"] == 1
    checks["perfect_peek_stopped_expectation"] = peeked_evalue(Q(1))["best_rich_stopping_expectation"] == Q(3, 2)

    # Completely independent exhaustive query allocation for 96 seeded one-step
    # stochastic problems; two timings produce 192 comparisons to Bellman DP.
    rng = random.Random(2601026)
    one_round = []
    same = ordered = True
    for n in range(2, 6):
        for _ in range(24):
            weights = tuple(rng.randrange(1, 6) for _ in range(n))
            events = tuple(tuple(bool(rng.randrange(2)) for _ in range(n)) for _ in range(3))
            queries = tuple(tuple((Q(t, 4), Q(4-t, 4)) for t in
                                  [rng.randrange(5) for _ in range(n)]) for _ in range(2))
            private = tuple((Q(t, 4), Q(4-t, 4)) for t in
                            [rng.randrange(5) for _ in range(n)])
            model = StochasticNull(weights, events, queries, private)
            values = []
            for timing in ("before", "after"):
                value = optimal(model, 1, timing)["risk"]
                same &= (value == independent_one_round_oracle(model, timing))
                values.append(value)
            ordered &= values[0] >= values[1] >= fixed_optimum(model, 1)["risk"]
            one_round.append((n, weights, tuple(tuple(int(v) for v in e) for e in events),
                              tuple(str(v) for v in values)))
    checks["192_independent_one_round_oracles"] = same and len(one_round) == 96
    checks["96_timing_order_cases"] = ordered

    # Separate random generator, two-round exact policy replay and order check.
    rng = random.Random(7412)
    two_round_cases = []
    two_replay = two_order = two_mono = True
    for n in range(2, 5):
        for _ in range(8):
            weights = tuple(rng.randrange(1, 5) for _ in range(n))
            events = tuple(tuple(bool(rng.randrange(2)) for _ in range(n)) for _ in range(2))
            queries = tuple(tuple((Q(t, 4), Q(4-t, 4)) for t in
                                  [rng.randrange(5) for _ in range(n)]) for _ in range(2))
            private = tuple((Q(t, 4), Q(4-t, 4)) for t in
                            [rng.randrange(5) for _ in range(n)])
            model = StochasticNull(weights, events, queries, private)
            left, right = [], []
            for k in range(3):
                early, late = optimal(model, k, "before"), optimal(model, k, "after")
                two_replay &= (
                    policy_risk_direct(model, early["policy"]) == early["risk"]
                    and policy_risk_direct(model, late["policy"]) == late["risk"])
                two_order &= early["risk"] >= late["risk"] >= fixed_optimum(model, k)["risk"]
                left.append(early["risk"])
                right.append(late["risk"])
            two_mono &= left == sorted(left) and right == sorted(right)
            two_round_cases.append((n, weights, tuple(str(x) for x in left),
                                    tuple(str(x) for x in right)))
    checks["144_independent_direct_policy_replays"] = two_replay and len(two_round_cases) == 24
    checks["24_two_round_timing_order_cases"] = two_order
    checks["24_budget_monotonicity_cases"] = two_mono

    # Fixed channel/event alphabet permits exact posterior-world compression.
    rng = random.Random(8433)
    compress_matches = True
    compression_cases = []
    for _ in range(40):
        n = rng.randrange(2, 6)
        base = StochasticNull(
            tuple(rng.randrange(1, 7) for _ in range(n)),
            tuple(tuple(bool(rng.randrange(2)) for _ in range(n)) for _ in range(2)),
            tuple(tuple((Q(t, 4), Q(4-t, 4)) for t in
                        [rng.randrange(5) for _ in range(n)]) for _ in range(2)),
            tuple((Q(t, 4), Q(4-t, 4)) for t in
                  [rng.randrange(5) for _ in range(n)]),
        )
        dup = StochasticNull(base.weights + tuple(2 * w for w in base.weights),
                             tuple(e + e for e in base.events),
                             tuple(q + q for q in base.queries),
                             base.private + base.private)
        packed = compress_equivalent_worlds(dup)
        compress_matches &= len(packed.weights) <= n and packed.total == dup.total
        for timing in ("before", "after"):
            for k in range(3):
                compress_matches &= (optimal(packed, k, timing)["risk"] ==
                                     optimal(dup, k, timing)["risk"])
        compression_cases.append((n, len(packed.weights), dup.total))
    checks["40_merged_world_compression_cases"] = compress_matches

    fingerprint = sha256(json.dumps(
        (one_round, two_round_cases, compression_cases),
        separators=(",", ":")).encode("utf-8")).hexdigest()
    return {
        "all_passed": all(checks.values()), "checks": checks,
        "one_round_independent_oracle_comparisons": 192,
        "policy_certificate_replays": 144,
        "world_compression_fixtures": 40,
        "case_sha256": fingerprint,
        "fixture": {
            "nominal_each_test": "1/20",
            "before_one_round_risk": str(optimal(calibrated, 1, "before")["risk"]),
            "after_one_round_risk": str(optimal(calibrated, 1, "after")["risk"]),
            "before_two_round_risk": str(optimal(calibrated, 2, "before")["risk"]),
            "after_two_round_risk": str(optimal(calibrated, 2, "after")["risk"]),
            "coarse_one_step_evalue": str(p["coarse_one_step_expectation"]),
            "rich_stopped_evalue": str(p["best_rich_stopping_expectation"]),
            "conditional_factors": [str(v) for v in p["conditional_factor_expectations"]],
            "peek_accuracy": "3/4", "query_accuracy": "3/4",
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    files = (
        "src/spiral_ln/evaluation_full_filtration.py",
        "tests/test_evaluation_full_filtration.py",
        "scripts/verify_evaluation_full_filtration.py",
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
