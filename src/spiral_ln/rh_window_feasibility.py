"""Exact dyadic feasibility of the pinned Lean SizeWindows *scalar* predicate.

Checks 16 conjuncts with fractions. No real-valued floating-point approximations,
arithmetic character data, GPsi bound or geometric witness are manufactured.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess

from spiral_ln.rh_distillation import git_blob_sha

PIN = "f150e02623b1e2bbe1f1da8eab5ffee5e930a6a3"
PREDICATE_FILE = "src/Formalism/SizeWindowBrackets/GrowthBoundGivesRiemannHypothesis.lean"
PREDICATE_BLOB = "a3ece4b4aea97a95ba2977fa9e8d437e72677774"
CLAUSES = (
    "x_min", "eps_positive", "C_nonnegative", "n_positive",
    "b_positive", "aE_nonnegative", "aE_cap", "nT_floor",
    "nT2_floor", "nT2_cap", "m_floor", "m_cap",
    "k_floor", "k_cap", "Err_cap", "eventual_x",
)


@dataclass(frozen=True)
class WindowParams:
    x_log2: int
    epsilon: Fraction
    n: int
    nT: int
    nT2: int
    m: int
    k: Fraction
    b: Fraction = Fraction(1)
    C: Fraction = Fraction(0)
    aE: Fraction = Fraction(0)
    Err: Fraction = Fraction(0)

    @property
    def x(self) -> Fraction:
        if not 0 < self.x_log2 <= 32768:
            raise ValueError("invalid x_log2")
        return Fraction(1 << self.x_log2)

    def power(self, exponent: Fraction) -> Fraction:
        """Exact x^a where x=2^e and e*a is an integer."""
        e = self.x_log2 * exponent
        if e.denominator != 1:
            raise ValueError(f"requested power has fractional binary exponent {e}")
        if abs(e.numerator) > 32768:
            raise ValueError("power exceeds bit-budget guard")
        return Fraction(1 << e.numerator) if e.numerator >= 0 else Fraction(1, 1 << -e.numerator)


def dyadic_witness(level: int) -> WindowParams:
    """For epsilon=2^-level, use x=2^(16/epsilon) and n=sqrt(x)."""
    if type(level) is not int or not 1 <= level <= 7:
        raise ValueError("dyadic epsilon level must be 1..7")
    inv = 1 << level
    xp, np = 16 * inv, 8 * inv
    n = 1 << np
    m = 1 << (np - 16)
    return WindowParams(x_log2=xp, epsilon=Fraction(1, inv), n=n,
                        nT=n // 8, nT2=m, m=m, k=Fraction((1 << xp) * m))


def evaluate(p: WindowParams) -> dict:
    if p.epsilon <= 0 or p.n <= 0 or p.nT < 0 or p.nT2 < 0 or p.m < 0 or p.k == 0:
        raise ValueError("invalid input scalars")
    x, eps = p.x, p.epsilon
    n, nt, nt2, m = (Fraction(k) for k in (p.n, p.nT, p.nT2, p.m))
    b, k, C, aE, Err = p.b, p.k, p.C, p.aE, p.Err
    bracket = nt * aE * (1 + m ** 2 / k) + m * (
        (2 * n) * m * b * p.power(eps) +
        nt2 * k * b * p.power(eps) / (n * (n * p.power(-eps))))
    values = {
        "x_min": 3 <= x,
        "eps_positive": 0 < eps,
        "C_nonnegative": 0 <= C,
        "n_positive": 0 < n,
        "b_positive": 0 < b,
        "aE_nonnegative": 0 <= aE,
        "aE_cap": aE <= 2 * x * b,
        "nT_floor": p.power(-eps / 8) * n / 2 <= nt,
        "nT2_floor": p.power(-eps) <= nt2 / n,
        "nT2_cap": nt2 <= n,
        "m_floor": p.power(Fraction(1, 2) - eps) <= m,
        "m_cap": m <= p.power(Fraction(1, 2) + eps / 2),
        "k_floor": x * m <= k,
        "k_cap": k <= n ** 2 * p.power(Fraction(1, 2) - eps),
        "Err_cap": Err <= p.power(C * eps) * bracket,
        "eventual_x": 26 <= p.power(3 * eps / 8),
    }
    assert tuple(values) == CLAUSES
    return {"exact_arithmetic": True, "predicate": "SizeWindows",
            "scope": "scalar conjuncts only",
            "x_log2": p.x_log2, "epsilon": str(eps),
            "n_bits": p.n.bit_length(), "nT_bits": p.nT.bit_length(),
            "nT2_bits": p.nT2.bit_length(), "m_bits": p.m.bit_length(),
            "k_bits": p.k.numerator.bit_length(), "checks": values,
            "total": len(values), "passes": sum(values.values()), "all_pass": all(values.values())}


def source_pin(root: Path) -> dict:
    head = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    if head != PIN:
        raise ValueError(f"source pin mismatch: {head}")
    raw = (root / PREDICATE_FILE).read_bytes()
    if git_blob_sha(raw) != PREDICATE_BLOB:
        raise ValueError("pinned SizeWindows source blob has changed")
    body = raw.decode("utf-8")
    i = body.index("def SizeWindows ")
    j = body.index("\ndef GrowthSizeBound ", i)
    statement = body[i:j]
    for phrase in ("26 ≤ x ^ (3 * ε / 8)", "x * m ≤ k",
                   "nT2 ≤ n", "Err ≤ x ^ (C * ε)", "x ^ (-(ε / 8)) * n / 2 ≤ nT"):
        if phrase not in statement:
            raise ValueError(f"pinned predicate wording no longer matches: {phrase}")
    return {"source_commit": PIN, "source_file": PREDICATE_FILE,
            "git_blob": PREDICATE_BLOB,
            "predicate_sha256": hashlib.sha256(statement.encode()).hexdigest(),
            "original_unlicensed_source_redistributed": False}


def campaign(levels=range(1, 6)) -> dict:
    examples = []
    for level in levels:
        witness = dyadic_witness(level)
        result = evaluate(witness)
        if not result["all_pass"]:
            raise AssertionError(f"exact candidate failed at epsilon level {level}")
        examples.append({"level": level, **result})
    if not examples:
        raise ValueError("at least one level is required")
    valid = dyadic_witness(1)
    near = evaluate(replace(valid, n=valid.n - 1))
    if near["all_pass"] or near["checks"]["k_cap"]:
        raise AssertionError("n-1 negative control did not fail k bound")
    smaller = WindowParams(x_log2=16, epsilon=Fraction(1, 2), n=256, nT=64,
                           nT2=1, m=1, k=Fraction(65536))
    early = evaluate(smaller)
    if early["all_pass"] or early["checks"]["eventual_x"]:
        raise AssertionError("small x negative control did not fail eventual threshold")
    return {
        "schema_version": 1,
        "method": "Fraction arithmetic on dyadic integer powers, no floats",
        "predicate": "Formalism.LFunctionChainParameters.ThickSetMeanBounds.SizeWindows",
        "clauses": list(CLAUSES),
        "positive_examples": examples,
        "negative_controls": [{"mutation": "n=n-1", **near},
                              {"mutation": "x=2^16, epsilon=1/2", **early}],
        "mathematical_scope": "Scalar SizeWindows satisfiability only. No HostFacts, GPsi, ThinScales, SmallCosts, ChainTied, or geometric construction provided.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--levels", type=int, default=5)
    args = parser.parse_args()
    if not 1 <= args.levels <= 7:
        parser.error("--levels must be 1..7")
    result = campaign(range(1, args.levels + 1))
    result["source_identity"] = source_pin(args.source_root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"source_commit": PIN, "feasible_cases": len(result["positive_examples"]),
                      "clause_count": len(CLAUSES),
                      "negative_controls": len(result["negative_controls"]),
                      "all_positive_pass": all(x["all_pass"] for x in result["positive_examples"]),
                      "exact_arithmetic": True,
                      "full_geometric_witness": False}, sort_keys=True))


if __name__ == "__main__":
    main()
