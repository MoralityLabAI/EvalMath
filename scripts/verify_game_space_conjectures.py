"""UGCS-01 deterministic finite receipt: moments, signed spectra, ANF, covers.

All-oracle enumeration is exponential and intentionally restricted to tiny
translation games. The output records evidence, never a proof of a conjecture.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path

from spiral_ln.unique_games_topology import Edge, TranslationGame, cycle_signature
from spiral_ln.game_space_conjectures import (
    anf_degree, degree_probe_min_detection, edited_holonomy_degree,
    holonomy_image, latent_stability, minimal_double_cover_frustration,
    moment_obstruction_probe, regular_holonomy_cover,
    spectral_cosystolic_probe,
)

SOURCES = (
    "src/spiral_ln/game_space_conjectures.py",
    "tests/test_game_space_conjectures.py",
    "scripts/verify_game_space_conjectures.py",
    "paper/game_space_conjectures_2026_11.md",
)
C4 = ((0, 2), (0, 3), (1, 2), (1, 3))
K23 = ((0, 2), (1, 2), (0, 3), (1, 3), (0, 4), (1, 4))


def game(n, bits, pairs, shifts):
    return TranslationGame(n, bits, tuple(
        Edge(u, v, s) for (u, v), s in zip(pairs, shifts)))


def census() -> dict:
    moment_count = 0
    frustrated_count = 0
    for shifts in product(range(4), repeat=4):
        rep = moment_obstruction_probe(game(4, 2, C4, shifts))
        if rep["first_frustrated_length"] is None:
            assert rep["all_matching"]
        else:
            assert rep["low_moments_equal"] and rep["first_coefficient_equal"]
            assert rep["first_frustrated_length"] == 4
            frustrated_count += 1
        moment_count += 1
    assert (moment_count, frustrated_count) == (256, 192)

    graph_specs = (
        ("C4_F2_squared", 4, 2, C4, product(range(4), repeat=4)),
        ("K4_F2", 4, 1, tuple(combinations(range(4), 2)),
         product((0, 1), repeat=6)),
        ("K33_F2", 6, 1, tuple((u, v) for u in range(3) for v in range(3, 6)),
         product((0, 1), repeat=9)),
    )
    spec: dict[str, dict] = {}
    for name, n, bits, pairs, shift_cases in graph_specs:
        count = 0
        ratios = []
        for shifts in shift_cases:
            p = spectral_cosystolic_probe(game(n, bits, pairs, shifts))
            assert p["upper_bound_verified"]
            if p["ratio"] is not None:
                ratios.append(p["ratio"])
            count += 1
        spec[name] = {
            "games": count,
            "nonflat": len(ratios),
            "ratio_min_rounded_6dp": round(min(ratios), 6),
            "ratio_max_rounded_6dp": round(max(ratios), 6),
            "upper_bound_failures": 0,
        }

    # A rank-2 holonomy witness on the K_{2,3} base.
    rank2 = game(5, 2, K23, (0, 0, 0, 1, 0, 2))
    cover, labels = regular_holonomy_cover(rank2)
    assert len(holonomy_image(rank2)) == 4
    assert all((labels[e.u] ^ labels[e.v]) == e.shift for e in cover.edges)
    double_phi = minimal_double_cover_frustration(rank2)
    assert double_phi == Fraction(1, 6)

    # Degree <= d probes contain any latent code whose ANF degree <= d.
    quadratic = tuple(int((u & 1) != 0 and (u & 2) != 0) for u in range(8))
    noise = ((1, 1), (1, 2), (0, 3), (0, 4))
    p = latent_stability(quadratic, noise)
    detection2, terms2 = degree_probe_min_detection(3, noise, 2)
    assert anf_degree(quadratic) == 2
    assert detection2 <= p

    return {
        "schema": "UGCS-01.0",
        "claim_level": "exact elementary identities and bounded experiments",
        "scope": "finite F2^s translation games; no UGC reduction or conjecture proof",
        "moments": {
            "C4_F2_squared_tested": moment_count,
            "nonflat": frustrated_count,
            "flat": moment_count - frustrated_count,
            "first_obstruction_coefficient": "-3/2048",
            "errors": 0,
        },
        "spectra": spec,
        "latent_negative_control": {
            "latent_degree": anf_degree(quadratic),
            "change_probability": str(p),
            "minimum_degree2_probe_detection": str(detection2),
            "minimizer_monomial_masks": list(terms2),
            "implication": "degree-d C is itself an admissible degree-d observable for K=F2",
        },
        "covers": {
            "K23_rank2_holonomy_size": len(holonomy_image(rank2)),
            "regular_cover_degree": cover.vertices // rank2.vertices,
            "regular_cover_perfect_label_verified": True,
            "best_connected_double_cover_frustration": str(double_phi),
            "degree_after_one_base_edge_edit": edited_holonomy_degree(rank2, 1),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    report = census()
    report["source_sha256"] = {p: sha256((root / p).read_bytes()).hexdigest()
                                for p in SOURCES}
    output = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as fh:
            fh.write(output)
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
