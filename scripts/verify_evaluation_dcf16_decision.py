"""DCF16-EVAL receipt: scores the three reference predictors on the real DCF-16 held-out split.

The held-out file is read in place from the Compactification-Theory checkout (override the directory
with DCF16_DIR) and is not copied into this repository; the receipt records its SHA-256.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

from spiral_ln.evaluation_dcf16_decision import (
    REFERENCE_PREDICTORS, decide_float, expected_utility, file_digests, is_hard_negative, jsonable,
    load_records, oracle_utility, paired, penalty, report, score,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DIR = Path.home() / "OneDrive/Documents/GitHub/Compactification-Theory/research/dcf16_decision_curriculum"
SOURCES = (
    "src/spiral_ln/evaluation_dcf16_decision.py",
    "tests/test_evaluation_dcf16_decision.py",
    "scripts/verify_evaluation_dcf16_decision.py",
    "scripts/score_dcf16_decision.py",
    "paper/dcf16_decision_eval.md",
    "fixtures/dcf16_heldout_sample.jsonl",
)


def receipt(data_dir: Path) -> dict:
    heldout = data_dir / "data" / "heldout.jsonl.gz"
    manifest = json.loads((data_dir / "MANIFEST.json").read_text(encoding="utf-8"))
    digests = file_digests(heldout)
    recs = load_records(heldout)
    preds = {name: [f(r) for r in recs] for name, f in REFERENCE_PREDICTORS.items()}
    scored = {name: score(recs, p) for name, p in preds.items()}
    rep = {name: {k: v for k, v in s.items() if k != "rows"} for name, s in scored.items()}
    sym, ab, un = (rep[k]["overall"] for k in ("symbolic", "always_abstain", "unary_shortcut"))

    # the record's own operator table must agree with the exact scorer
    op_regret_ok = op_action_ok = n_ops = 0
    for r in recs:
        q, pen = Q(r["verification"]["reference_p"]), penalty(r)
        for o in r["operators"]:
            n_ops += 1
            op_regret_ok += abs(float(oracle_utility(q, pen) - expected_utility(o["action"], q, pen)) - o["regret"]) < 1e-9
            if o["name"] != "particle":
                op_action_ok += o["action"] == decide_float(o["p"], pen)
    n_non_particle = sum(o["name"] != "particle" for r in recs for o in r["operators"])
    oracle_rows = score(recs, [dict(id=r["id"], algorithm=r["selected"]["operator"], action=r["final"]["action"]) for r in recs])
    stored_regret_ok = sum(abs(float(row["regret"]) - r["regret"]) < 1e-9 for r, row in zip(recs, oracle_rows["rows"]))

    pair = paired(recs, preds["symbolic"], preds["unary_shortcut"])
    pair_ab = paired(recs, preds["symbolic"], preds["always_abstain"])
    fams = sorted({r["family"] for r in recs})
    return {
        "experiment": "DCF16-EVAL",
        "evidence_level": "finite verified example: exact rational scoring of stored verifier-grounded records",
        "data": {"file": "dcf16_decision_curriculum/data/heldout.jsonl.gz", **digests,
                 "manifest_sha256_uncompressed": manifest["files"]["heldout.jsonl.gz"]["sha256_uncompressed"],
                 "records": len(recs), "families": fams, "hard_negative_records": sum(map(is_hard_negative, recs)),
                 "selected_operator_counts": dict(sorted(Counter(r["selected"]["operator"] for r in recs).items()))},
        "checks": {
            "heldout_digest_matches_manifest": digests["sha256_uncompressed"] == manifest["files"]["heldout.jsonl.gz"]["sha256_uncompressed"],
            "record_count_matches_manifest": len(recs) == manifest["files"]["heldout.jsonl.gz"]["examples"] == 200,
            "ids_unique": len({r["id"] for r in recs}) == len(recs),
            "hard_negative_count_matches_manifest": sum(map(is_hard_negative, recs)) == manifest["files"]["heldout.jsonl.gz"]["hard_negatives"],
            "stored_operator_regret_reproduced": op_regret_ok == n_ops,
            "stored_operator_action_is_bayes_action": op_action_ok == n_non_particle,
            "stored_oracle_regret_reproduced": stored_regret_ok == len(recs),
            "oracle_selection_has_full_algorithm_accuracy": oracle_rows["overall"]["algorithm_accuracy"] == 1,
            "always_abstain_eu_zero_exact": ab["eu"] == 0 and ab["coverage"] == 0 and ab["selective_risk"] is None,
            "abstain_regret_equals_oracle_eu": ab["regret"] == ab["oracle_eu"],
            "symbolic_within_budget": sym["budget_compliance"] == 1 and sym["claimed_ops_match"] == len(recs),
            "regret_nonnegative_all_predictors": all(rep[k]["overall"]["regret"] >= 0 for k in rep),
            "symbolic_beats_unary_shortcut_on_eu": sym["eu"] > un["eu"],
            "symbolic_beats_always_abstain_on_eu": sym["eu"] > ab["eu"],
            "symbolic_wins_exceed_losses_vs_unary": pair["eu"]["wins"] > pair["eu"]["losses"],
            "pair_counts_partition_records": all(pair[k]["wins"] + pair[k]["losses"] + pair[k]["ties"] == len(recs) for k in pair),
            "heldout_includes_six_heldout_only_families": {"star", "dense", "hyper", "ktree", "xor_noiseless", "weak_dense"} <= set(fams),
        },
        "numbers": {"predictors": jsonable(rep), "paired_symbolic_vs_unary": jsonable(pair),
                    "paired_symbolic_vs_always_abstain": jsonable(pair_ab)},
        "source_sha256": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in SOURCES},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, default=ROOT / "output/evaluation_dcf16_decision/dcf16_eval_v0_1.json")
    ap.add_argument("--data-dir", type=Path, default=Path(os.environ.get("DCF16_DIR", DEFAULT_DIR)))
    args = ap.parse_args()
    r = receipt(args.data_dir)
    failed = [k for k, v in r["checks"].items() if v is not True]
    if failed:
        raise SystemExit(f"DCF16-EVAL receipt failed checks: {failed}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(r, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
