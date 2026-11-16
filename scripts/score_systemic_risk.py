"""Score an exported SystemicRiskBench finite-world case bank with exact EvalMath metrics.

Usage: PYTHONPATH=src python scripts/score_systemic_risk.py --input case_bank.json
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from spiral_ln.evaluation_systemic_risk import json_exact, load_bank, score


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    raw = args.input.read_bytes()
    result = {
        "schema": "SRB-01-scored-v1",
        "source_sha256": sha256(raw).hexdigest(),
        "evidence": "exact evaluation conditional on supplied counterfactual finite-world bank",
        "metrics": json_exact(score(load_bank(args.input))),
    }
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")


if __name__ == "__main__":
    main()
