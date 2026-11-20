"""Regenerate the deterministic RHT-28 composition receipt using full-path oracles."""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

from spiral_ln.evaluation_finite_kernels import Kernel, identity
from spiral_ln.evaluation_contamination_composition import (
    composition_certificate, risk_certificate, trace_law, trace_total_variation,
    unrolled_contributions,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILES = (
    "src/spiral_ln/evaluation_finite_kernels.py",
    "tests/test_evaluation_finite_kernels.py",
    "src/spiral_ln/evaluation_contamination_composition.py",
    "tests/test_evaluation_contamination_composition.py",
    "scripts/verify_evaluation_contamination_composition.py",
    "TrainingParanoia/RHT-28/contamination_composition.md",
    "lean/FeedbackChannel/TrainingParanoia.lean",
)


def path_oracle(initial, kernels):
    """Direct product expansion; independent of all probability helper functions."""
    sizes = [len(initial)] + [len(kernel.rows[0]) for kernel in kernels]
    traces = {}
    terminal = [Q(0)] * sizes[-1]
    for path in product(*(range(size) for size in sizes)):
        mass = Q(initial[path[0]])
        for time in range(len(kernels)):
            mass *= kernels[time].rows[path[time]][path[time + 1]]
        traces[path] = mass
        terminal[path[-1]] += mass
    assert sum(traces.values(), Q(0)) == 1
    return traces, tuple(terminal)


def tv_oracle(left, right):
    return sum((abs(a - b) for a, b in zip(left, right)), Q(0)) / 2


def check_comparison(p, q, ps, qs):
    left_paths, left_terminal = path_oracle(p, ps)
    right_paths, right_terminal = path_oracle(q, qs)
    certificate = composition_certificate(p, q, ps, qs)
    terminal_tv = tv_oracle(left_terminal, right_terminal)
    path_tv = tv_oracle(left_paths.values(), right_paths.values())
    assert certificate.final_p == left_terminal
    assert certificate.final_q == right_terminal
    assert certificate.final_tv == terminal_tv
    assert terminal_tv <= certificate.terminal_bound <= 1
    assert terminal_tv <= certificate.recurrence_bound <= certificate.unrolled_bound <= 1
    assert path_tv <= certificate.trace_bound <= 1
    assert terminal_tv <= path_tv
    expanded = certificate.initial_contribution + sum(certificate.injection_contributions, Q(0))
    assert certificate.unrolled_bound == min(Q(1), expanded)
    expected_agreement = 1 - tv_oracle(p, q)
    for step, pk, qk in zip(certificate.steps, ps, qs):
        row_errors = [tv_oracle(pr, qr) for pr, qr in zip(pk.rows, qk.rows)]
        delta_p = max(tv_oracle(a, b) for a, b in product(pk.rows, repeat=2))
        delta_q = max(tv_oracle(a, b) for a, b in product(qk.rows, repeat=2))
        assert step.epsilon == max(row_errors)
        assert step.delta_p == delta_p and step.delta_q == delta_q
        assert step.delta == min(delta_p, delta_q)
        assert step.actual_tv <= step.recurrence_bound <= step.unrolled_bound
        expected_agreement *= 1 - max(row_errors)
    assert certificate.trace_bound == 1 - expected_agreement
    event_checks = 0
    for event in product((0, 1), repeat=len(left_terminal)):
        left_risk = sum((mass * outcome for mass, outcome in zip(left_terminal, event)), Q(0))
        right_risk = sum((mass * outcome for mass, outcome in zip(right_terminal, event)), Q(0))
        assert abs(left_risk - right_risk) <= certificate.terminal_bound
        event_checks += 1
    return event_checks


def finite_census():
    grid = (Q(0), Q(1, 2), Q(1))
    starts = tuple((value, 1 - value) for value in grid)
    kernels = tuple(Kernel(((a, 1 - a), (b, 1 - b))) for a, b in product(grid, repeat=2))
    deterministic = tuple(Kernel(((a, 1 - a), (b, 1 - b))) for a, b in product((0, 1), repeat=2))
    counts = {"zero_horizon": 0, "one_step_half_grid": 0,
              "two_step_deterministic_kernels": 0,
              "two_step_half_grid_from_clean": 0}
    event_checks = 0
    for p, q in product(starts, repeat=2):
        event_checks += check_comparison(p, q, (), ())
        counts["zero_horizon"] += 1
    for p, q, pk, qk in product(starts, starts, kernels, kernels):
        event_checks += check_comparison(p, q, (pk,), (qk,))
        counts["one_step_half_grid"] += 1
    for p, q, p1, p2, q1, q2 in product(starts, starts, deterministic, deterministic,
                                        deterministic, deterministic):
        event_checks += check_comparison(p, q, (p1, p2), (q1, q2))
        counts["two_step_deterministic_kernels"] += 1
    for p1, p2, q1, q2 in product(kernels, repeat=4):
        event_checks += check_comparison((1, 0), (1, 0), (p1, p2), (q1, q2))
        counts["two_step_half_grid_from_clean"] += 1
    return counts, event_checks


def verify() -> dict:
    counts, events = finite_census()
    clean = identity(2)
    harm = Kernel(((0, 1),) * 2)
    reset = Kernel(((1, 0),) * 2)
    wiped = composition_certificate((1, 0), (1, 0), (harm, reset), (reset, reset))
    wiped_path_tv = trace_total_variation((1, 0), (1, 0), (harm, reset), (reset, reset))
    left_paths = trace_law((1, 0), (harm, reset))
    right_paths = trace_law((1, 0), (reset, reset))
    ever_risks = tuple(sum(mass for path, mass in zip(trace.paths, trace.probabilities) if 1 in path)
                       for trace in (left_paths, right_paths))
    history_harm = Kernel(((0, 1, 0),) * 3)
    history_reset = Kernel(((1, 0, 0), (0, 0, 1), (0, 0, 1)))
    history = composition_certificate((1, 0, 0), (1, 0, 0),
                                      (history_harm, history_reset), (history_reset, history_reset))
    history_risk = risk_certificate(history, (0, 1, 1))
    average = composition_certificate((0, 1), (0, 1), (clean,), (reset,))
    singleton = composition_certificate((1,), (1,), (), ())
    changed = risk_certificate(singleton, (1,), (0,))
    same_unsafe = risk_certificate(singleton, (1,))
    initial_term, injections = unrolled_contributions(
        Q(1, 2), (Q(1, 4), Q(1, 8), 0), (Q(1, 2), Q(3, 4), Q(1, 3)))
    accumulating = Kernel(((Q(3, 4), Q(1, 4)), (0, 1)))
    hazard_rows = []
    for horizon in range(9):
        result = composition_certificate((1, 0), (1, 0), (accumulating,) * horizon, (clean,) * horizon)
        path_tv = trace_total_variation((1, 0), (1, 0), (accumulating,) * horizon, (clean,) * horizon)
        expected = 1 - Q(3, 4) ** horizon
        assert result.final_tv == result.terminal_bound == result.trace_bound == path_tv == expected
        hazard_rows.append({"horizon": horizon, "state_tv": str(result.final_tv),
                            "path_tv": str(path_tv), "bound": str(result.terminal_bound)})
    contraction = Kernel(((1, 0), (Q(1, 2), Q(1, 2))))
    contraction_rows = []
    for horizon in range(9):
        result = composition_certificate((1, 0), (0, 1), (contraction,) * horizon, (contraction,) * horizon)
        path_tv = trace_total_variation((1, 0), (0, 1), (contraction,) * horizon, (contraction,) * horizon)
        assert result.final_tv == result.terminal_bound == Q(1, 2) ** horizon
        assert path_tv == result.trace_bound == 1
        contraction_rows.append({"horizon": horizon, "state_tv": str(result.final_tv),
                                 "path_tv": str(path_tv), "initial_contribution": str(result.initial_contribution)})
    swap = Kernel(((0, 1), (1, 0)))
    clipped = composition_certificate((1, 0), (1, 0), (clean, clean, contraction),
                                      (swap, swap, contraction))
    uniform_reset = Kernel(((Q(1, 2), Q(1, 2)),) * 2)
    both_orientations = [composition_certificate((1, 0), (0, 1), (a,), (b,))
                         for a, b in ((uniform_reset, clean), (clean, uniform_reset))]
    rectangular = composition_certificate((1, 0), (1, 0),
        (Kernel(((0, 1, 0), (0, 0, 1))), Kernel(((1,), (1,), (1,)))),
        (Kernel(((1, 0, 0), (0, 0, 1))), Kernel(((1,), (1,), (1,)))))
    guard_rejected = False
    try:
        trace_law((1, 0), (clean,) * 20, max_paths=1024)
    except ValueError as error:
        guard_rejected = "exceeds max_paths" in str(error)
    checks = {
        "zero_horizon_full_initial_grid": counts["zero_horizon"] == 9,
        "one_step_full_half_probability_grid": counts["one_step_half_grid"] == 729,
        "two_step_all_deterministic_kernels_and_initial_grid": counts["two_step_deterministic_kernels"] == 2304,
        "two_step_full_half_probability_kernel_grid": counts["two_step_half_grid_from_clean"] == 6561,
        "all_terminal_events_bound_checked": events == 38412,
        "independent_path_census_total": sum(counts.values()) == 9603,
        "unrolled_initial_distance_term": initial_term == Q(1, 16),
        "unrolled_injection_time_order": injections == (Q(1, 16), Q(1, 24), 0),
        "unrolled_sum_exact": initial_term + sum(injections, Q(0)) == Q(1, 6),
        "reset_terminal_distance_zero": wiped.final_tv == wiped.terminal_bound == 0,
        "reset_retains_full_history_distance": wiped_path_tv == wiped.trace_bound == 1,
        "reset_retains_ever_harm_event": ever_risks == (1, 0),
        "absorbing_history_state_retains_evidence": history.final_tv == history_risk.absolute_gap == 1,
        "row_average_can_understate_selected_state_error": average.final_tv == average.steps[0].epsilon == 1 > Q(1, 2),
        "changed_endpoint_needs_own_discrepancy": changed.absolute_gap == changed.endpoint_discrepancy == changed.gap_bound == 1,
        "zero_discrepancy_does_not_remove_baseline_risk": same_unsafe.absolute_gap == 0 and same_unsafe.actual_risk_upper_bound == 1,
        "geometric_persistent_injection_sharp": len(hazard_rows) == 9,
        "initial_distance_contraction_sharp": len(contraction_rows) == 9,
        "intermediate_clipping_can_strengthen_terminal_bound": clipped.recurrence_bound == Q(1, 2) < clipped.unrolled_bound == 1,
        "minimum_of_two_contractions_is_licensed": all(r.steps[0].delta == 0 and r.terminal_bound == Q(1, 2) for r in both_orientations),
        "time_varying_rectangular_state_spaces": rectangular.final_tv == 0 and rectangular.trace_bound == 1,
        "complete_trace_allocation_guard": guard_rejected,
    }
    if not all(checks.values()):
        raise AssertionError([name for name, passed in checks.items() if not passed])
    return {
        "schema": "RHT-28-v1",
        "evidence": "exact finite examples with algebraic proofs in the note; no empirical or neural safety claim",
        "finite_census": counts,
        "comparison_count": sum(counts.values()),
        "terminal_event_checks": events,
        "persistent_injection": hazard_rows,
        "initial_distance_contraction": contraction_rows,
        "reset_history_witness": {"terminal_tv": str(wiped.final_tv), "path_tv": str(wiped_path_tv),
                                  "ever_harm_risks": [str(value) for value in ever_risks],
                                  "augmented_state_tv": str(history.final_tv)},
        "unrolled_example": {"initial_contribution": str(initial_term),
                             "injection_contributions": [str(value) for value in injections],
                             "sum": str(initial_term + sum(injections, Q(0)))},
        "checks": checks,
        "source_sha256": {path: sha256((ROOT / path).read_bytes()).hexdigest() for path in SOURCE_FILES},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=ROOT / "output/evaluation_contamination_composition/rht28_v1.json")
    args = parser.parse_args()
    receipt = verify()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"RHT-28: {len(receipt['checks'])} checks, {receipt['comparison_count']} complete-path comparisons, {receipt['terminal_event_checks']} terminal-event checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
