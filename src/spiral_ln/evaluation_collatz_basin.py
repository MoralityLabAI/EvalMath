"""COL-EVAL-01: exact finite basin/readout benchmark for a Collatz-like map.

All arithmetic used for evidence is integral or rational. A readout ceiling is
conditioned on its declared input partition; it is an oracle using basin labels,
not an estimate of a learned model's generalization. The algorithms deliberately
stand alone so MathCan's independently implemented census can cross-check them.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
from math import gcd


SCHEMA = "EvalMath/COL-EVAL-01/v1"
SPLIT_SALT = "COL-parameter-split-v1"


def validate_parameter(d: int) -> None:
    if type(d) is not int or d < 1 or d % 4 != 1 or gcd(d, 6) != 1:
        raise ValueError("d must be a positive integer, 1 modulo 4, and coprime to 6")


def parameter_split(d: int) -> str:
    """Immutable parameter-level split, including every seed and descendant."""
    validate_parameter(d)
    bucket = int(sha256(f"{SPLIT_SALT}:{d}".encode()).hexdigest(), 16) % 10
    return "train" if bucket < 6 else "dev" if bucket < 8 else "holdout"


def odd_step(n: int, d: int) -> tuple[int, int, int]:
    validate_parameter(d)
    if type(n) is not int or n <= 0 or n % 2 != 1:
        raise ValueError("n must be a positive odd integer")
    triple = int(n % 4 == 1)
    numerator = (3 if triple else 1) * n + d
    halvings = (numerator & -numerator).bit_length() - 1
    return numerator >> halvings, halvings, triple


@dataclass(frozen=True)
class Cycle:
    minimum: int
    states: tuple[int, ...]
    halvings: int
    triple_branches: int

    @property
    def period(self) -> int:
        return len(self.states) + self.halvings


@dataclass(frozen=True)
class Core:
    d: int
    states: tuple[int, ...]
    successor: dict[int, int]
    basin: dict[int, int]
    depth: dict[int, int]
    cycles: tuple[Cycle, ...]


def enumerate_core(d: int, *, max_vertices: int = 100_000) -> Core:
    """Enumerate the forward-invariant odd core, with a hard allocation bound."""
    validate_parameter(d)
    if type(max_vertices) is not int or max_vertices < 1:
        raise ValueError("max_vertices must be positive")
    if (d + 1) // 2 > max_vertices:
        raise ValueError("core exceeds the explicit max_vertices bound")
    states = tuple(range(1, d + 1, 2))
    steps = {n: odd_step(n, d) for n in states}
    successor = {n: step[0] for n, step in steps.items()}
    if any(t not in steps for t in successor.values()):
        raise AssertionError("the declared odd core is not forward invariant")
    basin: dict[int, int] = {}
    depth: dict[int, int] = {}
    cycles = []
    for start in states:
        if start in basin:
            continue
        path: list[int] = []
        position: dict[int, int] = {}
        n = start
        while n not in basin and n not in position:
            position[n] = len(path)
            path.append(n)
            n = successor[n]
        prefix = path
        if n in position:
            offset = position[n]
            raw = path[offset:]
            minimum = min(raw)
            pivot = raw.index(minimum)
            canonical = tuple(raw[pivot:] + raw[:pivot])
            cycles.append(Cycle(minimum, canonical,
                                sum(steps[x][1] for x in raw),
                                sum(steps[x][2] for x in raw)))
            for x in raw:
                basin[x], depth[x] = minimum, 0
            prefix = path[:offset]
        for x in reversed(prefix):
            basin[x], depth[x] = basin[successor[x]], depth[successor[x]] + 1
    return Core(d, states, successor, basin, depth,
                tuple(sorted(cycles, key=lambda cycle: cycle.minimum)))


def quotient_labels(d: int, *, max_residues: int = 200_000) -> tuple[int, ...]:
    """Orbits of multiplication by 2 and 3 on all of Z/dZ.

    Both multipliers are units by the parameter contract. Thus the components
    of their undirected edges equal their group orbits, including nonunits.
    Each orbit is named by its smallest residue.
    """
    validate_parameter(d)
    if type(max_residues) is not int or max_residues < 1:
        raise ValueError("max_residues must be a positive integer")
    if d > max_residues:
        raise ValueError("quotient exceeds the explicit max_residues bound")
    parent = list(range(d))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for n in range(d):
        for multiplier in (2, 3):
            x, y = find(n), find(multiplier * n % d)
            if x != y:
                parent[max(x, y)] = min(x, y)
    return tuple(find(n) for n in range(d))


def partition_ceiling(labels: list[int], targets: list[int]) -> Fraction:
    """Best deterministic classification accuracy through a finite partition."""
    if not labels or len(labels) != len(targets):
        raise ValueError("nonempty equal-length labels and targets required")
    fibers: dict[int, Counter] = defaultdict(Counter)
    for label, target in zip(labels, targets):
        fibers[label][target] += 1
    return Fraction(sum(max(counts.values()) for counts in fibers.values()), len(targets))


def parameter_summary(d: int) -> dict:
    core = enumerate_core(d)
    quotient = quotient_labels(d)
    targets = [core.basin[n] for n in core.states]
    qlabels = [quotient[n % d] for n in core.states]
    gcd_labels = [gcd(n, d) for n in core.states]
    by_label: dict[int, dict[int, int]] = defaultdict(dict)
    for n, label in zip(core.states, qlabels):
        by_label[label].setdefault(core.basin[n], n)
    witnesses = []
    for label, representatives in sorted(by_label.items()):
        if len(representatives) > 1:
            basins = sorted(representatives)
            witnesses.append({"quotient": label,
                              "seeds": [representatives[b] for b in basins[:2]],
                              "basins": basins[:2]})
    # Dynamic programming is independently checked by following every orbit.
    for n in core.states:
        if quotient[n % d] != quotient[core.successor[n] % d]:
            raise AssertionError("quotient label changed")
        if gcd(n, d) != gcd(core.successor[n], d):
            raise AssertionError("gcd label changed")
    for cycle in core.cycles:
        modulus = d // gcd(cycle.minimum, d)
        if pow(2, cycle.halvings, modulus) != pow(3, cycle.triple_branches, modulus):
            raise AssertionError("cycle product congruence failed")
    return {
        "d": d, "split": parameter_split(d), "n_cases": len(core.states),
        "n_unit_cases": sum(gcd(n, d) == 1 for n in core.states),
        "cycles": len(core.cycles), "observed_quotients": len(set(qlabels)),
        "residue_quotients": len(set(quotient)),
        "constant_ceiling": str(partition_ceiling([0] * len(targets), targets)),
        "gcd_ceiling": str(partition_ceiling(gcd_labels, targets)),
        "quotient_ceiling": str(partition_ceiling(qlabels, targets)),
        "basin_oracle": "1", "collision_witnesses": witnesses,
        "max_depth": max(core.depth.values()),
        "cycle_counts": [{"minimum": c.minimum, "odd_steps": len(c.states),
                          "halvings": c.halvings, "triple_branches": c.triple_branches,
                          "period": c.period} for c in core.cycles],
    }


def summarize(rows: list[dict]) -> dict:
    """Report root-macro and state-micro scores separately, using exact ratios."""
    if not rows or len({row["d"] for row in rows}) != len(rows):
        raise ValueError("unique nonempty parameter roots required")
    n_cases = sum(row["n_cases"] for row in rows)
    return {
        "n_parameter_roots": len(rows), "n_cases": n_cases,
        "roots_with_collisions": sum(bool(row["collision_witnesses"]) for row in rows),
        "scores": {name: {
            "macro": str(sum((Fraction(row[name]) for row in rows), Fraction()) / len(rows)),
            "micro": str(sum((Fraction(row[name]) * row["n_cases"] for row in rows), Fraction()) / n_cases),
        } for name in ("constant_ceiling", "gcd_ceiling", "quotient_ceiling", "basin_oracle")},
    }


def score_predictions(gold: list[dict], predictions: list[dict]) -> dict:
    """Score a candidate once, keeping state and parameter denominators apart.

    Candidate rows contain exactly id and cycle_minimum. A missing row or a
    null cycle_minimum is an abstention. Unknown and duplicate IDs are errors.
    Gold is evaluator-owned output from export_collatz_basin.py.
    """
    if not gold:
        raise ValueError("gold must contain at least one case")
    expected: dict[str, tuple[int, int]] = {}
    for row in gold:
        if type(row) is not dict or type(row.get("id")) is not str:
            raise ValueError("gold row requires a string id")
        case_id = row["id"]
        parts = case_id.split(":")
        if len(parts) != 3 or parts[0] != "COL":
            raise ValueError("invalid gold case id")
        try:
            d, n = int(parts[1]), int(parts[2])
        except ValueError as exc:
            raise ValueError("invalid gold case id") from exc
        validate_parameter(d)
        target = row.get("cycle_minimum")
        if (case_id != f"COL:{d}:{n}" or n < 1 or n > d or n % 2 != 1
                or type(target) is not int or target < 1 or target > d or target % 2 != 1):
            raise ValueError("gold id or target is outside the odd-core contract")
        if case_id in expected:
            raise ValueError("duplicate gold case id")
        expected[case_id] = (d, target)
    submitted = {}
    for row in predictions:
        if type(row) is not dict or set(row) != {"id", "cycle_minimum"}:
            raise ValueError("prediction requires exactly id and cycle_minimum")
        case_id, target = row["id"], row["cycle_minimum"]
        if type(case_id) is not str or case_id not in expected:
            raise ValueError("prediction contains an unknown case id")
        if case_id in submitted:
            raise ValueError("duplicate prediction case id")
        if target is not None and (type(target) is not int or target < 1 or target % 2 != 1):
            raise ValueError("prediction must be a positive odd integer or null")
        submitted[case_id] = target
    roots: dict[int, Counter] = defaultdict(Counter)
    for case_id, (d, target) in expected.items():
        prediction = submitted.get(case_id)
        roots[d]["cases"] += 1
        roots[d]["answered"] += prediction is not None
        roots[d]["correct"] += prediction == target
    counts = Counter()
    for row in roots.values():
        counts.update(row)
    return {
        "schema": "COL-EVAL-01/candidate-score/v1", "n_parameter_roots": len(roots),
        "n_cases": counts["cases"], "n_answered": counts["answered"],
        "n_correct": counts["correct"], "n_abstained": counts["cases"] - counts["answered"],
        "parameter_macro_accuracy": str(sum((Fraction(r["correct"], r["cases"])
                                                for r in roots.values()), Fraction()) / len(roots)),
        "state_micro_accuracy": str(Fraction(counts["correct"], counts["cases"])),
        "coverage": str(Fraction(counts["answered"], counts["cases"])),
        "selective_accuracy": (str(Fraction(counts["correct"], counts["answered"]))
                               if counts["answered"] else None),
        "roots": [{"d": d, **dict(row), "accuracy": str(Fraction(row["correct"], row["cases"]))}
                  for d, row in sorted(roots.items())],
    }
