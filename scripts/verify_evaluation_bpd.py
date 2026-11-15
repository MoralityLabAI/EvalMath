"""Regenerate a source-bound BPD-01 exact finite verification receipt."""
from __future__ import annotations

import argparse
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import random

from spiral_ln.evaluation_bpd import (
    NO_HYPOTHESIS_FITS,
    Probe,
    clock_visibility_floors,
    coverage,
    exhaustive_batch,
    fc12_cell_ledger,
    identify_hypothesis,
    minimum_test_collection,
    optimal_decision_tree_cost,
    refill_witness,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILES = (
    "src/spiral_ln/evaluation_bpd.py",
    "tests/test_evaluation_bpd.py",
    "scripts/verify_evaluation_bpd.py",
    "paper/bpd_interventional_separation.md",
)


def verify() -> dict:
    checked = 0
    for pattern in product(range(8), repeat=3):
        probes = tuple(Probe(str(i), tuple((bit >> j) & 1 for j in range(3)))
                       for i, bit in enumerate(pattern))
        dp = minimum_test_collection(probes)
        brute = exhaustive_batch(probes)
        assert dp == brute
        adaptive = optimal_decision_tree_cost(probes)
        assert (dp is None) == (adaptive is None)
        if dp is not None:
            assert adaptive <= dp[0]
        checked += 1
    rng = random.Random(11617)
    weighted = 0
    for _ in range(96):
        n = rng.randrange(2, 6)
        probes = tuple(Probe(str(i), tuple(rng.randrange(3) for _ in range(n)),
                             rng.randrange(1, 5), rng.choice((True, False, True)))
                       for i, bit in enumerate(range(rng.randrange(1, 7))))
        dp = minimum_test_collection(probes)
        assert dp == exhaustive_batch(probes)
        adaptive = optimal_decision_tree_cost(probes)
        assert (dp is None) == (adaptive is None)
        if dp is not None:
            assert adaptive <= dp[0]
        weighted += 1
    branch = (Probe("root", (0, 0, 1, 1)), Probe("left", (0, 1, 0, 0)),
              Probe("right", (0, 0, 0, 1)))
    switched = (branch[0], Probe("left", branch[1].outcomes, routed=False), branch[2])
    samples = [
        {"case": "g", "component": "c", "intervention": "single", "state": "s0", "visible": "v", "pass": 0, "label": 0},
        {"case": "g", "component": "c", "intervention": "single", "state": "s0", "visible": "v", "pass": 1, "label": 1},
        {"case": "g", "component": "c", "intervention": "single", "state": "s1", "visible": "v", "pass": 2, "label": 1},
    ]
    floor = clock_visibility_floors(samples)
    witness = refill_witness(4, 1)
    fc12_unprobed = fc12_cell_ledger(positives=39, negatives=0, untested=165)
    checks = {
        "all_binary_matrices_independent": checked == 512,
        "weighted_multiway_independent": weighted == 96,
        "adaptive_strict_example": minimum_test_collection(branch)[0] == 3 and optimal_decision_tree_cost(branch) == 2,
        "no_hypothesis_fits_outside_h": identify_hypothesis(branch, (1, 1, 1)) == NO_HYPOTHESIS_FITS,
        "routing_collision": coverage(switched)["separated_pairs"] == 5 and minimum_test_collection(switched) is None,
        "clock_fibre_gap": (floor["state_only"]["minimum_errors"], floor["state_clock"]["minimum_errors"]) == (1, 0),
        "visible_fibre_collision": floor["visible_only"]["minimum_errors"] == 1,
        "early_repair_obscures_final": witness["terminal_blind_early_cuts"] == 3 and witness["persistent_cut_final"] == 0,
        "fc12_ledger_sum_204": fc12_unprobed["total_cells"] == 204 and not fc12_unprobed["has_recorded_negatives"],
    }
    assert all(checks.values())
    return {
        "schema": "BPD-01-v2",
        "evidence": "finite exact deterministic oracle; mathematical proof in paper; no neural or Lean model measurements",
        "binary_matrices": checked,
        "weighted_categorical_cases": weighted,
        "branched_witness": {
            "minimum_test_collection_cost": 3,
            "optimal_decision_tree_cost": 2,
            "outside_h_outcome": identify_hypothesis(branch, (1, 1, 1)),
        },
        "clock_witness": {key: value["minimum_errors"] for key, value in floor.items()},
        "refill_witness": witness,
        "fc12_unprobed_ledger": fc12_unprobed,
        "checks": checks,
        "source_sha256": {p: sha256((ROOT / p).read_bytes()).hexdigest() for p in SOURCE_FILES},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "output/evaluation_bpd/bpd_01.json")
    args = parser.parse_args()
    result = verify()
    path = args.output
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"BPD-01 {result['binary_matrices']} exhaustive + {result['weighted_categorical_cases']} seeded; {len(result['checks'])} checks passed")


if __name__ == "__main__":
    main()
