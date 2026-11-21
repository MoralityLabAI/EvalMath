"""Exact feasibility checks independent of the unlicensed upstream source."""
from dataclasses import replace
from fractions import Fraction
import pytest

from spiral_ln.rh_window_feasibility import (
    CLAUSES, PREDICATE_BLOB, WindowParams, campaign, dyadic_witness,
    evaluate, source_pin,
)


def test_exact_dyadic_family_has_all_16_sizewindows_fields():
    result = campaign(range(1, 6))
    assert len(CLAUSES) == 16 and len(PREDICATE_BLOB) == 40
    for case in result["positive_examples"]:
        assert case["total"] == case["passes"] == 16
        assert case["all_pass"] and case["exact_arithmetic"]
    assert [x["epsilon"] for x in result["positive_examples"]] == ["1/2", "1/4", "1/8", "1/16", "1/32"]


def test_minimum_cardinality_mutation_and_threshold_mutation_fail():
    good = dyadic_witness(1)
    assert evaluate(good)["all_pass"]
    below = evaluate(replace(good, n=good.n - 1))
    assert not below["checks"]["k_cap"]
    assert not below["all_pass"]
    early = evaluate(WindowParams(x_log2=16, epsilon=Fraction(1, 2),
                                  n=256, nT=64, nT2=1, m=1, k=Fraction(65536)))
    assert not early["checks"]["eventual_x"]
    assert sum(early["checks"].values()) == 15


def test_power_exactness_and_exponent_budget_fail_closed():
    p = dyadic_witness(1)
    assert p.power(Fraction(3, 16)) == 64
    assert p.power(Fraction(-1, 16)) == Fraction(1, 4)
    with pytest.raises(ValueError):
        p.power(Fraction(1, 7))
    with pytest.raises(ValueError):
        dyadic_witness(0)
    with pytest.raises(ValueError):
        dyadic_witness(8)


def test_pin_rejects_missing_source(tmp_path):
    with pytest.raises(Exception):
        source_pin(tmp_path)


def test_original_sizesat_placesat_small_epsilon_regime():
    from spiral_ln.rh_window_feasibility import scale_witness, evaluate_scale
    for j in (6, 7):
        certificate = evaluate_scale(scale_witness(j))
        assert certificate["passes"] == certificate["total"] == 12
        assert certificate["all_scale_checks_pass"]
        assert certificate["sizewindows_passes"] == certificate["sizewindows_total"] == 16
        assert certificate["sizewindows_pass"]
    assert not evaluate_scale(dyadic_witness(6))["checks"]["SizesAt_n_lower"]
    with pytest.raises(ValueError):
        scale_witness(5)


def test_exact_exponent_log2_requires_power_of_two():
    from spiral_ln.rh_window_feasibility import binary_exponent
    assert binary_exponent(2**2176) == 2176
    with pytest.raises(ValueError):
        binary_exponent(3)
