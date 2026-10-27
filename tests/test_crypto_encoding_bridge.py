"""Exact toy-equivalence checks; no live cryptography or key attacks."""
from __future__ import annotations

import itertools

import pytest

from spiral_ln.crypto_encoding_bridge import (
    Circuit, count_cnf, eval_cnf, eval_poly, execute, local_output_cnf,
    matches, nist_aes_cnf_census, poly_add, poly_mul, poly_to_cnf,
    sparse_lemma_inventory, system_to_cnf, tseitin, xor_eliminate,
    zero_count,
)


def check(circuit):
    n, cnf = tseitin(circuit)
    n2, polys = xor_eliminate(circuit)
    actual = sum(matches(circuit, bits) for bits in range(1 << circuit.inputs))
    assert count_cnf(n, cnf) == actual
    assert zero_count(n2, polys) == actual
    assert count_cnf(n2, system_to_cnf(n2, polys)) == actual
    assert n2 == circuit.inputs + sum(op == "AND" for op, *_ in circuit.gates)
    return n, n2, cnf, polys


def test_single_gate_truth_table_and_unique_witness():
    for op in ("AND", "XOR", "XNOR"):
        for expected in (0, 1):
            circ = Circuit(2, ((op, 0, 1),), ((2, expected),))
            n, n2, cnf, polys = check(circ)
            assert n == 3
            assert n2 == (3 if op == "AND" else 2)
            assert len(cnf) == (4 if op != "AND" else 3) + 1
            assert all(len(clause) <= 3 for clause in cnf)


def test_nontrivial_chained_affine_and_nonlinear():
    circuits = (
        Circuit(3, (("XOR", 0, 1), ("AND", 3, 2), ("XNOR", 4, 1)), ((5, 1),)),
        Circuit(3, (("AND", 0, 1), ("XOR", 3, 2), ("AND", 4, 0)), ((5, 0), (4, 1))),
        Circuit(2, (("XOR", 0, 0), ("AND", 2, 1), ("XNOR", 3, 1)), ((4, 1),)),
        Circuit(3, (("XOR", 0, 1), ("XNOR", 3, 2), ("XOR", 4, 1)), ((5, 0),)),
    )
    for circ in circuits:
        check(circ)


def test_toy_exhaustive_gate_chains_with_output_pins():
    # All 3^2 gate types, all input pairs including identical wires, and
    # both target values: independent enumeration checks both encodings.
    for op1, op2 in itertools.product(("AND", "XOR", "XNOR"), repeat=2):
        for a, b in itertools.product(range(3), repeat=2):
            for expected in (0, 1):
                circ = Circuit(2, ((op1, 0, 1), (op2, a, b)), ((3, expected),))
                check(circ)


def test_local_map_preserves_original_variables():
    n = 6
    seed = 0b101101
    specs = (
        ((0, 2, 4), tuple(x.bit_count() % 2 for x in range(8))),
        ((1, 2, 5), tuple(int(x in (3, 7)) for x in range(8))),
        ((0, 3), (0, 1, 1, 0)),
        ((2, 3, 4), tuple((x & 1) & ((x >> 1) & 1) for x in range(8))),
    )
    all_clauses = []
    for scope, table in specs:
        idx = sum(((seed >> i) & 1) << j for j, i in enumerate(scope))
        target = table[idx]
        clauses = local_output_cnf(n, scope, table, target)
        assert all(len(c) == len(scope) for c in clauses)
        assert len(clauses) <= 1 << len(scope)
        all_clauses.extend(clauses)
    assert eval_cnf(all_clauses, seed)
    actual = 0
    for key in range(1 << n):
        good = all(table[sum(((key >> i) & 1) << j for j, i in enumerate(scope))] ==
                   table[sum(((seed >> i) & 1) << j for j, i in enumerate(scope))]
                   for scope, table in specs)
        actual += good
        assert good == eval_cnf(all_clauses, key)
    assert count_cnf(n, all_clauses) == actual


def test_local_map_constant_and_malformed():
    assert local_output_cnf(2, (), (1,), 1) == ()
    assert local_output_cnf(2, (), (1,), 0) == ((),)
    with pytest.raises(ValueError):
        local_output_cnf(2, (0, 0), (0, 1, 0, 1), 0)
    with pytest.raises(ValueError):
        local_output_cnf(2, (2,), (0, 1), 0)


