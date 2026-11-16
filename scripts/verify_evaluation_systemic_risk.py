"""Regenerate source-bound SRB-01 exact finite scenario receipt."""
from __future__ import annotations

import argparse
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import random

from spiral_ln.evaluation_systemic_risk import (
    expected_loss, load_bank, optimal_observable, score, weighted_cvar, json_exact,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = "fixtures/systemic_risk_evalmath/synthetic_two_worlds.json"
SOURCES = (
    "src/spiral_ln/evaluation_systemic_risk.py",
    "tests/test_evaluation_systemic_risk.py",
    "scripts/verify_evaluation_systemic_risk.py",
    "paper/systemic_risk_evalmath.md",
    FIXTURE,
)


def run() -> dict:
    bank = load_bank(ROOT / FIXTURE)
    s = score(bank)
    rng = random.Random(20261116)
    exhaustive = 0
    for _ in range(96):
        # Independent tiny-world oracle: enumerate complete policies by visible cell.
        n = rng.randrange(1, 7)
        raw = json.loads((ROOT / FIXTURE).read_text())
        raw["query_names"] = ["q"]
        raw["worlds"] = []
        for i in range(n):
            raw["worlds"].append({
                "id": f"w{i}", "mass": rng.randrange(1, 5),
                "visible": [rng.randrange(3)], "queries": [rng.randrange(3)],
                "outcomes": {
                    a: {"node_loss": [str(rng.randrange(9)), str(rng.randrange(9))],
                        "claimed_safe": rng.choice((True, False))}
                    for a in ("cut_a", "cut_b")},
            })
        from spiral_ln.evaluation_systemic_risk import parse_bank
        b = parse_bank(raw)
        cells = sorted({w.visible for w in b.worlds})
        brute = min(expected_loss(b, tuple(plan[cells.index(w.visible)] for w in b.worlds))
                    for plan in product((0, 1), repeat=len(cells)))
        measured = score(b)
        assert brute == measured["observable_loss"]
        assert measured["unobservable_regret"] == measured["binary_collision_certificate"]
        assert expected_loss(b, optimal_observable(b, 0)) <= brute
        # Independently enumerate the one-query adversarial event-selector policies.
        events = [[w.claims_safe[a] and sum(w.node_losses[a]) >= b.harm_threshold
                   for w in b.worlds] for a in (0, 1)]
        masses = [w.weight for w in b.worlds]
        prior = max(sum(m for m, hit in zip(masses, ev) if hit) for ev in events)
        split = sorted({w.queries[0] for w in b.worlds})
        after = sum(max(sum(w.weight for w, hit in zip(b.worlds, ev)
                            if w.queries[0] == answer and hit) for ev in events)
                    for answer in split)
        assert measured["false_authorization_selection"]["no_disclosure"] == Fraction(prior, sum(masses))
        assert measured["false_authorization_selection"]["one_query_optimum"] == Fraction(after, sum(masses))
        exhaustive += 1

    checks = {
        "hidden_fibre_regret": s["unobservable_regret"] == 4,
        "binary_collision_exact": s["binary_collision_certificate"] == 4,
        "query_resolves_collision": s["query_disclosure_loss"]["reveal_shock"] == 0,
        "tail_harm_exposed": s["baseline_harm_cvar"] == 8,
        "public_vs_postselection_risk": (
            s["false_authorization_selection"]["no_disclosure"] == Fraction(1, 2)
            and s["false_authorization_selection"]["one_query_optimum"] == 1),
        "independent_random_exact_oracles": exhaustive == 96,
        "cvar_boundary_alpha_zero": weighted_cvar(((Fraction(0), 3), (Fraction(8), 1)), Fraction(0)) == 2,
        "cvar_boundary_alpha_three_quarters": weighted_cvar(((Fraction(0), 3), (Fraction(8), 1)), Fraction(3, 4)) == 8,
    }
    assert all(checks.values())
    return {
        "schema": "SRB-01-receipt-v1",
        "evidence": "finite exact synthetic model and independent enumeration; no SystemicRiskBench replay or real agents",
        "independent_random_oracles": exhaustive,
        "synthetic_witness": json_exact(s),
        "checks": checks,
        "source_sha256": {p: sha256((ROOT / p).read_bytes()).hexdigest() for p in SOURCES},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=ROOT / "output/evaluation_systemic_risk/srb01.json")
    args = parser.parse_args()
    result = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"SRB-01: {result['independent_random_oracles']} independently checked cases; {len(result['checks'])} checks passed")


if __name__ == "__main__":
    main()
