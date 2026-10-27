"""Regenerate the exact HRC-FRC-01 synthetic receipt, with source hashes."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from spiral_ln.evaluation_frc_resonance import verify


SOURCES = (
    "src/spiral_ln/evaluation_frc_resonance.py",
    "tests/test_evaluation_frc_resonance.py",
    "scripts/verify_evaluation_frc_resonance.py",
    "paper/frc_harmonic_self_evaluation.md",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    payload = {
        "schema_version": "hrc-frc-01.1",
        **verify(),
        "source_sha256": {name: sha256((root / name).read_bytes()).hexdigest() for name in SOURCES},
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if payload["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
