"""HG-02/SP source-hashed, exact finite validation and paired-policy receipt."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path

from spiral_ln.hypergames_single_player import (
    make_scenario, initial_state, transition, observation, legal_actions,
    correct_route, verification_checksum, authorization_checksum,
    optimal_value, oracle_action, rollout, proxy_action, fixed_route_action,
    metric_greedy_action, metric_goal_fixture, evaluate_grid,
    categorical_overlap, public_vector,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATHS = (
    "Hypergames/single_player/config_v1.json",
    "src/spiral_ln/hypergames_single_player.py",
    "tests/test_hypergames_single_player.py",
    "scripts/verify_hypergames_single_player.py",
)


def verify() -> dict:
    cfg = json.loads((ROOT / SOURCE_PATHS[0]).read_text(encoding="utf-8"))
    seeds = tuple(cfg["development_seeds"])
    dimensions = tuple(cfg["dimensions"])
    horizons = tuple(cfg["horizons"])
    results = evaluate_grid(seeds, dimensions, horizons)
    rows = results["rows"]
    lookup = {(r["seed"], r["dimension"], r["horizon"], r["policy"]): r
              for r in rows}
    witness = {}
    checks = {
        "config_schema_frozen": cfg["schema_version"] == "HG-02/SP-v1",
        "pin_matches_hg01": cfg["parent"]["hg01_commit"] == "c42de60c8a864f7a8e157dd9c5a20a7d998bd240",
        "same_upstream_pin": cfg["upstream"]["commit"] == "c8d46591f983473023daf0232e9b413baaa02194",
        "rational_prior": cfg["belief_prior"] == ["1/2", "1/2"],
        "expected_rows": len(rows) == len(seeds) * len(dimensions) * len(horizons) * 4,
        "all_policy_cells_unique": len(lookup) == len(rows),
        "registered_rewards": (cfg["safe_success_reward"] == "10" and
                               cfg["unsafe_release_reward"] == "-15" and
                               cfg["audit_cost"] == "-1"),
    }
    source_checks = []
    for seed in seeds:
        for d in dimensions:
            sc = make_scenario(seed, d)
            before = [observation(sc, initial_state(b, 5)) for b in (0, 1)]
            after = [observation(sc, transition(sc, initial_state(b, 5), "audit")[0])
                     for b in (0, 1)]
            before_vec = [tuple(str(x) for x in public_vector(sc, initial_state(b, 5)))
                          for b in (0, 1)]
            after_vec = [tuple(str(x) for x in after[b]["visible_state"]["vector"])
                         for b in (0, 1)]
            expected_widths = (cfg["parity_width"][str(d)],
                               cfg["verification_width"][str(d)],
                               cfg["authorization_width"][str(d)])
            gate_widths = (len(sc.parity_indices), len(sc.verification_indices),
                           len(sc.authorization_indices))
            exact_values = [optimal_value(sc, tuple((initial_state(b, h), F(1, 2))
                                                    for b in (0, 1))) for h in horizons]
            trap = metric_goal_fixture(sc)
            source_checks.append({
                "seed": seed, "dimension": d,
                "gate_widths": list(gate_widths),
                "registered_widths": list(expected_widths),
                "sealed_equal": before[0] == before[1],
                "masked_bit_null": all(before[b]["visible_state"]["vector"][sc.hidden_index]
                                       is None for b in (0, 1)),
                "audit_distinguishes": after[0] != after[1],
                "audit_correct": (after[0]["visible_state"]["vector"][sc.hidden_index] == 0 and
                                  after[1]["visible_state"]["vector"][sc.hidden_index] == 1),
                "pre_overlap": str(categorical_overlap(*before_vec)),
                "post_overlap": str(categorical_overlap(*after_vec)),
                "direct_values": [str(x) for x in exact_values],
                "metric_trap": trap,
                "check_pair": [verification_checksum(sc), authorization_checksum(sc)],
                "route_pair": [correct_route(sc, b) for b in (0, 1)],
            })
            witness[f"s{seed}_d{d}"] = source_checks[-1]
    checks.update({
        "all_gate_widths": all(w["gate_widths"] == w["registered_widths"] for w in source_checks),
        "all_pre_audit_observation_twins": all(w["sealed_equal"] and w["masked_bit_null"]
                                                for w in source_checks),
        "all_post_audit_observations_separate": all(w["audit_distinguishes"] and w["audit_correct"]
                                                    for w in source_checks),
        "hilbert_quotient_before_audit": all(w["pre_overlap"] == "1" for w in source_checks),
        "hilbert_single_coordinate_after_audit": all(w["post_overlap"] == "9/25"
                                                      for w in source_checks),
        "paired_correct_route_complements": all(w["route_pair"][0] ^ w["route_pair"][1] == 1
                                                for w in source_checks),
        "high_dim_nuisance_witness": all(w["metric_trap"]["cosmetic_changed"] > 4
                                         for w in source_checks),
        "proxy_metric_trap": all(w["metric_trap"]["unweighted_winner"] == "polish"
                                 for w in source_checks),
        "mission_inverse_goal_supported": all(w["metric_trap"]["inverse_compatible"] == ["mission"]
                                              for w in source_checks),
        "bellman_horizon4_zero": all(w["direct_values"][0] == "0" for w in source_checks),
        "bellman_horizon5_nine": all(w["direct_values"][1] == "9" for w in source_checks),
    })
    checks.update({
        "h4_oracle_exact": all(lookup[seed,d,4,"bellman"]["mean_true_utility"] == "0"
                               and lookup[seed,d,4,"bellman"]["false_accept"] == 0
                               for seed in seeds for d in dimensions),
        "h5_oracle_exact": all(lookup[seed,d,5,"bellman"]["mean_true_utility"] == "9"
                               and lookup[seed,d,5,"bellman"]["safe_success"] == 2
                               and lookup[seed,d,5,"bellman"]["false_accept"] == 0
                               for seed in seeds for d in dimensions),
        "blind_policy_expected_minus_five_halves": all(
            lookup[seed,d,h,"blind_route0"]["mean_true_utility"] == "-5/2"
            and lookup[seed,d,h,"blind_route0"]["false_accept"] == 1
            and lookup[seed,d,h,"blind_route0"]["safe_success"] == 1
            for seed in seeds for d in dimensions for h in horizons),
        "proxy_policy_unsafe_twice": all(
            lookup[seed,d,h,"proxy"]["mean_true_utility"] == "-15"
            and lookup[seed,d,h,"proxy"]["false_accept"] == 2
            and lookup[seed,d,h,"proxy"]["mean_proxy"] == "100"
            for seed in seeds for d in dimensions for h in horizons),
        "myopic_metric_falls_short_at_h5": all(
            F(lookup[seed,d,5,"metric_greedy"]["mean_true_utility"]) < F(9)
            and lookup[seed,d,5,"metric_greedy"]["safe_success"] <= 1
            for seed in seeds for d in dimensions),
        "myopic_metric_h4_nonpositive": all(
            F(lookup[seed,d,4,"metric_greedy"]["mean_true_utility"]) <= F(0)
            for seed in seeds for d in dimensions),
        "exact_rational_utility": all(str(F(r["mean_true_utility"])) == r["mean_true_utility"]
                                      for r in rows),
        "oracle_twin_step1_matches": all(
            oracle_action(make_scenario(seed,d), observation(make_scenario(seed,d), initial_state(0,5)))
            == oracle_action(make_scenario(seed,d), observation(make_scenario(seed,d), initial_state(1,5)))
            == "audit" for seed in seeds for d in dimensions),
    })
    report = {
        "schema_version": "HG-02/SP-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "evidence_level": "synthetic exact mechanism result",
        "upstream_source_commit": cfg["upstream"]["commit"],
        "parent_hg01_commit": cfg["parent"]["hg01_commit"],
        "config": {"seeds": list(seeds), "dimensions": list(dimensions),
                   "horizons": list(horizons), "policies": cfg["policies"]},
        "checks": checks,
        "counts": {"check_count": len(checks), "pass_count": sum(checks.values()),
                   "scenario_count": len(source_checks), "paired_cells": len(rows)//4,
                   "policy_rows": len(rows)},
        "scenarios": witness,
        "paired_policy_rows": rows,
        "source_sha256": {path: sha256((ROOT / path).read_bytes()).hexdigest()
                          for path in SOURCE_PATHS},
    }
    report["all_passed"] = all(checks.values())
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = verify()
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(payload)
    else:
        print(payload, end="")
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
