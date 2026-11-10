"""Regenerate exact RHC-01 finite primal/dual and cochain certificates."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
from pathlib import Path

from spiral_ln.evaluation_reward_hacking_bootstrap import finite_witness

SOURCES = (
    "src/spiral_ln/evaluation_reward_hacking_bootstrap.py",
    "tests/test_evaluation_reward_hacking_bootstrap.py",
    "scripts/verify_reward_hacking_bootstrap.py",
    "paper/reward_hacking_bootstrap.md",
)


def _encode(value):
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, tuple):
        return list(value)
    raise TypeError(f"cannot encode {type(value)!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    witness = finite_witness()
    report = {
        "schema_version": "0.1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "claim_level": "algebraic identity; finite verified example",
        "scope": "two synthetic attack policies, three signals, two diamond-graph paths; no live agents",
        **witness,
        "source_sha256": {path: sha256((root / path).read_bytes()).hexdigest() for path in SOURCES},
    }
    rendered = json.dumps(report, default=_encode, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as out:
            out.write(rendered)
    else:
        print(rendered, end="")
    return 0 if witness["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
