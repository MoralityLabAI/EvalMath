"""Exact finite encodings for ETH-to-cryptography applicability audits.

Counts are toy exhaustions or audited gate census, never runtime estimates.
A multilinear Boolean polynomial over F2 is a set of integer monomial masks.
Symmetric difference adds polynomials; bitwise OR multiplies monomials in
F2[x]/(x_i^2-x_i). Symbolic XOR-elimination preserves the number of solutions
when uniquely-determined gate wires are removed.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import log2, sqrt
from typing import Iterable

Gate = tuple[str, int, int]   # operation, left wire, right wire (zero-based)
Clause = tuple[int, ...]       # signed one-based SAT literals
Poly = frozenset[int]          # monomial bitmask; mask zero is constant 1


@dataclass(frozen=True)
class Circuit:
    inputs: int
    gates: tuple[Gate, ...]
    pins: tuple[tuple[int, int], ...] = ()

    def validate(self) -> None:
        if type(self.inputs) is not int or not 0 <= self.inputs <= 30:
            raise ValueError("bad input count")
        for i, (op, a, b) in enumerate(self.gates):
            if op not in ("AND", "XOR", "XNOR") or not all(
                type(t) is int and 0 <= t < self.inputs + i for t in (a, b)
            ):
                raise ValueError("invalid gate or forward reference")
        for wire, bit in self.pins:
            if type(wire) is not int or not 0 <= wire < self.inputs + len(self.gates):
                raise ValueError("bad output wire")
            if type(bit) is not int or bit not in (0, 1):
                raise ValueError("bad output bit")


def execute(circuit: Circuit, input_bits: int) -> tuple[int, ...]:
    circuit.validate()
    if type(input_bits) is not int or not 0 <= input_bits < 1 << circuit.inputs:
        raise ValueError("input outside domain")
    wires = [(input_bits >> i) & 1 for i in range(circuit.inputs)]
    for op, a, b in circuit.gates:
        x, y = wires[a], wires[b]
        wires.append((x & y) if op == "AND" else (x ^ y) if op == "XOR" else (x ^ y ^ 1))
    return tuple(wires)


def matches(circuit: Circuit, input_bits: int) -> bool:
    wires = execute(circuit, input_bits)
    return all(wires[i] == bit for i, bit in circuit.pins)


def _reject(a: int, b: int, z: int, first: int, second: int, output: int) -> Clause:
    """CNF clause excluding exactly the indicated assignment."""
    return tuple((-v if assigned else v) for v, assigned in
                 ((first, a), (second, b), (output, z)))


def tseitin(circuit: Circuit) -> tuple[int, tuple[Clause, ...]]:
    """One uniquely constrained variable per gate; <=4 3-clauses per gate."""
    circuit.validate()
    clauses: list[Clause] = []
    for i, (op, a, b) in enumerate(circuit.gates):
        first, second, out = a + 1, b + 1, circuit.inputs + i + 1
        if op == "AND":
            clauses.extend(((-first, -second, out), (first, -out), (second, -out)))
        else:
            invert = 1 if op == "XNOR" else 0
            for x in (0, 1):
                for y in (0, 1):
                    wrong = 1 ^ x ^ y ^ invert
                    clauses.append(_reject(x, y, wrong, first, second, out))
    for wire, bit in circuit.pins:
        clauses.append(((wire + 1) if bit else -(wire + 1),))
    return circuit.inputs + len(circuit.gates), tuple(clauses)


def eval_cnf(clauses: Iterable[Clause], assignment: int) -> bool:
    return all(any(bool(assignment & (1 << (abs(lit) - 1))) == (lit > 0)
                   for lit in clause) for clause in clauses)


def count_cnf(n: int, clauses: Iterable[Clause]) -> int:
    if type(n) is not int or not 0 <= n <= 20:
        raise ValueError("bounded exact witness allows <=20 Boolean variables")
    clauses = tuple(clauses)
    return sum(eval_cnf(clauses, assignment) for assignment in range(1 << n))


def poly_add(a: Poly, b: Poly) -> Poly:
    return a.symmetric_difference(b)


def poly_mul(a: Poly, b: Poly) -> Poly:
    acc: set[int] = set()
    for left in a:
        for right in b:
            term = left | right
            if term in acc:
                acc.remove(term)
            else:
                acc.add(term)
    return frozenset(acc)


def eval_poly(poly: Poly, assignment: int) -> int:
    return sum((assignment & term) == term for term in poly) & 1


def zero_count(n: int, system: Iterable[Poly]) -> int:
    if type(n) is not int or not 0 <= n <= 20:
        raise ValueError("bounded exact witness allows <=20 Boolean variables")
    eqs = tuple(system)
    return sum(all(eval_poly(p, x) == 0 for p in eqs) for x in range(1 << n))


def xor_eliminate(circuit: Circuit) -> tuple[int, tuple[Poly, ...]]:
    """Eliminate XOR/XNOR outputs; leave one coordinate per AND.

    For every AND z=a*b, add z + A*B=0 over F2, where A,B are affine
    expressions on initial inputs and earlier AND coordinates. Endpoint pins
    add affine constraints. All assignments extend uniquely to circuit wires.
    """
    circuit.validate()
    affine = [frozenset((1 << i,)) for i in range(circuit.inputs)]
    equations: list[Poly] = []
    next_variable = circuit.inputs
    for op, a, b in circuit.gates:
        if op == "AND":
            z = frozenset((1 << next_variable,))
            equations.append(poly_add(z, poly_mul(affine[a], affine[b])))
            affine.append(z)
            next_variable += 1
        elif op == "XOR":
            affine.append(poly_add(affine[a], affine[b]))
        else:
            affine.append(poly_add(poly_add(affine[a], affine[b]), frozenset((0,))))
    for wire, bit in circuit.pins:
        equations.append(poly_add(affine[wire], frozenset((0,)) if bit else frozenset()))
    return next_variable, tuple(equations)


def poly_to_cnf(n: int, poly: Poly, scope_limit: int = 14) -> tuple[Clause, ...]:
    """Truth-table clauses with no auxiliary variables; limited toy scope.

    Each invalid assignment to variables in the polynomial's support yields
    one clause. The constant polynomial 1 produces one empty clause.
    """
    if type(n) is not int or n < 0:
        raise ValueError("bad variable count")
    if any(type(mask) is not int or not 0 <= mask < 1 << n for mask in poly):
        raise ValueError("bad polynomial monomial")
    scope = sorted({i for mask in poly for i in range(n) if mask & (1 << i)})
    if len(scope) > scope_limit:
        raise ValueError("truth table would exceed bounded witness scope")
    clauses = []
    for bits in range(1 << len(scope)):
        x = sum(((bits >> j) & 1) << i for j, i in enumerate(scope))
        if eval_poly(poly, x):
            clauses.append(tuple((-(i + 1) if (x >> i) & 1 else i + 1) for i in scope))
    return tuple(clauses)


def system_to_cnf(n: int, system: Iterable[Poly], scope_limit: int = 14) -> tuple[Clause, ...]:
    return tuple(clause for poly in system for clause in poly_to_cnf(n, poly, scope_limit))


def local_output_cnf(n: int, inputs: tuple[int, ...], truth_table: tuple[int, ...], target: int) -> tuple[Clause, ...]:
    """Encode one output bit of a fixed-locality map directly on key bits.

    inputs are zero-based positions; truth_table indexed by low-to-high bits.
    One width-d clause excludes each local tuple with an incorrect output.
    """
    if type(n) is not int or n < 0 or len(set(inputs)) != len(inputs) or any(
        type(i) is not int or not 0 <= i < n for i in inputs
    ) or not all(type(v) is int and v in (0, 1) for v in truth_table) or len(truth_table) != 1 << len(inputs):
        raise ValueError("malformed local truth table")
    if type(target) is not int or target not in (0, 1):
        raise ValueError("invalid desired output")
    clauses = []
    for mask, value in enumerate(truth_table):
        if value != target:
            clauses.append(tuple((-(index + 1) if (mask >> j) & 1 else index + 1)
                                 for j, index in enumerate(inputs)))
    return tuple(clauses)


def sparse_lemma_inventory(n: int, polys: tuple[Poly, ...], degree_bound: int, c: int) -> dict:
    """Gate the *manuscript-only* sparse polynomial counting lemma.

    Its hypotheses: n>=20; <=c*n equations; each listed equation has
    <=ceil(log2(n))**c monomials and degree <=fixed k=degree_bound.
    Boolean multilinearization is already baked into bitmask monomials.
    This does not certify the underlying theorem or its hidden constants.
    """
    if any(type(x) is not int or x < 1 for x in (n, degree_bound, c)):
        raise ValueError("n, fixed degree k, fixed c must be positive integers")
    if any(any(type(m) is not int or not 0 <= m < (1 << n) for m in poly) for poly in polys):
        raise ValueError("monomial outside declared variables")
    lam = (n - 1).bit_length()
    max_terms = max((len(p) for p in polys), default=0)
    max_degree = max((mon.bit_count() for p in polys for mon in p), default=0)
    failures = []
    if n < 20:
        failures.append("n_below_20")
    if len(polys) > c * n:
        failures.append("too_many_equations")
    if max_terms > lam ** c:
        failures.append("monomial_bound_exceeded")
    if max_degree > degree_bound:
        failures.append("degree_bound_exceeded")
    return {
        "n": n, "equations": len(polys), "maximum_monomials": max_terms,
        "maximum_degree": max_degree, "fixed_k": degree_bound, "fixed_c": c,
        "monomial_limit": lam ** c, "eligible_on_stated_syntactic_conditions": not failures,
        "failures": failures, "proof_level": "manuscript_only_not_lean_endpoint",
    }


NIST_AES_128 = {
    "key_bits": 128, "ciphertext_pins": 128, "and": 6400,
    "xor": 21356, "xnor": 844,
    "source": "https://csrc.nist.gov/projects/circuit-complexity/list-of-circuits",
    "object": "AES-128(k,m) published SLP census, variable key and message",
}


def nist_aes_cnf_census() -> dict:
    """Exact gate-count arithmetic for one published SLP, not an AES attack.

    Freeze plaintext bits as constants. No gate simplification or elimination
    is assumed. Each binary gate gets a Tseitin variable. Output pins each
    contribute one unit clause, and key bits remain free. An implementation
    would need to instantiate the NIST SLP to validate this counting model.
    """
    s = NIST_AES_128
    gates = s["and"] + s["xor"] + s["xnor"]
    variables = s["key_bits"] + gates
    clauses = 3 * s["and"] + 4 * (s["xor"] + s["xnor"]) + s["ciphertext_pins"]
    proxy = variables / sqrt(log2(variables))
    return {
        **s, "gates": gates, "tseitin_variables": variables,
        "tseitin_clauses": clauses, "clauses_per_variable": clauses / variables,
        "variables_per_key_bit": variables / s["key_bits"],
        "optimistic_fixed_density_exponent_proxy": round(proxy, 3),
        "proxy_over_bruteforce_key_exponent": round(proxy / s["key_bits"], 3),
        "unverified_xor_elimination_variable_count_ceiling": s["key_bits"] + s["and"],
        "proxy_warning": "C=1 exponent proxy; theorem has unknown large constants and no finite-scale efficiency guarantee; eliminating XORs may densify polynomials",
    }
