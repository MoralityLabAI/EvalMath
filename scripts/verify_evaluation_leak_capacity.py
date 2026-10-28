"""Regenerate exact capacity/leakage receipt using two independent collision counts."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path

from spiral_ln.evaluation_leak_capacity import (
    bounded_witness, collision_counts_direct, collision_counts_lattice,
    critical_uniform_capacity, sparse_kernel_certificate,
)

NONLOCAL = ((0, 0, 0), (0, 0, 1), (0, 1, 1), (1, 0, 1), (1, 1, 0))
SEPARATE = ((0,), (1,), (2,))


def all_cube_supports():
    grid = tuple(product(range(2), repeat=3))
    for n in range(2, 9):
        for cells in combinations(grid, n):
            if all({cell[j] for cell in cells} == {0, 1} for j in range(3)):
                yield cells


def verify():
    supports = tuple(all_cube_supports())
    positive_rank = strict = silent_rank = 0
    mismatches = 0
    pair_graph_mismatches = 0
    compared = 0
    case_rows = []
    for cells in supports:
        result = collision_counts_lattice(cells, SEPARATE)
        direct = collision_counts_direct(cells, SEPARATE)
        certificate = sparse_kernel_certificate(cells, SEPARATE)
        has_rank = certificate is not None
        has_witness = bounded_witness(cells, SEPARATE) is not None
        if (direct != (result["joint_record_pairs"], result["observed_record_pairs"])
                or has_witness != result["strict"]
                or result["strict"] != (result["collision_ratio"] > 1)):
            mismatches += 1
        if has_rank and not has_witness:
            silent_rank += 1
            if (max(abs(v) for v in certificate) != 2
                    or critical_uniform_capacity(cells, SEPARATE, 2) != 2):
                mismatches += 1
        if certificate is not None and max(abs(v) for v in certificate) > 2:
            mismatches += 1
        positive_rank += has_rank
        strict += has_witness
        case_rows.append((cells, result["joint_record_pairs"], result["observed_record_pairs"], certificate))
        compared += 1
        # Joined pair versus third map: the projection is a bipartite graph.
        for j in range(3):
            faces = (tuple(i for i in range(3) if i != j), (j,))
            value = collision_counts_lattice(cells, faces)
            cert = sparse_kernel_certificate(cells, faces)
            if (collision_counts_direct(cells, faces) !=
                (value["joint_record_pairs"], value["observed_record_pairs"]) or
                (cert is not None) != value["strict"]):
                pair_graph_mismatches += 1
            case_rows.append((cells, j, value["joint_record_pairs"], value["observed_record_pairs"], cert))
            compared += 1
    unit = collision_counts_lattice(NONLOCAL, SEPARATE)
    sizes = (1, 2, 1, 1, 1)
    enlarged = collision_counts_lattice(NONLOCAL, SEPARATE, sizes)
    checks = {
        "193_surjective_cube_supports": len(supports) == 193,
        "all_lattice_direct_comparisons": mismatches == 0,
        "all_pair_joint_graph_comparisons": pair_graph_mismatches == 0,
        "99_positive_rational_kernels": positive_rank == 99,
        "91_strict_binary_leaks": strict == 91,
        "8_rational_but_binary_silent": silent_rank == 8,
        "nonlocal_unit_invisible": unit["collision_ratio"] == 1 and bounded_witness(NONLOCAL, SEPARATE) is None,
        "nonlocal_uniform_threshold_two": critical_uniform_capacity(NONLOCAL, SEPARATE, 2) == 2,
        "nonlocal_one_cell_doubled_ratio": enlarged["collision_ratio"] == Fraction(49, 48),
        "nonlocal_doubled_joint_cp": enlarged["joint_collision_probability"] == Fraction(3, 128),
        "nonlocal_doubled_separate_cp": enlarged["observed_collision_probability"] == Fraction(49, 2048),
        "nonlocal_oracle": collision_counts_direct(NONLOCAL, SEPARATE, sizes) ==
        (enlarged["joint_record_pairs"], enlarged["observed_record_pairs"]),
        "comparison_count": compared == 193 * 4,
    }
    fingerprint = sha256(json.dumps(case_rows, separators=(",", ":")).encode()).hexdigest()
    return {
        "checks": checks,
        "all_passed": all(checks.values()),
        "support_count": len(supports),
        "total_independent_comparisons": compared,
        "strict_unit_support_count": strict,
        "rational_kernel_count": positive_rank,
        "rational_but_unit_silent_count": silent_rank,
        "case_sha256": fingerprint,
        "nonlocal_unit_ratio": str(unit["collision_ratio"]),
        "nonlocal_doubled_ratio": str(enlarged["collision_ratio"]),
        "nonlocal_doubled_joint_cp": str(enlarged["joint_collision_probability"]),
        "nonlocal_doubled_separate_cp": str(enlarged["observed_collision_probability"]),
        "nonlocal_first_move": enlarged["first_move"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    sources = ("src/spiral_ln/evaluation_leak_capacity.py",
               "scripts/verify_evaluation_leak_capacity.py",
               "tests/test_evaluation_leak_capacity.py")
    report = {"schema_version": "0.1",
              "generated_at_utc": datetime.now(timezone.utc).isoformat(),
              **verify(),
              "source_sha256": {name: sha256((root / name).read_bytes()).hexdigest() for name in sources}}
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(rendered)
    else:
        print(rendered, end="")
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
