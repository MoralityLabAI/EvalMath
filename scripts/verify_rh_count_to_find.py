#!/usr/bin/env python3
"""Regenerate source-pinned RH-05 exact finite-domain receipts."""
import argparse
import json
from pathlib import Path

from spiral_ln.rh_count_to_find import audit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=("dev", "confirm"), default="dev")
    parser.add_argument("--output", type=Path, default=Path("output/rh_count_to_find/dev.json"))
    args = parser.parse_args()
    result = audit(args.phase)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(f"exact RH-05 receipt: {args.output}; {result['cases']} tasks")


if __name__ == "__main__":
    main()
