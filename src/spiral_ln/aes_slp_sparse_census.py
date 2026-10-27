"""Exact affine-support monomial census for pinned NIST AES flat circuits.

For each AND gate z = A*B, A and B are affine Boolean functions of
128 symbolic key bits and earlier AND outputs. XOR/XNOR gate outputs are
eliminated. Quadratic monomial counts are obtained exactly using set
intersections, with no expansion or heuristic sampling.

Usage:
  python scripts/verify_nist_aes_slp.py --input aes.circ.txt --git-blob-sha1 SHA1
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from math import ceil, log2
from typing import Any


@dataclass(frozen=True)
class Affine:
    support: int
    constant: int

    def __post_init__(self) -> None:
        if type(self.support) is not int or self.support < 0 or self.constant not in (0, 1):
            raise ValueError("invalid affine form")


def monomial_counts_for_and(a: Affine, b: Affine) -> dict[str, int]:
    """Counts terms in z + A*B over Boolean quotient F2[x]/(x_i^2-x_i).

    U = supp(A)\supp(B), V = supp(B)\supp(A), I = intersection.
    Cross terms are U×V and I×(U union V); shared×shared cancels.
    """
    common = (a.support & b.support).bit_count()
    only_a = (a.support & ~b.support).bit_count()
    only_b = (b.support & ~a.support).bit_count()
    quadratic = only_a * only_b + common * (only_a + only_b)
    linear = only_a * b.constant + only_b * a.constant + common * (
        1 ^ a.constant ^ b.constant
    )
    constant = a.constant & b.constant
    return {
        "quadratic": quadratic,
        "linear": linear,
        "constant": constant,
        "fresh_nonlinear_coordinate": 1,
        "total": quadratic + linear + constant + 1,
    }


def git_blob_sha1(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def _quantiles(values: list[int]) -> dict[str, int]:
    if not values:
        raise ValueError("empty sample")
    s = sorted(values)
    q = lambda p: s[int((len(s) - 1) * p)]
    return {
        "count": len(s), "minimum": s[0], "median_lower": q(0.5),
        "p90": q(0.9), "p99": q(0.99), "maximum": s[-1],
        "sum": sum(s),
        "above_169": sum(v > 169 for v in s),
        "above_2197": sum(v > 2197 for v in s),
        "above_28561": sum(v > 28561 for v in s),
    }


def slp_census(
    raw: bytes, *,
    key_bits: int = 128,
    plaintext_bits: int = 128,
    output_bits: int = 128,
    plaintext_value: int = 0,
    ciphertext_value: int = 0,
    expected_git_blob_sha1: str | None = None,
) -> dict[str, Any]:
    """Read one full NIST NCFF-2026 SLP, fail closed on unknown gates.

    ptx[i] is fixed to bit i of plaintext_value; key[i] is symbolic.
    A fresh coordinate is introduced at every AND output. The ciphertext
    pins only change constant terms of the output equations.
    """
    sha = git_blob_sha1(raw)
    if expected_git_blob_sha1 is not None and sha != expected_git_blob_sha1:
        raise ValueError("NIST source blob SHA-1 mismatch")
    for width in (key_bits, plaintext_bits, output_bits):
        if type(width) is not int or width < 0:
            raise ValueError("invalid source bit width")
    if type(plaintext_value) is not int or not 0 <= plaintext_value < (1 << plaintext_bits):
        raise ValueError("invalid fixed plaintext")
    if type(ciphertext_value) is not int or not 0 <= ciphertext_value < (1 << output_bits):
        raise ValueError("invalid pinned ciphertext")
    text = raw.decode("utf-8")
    lines = text.splitlines()
    markers = [i for i, line in enumerate(lines) if line.strip() == "begin SLP"]
    endings = [i for i, line in enumerate(lines) if line.strip() == "end SLP"]
    if len(markers) != 1 or len(endings) != 1 or markers[0] >= endings[0]:
        raise ValueError("expected a unique complete SLP")
    header = re.search(
        r"Tally of gates \(G\): (\d+) AND; (\d+) XOR; (\d+) XNOR", text
    )
    if header is None:
        raise ValueError("missing NIST header gate tally")
    expected = dict(zip(("AND", "XOR", "XNOR"), map(int, header.groups())))
    wires = {
        **{f"ptx{i}": Affine(0, (plaintext_value >> i) & 1)
           for i in range(plaintext_bits)},
        **{f"key{i}": Affine(1 << i, 0) for i in range(key_bits)},
    }
    counts = {"AND": 0, "XOR": 0, "XNOR": 0}
    and_total: list[int] = []
    and_quadratic: list[int] = []
    and_linear: list[int] = []
    for line in lines[markers[0] + 1:endings[0]]:
        stripped = line.strip()
        if not stripped or stripped.startswith("%"):
            continue
        parts = stripped.split()
        if len(parts) != 4 or parts[0] not in counts:
            raise ValueError(f"unknown SLP operation: {stripped[:100]}")
        op, out, left, right = parts
        if out in wires:
            raise ValueError(f"duplicate output wire: {out}")
        if left not in wires or right not in wires:
            raise ValueError(f"undefined input wire in: {stripped[:100]}")
        a, b = wires[left], wires[right]
        if op == "AND":
            m = monomial_counts_for_and(a, b)
            and_total.append(m["total"])
            and_quadratic.append(m["quadratic"])
            and_linear.append(m["linear"])
            wires[out] = Affine(1 << (key_bits + counts["AND"]), 0)
        else:
            wires[out] = Affine(a.support ^ b.support,
                                a.constant ^ b.constant ^ int(op == "XNOR"))
        counts[op] += 1
    if counts != expected:
        raise ValueError(f"gate tally disagrees with source header: {counts} != {expected}")
    pins = []
    for j in range(output_bits):
        out = wires.get(f"ctx{j}")
        if out is None:
            raise ValueError(f"missing ciphertext output ctx{j}")
        target = (ciphertext_value >> j) & 1
        pins.append(out.support.bit_count() + (out.constant ^ target))
    n = key_bits + counts["AND"]
    equations = len(and_total) + len(pins)
    maximum = max(and_total + pins)
    if n < 2:
        raise ValueError("insufficient variables for logarithm")
    lam = ceil(log2(n))
    lowest_c = next((c for c in range(1, 16)
                    if equations <= c * n and maximum <= lam ** c), None)
    return {
        "source_git_blob_sha1": sha,
        "source_bytes": len(raw),
        "parameterization": {
            "key_bits": key_bits, "plaintext_bits": plaintext_bits,
            "output_bits": output_bits,
            "plaintext_value_hex": hex(plaintext_value),
            "ciphertext_value_hex": hex(ciphertext_value),
        },
        "gate_tally": counts, "gates": sum(counts.values()),
        "xor_eliminated_coordinates": n, "equations": equations,
        "degree_bound": 2,
        "and_equation_monomials": _quantiles(and_total),
        "and_quadratic_monomials": _quantiles(and_quadratic),
        "and_linear_monomials": _quantiles(and_linear),
        "ciphertext_pin_monomials": _quantiles(pins),
        "max_polynomial_monomials": maximum,
        "ceil_log2_coordinates": lam,
        "minimum_c_at_this_fixed_size": lowest_c,
        "c_bound_checks": [
            {"c": c, "max_monomials_allowed": lam ** c,
             "equations_allowed": c * n,
             "passes_syntactic_checks": equations <= c * n and maximum <= lam ** c}
            for c in range(1, 6)
        ],
        "scope_note": "fixed-size syntactic census only; not a uniform family or implementation of the ETH counting theorem",
    }
