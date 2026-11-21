"""Convert pairwise scored results into an EvalMath FSI-01 input.

Input rows must retain errors and gold-invalid tasks in the full denominator.
The optional filtered FSI-01 subset is only a prespecified valid-task analysis;
a post-score exclusion cannot be promoted to independent confirmation.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from manifest import lint


STATUS = {"scored", "infra_error", "invalid_gold", "grader_error"}
FSI_SCHEMA = 1


def compile_receipt(spec, catalog, rows):
    plan = lint(spec, catalog)
    if plan["errors"]:
        raise ValueError("invalid experiment manifest: " + "; ".join(plan["errors"]))
    if not isinstance(rows, list) or not rows:
        raise ValueError("paired scored rows required")
    allowed_roots = set(spec["sampling"]["root_ids"])
    ids, cases, excluded = set(), [], []
    status_counts = Counter()
    full = {"assigned": len(rows), "candidate_success_scored": 0,
            "baseline_success_scored": 0, "scored_pairs": 0}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("result row must be object")
        cid, rid, status = row.get("case_id"), row.get("root_id"), row.get("status")
        if not isinstance(cid, str) or not cid.strip() or cid in ids:
            raise ValueError("case_id must be unique and nonempty")
        ids.add(cid)
        if rid not in allowed_roots:
            raise ValueError(f"case {cid}: undeclared root_id")
        if status not in STATUS:
            raise ValueError(f"case {cid}: status must be explicit")
        status_counts[status] += 1
        if status == "scored":
            a, b = row.get("candidate"), row.get("baseline")
            if type(a) is not int or a not in (0, 1) or type(b) is not int or b not in (0, 1):
                raise ValueError(f"case {cid}: scored pair requires binary candidate and baseline")
            cases.append({"case_id": cid, "cluster_id": rid, "candidate": a, "baseline": b})
            full["scored_pairs"] += 1
            full["candidate_success_scored"] += a
            full["baseline_success_scored"] += b
        else:
            reason = row.get("reason")
            if not isinstance(reason, str) or not reason.strip():
                raise ValueError(f"case {cid}: excluded/error reason required")
            excluded.append({"case_id": cid, "root_id": rid, "status": status, "reason": reason})
    if spec["stage"] == "confirmation" and status_counts["invalid_gold"]:
        # A confirmation run must use the already-audited population; don't
        # transform post-scoring invalid tasks into a favourable denominator.
        raise ValueError("confirmation contains invalid-gold tasks; reassess registered target population")
    if not cases:
        raise ValueError("no pairs scored; FSI-01 requires observed outcomes")
    cl = spec["claim"]
    s = spec["sampling"]
    fsi = {"schema_version": FSI_SCHEMA, "experiment_id": spec["experiment_id"],
           "target_population": cl["target_population"], "evaluation_mode": "sampled",
           "alpha": cl["alpha"], "minimum_effect": cl["minimum_effect"],
           "planned_comparisons": cl["planned_comparisons"],
           "hypothesis_preregistered": bool(spec["controls"].get("registration_frozen", False)),
           "sealed_readout": bool(s["heldout_sealed"] and s["exposure"] == "sealed"),
           "clusters_independent": bool(s["root_independence_attested"]),
           "exchangeable_pair_labels": bool(spec["controls"].get("exchangeable_pair_labels", False)),
           "cases": cases}
    return {"schema": "preferred-evals/paired-receipt-v2", "experiment_id": spec["experiment_id"],
            "stage": spec["stage"], "full_denominator": full,
            "status_counts": dict(sorted(status_counts.items())),
            "non_scored": excluded, "independent_scored_roots": len({x["cluster_id"] for x in cases}),
            "fsi_01_manifest": fsi,
            "limitations": ["Scored subset reports only observed pairs; full assignment retained.",
                           "FSI-01 must independently judge root-level uncertainty and multiplicity.",
                           "Post-hoc invalid-task filtering is barred from prospective confirmation."]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--catalog", type=Path, default=Path(__file__).with_name("catalog.json"))
    ap.add_argument("--rows", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--fsi-out", type=Path)
    args = ap.parse_args()
    data = compile_receipt(json.loads(args.manifest.read_text()),
                           json.loads(args.catalog.read_text()),
                           json.loads(args.rows.read_text()))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    if args.fsi_out:
        args.fsi_out.parent.mkdir(parents=True, exist_ok=True)
        args.fsi_out.write_text(json.dumps(data["fsi_01_manifest"], indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
