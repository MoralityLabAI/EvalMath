"""Regenerate RHT-26's exact cue-count and safe-completion bridge receipt."""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from math import comb
from pathlib import Path

from spiral_ln.evaluation_reward_carryover_count import (
    MAX_CUES, after_exposures, append_cue, binary_projection_failure,
    collapse_presence, joint_persistence, point_mass, safe_completion_bounds,
    saturating_fixture, store_after_history, terminal_cue_count, terminal_risk,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILES = (
    "src/spiral_ln/evaluation_finite_kernels.py",
    "src/spiral_ln/evaluation_reward_carryover_count.py",
    "tests/test_evaluation_reward_carryover_count.py",
    "scripts/verify_reward_carryover_count.py",
    "TrainingParanoia/RHT-26/development_bridge.md",
)


def binomial_path_census():
    """Enumerate all write/no-write paths independently of transition helpers."""
    cases = paths = cleared_cases = capped_cases = 0
    for h, numerator in product(range(MAX_CUES + 1), range(9)):
        p = Q(numerator, 8)
        path_law = [Q(0)] * (MAX_CUES + 1)
        for writes in product((0, 1), repeat=h):
            mass = Q(1)
            for wrote in writes:
                mass *= p if wrote else 1 - p
            path_law[sum(writes)] += mass
            paths += 1
        binomial = tuple(Q(comb(h, k)) * p ** k * (1 - p) ** (h - k)
                         if k <= h else Q(0) for k in range(MAX_CUES + 1))
        actual = after_exposures(h, write_probability=p)
        assert actual == tuple(path_law) == binomial
        assert after_exposures(h, write_probability=p, clear_each_boundary=True) == point_mass(0)
        cases += 1
        cleared_cases += 1
        initial = point_mass(h)
        expected = tuple((1 - p) * initial[k] + p * point_mass(min(h + 1, MAX_CUES))[k]
                         for k in range(MAX_CUES + 1))
        assert append_cue(initial, probability=p) == expected
        capped_cases += 1
    return cases, paths, cleared_cases, capped_cases


def frechet_assignment_census():
    """Find every feasible intersection by enumerating binary case records."""
    assignments = margins = 0
    for n in range(1, 7):
        attained = {}
        for records in product(range(4), repeat=n):
            clean = sum(value // 2 for value in records)
            required = sum(value % 2 for value in records)
            intersection = sum(value == 3 for value in records)
            attained.setdefault((clean, required), set()).add(intersection)
            assignments += 1
        assert len(attained) == (n + 1) ** 2
        for (clean, required), intersections in attained.items():
            actual = safe_completion_bounds(n, clean, required)
            assert actual == (Q(min(intersections), n), Q(max(intersections), n))
            assert intersections == set(range(max(0, clean + required - n), min(clean, required) + 1))
            margins += 1
    return assignments, margins


def snapshot_census():
    """Use each key's final occurrence as an independent snapshot oracle."""
    actions = tuple(product(("a", "b"), ("cue", "sham")))
    endpoint = saturating_fixture()
    snapshots = {}
    histories = 0
    for length in range(5):
        for history in product(actions, repeat=length):
            expected = {}
            for key in ("a", "b"):
                matching_positions = [i for i, (slot, _) in enumerate(history) if slot == key]
                if matching_positions:
                    expected[key] = history[max(matching_positions)][1]
            actual = store_after_history(history)
            assert actual == expected
            cue_count = sum(value == "cue" for value in expected.values())
            assert terminal_cue_count(actual) == cue_count
            risk = terminal_risk(actual, endpoint)
            assert risk == endpoint[cue_count]
            # Sorting is only an index for grouping equal finite mappings here.
            # No claim about a model-facing prompt serializer follows from it.
            key = tuple(sorted(expected.items()))
            if key in snapshots:
                assert snapshots[key] == risk
            snapshots[key] = risk
            histories += 1
    return histories, len(snapshots)


def rejected(call, exceptions=(ValueError, TypeError)):
    try:
        call()
    except exceptions:
        return True
    return False


def verify():
    count_cases, paths, cleared, capped = binomial_path_census()
    assignments, margins = frechet_assignment_census()
    histories, snapshots = snapshot_census()
    endpoint = saturating_fixture()
    chronological = tuple((f"ep-{i}", "cue") for i in range(1, 9))
    first = store_after_history(chronological)
    second = store_after_history(tuple(reversed(chronological)))
    zero_validation = all(rejected(lambda p=p: after_exposures(0, write_probability=p))
                          for p in (True, False, 0.5, Q(-1, 8), Q(9, 8)))
    flag_validation = all(rejected(lambda flag=flag: after_exposures(0, clear_each_boundary=flag))
                          for flag in (0, 1, "false", None))
    endpoint_validation = True
    for invalid in (Q(-1, 8), Q(9, 8), True, 0.5):
        bad = dict(endpoint)
        bad[0] = invalid
        endpoint_validation &= rejected(lambda: binary_projection_failure(bad))
        endpoint_validation &= rejected(lambda: terminal_risk({"a": "cue"}, bad))
        endpoint_validation &= rejected(lambda: joint_persistence(point_mass(8), bad))
    for invalid_key in (False, 0.0, "0"):
        bad = {key: value for key, value in endpoint.items() if key != 0}
        bad[invalid_key] = Q(0)
        endpoint_validation &= rejected(lambda: binary_projection_failure(bad))
    checks = {
        "binomial_laws_match_complete_path_oracle": count_cases == 81 and paths == 4599,
        "boundary_clearing_returns_zero_count": cleared == 81,
        "capped_append_transition_boundaries": capped == 81,
        "complete_binary_assignment_census": assignments == 5460,
        "frechet_endpoints_and_all_intermediate_counts_attained": margins == 139,
        "last_occurrence_snapshot_oracle": histories == 341 and snapshots == 9,
        "equal_mappings_can_have_different_insertion_order": first == second and
            tuple(first.items()) != tuple(second.items()),
        "equal_mapping_count_endpoints_coincide": terminal_risk(first, endpoint) == terminal_risk(second, endpoint),
        "binary_presence_loses_count_endpoint_information": collapse_presence(point_mass(1)) ==
            collapse_presence(point_mass(8)) and joint_persistence(point_mass(1), endpoint) !=
            joint_persistence(point_mass(8), endpoint) and binary_projection_failure(endpoint),
        "synthetic_endpoint_can_decline_at_largest_count": endpoint[8] < endpoint[4],
        "complete_task_marginal_identifies_clean_intersection":
            safe_completion_bounds(256, 38, 256) == (Q(19, 128), Q(19, 128)),
        "zero_horizon_validates_probability_and_clear_flag": zero_validation and flag_validation,
        "all_endpoint_states_and_key_types_validated": endpoint_validation,
        "terminal_store_keys_must_be_nonempty_strings": all(
            rejected(lambda key=key: terminal_cue_count({key: "cue"})) for key in ("", " ", 0, True, None)),
    }
    if not all(checks.values()):
        raise AssertionError([name for name, passed in checks.items() if not passed])
    return {
        "schema": "RHT-26-count-v1",
        "evidence": "exact finite count laws, declared synthetic endpoints and enumerated binary-case bounds; no new neural data",
        "binomial_cases": count_cases,
        "binary_write_paths": paths,
        "cleared_cases": cleared,
        "capped_transition_cases": capped,
        "binary_case_assignments": assignments,
        "frechet_marginal_pairs": margins,
        "store_histories": histories,
        "distinct_mapping_snapshots": snapshots,
        "synthetic_endpoint": {str(n): str(value) for n, value in endpoint.items()},
        "checks": checks,
        "source_sha256": {path: sha256((ROOT / path).read_bytes()).hexdigest() for path in SOURCE_FILES},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=ROOT / "output/evaluation_reward_carryover_count/rht26_count_v1.json")
    args = parser.parse_args()
    receipt = verify()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"RHT-26 count: {len(receipt['checks'])} checks; {receipt['binomial_cases']} binomial laws; "
          f"{receipt['binary_case_assignments']} binary case assignments; {receipt['store_histories']} store histories")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
