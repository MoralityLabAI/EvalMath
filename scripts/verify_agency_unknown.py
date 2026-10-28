"""Regenerate exact FAW-03 unknown-reliability Bayesian experiment receipt."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
from pathlib import Path

from spiral_ln.agency_unknown import fixture

SOURCES = (
    "src/spiral_ln/agency_unknown.py",
    "tests/test_agency_unknown.py",
    "scripts/verify_agency_unknown.py",
    "paper/agency_unknown_reliability.md",
)


def _encode(value: object) -> str:
    if isinstance(value, Fraction):
        return str(value)
    raise TypeError(f"cannot encode {type(value)!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        **fixture(),
        "source_sha256": {rel: sha256((root/rel).read_bytes()).hexdigest()
                          for rel in SOURCES},
    }
    output = json.dumps(report, indent=2, default=_encode)+"\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(output)
    else:
        print(output, end="")
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
