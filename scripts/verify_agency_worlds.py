"""Regenerate a deterministic exact-rational finite agency receipt."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
from pathlib import Path

from spiral_ln.agency_worlds import fixture


SOURCES = (
    "src/spiral_ln/agency_worlds.py",
    "tests/test_agency_worlds.py",
    "scripts/verify_agency_worlds.py",
    "paper/agency_without_cryptomania.md",
)


def _encode(value: object) -> str:
    if isinstance(value, Fraction):
        return str(value)
    raise TypeError(f"nonserializable: {type(value)!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    report = {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        **fixture(),
        "source_sha256": {name: sha256((root / name).read_bytes()).hexdigest()
                          for name in SOURCES},
    }
    rendered = json.dumps(report, indent=2, default=_encode) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(rendered)
    else:
        print(rendered, end="")
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
