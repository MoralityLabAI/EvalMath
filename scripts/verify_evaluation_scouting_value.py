"""Recompute the source-hashed SCOUT-01 development receipt, without network/model calls."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from spiral_ln import evaluation_scouting_value as s  # noqa: E402

SOURCES = (
    "src/spiral_ln/evaluation_scouting_value.py",
    "tests/test_evaluation_scouting_value.py",
    "scripts/verify_evaluation_scouting_value.py",
    "paper/scout01_information_purchase.md",
)


def canonical_json(obj: object) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def receipt() -> dict:
    worlds = s.development_cases()
    cases = {(w.root_id, w.case_id): w for w in worlds}
    views = s.development_views()
    cheap = cases[("scout-cost-001", "cheap")]
    tie = cases[("scout-cost-001", "break_even")]
    expensive = cases[("scout-cost-001", "expensive")]
    shared = cases[("provenance-003", "shared_relays")]
    independent = cases[("provenance-003", "independent_witnesses")]
    cue = cases[("cue-trap-002", "cue_conflict")]
    checks = {
        "distinct_root_count_five": len({w.root_id for w in worlds}) == 5,
        "twelve_development_cases": len(worlds) == 12,
        "eight_views_two_roots": len(views) == 8 and len({v["parent_root"] for v in views}) == 2,
        "cost_point_one_scout": s.values(cheap)[s.SCOUT] == F(7, 10)
                                and s.optimal_actions(cheap) == (s.SCOUT,),
        "cost_point_three_exact_tie": s.optimal_actions(tie) == s.ACTIONS,
        "cost_point_four_commit": s.optimal_actions(expensive) == (s.LEFT, s.RIGHT),
        "gross_value_three_tenths": s.information_value(cheap) == F(3, 10),
        "shared_report_scout": s.posterior_right(shared) == F(2, 5)
                               and s.optimal_actions(shared) == (s.SCOUT,),
        "independent_reports_commit": s.posterior_right(independent) == F(8, 35)
                                      and s.optimal_actions(independent) == (s.LEFT,),
        "double_count_control_fails": s.regret(shared, s.policy_action(shared, "double_count_relays")) == F(1, 10),
        "cue_control_fails": s.regret(cue, s.policy_action(cue, "cue_following")) == F(3, 5),
        "always_scout_control_fails": s.regret(expensive, s.SCOUT) == F(1, 10),
        "cosmetic_sham_invariant": all(
            s.values(cases[(root, original)]) == s.values(cases[(root, "cosmetic_cue")])
            for root, original in (("cue-trap-002", "cue_conflict"),
                                   ("provenance-003", "shared_relays"))
        ),
        "independent_enumerator_agrees": all(
            s.enumerated_expected_reward(w, a) == value
            for w in worlds for a, value in s.values(w).items()
        ),
        "exact_policy_zero_regret": all(s.regret(w, s.policy_action(w, "exact")) == 0 for w in worlds),
        "public_omits_oracle": all(
            not {"root_id", "case_id", "posterior_right", "optimal_actions", "action_values"}
            .intersection(s.public_task(w)) for w in worlds
        ),
    }
    case_records = []
    for w in worlds:
        grade = s.private_grade(w)
        case_records.append({
            "root_id": w.root_id, "case_id": w.case_id, "split": "dev",
            "public_task_sha256": sha256(canonical_json(s.public_task(w))),
            "grader": grade,
        })
    cases_hash = sha256(canonical_json(case_records))
    return {
        "schema": "scout01-dev-v1", "evidence_level": "finite synthetic development; unsealed",
        "heldout_sealed": False,
        "independent_generator_roots": len({w.root_id for w in worlds}),
        "development_cases": len(worlds),
        "development_views": len(views),
        "case_records_sha256": cases_hash,
        "source_sha256": {path: sha256((ROOT / path).read_bytes()) for path in SOURCES},
        "checks": checks,
        "cases": case_records,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, default=ROOT / "output/evaluation_scouting_value/scout01_dev_v1.json")
    args = p.parse_args()
    result = receipt()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"SCOUT-01: {sum(result['checks'].values())}/{len(result['checks'])} checks, "
          f"{result['independent_generator_roots']} development roots, "
          f"{result['development_cases']} cases, {result['development_views']} linked views")
    return 0 if all(result["checks"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
