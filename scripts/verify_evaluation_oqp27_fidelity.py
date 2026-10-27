"""Regenerate the exact finite OQP27 objective-fidelity receipt.

Run from the repository root: python scripts/verify_evaluation_oqp27_fidelity.py
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

from spiral_ln.evaluation_oqp27_fidelity import verify

SOURCES = (
    "src/spiral_ln/evaluation_oqp27_fidelity.py",
    "scripts/verify_evaluation_oqp27_fidelity.py",
    "tests/test_evaluation_oqp27_fidelity.py",
    "paper/evaluation_oqp27_objective_fidelity.md",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    report = {
        "schema_version": "0.1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        **verify(),
        "source_sha256": {name: sha256((root / name).read_bytes()).hexdigest() for name in SOURCES},
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(rendered)
    else:
        print(rendered, end="")
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
