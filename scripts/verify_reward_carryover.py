"""Regenerate the deterministic, source-bound RHT-26 finite-model receipt."""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import random

from spiral_ln.evaluation_reward_carryover import (
    STATES, ZERO_STATE, IDENTITY, RESET_ARTIFACT, RESET_ALL,
    Kernel, Episode, JointOutcome, apply, compose, evolve, run_episodes,
    factorial, total_variation, dobrushin, transmission_certificate,
    copied_cues, iid_cues, carryover_fixture, accumulation_fixture,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILES = (
    "src/spiral_ln/evaluation_reward_carryover.py",
    "tests/test_evaluation_reward_carryover.py",
    "scripts/verify_reward_carryover.py",
    "TrainingParanoia/RHT-26/carryover.md",
    "TrainingParanoia/RHT-26/protocol.md",
    "configs/rht26_carryover_protocol.json",
)


def path_oracle(initial, kernels):
    """Enumerate complete state paths without matrix multiplication helpers."""
    out = [Q(0)] * 4
    for path in product(range(4), repeat=len(kernels) + 1):
        mass = initial[path[0]]
        for step, kernel in enumerate(kernels):
            mass *= kernel.rows[path[step]][path[step + 1]]
        out[path[-1]] += mass
    return tuple(out)


def deterministic_census():
    """All 16 artifact maps × 16 update maps, four starts, arms and horizons."""
    checked = 0
    for write_map in product((0, 1), repeat=4):
        exposure = Kernel(tuple(
            tuple(Q(j == 2 * write_map[i] + STATES[i][1]) for j in range(4))
            for i in range(4)))
        for update_map in product((0, 1), repeat=4):
            update = Kernel(tuple(
                tuple(Q(j == 2 * STATES[i][0] + update_map[i]) for j in range(4))
                for i in range(4)))
            episode = Episode(exposure, update)
            for initial, keep, learn, horizon in product(range(4), (False, True),
                                                        (False, True), range(4)):
                a, p = STATES[initial]
                for _ in range(horizon):
                    a = write_map[2 * a + p]
                    if learn:
                        p = update_map[2 * a + p]
                    if not keep:
                        a = 0
                expected = tuple(Q(s == (a, p)) for s in STATES)
                start = tuple(Q(i == initial) for i in range(4))
                observed = run_episodes(start, (episode,) * horizon,
                                        keep_artifacts=keep, learn=learn)
                assert observed == expected
                checked += 1
    return checked


def seeded_path_census():
    rng = random.Random(261119)
    checked = 0
    for _ in range(12):
        kernels = []
        for _ in range(3):
            rows = []
            for _ in range(4):
                weights = [rng.randrange(5) for _ in range(4)]
                if sum(weights) == 0:
                    weights[0] = 1
                rows.append(tuple(Q(w, sum(weights)) for w in weights))
            kernels.append(Kernel(tuple(rows)))
        initial = (Q(1, 8), Q(3, 8), Q(1, 4), Q(1, 4))
        for horizon in range(4):
            schedule = tuple(kernels[:horizon])
            expected = path_oracle(initial, schedule)
            assert evolve(initial, schedule) == expected
            assert apply(initial, compose(*schedule)) == expected
            checked += 1
    return checked


def verify() -> dict:
    deterministic = deterministic_census()
    stochastic = seeded_path_census()
    episode, endpoint = carryover_fixture()
    one = factorial(ZERO_STATE, (episode,), endpoint)
    p = tuple(arm.outcome.joint_persistence for arm in one.arms)
    accumulation = accumulation_fixture()
    retained = [run_episodes(ZERO_STATE, (accumulation,) * h,
                            keep_artifacts=True, learn=False) for h in range(9)]
    cleared = [run_episodes(ZERO_STATE, (accumulation,) * h,
                           keep_artifacts=False, learn=False) for h in range(9)]
    late = run_episodes(ZERO_STATE, (episode,), keep_artifacts=False, learn=True)
    early = run_episodes(ZERO_STATE, (episode,), keep_artifacts=False, learn=True,
                         reset_before_update=True)
    policy_endpoint = JointOutcome(tuple(
        (Q(1 - policy), Q(0), Q(0), Q(policy)) for _, policy in STATES))
    and_endpoint = JointOutcome(tuple(
        (Q(1 - artifact * policy), Q(0), Q(0), Q(artifact * policy))
        for artifact, policy in STATES))
    or_endpoint = JointOutcome(tuple(
        (Q(1 - (artifact | policy)), Q(0), Q(0), Q(artifact | policy))
        for artifact, policy in STATES))
    correlated = (Q(1, 2), Q(0), Q(0), Q(1, 2))
    factorized = (Q(1, 4),) * 4
    correlation_risks = (and_endpoint.report(correlated).joint_persistence,
                         and_endpoint.report(factorized).joint_persistence)
    copy = copied_cues(Q(3, 4), Q(1, 4), 3)
    independent = iid_cues(Q(3, 4), Q(1, 4), 3)
    copied_posterior = copy.posterior(Q(1, 2), copy.transcripts.index("111"))
    independent_posterior = independent.posterior(Q(1, 2), independent.transcripts.index("111"))
    cleared_certificate = transmission_certificate(
        ZERO_STATE, (Q(0), Q(1), Q(0), Q(0)), (RESET_ARTIFACT,), policy_endpoint)
    all_reset_certificate = transmission_certificate(
        ZERO_STATE, (Q(0), Q(1), Q(0), Q(0)), (RESET_ALL,), policy_endpoint)
    contraction = Kernel(tuple(
        tuple(Q(2, 3) * ZERO_STATE[j] + Q(1, 3) * Q(i == j) for j in range(4))
        for i in range(4)))
    contraction_rows = []
    for h in range(7):
        certificate = transmission_certificate(
            ZERO_STATE, (Q(0), Q(0), Q(0), Q(1)), (contraction,) * h, policy_endpoint)
        assert certificate.final_tv == certificate.contraction_bound == Q(1, 3) ** h
        assert certificate.joint_persistence_gap == Q(1, 3) ** h
        contraction_rows.append({"horizon": h, "tv": str(certificate.final_tv)})
    conditional = tuple(arm.outcome.conditional_persistence for arm in one.arms)
    corrected_all = JointOutcome(((Q(1), Q(0), Q(0), Q(0)),) * 4).report(ZERO_STATE)
    induced = JointOutcome(((Q(0), Q(1), Q(0), Q(0)),) * 4).report(ZERO_STATE)
    negative_interaction = factorial(ZERO_STATE, (episode,), or_endpoint).interaction
    checks = {
        "deterministic_map_census": deterministic == 16384,
        "stochastic_complete_path_census": stochastic == 48,
        "four_factorial_risks": p == (Q(1, 8), Q(5, 32), Q(9, 64), Q(13, 64)),
        "positive_interaction_exact": one.interaction == Q(1, 32),
        "interaction_can_be_negative": negative_interaction == -Q(1, 8),
        "zero_exposure_arms_coincide": len({a.final_state for a in factorial(ZERO_STATE, (), endpoint).arms}) == 1,
        "retained_artifact_geometric_accrual": all(law[2] + law[3] == 1 - Q(3, 4) ** h for h, law in enumerate(retained)),
        "reset_frozen_no_carry": all(law == ZERO_STATE for law in cleared),
        "learned_state_survives_artifact_reset": late == (Q(7, 8), Q(1, 8), Q(0), Q(0)),
        "reset_before_update_blocks_this_learning_channel": early == ZERO_STATE,
        "reset_order_changes_endpoint": endpoint.report(late).joint_persistence - endpoint.report(early).joint_persistence == Q(1, 32),
        "frozen_update_preserves_existing_policy": run_episodes((0, 1, 0, 0), (episode,) * 3, keep_artifacts=False, learn=False) == (0, 1, 0, 0),
        "same_marginals_different_joint_risk": correlation_risks == (Q(1, 2), Q(1, 4)),
        "copied_hook_not_fresh_evidence": copied_posterior == Q(3, 4),
        "independent_hooks_accumulate_evidence": independent_posterior == Q(27, 28),
        "zero_hooks_preserve_prior": copied_cues(Q(3, 4), Q(1, 4), 0).posterior(Q(2, 5), 0) == Q(2, 5),
        "impossible_transcript_undefined": copy.posterior(Q(1, 2), copy.transcripts.index("010")) is None,
        "artifact_reset_preserves_policy_transmission": cleared_certificate.joint_persistence_gap == cleared_certificate.contraction_bound == 1,
        "full_reset_removes_declared_state_transmission": all_reset_certificate.contraction_bound == all_reset_certificate.joint_persistence_gap == 0,
        "dobrushin_values": (dobrushin(IDENTITY), dobrushin(RESET_ARTIFACT), dobrushin(RESET_ALL), dobrushin(contraction)) == (1, 1, 0, Q(1, 3)),
        "conditional_endpoint_denominators": all(arm.outcome.joint_persistence == arm.outcome.pre_drift * cond for arm, cond in zip(one.arms, conditional)),
        "zero_pre_drift_has_no_conditional_rate": corrected_all.conditional_persistence is None,
        "post_drift_distinct_from_persistence": induced.post_drift == 1 and induced.joint_persistence == 0 and induced.conditional_persistence is None,
    }
    if not all(checks.values()):
        raise AssertionError([key for key, value in checks.items() if not value])
    return {
        "schema": "RHT-26-v3",
        "evidence": "exact finite examples and synthetic mechanism results; no model training, measured neural mechanism, or empirical pilot",
        "state_order": [list(state) for state in STATES],
        "deterministic_cases": deterministic,
        "complete_path_cases": stochastic,
        "factorial_one_episode": [
            {"keep_artifacts": arm.keep_artifacts, "learn": arm.learn,
             "state_law": [str(x) for x in arm.final_state],
             "pre_drift": str(arm.outcome.pre_drift),
             "post_drift": str(arm.outcome.post_drift),
             "joint_persistence": str(arm.outcome.joint_persistence),
             "conditional_persistence": str(arm.outcome.conditional_persistence)}
            for arm in one.arms],
        "interaction": str(one.interaction),
        "negative_interaction_control": str(negative_interaction),
        "artifact_accumulation": [{"exposures": h, "probability": str(law[2] + law[3])}
                                  for h, law in enumerate(retained)],
        "cue_posteriors": {"copied_positive_three": str(copied_posterior),
                           "independent_positive_three": str(independent_posterior)},
        "correlation_risks": [str(x) for x in correlation_risks],
        "sharp_contraction": contraction_rows,
        "checks": checks,
        "source_sha256": {path: sha256((ROOT / path).read_bytes()).hexdigest() for path in SOURCE_FILES},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=ROOT / "output/evaluation_reward_carryover/rht26_v3.json")
    args = parser.parse_args()
    receipt = verify()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"RHT-26: {len(receipt['checks'])} checks, {receipt['deterministic_cases']} deterministic cases, {receipt['complete_path_cases']} path cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
