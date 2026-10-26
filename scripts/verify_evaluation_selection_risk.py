"""Reproduce selection-risk and continuation-state mathematical certificates."""
from __future__ import annotations

import argparse
import json
import random
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path

from spiral_ln.evaluation_selection_risk import (
    NullModel, adaptive_optimum, compress_contingency,
    dependent_five_percent_models, distinguish, exhaustive_two_round_optimum,
    fixed_optimum, full_information_risk, hidden_prepeek_risk, no_feedback_risk,
    one_step_profile, partition_refinement, root_and_amendment_machine,
    run_events, state_bits,
)


def verify() -> dict:
    checks: dict[str, bool] = {}
    shared, disjoint = dependent_five_percent_models()
    checks["marginal_five_percent_rates_match"] = (
        shared.marginals() == disjoint.marginals() == (Q(1, 20), Q(1, 20)))
    checks["same_current_decision_risk"] = (
        no_feedback_risk(shared) == no_feedback_risk(disjoint) == Q(1, 20))
    checks["different_risk_after_one_observation"] = (
        adaptive_optimum(shared, 1)["risk"] == Q(1, 20)
        and adaptive_optimum(disjoint, 1)["risk"] == Q(1, 10)
        and one_step_profile(shared, 0) != one_step_profile(disjoint, 0))

    toy = NullModel(
        (1, 1, 1, 1, 36),
        ((False, True, False, False, False),
         (False, False, True, True, False),
         (True, False, False, False, False)),
        ((1, 1, 0, 1, 0),
         (0, 0, 0, 1, 0),
         (1, 0, 0, 1, 0)),
    )
    fixed = fixed_optimum(toy, 2)
    adaptive = adaptive_optimum(toy, 2)
    checks["each_event_at_most_five_percent"] = max(toy.marginals()) == Q(1, 20)
    checks["two_rounds_nominal_five_percent"] = no_feedback_risk(toy) == Q(1, 20)
    checks["two_rounds_fixed_seven_point_five_percent"] = fixed["risk"] == Q(3, 40)
    checks["two_rounds_adaptive_ten_percent"] = adaptive["risk"] == Q(1, 10)
    checks["two_rounds_full_information_bound_is_tight"] = full_information_risk(toy) == adaptive["risk"]
    checks["two_rounds_independent_policy_enumerator"] = (
        exhaustive_two_round_optimum(toy) == adaptive["risk"])
    checks["post_selection_prepeek_exact"] = (
        hidden_prepeek_risk(20, Q(1, 20)) == 1 - Q(19, 20) ** 20)

    rng = random.Random(7319)
    cases = []
    independent_equal = True
    compression_equal = True
    ordered = True
    for n in range(2, 6):
        for _ in range(48):
            events = tuple(tuple(bool(rng.getrandbits(1)) for _ in range(n))
                           for _ in range(3))
            queries = tuple(tuple(rng.randrange(3) for _ in range(n))
                            for _ in range(3))
            null = NullModel(tuple(rng.randrange(1, 8) for _ in range(n)), events, queries)
            opt = adaptive_optimum(null, 2)["risk"]
            independent_equal &= opt == exhaustive_two_round_optimum(null)
            ordered &= no_feedback_risk(null) <= fixed_optimum(null, 2)["risk"] <= opt <= full_information_risk(null)
            reduced = compress_contingency(null)
            compression_equal &= (adaptive_optimum(reduced, 2)["risk"] == opt
                                  and fixed_optimum(reduced, 2)["risk"] == fixed_optimum(null, 2)["risk"])
            cases.append([n, list(null.weights), [list(map(int, e)) for e in null.events],
                          [list(q) for q in null.queries], str(opt)])
    checks["192_independent_two_round_exhaustive_checks"] = independent_equal and len(cases) == 192
    checks["192_risk_monotonicity_checks"] = ordered
    checks["192_contingency_compression_checks"] = compression_equal

    classes = []
    for m in range(1, 5):
        machine = root_and_amendment_machine(m)
        quotient = partition_refinement(machine)
        classes.append([m, len(quotient), state_bits(len(quotient))])
    checks["3_times_2_power_m_minimal_classes"] = all(
        count == 3 * 2 ** m for m, count, _ in classes)
    checks["m_plus_two_minimal_bits"] = all(bits == m + 2 for m, _, bits in classes)
    machine = root_and_amendment_machine(3)
    witness_pair_count = 0
    all_distinct = True
    for left in range(24):
        for right in range(left + 1, 24):
            suffix = distinguish(machine, left, right)
            all_distinct &= suffix is not None
            if suffix is not None:
                all_distinct &= run_events(machine, left, suffix)[1] != run_events(machine, right, suffix)[1]
            witness_pair_count += 1
    checks["276_independent_pairwise_continuation_witnesses"] = all_distinct and witness_pair_count == 276
    unseen_state, current_label = run_events(machine, 0, ("GRANT_0",))
    seen_state, current_label_after = run_events(machine, 0, ("GRANT_0", "VIEW"))
    checks["same_current_label_amendment_order_counterexample"] = (
        current_label == current_label_after == ("GO", "eligible")
        and run_events(machine, unseen_state, ("AMEND",))[1] == ("GO", "eligible")
        and run_events(machine, seen_state, ("AMEND",))[1] == ("GO", "exploratory"))
    root_a = run_events(machine, 0, ("GRANT_0",))[0]
    root_b = run_events(machine, 0, ("GRANT_1",))[0]
    checks["same_GO_distinct_revocable_roots"] = (
        machine.outputs[root_a] == machine.outputs[root_b]
        and run_events(machine, root_a, ("REVOKE_0",))[1][0] == "STOP"
        and run_events(machine, root_b, ("REVOKE_0",))[1][0] == "GO")

    digest = sha256(json.dumps(cases, separators=(",", ":")).encode("utf-8")).hexdigest()
    return {
        "checks": checks, "all_passed": all(checks.values()),
        "independent_policy_comparisons": len(cases),
        "continuation_pair_witnesses": witness_pair_count,
        "model_samples_sha256": digest,
        "nominal_five_percent": str(no_feedback_risk(toy)),
        "fixed_two_queries": str(fixed["risk"]),
        "adaptive_two_queries": str(adaptive["risk"]),
        "correlated_one_query": str(adaptive_optimum(shared, 1)["risk"]),
        "disjoint_one_query": str(adaptive_optimum(disjoint, 1)["risk"]),
        "prepeek_twenty_candidates": str(hidden_prepeek_risk(20, Q(1, 20))),
        "audit_minimal_classes_by_roots": classes,
        "exact_fixed_schedule": list(fixed["schedule"]),
        "adaptive_two_query_tree": str(adaptive["tree"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    sources = (
        "src/spiral_ln/evaluation_selection_risk.py",
        "tests/test_evaluation_selection_risk.py",
        "scripts/verify_evaluation_selection_risk.py",
    )
    result = {
        "schema_version": "0.1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        **verify(),
        "source_sha256": {p: sha256((root / p).read_bytes()).hexdigest() for p in sources},
    }
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
