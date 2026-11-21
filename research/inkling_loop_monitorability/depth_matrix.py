"""Descriptive, root-aware Inkling depth audit and FSI-01 manifest export.

This module DOES NOT compute a confirmatory p-value or inspect protected
splits. The exported FSI manifest has registration and seal flags false.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any


def _jsonl(path: Path) -> list[dict[str, Any]]:
    if path.stat().st_size > 32 * 1024 * 1024:
        raise ValueError("input exceeds 32 MiB bound")
    rows = []
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise ValueError("all rows must be JSON objects")
                rows.append(value)
    if not rows or len(rows) > 100000:
        raise ValueError("missing or too many rows")
    return rows


def _positive_number(value: Any) -> bool:
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def audit(rows: list[dict[str, Any]], *, baseline_depth: int, candidate_depth: int) -> tuple[dict, dict]:
    """Reject incomplete or split-reused depth sweeps. Keep root clusters explicit."""
    if not 1 <= baseline_depth < candidate_depth <= 64:
        raise ValueError("choose ascending positive loop depths <= 64")
    cells: dict[tuple[str, int], dict[str, Any]] = {}
    root_for_case: dict[str, str] = {}
    family_for_case: dict[str, str] = {}
    common_fields: dict[str, Any] = {}
    depths = set()
    for row in rows:
        for name in ("case_id", "root_id", "family", "model_sha", "cache_mode", "split"):
            if not isinstance(row.get(name), str) or not row[name]:
                raise ValueError(f"missing identifier {name}")
        if row["split"] not in {"train", "calibration", "development"}:
            raise ValueError("audit is development only; reserved splits remain sealed")
        if row.get("fixture") is True or row.get("oracle") is True:
            raise ValueError("fixture and oracle rows are excluded from model comparison")
        if type(row.get("depth")) is not int or not 1 <= row["depth"] <= 64:
            raise ValueError("invalid architectural depth")
        if type(row.get("verified")) is not bool:
            raise ValueError("environment-owned verified correctness required")
        for optional in ("reasoning_tokens", "total_tokens", "wall_ms", "joules"):
            if row.get(optional) is not None and not _positive_number(row[optional]):
                raise ValueError(f"invalid {optional}")
        case_id, depth = row["case_id"], row["depth"]
        key = (case_id, depth)
        if key in cells:
            raise ValueError("duplicate case/depth record")
        if case_id in root_for_case and root_for_case[case_id] != row["root_id"]:
            raise ValueError("case changed root across depths")
        if case_id in family_for_case and family_for_case[case_id] != row["family"]:
            raise ValueError("case changed family across depths")
        root_for_case[case_id] = row["root_id"]
        family_for_case[case_id] = row["family"]
        for shared in ("model_sha", "cache_mode", "split"):
            if shared in common_fields and common_fields[shared] != row[shared]:
                raise ValueError(f"comparison changed {shared}")
            common_fields[shared] = row[shared]
        cells[key] = row
        depths.add(depth)
    if not {baseline_depth, candidate_depth} <= depths:
        raise ValueError("requested depths are absent")
    expected = {(case_id, depth) for case_id in root_for_case for depth in depths}
    if expected != set(cells):
        raise ValueError("incomplete matched case by depth matrix")
    if len(set(root_for_case.values())) < 2:
        raise ValueError("at least two source roots required for descriptive comparisons")

    by_depth = []
    for depth in sorted(depths):
        subset = [cells[(case_id, depth)] for case_id in sorted(root_for_case)]
        successes = sum(item["verified"] for item in subset)
        report = {"depth": depth, "verified_correct": successes, "n_cases": len(subset),
                  "accuracy": successes / len(subset)}
        for field in ("reasoning_tokens", "total_tokens", "wall_ms", "joules"):
            available = [row[field] for row in subset if row.get(field) is not None]
            report[f"mean_{field}"] = sum(available) / len(available) if available else None
            report[f"{field}_known_cases"] = len(available)
        by_depth.append(report)

    paired = []
    cluster_cases: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for case_id in sorted(root_for_case):
        a, b = cells[(case_id, baseline_depth)], cells[(case_id, candidate_depth)]
        pair = {
            "case_id": case_id, "root_id": root_for_case[case_id],
            "family": family_for_case[case_id],
            "baseline": int(a["verified"]), "candidate": int(b["verified"]),
            "difference": int(b["verified"]) - int(a["verified"]),
        }
        paired.append(pair)
        cluster_cases[pair["root_id"]].append(pair)
    root_means = [sum(p["difference"] for p in group) / len(group) for group in cluster_cases.values()]
    mean_root_effect = sum(root_means) / len(root_means)

    fsi = {
        "schema_version": 1,
        "experiment_id": f"inkling_pass_{candidate_depth}_vs_{baseline_depth}_DEV_ONLY",
        "target_population": "operator-specified development roots; external independence unverified",
        "evaluation_mode": "sampled", "alpha": "0.05", "minimum_effect": "0.00",
        "planned_comparisons": len(depths) - 1,
        "hypothesis_preregistered": False, "sealed_readout": False,
        "clusters_independent": False, "exchangeable_pair_labels": False,
        "cases": [
            {"case_id": p["case_id"], "cluster_id": p["root_id"],
             "candidate": p["candidate"], "baseline": p["baseline"]}
            for p in paired
        ],
    }
    result = {
        "schema_version": "inkling_depth_audit.v1",
        "evidence_class": "descriptive_development_only",
        "model_sha": common_fields["model_sha"],
        "cache_mode": common_fields["cache_mode"],
        "split": common_fields["split"],
        "depths": sorted(depths), "source_roots": len(cluster_cases),
        "case_count": len(root_for_case), "baseline_depth": baseline_depth,
        "candidate_depth": candidate_depth, "per_depth": by_depth,
        "root_macro_paired_effect": mean_root_effect,
        "case_weighted_paired_effect": sum(p["difference"] for p in paired) / len(paired),
        "first_stage_training_depth_confound": True,
        "monitorability_not_inferred_from_legibility": True,
        "claim_boundary": (
            "Scores are descriptive on development data. Depths share roots. "
            "FSI-01 requires prospective registration, independent roots, "
            "sham resolution and a sealed confirmation set."
        ),
    }
    return result, fsi


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--baseline-depth", type=int, default=1)
    parser.add_argument("--candidate-depth", type=int, default=3)
    args = parser.parse_args()
    if args.out.exists():
        parser.error("output directory already exists")
    rows = _jsonl(args.input)
    report, fsi = audit(rows, baseline_depth=args.baseline_depth,
                        candidate_depth=args.candidate_depth)
    report["input_sha256"] = hashlib.sha256(args.input.read_bytes()).hexdigest()
    args.out.mkdir(parents=True)
    (args.out / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (args.out / "fsi_dev_manifest.json").write_text(
        json.dumps(fsi, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"out": str(args.out), "roots": report["source_roots"],
                      "root_effect": report["root_macro_paired_effect"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
