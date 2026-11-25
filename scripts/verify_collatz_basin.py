"""Regenerate COL-EVAL-01 exact public train/dev receipts.

The public hash split prevents parameter overlap in exports. It does not attest
that a future model or researcher has never seen a parameter. No holdout scores
are produced by this verifier.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from math import gcd
from pathlib import Path

from spiral_ln.evaluation_collatz_basin import (
    SCHEMA, enumerate_core, parameter_split, parameter_summary, summarize,
)

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=ROOT / "output/collatz_basin/col_eval_01.json")
    args = parser.parse_args()
    references = json.loads((ROOT / "fixtures/collatz_basin/small_reference.json").read_text())
    reference_checks = []
    for reference in references:
        core = enumerate_core(reference["d"])
        row = parameter_summary(reference["d"])
        reference_checks.append(row["residue_quotients"] == reference["quotient_count"])
        reference_checks.append(Fraction(row["quotient_ceiling"]) == Fraction(*reference["quotient_ceiling"]))
        reference_checks.append(row["cycle_counts"] == [
            {key: value for key, value in c.items() if key not in {"gcd_with_d", "basin_size"}}
            for c in reference["cycles"]])
        reference_checks.append(all(
            sum(label == c["minimum"] for label in core.basin.values()) == c["basin_size"]
            for c in reference["cycles"]))
    parameters = [d for d in range(1, 4094, 4) if gcd(d, 6) == 1]
    rows = [parameter_summary(d) for d in parameters if parameter_split(d) != "holdout"]
    by_split = {split: [row for row in rows if row["split"] == split] for split in ("train", "dev")}
    holdout = [d for d in parameters if parameter_split(d) == "holdout"]
    checks = {
        "independent_mathcan_reference_matches": all(reference_checks),
        "train_dev_parameters_disjoint": not ({r["d"] for r in by_split["train"]} &
                                               {r["d"] for r in by_split["dev"]}),
        "holdout_absent_from_scored_rows": not (set(holdout) & {r["d"] for r in rows}),
        "quotient_ceiling_refines_gcd": all(Fraction(r["constant_ceiling"]) <=
                                               Fraction(r["gcd_ceiling"]) <=
                                               Fraction(r["quotient_ceiling"]) <= 1 for r in rows),
        "every_observed_collision_has_ceiling_loss": all(bool(r["collision_witnesses"]) ==
                                                            (Fraction(r["quotient_ceiling"]) < 1)
                                                            for r in rows),
        "complete_case_accounting": sum(r["n_cases"] for r in rows) ==
                                     sum((r["d"] + 1) // 2 for r in rows),
        "cross_reference_checks_40": len(reference_checks) == 40,
    }
    sources = ["src/spiral_ln/evaluation_collatz_basin.py", "scripts/verify_collatz_basin.py",
               "scripts/export_collatz_basin.py",
               "tests/test_evaluation_collatz_basin.py", "fixtures/collatz_basin/small_reference.json",
               "paper/collatz_basin_readout.md", "configs/collatz_basin_pilot.json",
               "output/collatz_basin/preflight.json"]
    report = {
        "schema": SCHEMA, "evidence": "finite verified example",
        "unit": "parameter d", "distribution": "uniform odd core within each d",
        "max_parameter": 4093, "holdout_parameter_count": len(holdout),
        "holdout_manifest_sha256": hashlib.sha256(json.dumps(holdout).encode()).hexdigest(),
        "readout_selection_exposure": "public deterministic fixtures; no sealed neural confirmation claim",
        "reference_scope": "ten public parameters, including every basin size and branch count",
        "checks": checks,
        "summaries": {split: summarize(values) for split, values in by_split.items()},
        "rows": rows,
        "source_sha256": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in sources},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"checks": checks, "summaries": report["summaries"],
                      "holdout_parameter_count": len(holdout)}, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
