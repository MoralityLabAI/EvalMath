"""Regenerate a source-hashed, exact finite EVAL-AUTH-01 pilot receipt.

PYTHONPATH=src python scripts/verify_eval_auth01.py --output /tmp/authq01.json
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spiral_ln.evaluation_authorization_quotient import (
    AuthorizationWorld, inspection_value, optimal_observation_policy,
)


def run() -> dict:
    counts = {}
    for n in range(1, 5):
        checked = 0
        for labels in product((False, True), repeat=n):
            for public in product((0, 1), repeat=n):
                for audit in product((0, 1), repeat=n):
                    worlds = [
                        AuthorizationWorld(f"w{i}", str(public[i]), str(audit[i]),
                                           bool(labels[i]), Q(1))
                        for i in range(n)
                    ]
                    old = optimal_observation_policy(worlds)
                    new = optimal_observation_policy(worlds, inspected=True)
                    assert old.error >= new.error
                    assert inspection_value(worlds) == old.error - new.error
                    checked += 1
        counts[str(n)] = checked

    paths = [
        "src/spiral_ln/evaluation_authorization_quotient.py",
        "tests/test_evaluation_authorization_quotient.py",
        "scripts/verify_eval_auth01.py",
    ]
    hashes = {
        path: sha256((ROOT / path).read_bytes()).hexdigest() for path in paths
    }
    return {
        "schema": "eval_auth01_v1",
        "evidence_level": "exact finite enumeration and algebraic identity",
        "model_evaluations": 0,
        "worlds": counts,
        "total_finite_world_families": sum(counts.values()),
        "source_sha256": hashes,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run()
    serialized = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.output is None:
        sys.stdout.write(serialized)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
        print(args.output)
