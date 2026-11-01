"""Verify exact PPT sample-reuse witnesses; write a source-hashed receipt."""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path

from spiral_ln.evaluation_ppt_reuse import (
    Candidate, FOUR_POINT_PRIOR, TWO_POINT_PRIOR,
    closed_form_two_utility_gap, exact_selection_profile, exact_uniform_coverage,
)

ROOT = Path(__file__).resolve().parents[1]
FILES = (
    "src/spiral_ln/evaluation_ppt_reuse.py",
    "tests/test_evaluation_ppt_reuse.py",
    "scripts/verify_evaluation_ppt_reuse.py",
)


def profile_strings(profile):
    return {key: ([str(x) for x in value] if isinstance(value, tuple) else
                  str(value) if isinstance(value, Q) else value)
            for key, value in profile.items()}


def verify():
    utility_candidates = (Candidate(Q(1, 2), 6, "one"),
                          Candidate(Q(1, 2), 6, "zero"))
    utility = exact_selection_profile(TWO_POINT_PRIOR, utility_candidates, 2)
    prefix_candidates = (Candidate(Q(0), 1, "change"),
                         Candidate(Q(1), 1, "change"))
    prefix = exact_selection_profile(FOUR_POINT_PRIOR, prefix_candidates, 2, Q(1, 16))
    coverage_candidates = (Candidate(Q(1, 4), 2, "one"),
                           Candidate(Q(3, 4), 2, "zero"),
                           Candidate(Q(1, 2), 2, "change"))
    coverage = exact_uniform_coverage(FOUR_POINT_PRIOR, coverage_candidates, 3, Q(1, 8))
    checks = {
        "two_utility_marginal_true_half": utility["true_values"] == (Q(1, 2), Q(1, 2)),
        "two_utility_selected_five_eighths": utility["selected_estimate_mean"] == Q(5, 8),
        "utility_reuse_gap_one_eighth": utility["selection_optimism"] == Q(1, 8),
        "utility_fixed_tail_one_quarter": utility["fixed_false_risks"] == (Q(1, 4), Q(1, 4)),
        "utility_adaptive_tail_one_half": utility["selected_false_risk"] == Q(1, 2),
        "maximal_ess_still_has_selection_bias": utility["min_ess"] == utility["max_ess"] == Q(2),
        "utility_formula_agrees_all_n_1_to_7": all(
            exact_selection_profile(TWO_POINT_PRIOR, utility_candidates, n)["selection_optimism"]
            == closed_form_two_utility_gap(n) for n in range(1, 8)),
        "fixed_utility_equal_true_prefix_values": prefix["true_values"] == (Q(11, 32), Q(11, 32)),
        "prefix_selected_mean_73_over_192": prefix["selected_estimate_mean"] == Q(73, 192),
        "prefix_selection_increment_13_over_480": prefix["extra_over_first_estimator"] == Q(13, 480),
        "prefix_selected_false_risk_three_quarters": prefix["selected_false_risk"] == Q(3, 4),
        "all_candidate_ratio_interval_follows_mean_event": coverage["uniform_event_implies_all_intervals"],
    }
    payload = {
        "name": "PPT-EVAL-01",
        "version": "0.1",
        "evidence": "exact finite toy and algebraic identities; no empirical BFT evaluation or Lean theorem",
        "passed": all(checks.values()),
        "checks": checks,
        "sample_reuse_utility": profile_strings(utility),
        "fixed_utility_prefix_selection": profile_strings(prefix),
        "ratio_interval_audit": profile_strings(coverage),
        "source_sha256": {f: sha256((ROOT / f).read_bytes()).hexdigest() for f in FILES},
    }
    if not payload["passed"]:
        raise AssertionError("PPT reuse certificate failed")
    return payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="output/evaluation_ppt_reuse/ppt_reuse_v0_1.json")
    args = parser.parse_args()
    receipt = verify()
    dest = ROOT / args.output
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{len(receipt['checks'])} checks passed; receipt: {dest.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