def test_boolean_polynomial_normalization_and_direct_cnf():
    a = frozenset((1, 3, 7))
    b = frozenset((1, 6))
    assert poly_add(a, b) == frozenset((3, 6, 7))
    assert poly_mul(frozenset((1,)), frozenset((1,))) == frozenset((1,))
    assert poly_mul(frozenset((0, 1)), frozenset((0, 1))) == frozenset((0, 1))
    for masks in ((), (0,), (1, 2, 0), (1, 2, 3), (3, 5, 7)):
        p = frozenset(masks)
        clauses = poly_to_cnf(3, p)
        assert len(clauses) <= 1 << 3
        for x in range(8):
            assert (eval_poly(p, x) == 0) == eval_cnf(clauses, x)


def test_structural_sparse_lemma_gate_fails_closed():
    linear = tuple(frozenset((1 << (i % 23),)) for i in range(30))
    ok = sparse_lemma_inventory(30, linear, degree_bound=2, c=2)
    assert ok["eligible_on_stated_syntactic_conditions"]
    assert ok["monomial_limit"] == 25
    assert ok["maximum_degree"] == 1
    dense = (frozenset(range(26)),)
    bad = sparse_lemma_inventory(30, dense, 2, 2)
    assert "monomial_bound_exceeded" in bad["failures"]
    bad = sparse_lemma_inventory(30, (frozenset((1 << 0 | 1 << 1 | 1 << 2,)),), 2, 2)
    assert "degree_bound_exceeded" in bad["failures"]
    bad = sparse_lemma_inventory(30, linear * 3, 2, 2)
    assert "too_many_equations" in bad["failures"]
    assert "n_below_20" in sparse_lemma_inventory(5, (frozenset((1,)),), 2, 2)["failures"]


def test_nist_aes_census_is_published_gate_arithmetic():
    d = nist_aes_cnf_census()
    assert d["gates"] == 28_600
    assert d["tseitin_variables"] == 28_728
    assert d["tseitin_clauses"] == 108_128
    assert d["unverified_xor_elimination_variable_count_ceiling"] == 6_528
    assert 7_460 < d["optimistic_fixed_density_exponent_proxy"] < 7_470
    assert d["variables_per_key_bit"] > 200


def test_xor_elimination_preserves_affine_sparsity_positive_control():
    # Parity on 24 inputs produces one 25-term linear relation after XOR elimination.
    gates = [("XOR", 0, 1)]
    for v in range(2, 24):
        gates.append(("XOR", 24 + len(gates) - 1, v))
    circ = Circuit(24, tuple(gates), ((24 + len(gates) - 1, 1),))
    n, polys = xor_eliminate(circ)
    assert n == 24 and len(polys) == 1
    assert len(polys[0]) == 25  # 24 singleton monomials and constant 1
    eligibility = sparse_lemma_inventory(n, polys, degree_bound=2, c=2)
    assert eligibility["eligible_on_stated_syntactic_conditions"]
    assert eligibility["monomial_limit"] == 25
    for bits in (0, 1, 3, 7, (1 << 24) - 1, (1 << 24) - 2):
        assert (eval_poly(polys[0], bits) == 0) == matches(circ, bits)


def test_xor_elimination_quadratic_monomial_explosion_negative_control():
    # Two 12-input parities multiplied into an AND give 12^2 distinct
    # quadratic terms after the XOR wires are removed.
    gates = []
    end = []
    for start in (0, 12):
        gates.append(("XOR", start, start + 1))
        for v in range(start + 2, start + 12):
            gates.append(("XOR", 24 + len(gates) - 1, v))
        end.append(24 + len(gates) - 1)
    gates.append(("AND", end[0], end[1]))
    circ = Circuit(24, tuple(gates), ((24 + len(gates) - 1, 1),))
    n, polys = xor_eliminate(circ)
    assert n == 25 and len(polys) == 2
    assert len(polys[0]) == 145  # 144 cross terms and fresh AND output
    assert len(polys[1]) == 2  # pin AND output to true
    eligibility = sparse_lemma_inventory(n, polys, degree_bound=2, c=2)
    assert "monomial_bound_exceeded" in eligibility["failures"]
    assert eligibility["maximum_degree"] == 2
    for bits in (0, 1, 3, 7, 0x123456, 0xabcdef, (1 << 24) - 1):
        computed = execute(circ, bits)
        extension = bits | (computed[-1] << 24)
        assert all(eval_poly(poly, extension) == 0 for poly in polys) == matches(circ, bits)
        flipped = extension ^ (1 << 24)
        assert eval_poly(polys[0], flipped) == 1
