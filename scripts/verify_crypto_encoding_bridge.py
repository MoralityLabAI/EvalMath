#!/usr/bin/env python3
"""Deterministic finite evidence ledger for cipher-to-#SAT encodings."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from spiral_ln.crypto_encoding_bridge import (
    Circuit, count_cnf, eval_poly, local_output_cnf, matches,
    nist_aes_cnf_census, nist_aes_pareto_frontier, sparse_lemma_inventory, tseitin, xor_eliminate,
    zero_count,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCES = (
    "src/spiral_ln/crypto_encoding_bridge.py",
    "tests/test_crypto_encoding_bridge.py",
    "scripts/verify_crypto_encoding_bridge.py",
    "paper/crypto_encoding_bridge.md",
)


def _parity_block(start: int, length: int, inputs: int, existing_gates: list) -> int:
    existing_gates.append(("XOR", start, start + 1))
    for v in range(start + 2, start + length):
        existing_gates.append(("XOR", inputs + len(existing_gates) - 1, v))
    return inputs + len(existing_gates) - 1


def make_receipt() -> dict:
    circ = Circuit(3, (("XOR", 0, 1), ("AND", 3, 2), ("XNOR", 4, 1)), ((5, 1),))
    n, cnf = tseitin(circ)
    n2, polys = xor_eliminate(circ)
    count_direct = sum(matches(circ, x) for x in range(1 << circ.inputs))
    count_boolean = count_cnf(n, cnf)
    count_algebraic = zero_count(n2, polys)

    n_local = 6
    secret = 0b101101
    locality = (0, 2, 4)
    predicate = tuple(x.bit_count() % 2 for x in range(8))
    selected = sum(((secret >> i) & 1) << j for j, i in enumerate(locality))
    target = predicate[selected]
    local_cnf = local_output_cnf(n_local, locality, predicate, target)
    local_direct = sum(predicate[sum(((x >> i) & 1) << j for j, i in enumerate(locality))] == target
                       for x in range(1 << n_local))

    sparse_gates = []
    _parity_block(0, 24, 24, sparse_gates)
    linear = Circuit(24, tuple(sparse_gates), ((24 + len(sparse_gates) - 1, 1),))
    lin_n, lin_eq = xor_eliminate(linear)
    lin_inventory = sparse_lemma_inventory(lin_n, lin_eq, 2, 2)

    dense_gates = []
    first = _parity_block(0, 12, 24, dense_gates)
    second = _parity_block(12, 12, 24, dense_gates)
    dense_gates.append(("AND", first, second))
    nonlinear = Circuit(24, tuple(dense_gates), ((24 + len(dense_gates) - 1, 1),))
    dense_n, dense_eq = xor_eliminate(nonlinear)
    dense_inventory = sparse_lemma_inventory(dense_n, dense_eq, 2, 2)

    aes = nist_aes_cnf_census()
    frontier = nist_aes_pareto_frontier()
    checks = {
        "tseitin_toy_exact_count": count_boolean == count_direct,
        "xor_eliminated_toy_exact_count": count_algebraic == count_direct,
        "xor_eliminated_toy_fewer_variables": n2 < n,
        "local_map_no_aux_variable": len(locality) == max(map(len, local_cnf)),
        "local_map_exact_count": count_cnf(n_local, local_cnf) == local_direct,
        "affine_system_meets_manuscript_syntactic_conditions": lin_inventory["eligible_on_stated_syntactic_conditions"],
        "affine_system_25_terms": len(lin_eq[0]) == 25,
        "quadratic_system_exceeds_fixed_sparsity": not dense_inventory["eligible_on_stated_syntactic_conditions"],
        "quadratic_system_145_terms": len(dense_eq[0]) == 145,
        "quadratic_system_preserves_low_degree": dense_inventory["maximum_degree"] == 2,
        "nist_aes_gate_census": aes["gates"] == 28_600,
        "nist_aes_tseitin_census": aes["tseitin_variables"] == 28_728 and aes["tseitin_clauses"] == 108_128,
        "nist_aes_subexp_proxy_above_bruteforce": aes["optimistic_fixed_density_exponent_proxy"] > aes["key_bits"],
        "nist_frontier_header_count": [(x["gates"], x["tseitin_variables"], x["tseitin_clauses"]) for x in frontier] == [
            (27856, 27984, 105152), (33656, 33784, 128952)
        ],
        "nist_and_minimum_changes_coordinate_budget": (
            frontier[1]["unverified_xor_elimination_variable_count"] == 5928
            and frontier[1]["gates"] > frontier[0]["gates"]
        ),
    }
    return {
        "schema_version": "crypto-encoding-bridge-v1",
        "evidence_levels": {
            "toy_counts": "finite_verified_example",
            "aes_gate_census": "cited_from_nist_not_slp_replayed",
            "sparse_poly_lemma": "manuscript_statement_only",
            "formal_sat_bound": "pinned_upstream_lean_scope_claim",
        },
        "source_sha256": {
            path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in SOURCES
        },
        "checks": checks,
        "all_passed": all(checks.values()),
        "small_circuit_counts": {
            "input_bits": circ.inputs, "tseitin_variables": n,
            "xor_eliminated_variables": n2, "input_preimages": count_direct,
            "tseitin_preimages": count_boolean, "polynomial_preimages": count_algebraic,
        },
        "local_function": {
            "input_bits": n_local, "locality": len(locality),
            "clauses": len(local_cnf), "preimages": local_direct,
        },
        "sparse_lemma_positive_control": lin_inventory,
        "sparse_lemma_negative_control": dense_inventory,
        "nist_aes_128_census": aes,
        "nist_pareto_frontier_census": list(frontier),
        "warning": "No real cipher cryptanalysis, executable ETH implementation, key search, or practical speedup is claimed.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    receipt = make_receipt()
    serialized = json.dumps(receipt, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
        print(f"wrote {args.output}: {sum(receipt['checks'].values())} checks")
    else:
        print(serialized, end="")
    return 0 if receipt["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
