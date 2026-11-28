"""Replay COG08's adversarial accounting witness and write a source-bound receipt."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from spiral_ln.cogentic_ledger import evaluate, fixture, replay_episode


def build():
    task, events = fixture()
    result = replay_episode(task, events, 6)
    checks = {
        "six_attempts_charged": result["calls"] == 6,
        "five_accepts": result["accepted"] == 5,
        "rejection_charged": result["rejected"] == 1,
        "duplicate_has_zero_new_credit": result["duplicates"] == 1 and result["unique_verified_facts"] == 4,
        "irrelevant_lemma_has_zero_goal_credit": result["goal_ancestor_verified_facts"] == 3,
        "goal_only_completed_on_sixth_call": result["first_solution_call"] == 6,
        "goal_progress_rate_is_exact": result["goal_ancestor_facts_per_call"] == "1/2",
        "zero_cost_rate_is_undefined": replay_episode(task, [], 0)["verified_facts_per_call"] is None,
    }
    for name, key, value in [("forged_receipt_rejected", "accepted", True),
                              ("cost_forgery_rejected", "verifier_calls", 0),
                              ("fake_goal_rejected", "solved", True)]:
        forged = copy.deepcopy(events)
        forged[0]["receipt"][key] = value
        try:
            replay_episode(task, forged, 6)
        except ValueError:
            checks[name] = True
        else:
            checks[name] = False
    protocol = {"schema_version": 1, "arms": ["candidate", "empty"],
                "seeds": [17, 29], "splits": ["development"], "budget": 6}
    rows = [dict(r, arm="candidate", seed=17, root_id=task["root_id"]) for r in events]
    report = evaluate([task], rows, protocol)
    summary = next(r for r in report["summary"] if r["arm"] == "candidate")
    checks["seed_repeats_share_one_root"] = summary["independent_roots"] == 1 and summary["seed_runs"] == 2
    checks["missing_run_retained_in_denominator"] = summary["solve_fraction_exact"] == "1/2"
    paths = ["src/spiral_ln/cogentic_ledger.py", "scripts/verify_cogentic_ledger.py"]
    return {"schema": "EvalMath/cog08-audit/v1", "evidence_level": "finite verified example",
            "source_sha256": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths},
            "checks": checks, "witness": result, "run_coverage_witness": report["summary"]}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, default=ROOT / "output/cogentic_ledger/cog08_v1.json")
    args = p.parse_args()
    receipt = build()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"checks": len(receipt["checks"]), "passed": all(receipt["checks"].values())}))
    return 0 if all(receipt["checks"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
