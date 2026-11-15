"""BPD pre-run specificity: paired, same-pass donor-activation swaps.

This is an *observational contrast test* over two independently captured,
host-declared item strata (target and matched collision). The caller must
declare matching before evaluation; this module never learns the grouping
from outcome labels. Effects are computed at one explicit next readout.

The rotation null remains a diagnostic of fragility, not the definition
of specificity. This module does not train a neural decomposition.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Callable

import torch

from mechinterp.bpd.components import BPDModel, RolloutTrajectory
from mechinterp.bpd.losses import kl_divergence_logits


@dataclass(frozen=True)
class ItemContrastResult:
    module: str
    component: int
    intervention_pass: int
    next_readout: int
    target_effect: float
    collision_effect: float
    target_minus_collision: float
    target_items: int
    collision_items: int
    specificity_rule: str = "target_vs_matched_collision_donor_swap"

    def to_dict(self) -> dict:
        return asdict(self)


@torch.no_grad()
def evaluate_item_donor_contrast(
    model: BPDModel,
    module: str,
    component: int,
    *,
    intervention_pass: int,
    next_readout: int,
    target_clean: RolloutTrajectory,
    collision_clean: RolloutTrajectory,
    run_target: Callable[[], RolloutTrajectory],
    run_collision: Callable[[], RolloutTrajectory],
) -> ItemContrastResult:
    """Swap component reads between pre-matched target/collision batches.

    One target trajectory receives component activity from the collision
    batch at the *same* module and recurrent pass; the reciprocal collision
    run receives activity from the target batch. No refitting is performed.
    Data matching, context leakage controls and route equality are caller
    obligations; this function fails on incompatible dimensions.
    """
    if module not in model.wrappers:
        raise KeyError(module)
    w = model.wrappers[module]
    if type(component) is not int or component < 0 or component >= w.C:
        raise ValueError("component out of range")
    if type(intervention_pass) is not int or intervention_pass < 0:
        raise ValueError("intervention_pass must be nonnegative integer")
    if type(next_readout) is not int or next_readout <= intervention_pass:
        raise ValueError("next_readout must strictly follow the intervention")
    for name, tr in (("target", target_clean), ("collision", collision_clean)):
        if module not in tr.module_inputs:
            raise ValueError(f"{name} trajectory lacks module inputs")
        xs = tr.module_inputs[module]
        if xs.ndim != 4 or xs.shape[1] <= intervention_pass:
            raise ValueError(f"{name} input is not [B,T,P,D] at selected pass")
        if next_readout not in tr.readouts:
            raise ValueError(f"{name} lacks the explicitly requested readout")
    target_x = target_clean.module_inputs[module][:, intervention_pass]
    collision_x = collision_clean.module_inputs[module][:, intervention_pass]
    if target_x.shape != collision_x.shape:
        raise ValueError("Matched strata must share [B,P,D] shape")
    if target_clean.readouts[next_readout].shape != collision_clean.readouts[next_readout].shape:
        raise ValueError("Matched strata must share readout shape")
    v = w.V[:, component:component+1].detach()
    target_donor = collision_x.float() @ v
    collision_donor = target_x.float() @ v
    with model.intervene(
        module, component, passes={intervention_pass},
        mode="swap_acts", donor_acts=target_donor,
    ):
        target_pert = run_target()
    with model.intervene(
        module, component, passes={intervention_pass},
        mode="swap_acts", donor_acts=collision_donor,
    ):
        collision_pert = run_collision()
    if next_readout not in target_pert.readouts or next_readout not in collision_pert.readouts:
        raise ValueError("Perturbed rollouts lack the requested next readout")
    targ = float(kl_divergence_logits(
        target_pert.readouts[next_readout], target_clean.readouts[next_readout]
    ).item())
    coll = float(kl_divergence_logits(
        collision_pert.readouts[next_readout], collision_clean.readouts[next_readout]
    ).item())
    return ItemContrastResult(
        module=module,
        component=component,
        intervention_pass=intervention_pass,
        next_readout=next_readout,
        target_effect=targ,
        collision_effect=coll,
        target_minus_collision=targ-coll,
        target_items=int(target_x.shape[0]),
        collision_items=int(collision_x.shape[0]),
    )
