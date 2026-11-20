"""Regenerate the deterministic, source-bound RHT-27 finite-domain receipt."""
from __future__ import annotations

import argparse
from dataclasses import asdict
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

from spiral_ln.evaluation_finite_kernels import Kernel, dobrushin, identity
from spiral_ln.evaluation_noninterference import (
    EvaluationInterface, permitted_learning_fixture, reset_order_fixture,
    unsafe_permitted_feedback_fixture,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILES = (
    "src/spiral_ln/evaluation_finite_kernels.py",
    "src/spiral_ln/evaluation_noninterference.py",
    "tests/test_evaluation_finite_kernels.py",
    "tests/test_evaluation_noninterference.py",
    "scripts/verify_evaluation_noninterference.py",
    "TrainingParanoia/RHT-27/evaluation_noninterference.md",
    "lean/FeedbackChannel/TrainingParanoia.lean",
)


def event_oracle(p, q):
    """Compute sup event gaps by enumerating the full powerset."""
    return max(abs(sum((a - b) * take for a, b, take in zip(p, q, mask)))
               for mask in product((0, 1), repeat=len(p)))


def rational_census():
    grid = tuple(Q(i, 4) for i in range(5))
    channels = tuple(Kernel(((1 - a, a), (1 - b, b)))
                     for a, b in product((Q(0), Q(1, 2), Q(1)), repeat=2))
    cases = postprocess_cases = 0
    for probabilities in product(grid, repeat=4):
        left = Kernel(tuple((1 - p, p) for p in probabilities[:2]))
        right = Kernel(tuple((1 - p, p) for p in probabilities[2:]))
        interface = EvaluationInterface(("plain", "hook"), ("z", "z"), (left, right))
        expected = max(event_oracle(p, q) for p, q in zip(left.rows, right.rows))
        audit = interface.audit()
        assert audit.epsilon == expected
        witness = audit.witness
        assert witness is not None
        assert sum(left.rows[witness.initial_state][j] - right.rows[witness.initial_state][j]
                   for j in witness.event) == expected
        assert interface.residual(interface.permitted_simulator()) == expected
        assert interface.residual(interface.permitted_simulator({"z": (Q(1, 2), Q(1, 2))})) == expected / 2
        if expected == 0:
            assert interface.residual(interface.factorization()) == 0
        else:
            try:
                interface.factorization()
            except ValueError:
                pass
            else:
                raise AssertionError("nonzero diameter accepted as exact factorization")
        for channel in channels:
            assert interface.postprocess(channel).audit().epsilon <= dobrushin(channel) * expected
            postprocess_cases += 1
        cases += 1
    return cases, postprocess_cases


def deterministic_census():
    count = 0
    for images in product((0, 1), repeat=8):
        kernels = tuple(Kernel(tuple(tuple(int(j == target) for j in range(2))
                                     for target in images[2 * e:2 * e + 2]))
                        for e in range(4))
        interface = EvaluationInterface(("a0", "a1", "b0", "b1"),
                                        ("a", "a", "b", "b"), kernels)
        expected = Q(int(any(images[2 * left + s] != images[2 * right + s]
                             for left, right in ((0, 1), (2, 3)) for s in range(2))))
        audit = interface.audit()
        assert audit.epsilon == expected
        assert audit.coverage == 1 and audit.row_comparisons == 4
        count += 1
    return count


def verify():
    rational, postprocess = rational_census()
    deterministic = deterministic_census()
    learning = permitted_learning_fixture()
    unsafe = unsafe_permitted_feedback_fixture()
    unsafe_risk = unsafe.risk_certificate(unsafe.factorization(), (0, 1))
    late, early, artifact = reset_order_fixture()
    identity_phi = EvaluationInterface(("plain", "hook"), ("plain", "hook"),
                                       (Kernel(((1, 0),)), Kernel(((0, 1),))))
    partial = EvaluationInterface(("a", "b", "c"), ("z", "z", "c"), (identity(2),) * 3)
    observational = EvaluationInterface(("E0", "E1"), ("same", "same"), (identity(2),) * 2)
    erased = EvaluationInterface(("plain", "hook"), ("z", "z"), (Kernel(((1,),)),) * 2)
    separate_continuations = EvaluationInterface(("plain", "hook"), ("z", "z"),
                                                  (Kernel(((1, 0),)), Kernel(((0, 1),))))
    sharp = EvaluationInterface(("plain", "hook"), ("z", "z"),
                                (Kernel(((Q(7, 8), Q(1, 8)),)),
                                 Kernel(((Q(5, 8), Q(3, 8)),))))
    sharp_risk = sharp.risk_certificate(sharp.permitted_simulator(), (0, 1))
    checks = {
        "rational_full_event_oracle_census": rational == 625,
        "common_postprocessing_census": postprocess == 5625,
        "deterministic_two_fibre_census": deterministic == 256,
        "exact_factorization_preserves_score_bit_learning": learning.audit().epsilon == 0 and
            learning.factorization().kernel("score:0") != learning.factorization().kernel("score:1"),
        "fully_covered_learning_fibres": learning.audit().coverage == 1,
        "identity_feedback_reports_vacuity": identity_phi.audit().identity_feedback_vacuous and
            identity_phi.audit().epsilon == 0 and identity_phi.audit().witness is None,
        "partial_coverage_is_reported": partial.audit().coverage == Q(2, 3),
        "zero_residual_can_have_certain_unsafe_behavior": unsafe_risk.residual == 0 and
            unsafe_risk.actual_risk == unsafe_risk.reference_risk == unsafe_risk.risk_bound == 1,
        "reference_plus_residual_bound_is_sharp": sharp_risk.reference_risk == Q(1, 8) and
            sharp_risk.residual == Q(1, 4) and sharp_risk.actual_risk == sharp_risk.risk_bound == Q(3, 8),
        "artifact_reset_after_update_retains_policy_channel": late.audit().epsilon == 1,
        "artifact_reset_before_update_blocks_declared_write_channel": early.audit().epsilon == 0,
        "artifact_only_readout_hides_retained_policy_channel": late.postprocess(artifact).audit().epsilon == 0,
        "observational_conditioning_can_disagree_with_intervention":
            observational.audit().epsilon == 0 and event_oracle((1, 0), (0, 1)) == 1,
        "transcript_specific_continuation_can_reintroduce_influence":
            erased.audit().epsilon == 0 and separate_continuations.audit().epsilon == 1,
    }
    if not all(checks.values()):
        raise AssertionError([key for key, passed in checks.items() if not passed])
    return {
        "schema": "RHT-27-v1",
        "evidence": "exact finite examples and algebraic bounds under declared interventional kernels; no model data or physical boundary certificate",
        "rational_cases": rational,
        "postprocessing_cases": postprocess,
        "deterministic_cases": deterministic,
        "learning_audit": asdict(learning.audit()),
        "reset_after_update_audit": asdict(late.audit()),
        "reset_before_update_audit": asdict(early.audit()),
        "unsafe_permitted_feedback": asdict(unsafe_risk),
        "sharp_reference_risk_certificate": asdict(sharp_risk),
        "checks": checks,
        "source_sha256": {path: sha256((ROOT / path).read_bytes()).hexdigest() for path in SOURCE_FILES},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=ROOT / "output/evaluation_noninterference/rht27_v1.json")
    args = parser.parse_args()
    receipt = verify()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, default=str, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    print(f"RHT-27: {len(receipt['checks'])} checks; {receipt['rational_cases']} rational, "
          f"{receipt['deterministic_cases']} deterministic, {receipt['postprocessing_cases']} postprocessing cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
