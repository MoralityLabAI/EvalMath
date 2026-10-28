#!/usr/bin/env python3
"""Emit deterministic Cryptomania Assumption Audit evidence.

Usage:
  python scripts/verify_cryptomania_audit.py [--scenario unadjudicated] [--output PATH]

JSON has no clock time. A failed check exits nonzero. Publications are never
automatically promoted to facts; only explicit scenario literals are propagated.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from spiral_ln.cryptomania_audit import (
    WORLD_ORDER, bayes_example, compatible_worlds, propagate, report,
)
from spiral_ln.cryptomania_toy_count import run_toy_suite

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "configs/cryptomania_assumptions_v1.json"
SOURCES = (
    "configs/cryptomania_assumptions_v1.json",
    "src/spiral_ln/cryptomania_audit.py",
    "src/spiral_ln/cryptomania_toy_count.py",
    "tests/test_cryptomania_audit.py",
    "paper/cryptomania_assumption_audit.md",
    "scripts/verify_cryptomania_audit.py",
)


def make_receipt(scenario: str = "unadjudicated") -> dict:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    audit = report(data, scenario)
    rows = run_toy_suite()
    empty, _ = propagate(data, {"ETH": False})
    count, _ = propagate(data, {"HASH_ETH": False})
    reported, _ = propagate(data, data["scenarios"]["accept_october_2026_reports"])
    checks = {
        "five_worlds_under_eth_false": compatible_worlds(data, {"ETH": False}) == list(WORLD_ORDER),
        "eth_false_does_not_refute_count_eth": empty["HASH_ETH"] is None,
        "count_eth_false_implies_eth_false": count["ETH"] is False,
        "reported_lwe_remains_unadjudicated": reported["LWE_HARD"] is None,
        "reported_pke_remains_unadjudicated": reported["PKE"] is None,
        "no_reported_scenario_eliminates_worlds": len(
            compatible_worlds(data, data["scenarios"]["accept_october_2026_reports"])
        ) == 5,
        "toy_count_equivalence": all(row["exactly_equal"] for row in rows),
        "connected_controls_no_assignment_proxy_gain": all(
            row["baseline_assignments"] == row["factorized_assignments"]
            for row in rows if row["linked_control"]
        ),
        "disconnected_controls_assignment_proxy_gain": all(
            row["factorized_assignments"] < row["baseline_assignments"]
            for row in rows if not row["linked_control"]
        ),
        "exact_bayesian_tenfold": bayes_example()["algorithmica_multiplier"] == "10",
        "all_observations_stage_gated": audit["evidence_not_promoted"] == len(data["evidence"]),
    }
    receipt = {
        "schema_version": "cryptomania-audit-v1",
        "scenario": scenario,
        "source_sha256": {
            rel: hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() for rel in SOURCES
        },
        "checks": checks,
        "all_passed": all(checks.values()),
        "audit": audit,
        "toy_count": rows,
        "metric_caveat": "assignment enumeration proxy; no timing and no general SAT speedup",
    }
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", default="unadjudicated")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    receipt = make_receipt(args.scenario)
    serialized = json.dumps(receipt, sort_keys=True, indent=2) + "\n"
    if args.output is None:
        print(serialized, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
        print(f"wrote {args.output} ({sum(receipt['checks'].values())} checks)")
    return 0 if receipt["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
