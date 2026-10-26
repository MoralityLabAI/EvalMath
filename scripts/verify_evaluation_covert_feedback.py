"""Reproducible exact finite risk certificates for bounded covert feedback."""
from __future__ import annotations

import argparse
import json
import random
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path

from spiral_ln.evaluation_selection_risk import (
    NullModel, QueryNode, dependent_five_percent_models,
    full_information_risk,
)
from spiral_ln.evaluation_covert_feedback import (
    brute_force_covert_risk, covert_risk, covert_tree_risk,
    covert_witness_labels, independent_boolean_null,
    minimum_full_exposure_messages,
)


def verify() -> dict:
    checks = {}
    shared, disjoint = dependent_five_percent_models()
    checks["marginals_equal_public_risk_equal"] = (
        shared.marginals() == disjoint.marginals() == (Q(1, 20), Q(1, 20))
        and covert_risk(shared, 1)["risk"] == covert_risk(disjoint, 1)["risk"] == Q(1, 20))
    checks["correlated_one_hidden_bit_remains_five_percent"] = (
        covert_risk(shared, 2)["risk"] == Q(1, 20))
    checks["disjoint_one_hidden_bit_doubles_risk"] = (
        covert_risk(disjoint, 2)["risk"] == Q(1, 10))
    checks["dependence_changes_minimum_hidden_alphabet"] = (
        minimum_full_exposure_messages(shared)["messages"] == 1
        and minimum_full_exposure_messages(disjoint)["messages"] == 2)

    disjoint3 = NullModel((17, 1, 1, 1),
                          ((False, True, False, False),
                           (False, False, True, False),
                           (False, False, False, True)), ((0, 1, 0, 0),))
    checks["factor_two_bound_is_sharp"] = (
        covert_risk(disjoint3, 1)["risk"] == Q(1, 20)
        and covert_risk(disjoint3, 2)["risk"] == Q(1, 10)
        and covert_risk(disjoint3, 3)["risk"] == Q(3, 20))
    checks["covert_witness_realizes_upper_bound"] = (
        covert_witness_labels(disjoint3, 2)["covered_mass"] == 2)

    iid = independent_boolean_null(3)
    checks["iid_marginals_exact"] = (iid.total == 8000
                                     and iid.marginals() == (Q(1, 20),) * 3)
    checks["iid_one_bit_risk"] = covert_risk(iid, 2)["risk"] == Q(39, 400)
    checks["iid_two_bit_full_risk"] = (
        covert_risk(iid, 3)["risk"] == Q(1141, 8000)
        and full_information_risk(iid) == Q(1141, 8000))
    public = (tuple(i for i in range(8) if iid.events[0][i] is False),
              tuple(i for i in range(8) if iid.events[0][i] is True))
    checks["public_one_bit_plus_covert_one_bit_reaches_full"] = (
        covert_risk(iid, 1, public)["risk"] == Q(39, 400)
        and covert_risk(iid, 2, public)["risk"] == Q(1141, 8000))
    checks["min_hidden_alphabet_three_to_two_after_public_bit"] = (
        minimum_full_exposure_messages(iid)["messages"] == 3
        and minimum_full_exposure_messages(iid, public)["messages"] == 2)
    terminal = QueryNode()
    policy = QueryNode(1, ((0, terminal), (1, terminal)))
    checks["existing_query_tree_adapter"] = (
        covert_tree_risk(iid, policy, 2)["risk"] == Q(1141, 8000))

    # Randomized *deterministic-seed* finite exact comparisons against a
    # separately coded oracle that enumerates hidden message assignments.
    rng = random.Random(2601026)
    cases = []
    correct = ordered = bounded = True
    total = 0
    for n in range(2, 7):
        for _ in range(14):
            null = NullModel(tuple(rng.randrange(1, 9) for _ in range(n)),
                             tuple(tuple(bool(rng.randrange(2)) for _ in range(n))
                                   for _ in range(3)),
                             (tuple(rng.randrange(2) for _ in range(n)),))
            reports = tuple(covert_risk(null, m) for m in (1, 2, 3))
            for m, report in zip((1, 2, 3), reports):
                correct &= report["risk"] == brute_force_covert_risk(null, m)
                bounded &= report["risk"] <= min(report["full_information_risk"],
                                                   m * report["public_risk"])
                total += 1
            ordered &= reports[0]["risk"] <= reports[1]["risk"] <= reports[2]["risk"]
            cases.append((n, null.weights,
                          tuple(tuple(int(x) for x in ev) for ev in null.events),
                          tuple(str(report["risk"]) for report in reports)))

    checks["210_independent_hidden_assignment_oracles"] = correct and total == 210
    checks["70_monotone_alphabet_sequences"] = ordered and len(cases) == 70
    checks["210_coverage_and_factor_bounds"] = bounded
    checks["fair_zero_one_boundary"] = (
        covert_risk(NullModel((1,), ((False,),), ((0,),)), 1)["risk"] == 0
        and covert_risk(NullModel((1,), ((True,),), ((0,),)), 5)["risk"] == 1)
    digest = sha256(json.dumps(cases, separators=(',', ':')).encode()).hexdigest()
    return {
        "checks": checks, "all_passed": all(checks.values()),
        "independent_oracle_comparisons": total,
        "seeded_models": len(cases), "case_sha256": digest,
        "nominal_event_rate": "1/20",
        "disjoint_one_bit": "1/10",
        "shared_one_bit": "1/20",
        "iid_three_events_hidden_one_bit": str(covert_risk(iid, 2)["risk"]),
        "iid_three_events_full_exposure": str(covert_risk(iid, 3)["risk"]),
        "public_bit_plus_hidden_bit": str(covert_risk(iid, 2, public)["risk"]),
        "minimum_messages_sealed": minimum_full_exposure_messages(iid)["messages"],
        "minimum_messages_after_first_public_bit": minimum_full_exposure_messages(iid, public)["messages"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    sources = ("src/spiral_ln/evaluation_covert_feedback.py",
               "tests/test_evaluation_covert_feedback.py",
               "scripts/verify_evaluation_covert_feedback.py")
    report = {"schema_version": "0.1",
              "generated_at_utc": datetime.now(timezone.utc).isoformat(),
              **verify(),
              "source_sha256": {p: sha256((root / p).read_bytes()).hexdigest()
                                for p in sources}}
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as out:
            out.write(rendered)
    else:
        print(rendered, end="")
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
