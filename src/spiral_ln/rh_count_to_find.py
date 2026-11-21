"""RH-CRYPTO-26 / RH-05: exact finite-field count-to-find negative-control gym.

This is an *exact finite-domain synthetic task*, not a model-power study or a
theorem that a hard polynomial system is easy/hard. All systems here are affine
with an explicit one-query constructive solver.

Run: PYTHONPATH=src python -m spiral_ln.rh_count_to_find --phase dev
Optional grading: ... --submissions /path/to/queries.jsonl
Each submission is {"id": "...", "queries": [[x,y], ...]}.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

PHASE_PRIMES = {"dev": (17, 31), "confirm": (43, 53)}
FORMS = ("early_vertical", "late_vertical", "late_horizontal", "scrambled")


def is_prime_trial(n: int) -> bool:
    return n >= 2 and all(n % d for d in range(2, math.isqrt(n) + 1))


@dataclass(frozen=True)
class Instance:
    p: int
    a: int
    b: int
    c: int
    id: str

    def __post_init__(self):
        if not is_prime_trial(self.p):
            raise ValueError("p must be prime")
        if self.a % self.p == 0 and self.b % self.p == 0:
            raise ValueError("nonzero affine coefficient required")

    def accepts(self, x: int, y: int) -> bool:
        return (self.a * x + self.b * y - self.c) % self.p == 0

    def construct(self):
        """Explicit affine solver; cost of inversion is outside query-count score."""
        if self.b % self.p:
            return (0, self.c * pow(self.b, -1, self.p) % self.p)
        return (self.c * pow(self.a, -1, self.p) % self.p, 0)

    def verify_by_enumeration(self):
        first = None
        count = 0
        checks = 0
        for x in range(self.p):
            for y in range(self.p):
                checks += 1
                if self.accepts(x, y):
                    count += 1
                    if first is None:
                        first = checks
        if count != self.p:
            raise AssertionError("affine counting invariant violated")
        candidate = self.construct()
        if not self.accepts(*candidate):
            raise AssertionError("explicit witness failed")
        return {"solution_count": count, "first_lexicographic_query": first,
                "enumeration_queries": checks, "constructed_witness": list(candidate),
                "constructive_witness_queries": 1}


def make_instances(phase="dev"):
    if phase not in PHASE_PRIMES:
        raise ValueError("unknown phase")
    cases = []
    for p in PHASE_PRIMES[phase]:
        parameters = (
            (1, 0, 0),
            (1, 0, p - 1),
            (0, 1, p - 1),
            (3, 7, p - 1),
        )
        for name, (a, b, c) in zip(FORMS, parameters):
            cases.append(Instance(p, a, b, c, f"RHCF-{phase}-p{p}-{name}"))
    return cases


def combinatorial_first_hit_bound(N: int, M: int):
    """For exactly M marked states among N, worst first hit is N-M+1."""
    if not (1 <= M <= N):
        raise ValueError("require 1 <= M <= N")
    return N - M + 1


def uniform_without_replacement_expectation(N: int, M: int) -> Fraction:
    if not (1 <= M <= N):
        raise ValueError("require 1 <= M <= N")
    return Fraction(N + 1, M + 1)


def exact_first_hit_distribution(N: int, M: int):
    """Probability of earliest of M uniformly sampled marked locations."""
    if not (1 <= M <= N):
        raise ValueError("require 1 <= M <= N")
    denom = math.comb(N, M)
    return [Fraction(math.comb(N - t, M - 1), denom)
            for t in range(1, N - M + 2)]


def grade_queries(case: Instance, queries):
    if not isinstance(queries, list):
        raise ValueError("queries must be a list")
    limit = case.p * case.p
    if len(queries) > limit:
        raise ValueError("query budget exceeds full enumeration")
    for j, point in enumerate(queries, 1):
        if (not isinstance(point, list) or len(point) != 2
                or any(type(x) is not int or not (0 <= x < case.p) for x in point)):
            raise ValueError("each query must be an in-field integer pair")
        if case.accepts(*point):
            return {"solved": True, "first_hit_queries": j}
    return {"solved": False, "first_hit_queries": None}


def audit(phase="dev", submissions=None):
    cases = make_instances(phase)
    by_id = {c.id: c for c in cases}
    rows = []
    for c in cases:
        checked = c.verify_by_enumeration()
        N, M = c.p ** 2, c.p
        bound = combinatorial_first_hit_bound(N, M)
        if checked["first_lexicographic_query"] > bound:
            raise AssertionError("combinatorial worst-case bound violated")
        rows.append({
            "id": c.id, "p": c.p, "a": c.a, "b": c.b, "c": c.c,
            "domain_size": N, "worst_case_first_hit_bound": bound,
            "uniform_random_expected_first_hit": str(
                uniform_without_replacement_expectation(N, M)),
            **checked,
        })
    grades = {}
    if submissions:
        for raw in Path(submissions).read_text(encoding="utf-8").splitlines():
            if not raw.strip():
                continue
            item = json.loads(raw)
            key = item["id"]
            if key not in by_id or key in grades:
                raise ValueError("invalid or duplicated submission id")
            grades[key] = grade_queries(by_id[key], item["queries"])
    return {
        "campaign": "RH-CRYPTO-26", "experiment": "RH-05",
        "phase": phase, "evidence": "exact finite-domain synthetic control",
        "independent_units": len(PHASE_PRIMES[phase]),
        "cases": len(cases), "model_intervention": None,
        "physical_dose": None, "effect_floor": None,
        "matched_sham_floor": None, "planned_causal_comparisons": 0,
        "power": "not applicable to finite arithmetic truth checks",
        "warning": "exact affine point count and a known one-query solver; no hardness/GRH claim",
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "rows": rows, "grades": grades,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=tuple(PHASE_PRIMES), default="dev")
    parser.add_argument("--submissions", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    data = json.dumps(audit(args.phase, args.submissions), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(data, encoding="utf-8")
    print(data, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
