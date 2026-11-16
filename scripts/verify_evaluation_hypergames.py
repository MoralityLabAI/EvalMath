"""HG-01 source-hashed exact CPU verification for storyworld hypergames."""
from __future__ import annotations

import argparse
import hashlib
import json
import unittest
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path

from spiral_ln.evaluation_hypergames import (
    categorical_overlap, dirac_distance_squared, infer_goals,
    minimum_robust_probe_cover, hypergame_view_gap,
    projection_margin_certificate, diplomacy_v2_visible_numeric,
    inverse_voronoi_halfspaces, halfspaces_accept,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCES = (
    "src/spiral_ln/evaluation_hypergames.py",
    "tests/test_evaluation_hypergames.py",
    "scripts/verify_evaluation_hypergames.py",
    "Hypergames/fixtures/hg01_registered.json",
    "Hypergames/fixtures/diplomacy_min_visible.json",
)


def _build_fixture():
    cfg = json.loads((ROOT / "Hypergames/fixtures/hg01_registered.json").read_text())
    n = cfg["nuisance_count"]
    if cfg["dimensions"] != n + 2 or n < 1:
        raise ValueError("bad registered dimensions")
    tail = {f"{cfg['nuisance_prefix']}{j:03d}": F(0) for j in range(n)}
    def state(s):
        return {"x": F(s["x"]), "y": F(s["y"]), **tail}
    goals = {key: state(value) for key, value in cfg["goals"].items()}
    probes = {key: {a: state(v) for a, v in arms.items()}
              for key, arms in cfg["probes"].items()}
    return cfg, goals, probes


def verify() -> dict:
    cfg, goals, probes = _build_fixture()
    obs = cfg["observations"]
    decisions = [(o["chosen"], probes[o["probe"]]) for o in obs]
    first = infer_goals(decisions[:1], goals)
    final = infer_goals(decisions, goals)
    cover = minimum_robust_probe_cover(probes, goals, cfg["probe_costs"])
    voronoi = inverse_voronoi_halfspaces(decisions)
    g = {"trust": F(1)}
    view = hypergame_view_gap("ally", g,
        {"ally": {"trust": F(1)}, "wait": {"trust": F(0)}},
        {"ally": {"trust": F(-1)}, "wait": {"trust": F(0)}})
    stable = projection_margin_certificate(
        {"a": {"x": F(0), "y": F(1, 5)}, "b": {"x": F(1), "y": F(0)}},
        {"x": F(0), "y": F(0)}, ["x"])
    failure_witness = projection_margin_certificate(
        {"a": {"x": F(0), "y": F(1)}, "b": {"x": F(1, 2), "y": F(0)}},
        {"x": F(0), "y": F(0)}, ["x"])
    original = json.loads((ROOT / "Hypergames/fixtures/diplomacy_min_visible.json").read_text())
    before = diplomacy_v2_visible_numeric(original, ["round"])
    redacted = json.loads(json.dumps(original))
    redacted["hidden_state_reveal"] = [{"key": "secret_payoff", "value": "entirely different"}]
    redacted["realized_outcome"] = {"outcome": "another ending"}
    after = diplomacy_v2_visible_numeric(redacted, ["round"])
    z = {f"z{i:03d}": F(0) for i in range(138)}
    large_a = {"x": F(0), "y": F(0), **z}
    large_b = {"x": F(0), "y": F(1), **z}
    checks = {
        "registered_dimension_140": len(goals["g01"]) == 140,
        "inverse_voronoi_rank_2": voronoi["comparison_rank"] == 2 and voronoi["blind_linear_dimensions"] == 138,
        "halfspace_goal_certificate": all(halfspaces_accept(voronoi, g) == (name in final["compatible"]) for name, g in goals.items()),
        "clifford_140_exact": dirac_distance_squared(large_a, large_b) == 1,
        "tensor_140_exact": categorical_overlap(["a"] * 140, ["b"] * 140) == F(9, 25)**140,
        "ambiguous_first_probe": first["compatible"] == tuple(cfg["expected_compatible_after_first"]),
        "unique_after_active_probe": final["compatible"] == tuple(cfg["expected_compatible_final"]),
        "robust_probe_cover": cover["min_cost"] == cfg["expected_min_probe_cost"] and cover["probes"] == ("x", "y"),
        "subjective_objective_separation": view["subjective_regret"] == "0" and view["objective_regret"] == "3",
        "projection_stable": stable["certified_stable"] and stable["winner"] == "a",
        "projection_flip_witness": not failure_witness["certified_stable"] and failure_witness["winner"] == "b" and failure_witness["projected_minimizers"] == ("a",),
        "hidden_reveal_immaterial": before == after,
        "visible_dimension_16": len(before) == 16,
    }
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_evaluation_hypergames.py")
    import io
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=0).run(suite)
    checks["adversarial_unittests_pass"] = result.wasSuccessful() and result.testsRun >= 12
    return {
        "schema_version": "HG-01.v1",
        "evidence": "exact finite verified example; synthetic mechanism, no trained agents",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "upstream": {
            "repository": "MoralityLabAI/GPTStoryworld",
            "commit": "c8d46591f983473023daf0232e9b413baaa02194",
            "paths": ["storyworld/env/diplomacy_env.py", "storyworld/benchmarking/turn_trace_export.py",
                      "storyworld/examples/diplomacy_min.json", "verifiers_envs/storyworld-env/manifold_projection.py"],
        },
        "cases": {
            "dimension": cfg["dimensions"],
            "goal_count": len(goals), "probe_count": len(probes),
            "first_probe": first, "two_probes": final,
            "minimum_robust_cover": cover,
            "misperception": view,
            "projection_stability": stable,
            "projection_counterexample": failure_witness,
            "visible_numeric_axes": len(before),
            "tensor_overlap_all_different": str(F(9, 25)**140),
            "unittest_count": result.testsRun,
            "inverse_voronoi": {"comparison_rank": voronoi["comparison_rank"],
                                "blind_linear_dimensions": voronoi["blind_linear_dimensions"],
                                "inequalities": len(voronoi["constraints"])},
        },
        "checks": checks,
        "all_passed": all(checks.values()),
        "source_sha256": {
            name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in SOURCES
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = verify()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as fp:
            fp.write(rendered)
    else:
        print(rendered, end="")
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
