"""Reproduce exact Unique Games cohomology census (no model and no SAT solver)."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

from spiral_ln.unique_games_topology import finite_census


SOURCES = (
    "src/spiral_ln/unique_games_topology.py",
    "tests/test_unique_games_topology.py",
    "scripts/verify_unique_games_topology.py",
    "paper/unique_games_topology_eth.md",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    census = finite_census()
    checks = {
        "c4_partition": census["c4_F2_2"] == {"0": 64, "1": 192},
        "k23_partition": census["k23_F2_2_gauge_classes"] == {"0": 1, "1": 9, "2": 6},
        "signed_K4_count": census["all_signed_simple_K4_subgraphs"] == 729,
        "independent_oracle_agreement": census["checks"] == 1001,
    }
    report = {
        "schema_version": "0.1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "claim_level": "finite verified example",
        "scope": "F_2^s translation games only; no reduction or ETH proof",
        "census": census,
        "checks": checks,
        "all_passed": all(checks.values()),
        "source_sha256": {path: sha256((root / path).read_bytes()).hexdigest() for path in SOURCES},
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as fd:
            fd.write(rendered)
    else:
        print(rendered, end="")
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
