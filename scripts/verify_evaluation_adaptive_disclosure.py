"""Regenerate exact adaptive-disclosure receipts; no model or grader is contacted."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path

from spiral_ln.evaluation_adaptive_disclosure import (
    Node, adaptive_optimum, direct_bit_profile, fair_bit_prior, fixed_optimum,
    fixed_tree, interval_bank, leaf_fibres, one_hot_interval_law, one_hot_prior,
    prefix_collision_sequence, reachable_alphabet_bound, transcript,
    transcript_profile, tree_as_data,
)


def verify():
    checks = {}
    grid = []
    for n in range(1, 9):
        prior, queries = one_hot_prior(n), interval_bank(n)
        for k in range(4):
            law = one_hot_interval_law(n, k)
            adaptive = adaptive_optimum(prior, queries, k)
            fixed = fixed_optimum(prior, queries, k)
            checks.setdefault("interval_optima_formula_exhaustive", True)
            checks["interval_optima_formula_exhaustive"] &= (
                adaptive["mass"] == law["adaptive"] and fixed["mass"] == law["fixed"])
            grid.append((n, k, adaptive["mass"], fixed["mass"]))
    p8, b8 = one_hot_prior(8), interval_bank(8)
    adaptive8 = adaptive_optimum(p8, b8, 3)
    fixed8 = fixed_optimum(p8, b8, 3)
    ap = transcript_profile(p8, b8, adaptive8["tree"])
    fp = transcript_profile(p8, b8, fixed_tree(p8, b8, fixed8["schedule"]))
    checks["one_hot_eight_three_adaptive_is_one"] = adaptive8["bayes_success"] == Q(1)
    checks["one_hot_eight_three_fixed_is_three_quarters"] = fixed8["bayes_success"] == Q(3, 4)
    checks["one_hot_eight_three_8436_schedules"] = fixed8["schedules_checked"] == 8436
    checks["one_hot_adaptive_transcript_reaches_eight"] = ap["leaves"] == 8
    checks["one_hot_fixed_transcript_reaches_six"] = fp["leaves"] == 6
    checks["one_hot_fixed_collision_ratio"] = fp["collision_ratio"] == Q(7, 4)
    checks["one_hot_adaptive_collision_ratio"] = ap["collision_ratio"] == Q(1)
    checks["one_hot_8_adaptive_prefix_collision"] = prefix_collision_sequence(p8, b8, adaptive8["tree"]) == (
        Q(1), Q(1, 2), Q(1, 4), Q(1, 8))
    checks["one_hot_8_conditional_alphabet_bound"] = reachable_alphabet_bound(p8, b8, adaptive8["tree"])["product_bound"] == 8
    checks["one_hot_witness_collision_values"] = (ap["observed_collision_probability"] == Q(1, 8)
                                                     and fp["observed_collision_probability"] == Q(7, 32))
    unrestricted = tuple(tuple((i >> bit) & 1 for i in range(8)) for bit in range(3))
    unrestricted_tree = fixed_tree(p8, unrestricted, (0, 1, 2))
    checks["unrestricted_fixed_queries_eliminate_gap"] = (
        transcript_profile(p8, unrestricted, unrestricted_tree)["leaves"] == 8)


    # Fair independent item bits: an empirical adaptive separation without
    # the one-hot conditional prior. Both optimizers are exhaustive and exact.
    iid_cases = []
    checks["iid_six_bits_three_rounds_adaptive_gain"] = True
    checks["iid_seven_bits_three_rounds_adaptive_gain"] = True
    checks["iid_adaptive_direct_oracle_agrees"] = True
    for n, expected_adaptive, expected_fixed, expected_adaptive_leaves, expected_fixed_leaves in (
        (6, Q(39, 64), Q(17, 32), 39, 34),
        (7, Q(27, 64), Q(3, 8), 54, 48),
    ):
        prior, bank = fair_bit_prior((1,) * n), interval_bank(n)
        adaptive, fixed = adaptive_optimum(prior, bank, 3), fixed_optimum(prior, bank, 3)
        iid_ap = transcript_profile(prior, bank, adaptive["tree"])
        iid_fp = transcript_profile(prior, bank, fixed_tree(prior, bank, fixed["schedule"]))
        target = "iid_six_bits_three_rounds_adaptive_gain" if n == 6 else "iid_seven_bits_three_rounds_adaptive_gain"
        checks[target] &= (
            adaptive["bayes_success"] == expected_adaptive and
            fixed["bayes_success"] == expected_fixed and
            iid_ap["leaves"] == expected_adaptive_leaves and
            iid_fp["leaves"] == expected_fixed_leaves and
            expected_adaptive > expected_fixed)
        checks["iid_adaptive_direct_oracle_agrees"] &= (
            iid_ap == direct_bit_profile(prior.capacities, bank, adaptive["tree"]))
        iid_cases.append({
            "n": n, "budget": 3,
            "adaptive_success": str(adaptive["bayes_success"]),
            "fixed_success": str(fixed["bayes_success"]),
            "adaptive_leaves": iid_ap["leaves"], "fixed_leaves": iid_fp["leaves"],
            "adaptive_collision_probability": str(iid_ap["observed_collision_probability"]),
            "fixed_collision_probability": str(iid_fp["observed_collision_probability"]),
            "fixed_schedule_indices": fixed["schedule"],
            "fixed_schedules_enumerated": fixed["schedules_checked"],
        })

    # Separate oracle enumerates literal item-bit records rather than cell counts.
    direct_compared = 0
    direct_cases = []
    checks["direct_record_enumeration_agrees"] = True
    checks["decision_tree_prefix_collision_mono"] = True
    checks["reachable_leaf_alphabet_bound"] = True
    checks["path_equations_exact"] = True
    for capacities in ((1,), (1, 1), (2, 1), (1, 2, 1), (2, 2)):
        prior = fair_bit_prior(capacities)
        bank = interval_bank(len(capacities))
        schedules = ((), (0,), (len(bank) - 1,), (0, len(bank) - 1))
        for schedule in schedules:
            tree = fixed_tree(prior, bank, schedule)
            profile = transcript_profile(prior, bank, tree)
            direct = direct_bit_profile(capacities, bank, tree)
            seq = prefix_collision_sequence(prior, bank, tree)
            alphabet = reachable_alphabet_bound(prior, bank, tree)
            fibres = leaf_fibres(prior, bank, tree)
            checks["direct_record_enumeration_agrees"] &= profile == direct
            checks["decision_tree_prefix_collision_mono"] &= (
                seq[0] == 1 and seq[-1] == profile["observed_collision_probability"]
                and all(x >= y for x, y in zip(seq, seq[1:])))
            checks["reachable_leaf_alphabet_bound"] &= (
                profile["leaves"] <= alphabet["product_bound"])
            checks["path_equations_exact"] &= (
                sum(len(values) for values in fibres.values()) == len(prior.states))
            direct_compared += 1
            direct_cases.append((capacities, schedule, str(profile["collision_ratio"]),
                                 str(profile["bayes_success"]), alphabet["product_bound"]))

    # The union of all query rows can have full rank while one path hides data.
    bank = ((1, 0), (0, 1))
    prior = fair_bit_prior((1, 1))
    leaf = Node()
    path_sensitive = Node(0, ((0, Node(1, ((0, leaf), (1, leaf)))),
                              (1, Node(0, ((1, leaf),)))))
    checks["full_query_union_can_hide_on_branch"] = (
        transcript((1, 0), path_sensitive, bank) == transcript((1, 1), path_sensitive, bank)
        and transcript_profile(prior, bank, path_sensitive)["leaves"] == 3)
    checks["branchwise_prefix_exact"] = (
        prefix_collision_sequence(prior, bank, path_sensitive) ==
        (Q(1), Q(1, 2), Q(3, 8)))

    # Even at positive rational kernel rank, one particular leaf may have
    # only one feasible solution: the observed right-hand side matters.
    single_sum = fixed_tree(prior, ((1, 1),), (0,))
    fibre = leaf_fibres(prior, ((1, 1),), single_sum)
    checks["path_right_hand_side_matters"] = (
        fibre[((0, 0),)] == ((0, 0),) and
        set(fibre[((0, 1),)]) == {(1, 0), (0, 1)})

    checks["verified_full_prior_sample_count"] = direct_compared == 20
    checks["verified_interval_grid_count"] = len(grid) == 32
    case_sha = sha256(json.dumps((grid, direct_cases, iid_cases), separators=(",", ":")).encode()).hexdigest()
    return {
        "checks": checks,
        "all_passed": all(checks.values()),
        "finite_grid_n_1_to_8_budget_0_to_3": grid,
        "direct_record_cases_checked": direct_compared,
        "iid_fair_bit_cases": iid_cases,
        "case_sha256": case_sha,
        "witness": {
            "n": 8, "query_budget": 3, "query_bank": "contiguous intervals",
            "prior": "one-hot uniform on eight positions",
            "adaptive_success": str(adaptive8["bayes_success"]),
            "fixed_success": str(fixed8["bayes_success"]),
            "adaptive_collision_probability": str(ap["observed_collision_probability"]),
            "fixed_collision_probability": str(fp["observed_collision_probability"]),
            "adaptive_optimal_tree": tree_as_data(adaptive8["tree"]),
            "fixed_best_query_indices": fixed8["schedule"],
        }
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    sources = (
        "src/spiral_ln/evaluation_adaptive_disclosure.py",
        "tests/test_evaluation_adaptive_disclosure.py",
        "scripts/verify_evaluation_adaptive_disclosure.py",
    )
    result = {"schema_version": "0.1",
              "generated_at_utc": datetime.now(timezone.utc).isoformat(), **verify(),
              "source_sha256": {name: sha256((root / name).read_bytes()).hexdigest()
                                for name in sources}}
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as f:
            f.write(rendered)
    else:
        print(rendered, end="")
    return 0 if result["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
