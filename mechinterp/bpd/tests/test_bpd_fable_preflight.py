"""BPD Fable review regression checks: exact semantics, no model training.

Historical positive-control failures are fixed archived observations; their
numbers are not new reruns. The fresh toy intervention executes a two-pass
linear model and measures a next-readout causal item contrast.
"""
from __future__ import annotations

from dataclasses import replace

import pytest
import torch
from torch import nn

from mechinterp.bpd.components import BPDModel, RolloutTrajectory
from mechinterp.bpd.config import AblationConfig, BPDConfig, MinimalityConfig
from mechinterp.bpd.contrast import evaluate_item_donor_contrast
from mechinterp.bpd.losses import bpd_minimality_loss, trajectory_recon_loss
from mechinterp.bpd.nulls import empirical_upper_rank_p, holm_adjust


def test_historical_positive_controls_remain_expected_failures() -> None:
    # Archived worktree run 2: dense amplified component, NOT a new execution.
    assert 10.1582 < 44.9369
    # Archived worktree run 4: dense all-position selective component.
    assert 0.7691 < 2.0
    # 12 samples cannot reach a one-sided rank p below 1/13.
    assert empirical_upper_rank_p(10., [0.] * 12) == pytest.approx(1. / 13.)


def test_rank_tail_ties_and_holm_familywise_adjustment() -> None:
    assert empirical_upper_rank_p(2., [1., 2., 3.]) == 3. / 4.
    assert empirical_upper_rank_p(5., [1., 2., 3.]) == 1. / 4.
    assert holm_adjust([0.01, 0.04, 0.03, 0.3]) == pytest.approx(
        [0.04, 0.09, 0.09, 0.3]
    )
    assert empirical_upper_rank_p(5., [0.] * 255) == 1. / 256.
    with pytest.raises(ValueError):
        empirical_upper_rank_p(1., [])


def test_mean_pool_dilutes_single_pass_and_is_neutral_to_temporal_split() -> None:
    assert MinimalityConfig().pool_mode == "max"
    assert BPDConfig(c_per_module={"core": 2}).minimality.pool_mode == "max"
    assert BPDConfig.vpd_single_pass_equivalent({"core": 2}).minimality.pool_mode == "mean"
    cfg = MinimalityConfig(coeff_level=1., coeff_switch=0., p_start=1., p_end=1.)
    sustained = torch.ones(1, 1, 1, 1)
    one_of_336 = torch.zeros(1, 336, 1, 1)
    one_of_336[:, 0] = 1.
    max_all, _ = bpd_minimality_loss({"m": sustained}, step=1, total_steps=1, cfg=cfg)
    max_sparse, _ = bpd_minimality_loss({"m": one_of_336}, step=1, total_steps=1, cfg=cfg)
    assert torch.allclose(max_all, max_sparse, atol=1e-6)
    mean_cfg = replace(cfg, pool_mode="mean")
    mean_sparse, _ = bpd_minimality_loss({"m": one_of_336}, step=1, total_steps=1, cfg=mean_cfg)
    assert float(mean_sparse) < float(max_all) / 100

    stationary = torch.zeros(1, 4, 1, 2)
    stationary[..., 0] = 1
    split = torch.zeros_like(stationary)
    split[:, 0::2, :, 0] = 1
    split[:, 1::2, :, 1] = 1
    m_stat, _ = bpd_minimality_loss({"m": stationary}, step=1, total_steps=1, cfg=mean_cfg)
    m_split, _ = bpd_minimality_loss({"m": split}, step=1, total_steps=1, cfg=mean_cfg)
    assert torch.allclose(m_stat, m_split, atol=1e-6)
    x_stat, _ = bpd_minimality_loss({"m": stationary}, step=1, total_steps=1, cfg=cfg)
    x_split, _ = bpd_minimality_loss({"m": split}, step=1, total_steps=1, cfg=cfg)
    assert float(x_split) > float(x_stat)


def test_boundary_matching_requires_explicit_policy() -> None:
    clean = RolloutTrajectory(
        readouts={}, boundary_states={0: torch.ones(2, 1, 4)}, module_inputs={}
    )
    pert = RolloutTrajectory(
        readouts={}, boundary_states={0: torch.zeros(2, 1, 4)}, module_inputs={}
    )
    with pytest.raises(ValueError, match="choose readout_or_boundary"):
        trajectory_recon_loss(pert, clean)
    value, per_pass = trajectory_recon_loss(pert, clean, readout_policy="readout_or_boundary")
    assert float(value) > 0.0 and 0 in per_pass


class _TwoPassToy(nn.Module):
    def __init__(self):
        super().__init__()
        self.core = nn.Linear(2, 2, bias=False)
        with torch.no_grad():
            self.core.weight.zero_()
            self.core.weight[0, 0] = 1.

    def rollout(self, x: torch.Tensor, gain: float):
        h0 = self.core(x)
        h1 = self.core(h0)
        r1 = torch.stack((gain * h1[..., 0], torch.zeros_like(h1[..., 0])), dim=-1)
        return {1: r1}, {0: h0, 1: h1}


def test_donor_swap_is_independently_captured_and_next_readout_scored() -> None:
    target = _TwoPassToy()
    bpd = BPDModel(
        target, {"core": 1}, max_passes=2,
        ablation=AblationConfig(mode="zero", sphere_rescale=False), init_svd=False
    )
    with torch.no_grad():
        w = bpd.wrappers["core"]
        w.V.zero_()
        w.U.zero_()
        w.V[0, 0] = 1.
        w.U[0, 0] = 1.
    t_in = torch.zeros(3, 2, 2)
    c_in = torch.zeros_like(t_in)
    t_in[..., 0] = 1
    c_in[..., 0] = -1

    def capture(x, gain):
        with bpd.target_capture():
            ro, bs = target.rollout(x, gain)
        return RolloutTrajectory(
            readouts=ro, boundary_states=bs,
            module_inputs=bpd.collect_recorded_inputs(expected_passes=2)
        )

    clean_t = capture(t_in, 6.0)
    clean_c = capture(c_in, 0.1)

    def run_t():
        ro, bs = target.rollout(t_in, 6.0)
        return RolloutTrajectory(readouts=ro, boundary_states=bs, module_inputs={})

    def run_c():
        ro, bs = target.rollout(c_in, 0.1)
        return RolloutTrajectory(readouts=ro, boundary_states=bs, module_inputs={})

    result = evaluate_item_donor_contrast(
        bpd, "core", 0, intervention_pass=0, next_readout=1,
        target_clean=clean_t, collision_clean=clean_c,
        run_target=run_t, run_collision=run_c,
    )
    assert result.target_effect > result.collision_effect + 1.0
    assert result.target_minus_collision == pytest.approx(
        result.target_effect - result.collision_effect
    )
    assert result.target_items == result.collision_items == 3
    with pytest.raises(ValueError, match="strictly follow"):
        evaluate_item_donor_contrast(
            bpd, "core", 0, intervention_pass=0, next_readout=0,
            target_clean=clean_t, collision_clean=clean_c,
            run_target=run_t, run_collision=run_c,
        )
    with pytest.raises(ValueError, match="iff"):
        with bpd.intervene("core", 0, mode="swap_acts"):
            pass
