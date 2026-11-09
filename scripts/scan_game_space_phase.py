"""Finite fixed-cubic-graph random-cluster balance scan, no asymptotic claims.

Zero GPU work. Every graph is degree three; a deterministic PRNG supplies
one reproducible F2 edge-gain sample per graph. Exact partition polynomials
are evaluated before logarithms. The phase labels are exploratory only.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import json
from math import log
import random

from spiral_ln.unique_games_topology import Edge, TranslationGame
from spiral_ln.game_space_partition import (
    balanced_subgraph_coefficients, flat_subgraph_coefficients,
    polynomial_value,
)


def graphs():
    k33 = [(i, j) for i in range(3) for j in range(3, 6)]
    cube = [(i, i ^ (1 << k)) for i in range(8) for k in range(3)
            if i < (i ^ (1 << k))]
    petersen = ([(i, (i + 1) % 5) for i in range(5)]
                + [(5+i, 5 + (i+2) % 5) for i in range(5)]
                + [(i, 5+i) for i in range(5)])
    prism = ([(i, (i+1) % 6) for i in range(6)]
             + [(6+i, 6+(i+1) % 6) for i in range(6)]
             + [(i, 6+i) for i in range(6)])
    return (("K33", 6, k33), ("Cube", 8, cube),
            ("Petersen", 10, petersen), ("Prism12", 12, prism))


def scan(max_vertices=12):
    rows = []
    for idx, (name, n, pairs) in enumerate(graphs()):
        if n > max_vertices:
            continue
        rng = random.Random(20261109 + idx)
        game = TranslationGame(n, 1, tuple(
            Edge(u, v, rng.randrange(2)) for u, v in pairs))
        degree = [0] * n
        for edge in game.edges:
            degree[edge.u] += 1
            degree[edge.v] += 1
        assert all(d == 3 for d in degree)
        coeff = balanced_subgraph_coefficients(game)
        flat = flat_subgraph_coefficients(game)
        for z in (Fraction(1, 2), Fraction(1), Fraction(2), Fraction(4), Fraction(8)):
            prob = polynomial_value(coeff, z) / polynomial_value(flat, z)
            rows.append({
                "graph": name, "n": n, "m": len(game.edges),
                "q": game.alphabet_size, "z": str(z),
                "balanced_probability": str(prob),
                "holonomy_rate_per_edge": round(-log(float(prob)) / len(game.edges), 6),
            })
    return {"schema": "UGCS-02-scan.1", "seed": 20261109,
            "claim_level": "finite fixed-graph exact partition computations",
            "note": "one seeded F2 gain sample per named 3-regular graph; no thermodynamic inference",
            "rows": rows}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--max-vertices", type=int, default=12)
    args = ap.parse_args()
    print(json.dumps(scan(args.max_vertices), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
