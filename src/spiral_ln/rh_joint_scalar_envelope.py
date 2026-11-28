"""Source-pinned sufficient scalar certificates for LargeX and SmallCosts.

All checks use integer/Fraction inequalities. For exponential/logarithmic
conditions we verify explicit sufficient inequalities using standard analytic
facts log(2) <= 1, log(x+1) <= 1+log2(x) for x a power of 2, and monotonicity
of exp. These facts are explained in the report, not proved in this module.

This is a scalar envelope, not an actual Scale/D7/FamP construction.
"""
from __future__ import annotations

import argparse
from dataclasses import replace
from fractions import Fraction
import json
from pathlib import Path

from spiral_ln.rh_window_feasibility import (
    WindowParams, binary_exponent, evaluate, evaluate_scale, scale_witness, source_pin,
)


def enlarged_scale(level: int) -> WindowParams:
    """x far beyond the large-x thresholds for epsilon=1/64 or 1/128."""
    if type(level) is not int or level not in (6, 7):
        raise ValueError("level must be 6 or 7")
    inv = 1 << level
    eps = Fraction(1, inv)
    L = 256 * inv
    q = L // inv
    n_exp = 2 * L + 8 * q
    m_exp = (L - q // 8) // 2
    k_exp = 9 * L // 2 + 10 * q
    nT_exp = n_exp - q // 8 - 1
    nT2_exp = n_exp - q
    return WindowParams(
        x_log2=L, epsilon=eps,
        n=1 << n_exp, nT=1 << nT_exp, nT2=1 << nT2_exp,
        m=1 << m_exp, k=Fraction(1 << k_exp),
    )


def bounds(p: WindowParams) -> dict:
    """Exact arithmetic for sufficient, rather than evaluated transcendental, gates."""
    L = p.x_log2
    eps = p.epsilon
    x = p.x
    # The original proof uses f = 2*n in smallCosts. Here these are
    # independent scalar choices; not claimed to be Scale.b/Scale.theta.
    f = 2 * p.n
    eta = Fraction(1)
    b = Fraction(12 * f) * x * (x + 1)
    theta = Fraction(1, 4 * f) / (x * (x + 1))
    revised = replace(p, b=b)
    size = evaluate(revised)
    scale = evaluate_scale(revised)
    checks = {
        "large_x_at_least_3": 3 <= x,
        # Since log(8) < 3 and log(x)=L*log(2) <= L:
        "sufficient_8x5_le_exp_xeps8": 3 + 5 * L <= p.power(eps / 8),
        # Since log(48) < 6:
        "sufficient_48x5_le_exp_xeps4": 6 + 5 * L <= p.power(eps / 4),
        "large_x_power_two": 2 <= p.power(3 * eps / 4),
        "large_x_power_26": 26 <= p.power(3 * eps / 8),
        # With Cd=CL=0, moveCost = 3*log(x+1) and
        # log(x+1) <= (L+1)*log(2) <= L+1.
        "sufficient_move_cost": 3 * (L + 1) <= p.power(Fraction(1, 2) + eps),
        "eta_positive": 0 < eta,
        "eta_log_condition": 1 <= p.power(eps / 4),  # log(1)=0
        "theta_positive": 0 < theta,
        "small_cost_theta": 2 * f * (x + 1) * theta <= 1 / x,
        "small_cost_b": 6 * f * (x + 1) * (eta + 1) <= b / x,
    }
    return {
        "epsilon": str(eps), "x_log2": L,
        "log2_n": binary_exponent(p.n),
        "log2_k": binary_exponent(p.k.numerator),
        "f_relation": "f=2n",
        "parameter_choices": {
            "eta": 1, "c": 1, "Cd": 0, "CL": 0,
            "b_formula": "12*f*x*(x+1)",
            "theta_formula": "1/(4*f*x*(x+1))",
            "b_bits": b.numerator.bit_length(),
            "theta_denominator_bits": theta.denominator.bit_length(),
        },
        "sufficient_gate_inequalities": checks,
        "all_sufficient_gates_pass": all(checks.values()),
        "sizewindows_scalar_passes": size["passes"],
        "sizewindows_scalar_total": size["total"],
        "source_scale_passes": scale["passes"],
        "source_scale_total": scale["total"],
        "all_scale_and_sizewindow": size["all_pass"] and scale["all_scale_checks_pass"],
        "full_scale_structure_proved": False,
        "full_analytic_or_geometric_witness_proved": False,
    }


def campaign() -> dict:
    cases = [bounds(enlarged_scale(j)) for j in (6, 7)]
    if not all(c["all_sufficient_gates_pass"] and c["all_scale_and_sizewindow"] for c in cases):
        raise AssertionError("a sufficient scalar gate failed")
    early = scale_witness(6)
    precondition = 3 + 5 * early.x_log2 <= early.power(early.epsilon / 8)
    if precondition:
        raise AssertionError("short-scale negative control unexpectedly sufficient")
    return {
        "schema_version": 1,
        "kind": "source_regime_exact_scalar_sufficient_conditions",
        "method": "exact integers/Fractions, plus cited elementary log-exp inequalities",
        "cases": cases,
        "negative_control": {
            "epsilon": "1/64", "x_log2": early.x_log2,
            "short_scale_passes_sufficient_8x5_exp_test": precondition,
            "interpretation": "failure of this sufficient test does not alone refute LargeX",
        },
        "logical_bridge": [
            "log(2) <= 1",
            "for x=2^L and x>=1, log(x+1) <= L+1",
            "log(8*x^5) <= 3+5*L and log(48*x^5) <= 6+5*L",
            "exp is strictly increasing",
        ],
        "scope": "Scalar gates for chosen free parameters only; actual Scale.b, Scale.theta, adm5, adm6, adm7 and geometric family data are not constructed",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = campaign()
    result["source_identity"] = source_pin(args.source_root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps({
        "cases": len(result["cases"]), "all_gates_pass": all(c["all_sufficient_gates_pass"] for c in result["cases"]),
        "all_sizewindows_and_scale": all(c["all_scale_and_sizewindow"] for c in result["cases"]),
        "proof_term_data": False,
        "source_commit": result["source_identity"]["source_commit"],
        "full_geometric_witness": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
