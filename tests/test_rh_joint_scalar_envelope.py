from spiral_ln.rh_joint_scalar_envelope import (
    bounds, campaign, enlarged_scale,
)
from spiral_ln.rh_window_feasibility import scale_witness


def test_large_x_and_smallcosts_sufficient_scalar_envelopes():
    receipt = campaign()
    assert len(receipt["cases"]) == 2
    for case in receipt["cases"]:
        assert case["all_sufficient_gates_pass"]
        assert case["sizewindows_scalar_passes"] == case["sizewindows_scalar_total"] == 16
        assert case["source_scale_passes"] == case["source_scale_total"] == 12
        assert case["all_scale_and_sizewindow"]
        assert not case["full_scale_structure_proved"]


def test_short_scale_fails_sufficient_exponential_check():
    prior = scale_witness(6)
    assert prior.power(prior.epsilon / 8) == 4
    assert 3 + 5 * prior.x_log2 > 4
    result = bounds(enlarged_scale(6))
    assert result["x_log2"] == 16384
    assert result["sufficient_gate_inequalities"]["sufficient_8x5_le_exp_xeps8"]
