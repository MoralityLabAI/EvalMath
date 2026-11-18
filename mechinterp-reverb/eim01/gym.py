"""EIM-01: a bounded eval -> BPD intervention -> training loop.

Source data: kernel-audited BPD-LG-02 *synthetic* Lean/Horn cases.
Model: a planted two-factor, shared-weight torch graph-relay circuit, NOT
a trained compact theorem prover. A deliberately confounded 'cue' is the
model-visible shortcut, used as a falsification control. The eval changes
that cue without changing the verified graph proof label.

All causal-effect rows are measured by actual BPDModel interventions using
same-pass donor activations and a subsequent readout. The two-component
head is trained after candidate evaluation types are selected with a rank
criterion. Held-out fourth-family labels never enter training or selection.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
from typing import Iterable
import json

import torch
from torch import nn
import torch.nn.functional as F

from experiments.bpd_lean_curriculum_v2.generate import roster
from mechinterp.bpd.components import BPDModel, RolloutTrajectory
from mechinterp.bpd.config import AblationConfig
from .design import (EffectRow, PreReadoutGeometry, select_identifying_evals,
                     two_column_certificate, select_geometry_basis,
                     check_joint_linear_response)

NODES = 24
PASSES = 22
MODEL_NAME = "eim01-planted-two-channel-bpd-20261115"


@dataclass(frozen=True)
class GraphEval:
    case_id: str
    family: str
    split: str
    root_group: str
    alpha_hash: str
    adjacency: torch.Tensor
    goal_index: int
    label: int
    cue: int

    def with_cue(self, cue: int) -> "GraphEval":
        if cue not in (0, 1):
            raise ValueError("The cue is binary")
        return replace(self, cue=cue)


def source_cases() -> list[GraphEval]:
    """Host-scored source cases, then converted to cue-confounded model inputs.

    rw is undirected equality connectivity. Other families use directed
    Horn edges. Induction's additional hloop is irrelevant to the base
    reachability label and never synthesized as a new proof claim here.
    """
    result = []
    for row in roster():
        h = row["host_only"]
        signature = h["model_signature"]
        d = row["structural_depth"]
        fam = row["family"]
        stem = "X" if fam == "rw" else "P"
        names = [f"{stem}{i}" for i in range(d+1)]
        names += [f"D{i}" for i in range(signature["decoy_count"])]
        if len(names) > NODES:
            raise ValueError("Graph too large for fixed-size relay")
        idx = {name: i for i, name in enumerate(names)}
        adj = torch.zeros(NODES, NODES)
        for a, b in h["source_edges"]:
            adj[idx[a], idx[b]] = 1.
            if fam == "rw":
                adj[idx[b], idx[a]] = 1.
        y = int(h["solvable"])
        result.append(GraphEval(
            case_id=row["case_id"], family=fam, split=row["split"],
            root_group=row["root_group"], alpha_hash=row["alpha_hash"],
            adjacency=adj, goal_index=idx[h["target_node"]],
            label=y, cue=y,   # intentional observational confound
        ))
    return result


def check_source_oracle(items: Iterable[GraphEval]) -> dict[str, int]:
    """Independent graph recurrence must reproduce host-labelled statements."""
    cases = list(items)
    if not cases:
        raise ValueError("Empty source")
    for c in cases:
        seen = torch.zeros(NODES)
        seen[0] = 1.
        for _ in range(NODES):
            seen = (seen + seen @ c.adjacency).clamp(max=1.)
        if int(seen[c.goal_index].item() > 0.5) != c.label:
            raise AssertionError(f"Graph oracle disagrees with host: {c.case_id}")
    return {"checked": len(cases), "disagreements": 0}


def batch(items: list[GraphEval]) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    if not items:
        raise ValueError("Batch must be nonempty")
    return (torch.stack([c.adjacency for c in items]),
            torch.tensor([c.goal_index for c in items], dtype=torch.long),
            torch.tensor([c.cue for c in items], dtype=torch.float32),
            torch.tensor([c.label for c in items], dtype=torch.long))


class PlantedGraphRelay(nn.Module):
    """A looped reasoning demonstration with two known BPD rank-one channels.

    Channel 0 carries actual graph-closure evidence; channel 1 carries a
    deliberately misleading surface cue. A trainable readout can choose
    either or both. Shared core is applied on EVERY pass, giving real
    pass-specific BPD intervention sites and causal propagation.
    """
    def __init__(self):
        super().__init__()
        self.core = nn.Linear(2, 2, bias=False)
        with torch.no_grad():
            self.core.weight.copy_(torch.eye(2))
        self.mix = nn.Parameter(torch.tensor([0.15, 1.75]))
        self.bias = nn.Parameter(torch.tensor(0.83))

    def rollout(self, graph: torch.Tensor, goals: torch.Tensor, cue: torch.Tensor,
                *, passes: int = PASSES) -> tuple[dict[int, torch.Tensor], dict[int, torch.Tensor]]:
        bsz = graph.shape[0]
        if graph.shape != (bsz, NODES, NODES) or goals.shape != (bsz,) or cue.shape != (bsz,):
            raise ValueError("Graph, goal and cue shapes must agree")
        reach = torch.zeros(bsz, NODES, device=graph.device)
        reach[:, 0] = 1.
        carry = torch.zeros(bsz, 1, 2, device=graph.device)
        readouts, boundaries = {}, {}
        rows = torch.arange(bsz, device=graph.device)
        for tau in range(passes):
            reach = (reach + torch.bmm(reach.unsqueeze(1), graph).squeeze(1)).clamp(max=1.)
            evidence = reach[rows, goals]
            x = torch.stack((evidence, cue), dim=-1).unsqueeze(1)
            write = self.core(x)
            carry = .35 * carry + .65 * write
            score = 3.5 * ((carry.squeeze(1) * self.mix).sum(dim=-1) - self.bias)
            logits = torch.stack((-score, score), dim=-1).unsqueeze(1)
            readouts[tau] = logits
            boundaries[tau] = carry
        return readouts, boundaries


def planted_bpd() -> tuple[PlantedGraphRelay, BPDModel]:
    target = PlantedGraphRelay()
    bpd = BPDModel(target, {"core": 2}, max_passes=PASSES,
                   ablation=AblationConfig(mode="zero", sphere_rescale=False),
                   init_svd=False)
    with torch.no_grad():
        bpd.wrappers["core"].V.copy_(torch.eye(2))
        bpd.wrappers["core"].U.copy_(torch.eye(2))
    # BPDModel freezes pretrained parameters. Train the readout ONLY.
    target.mix.requires_grad_(True)
    target.bias.requires_grad_(True)
    return target, bpd


def clean_capture(target: PlantedGraphRelay, bpd: BPDModel,
                  examples: list[GraphEval]) -> RolloutTrajectory:
    graph, goals, cue, _ = batch(examples)
    with bpd.target_capture():
        ro, bs = target.rollout(graph, goals, cue)
    return RolloutTrajectory(readouts=ro, boundary_states=bs,
                             module_inputs=bpd.collect_recorded_inputs(expected_passes=PASSES))


def model_fingerprint(target: PlantedGraphRelay) -> str:
    """Source- and weight-bound identity of the EXACT currently measured model.

    Avoid a decorative model name as the observation ledger identity: the
    readout weights change during training, and pre/post rows must carry
    distinct model hashes. State tensors are serialized as plain JSON lists
    to avoid an implicit NumPy dependency on the CPU CI runner.
    """
    params = {key: value.detach().float().cpu().tolist()
              for key, value in sorted(target.state_dict().items())}
    payload = {"arch": MODEL_NAME, "passes": PASSES, "state_dict": params}
    return sha256(json.dumps(payload, sort_keys=True,
                             separators=(",", ":")).encode()).hexdigest()


def signed_swap_row(target: PlantedGraphRelay, bpd: BPDModel,
                    recipient: GraphEval, donor: GraphEval, role: str) -> EffectRow:
    """Actual same-clock BPD donor swaps at penultimate pass; signed logit effects."""
    if recipient.split != "train" or donor.split != "train":
        raise ValueError("Probe design uses training roots only")
    t = PASSES-2
    clean = clean_capture(target, bpd, [recipient])
    source = clean_capture(target, bpd, [donor])
    g, goals, cue, _ = batch([recipient])
    effects = []
    for c in (0, 1):
        v = bpd.wrappers["core"].V[:, c:c+1].detach()
        donor_read = source.module_inputs["core"][:, t].float() @ v
        with bpd.intervene("core", c, passes={t}, mode="swap_acts",
                           donor_acts=donor_read):
            altered, _ = target.rollout(g, goals, cue)
        effect = float((clean.readouts[t+1][0, 0, 1] -
                        altered[t+1][0, 0, 1]).detach().item())
        effects.append(effect)
    return EffectRow(
        case_id=recipient.case_id+"|"+role, donor_id=donor.case_id+"|"+str(donor.cue),
        origin_hash=recipient.alpha_hash, donor_hash=donor.alpha_hash,
        model_hash=model_fingerprint(target), split="train", family=recipient.family, role=role,
        intervention_pass=t, next_readout=t+1, signed_effects=tuple(effects),
        label_certified=True, route_observed=True,
    )


def measure_pre_readout_geometry(target: PlantedGraphRelay, bpd: BPDModel,
                                 recipient: GraphEval, donor: GraphEval,
                                 response: EffectRow) -> PreReadoutGeometry:
    """An input-to-readout design row independent of existing head coefficients.

    The source/recipient differences are collected at the same BPD input
    site, *before* multiplying by output-routing weights. A separate joint
    swap supplies the measured dependent variable. This avoids feeding
    already-weighted causal effects into the inverse-rank theorem.
    """
    t = response.intervention_pass
    recipient_state = clean_capture(target, bpd, [recipient])
    donor_state = clean_capture(target, bpd, [donor])
    V = bpd.wrappers["core"].V.detach()
    x = recipient_state.module_inputs["core"][:, t].float()
    x_donor = donor_state.module_inputs["core"][:, t].float()
    q = ((x-x_donor) @ V).reshape(-1).tolist()
    if len(q) != 2:
        raise AssertionError("Unexpected component geometry")
    graph, goals, cue, _ = batch([recipient])
    with bpd.intervene("core", (0, 1), passes={t},
                       mode="swap_acts", donor_acts=x_donor @ V):
        altered, _ = target.rollout(graph, goals, cue)
    d = float((recipient_state.readouts[t+1][0,0,1] -
               altered[t+1][0,0,1]).detach().item())
    # For this planted relay only: next-pass carry transport is .35*.65
    # and the readout logit multiplies carry by 3.5.
    known_transport = .35 * .65 * 3.5
    return PreReadoutGeometry(response, (float(q[0]), float(q[1])),
                              d, known_transport)


def select_probe_pairs(cases: list[GraphEval]) -> list[tuple[GraphEval, GraphEval, str]]:
    """Use a single matched train root as demonstration; no test-label reads."""
    train = [c for c in cases if c.split == "train" and c.family == "exact"]
    groups = sorted({c.root_group for c in train})
    for root in groups:
        group = [c for c in train if c.root_group == root]
        positive = next((x for x in group if x.label == 1), None)
        negative = next((x for x in group if x.label == 0), None)
        if positive is not None and negative is not None:
            return [
                (positive.with_cue(1), negative.with_cue(0), "aligned"),
                (positive.with_cue(1), positive.with_cue(0), "cue_only"),
                (positive.with_cue(0), negative.with_cue(0), "graph_only"),
            ]
    raise AssertionError("No training matched positive/negative root")


def train_readout(target: PlantedGraphRelay, bpd: BPDModel,
                  examples: list[GraphEval], *, updates: int = 80,
                  lr: float = .09) -> list[float]:
    """Train only the two output-routing weights; BPD factors remain frozen."""
    torch.set_num_threads(2)
    graph, goals, cue, labels = batch(examples)
    opt = torch.optim.Adam((target.mix, target.bias), lr=lr)
    losses = []
    for _ in range(updates):
        opt.zero_grad()
        bpd.reset_wrappers()
        ro, _ = target.rollout(graph, goals, cue)
        loss = F.cross_entropy(ro[PASSES-1].squeeze(1), labels)
        loss.backward()
        opt.step()
        losses.append(float(loss.detach().item()))
    return losses


def train_interchange_readout(target: PlantedGraphRelay, bpd: BPDModel,
                              examples: list[GraphEval], *, component: int,
                              updates: int = 90, lr: float = .09) -> list[float]:
    """Interchange intervention training from a selected causal eval family.

    Independently capture a counterfactual source with identical proof graph
    and flipped cue. On each update train against BOTH ordinary and *all-pass*
    internal donor swaps at the selected BPD factor, while preserving the
    verified graph label. This is a genuine differentiable counterfactual
    rollout through the BPD wrapper, not merely a text-level augmented input.
    Factors remain planted/frozen; only the readout routing weights learn.
    """
    if component not in (0, 1):
        raise ValueError("Only planted factor indices 0/1 supported")
    graph, goals, cue, labels = batch(examples)
    with torch.no_grad():
        with bpd.target_capture():
            target.rollout(graph, goals, 1.-cue)
        donor_x = bpd.collect_recorded_inputs(expected_passes=PASSES)["core"]
        v = bpd.wrappers["core"].V[:, component:component+1].detach()
        donor = donor_x.float() @ v
        if donor.shape != (len(examples), PASSES, 1, 1):
            raise AssertionError("Unexpected source activation schedule shape")
    opt = torch.optim.Adam((target.mix, target.bias), lr=lr)
    losses = []
    for _ in range(updates):
        opt.zero_grad()
        bpd.reset_wrappers()
        clean_ro, _ = target.rollout(graph, goals, cue)
        with bpd.intervene("core", component, passes=None,
                           mode="swap_acts", donor_acts=donor):
            swapped_ro, _ = target.rollout(graph, goals, cue)
        loss = .5 * (F.cross_entropy(clean_ro[PASSES-1].squeeze(1), labels)
                     + F.cross_entropy(swapped_ro[PASSES-1].squeeze(1), labels))
        loss.backward()
        opt.step()
        losses.append(float(loss.detach().item()))
    return losses


@torch.no_grad()
def evaluate_accuracy(target: PlantedGraphRelay, bpd: BPDModel,
                      examples: list[GraphEval]) -> float:
    graph, goals, cue, labels = batch(examples)
    bpd.reset_wrappers()
    logits, _ = target.rollout(graph, goals, cue)
    return float((logits[PASSES-1].squeeze(1).argmax(-1) == labels).float().mean())


def run_campaign() -> dict:
    """Bounded preregistration-style demonstration, no pretrained LLM claims.

    The train model first learns on an intentionally cue-confounded source
    cohort. Probe selection is on training roots and is frozen BEFORE
    fourth-family testing. Natural-only and cue-contrast arms receive equal
    numbers of optimizer updates.
    """
    torch.manual_seed(61017)
    cases = source_cases()
    oracle = check_source_oracle(cases)
    train = [c for c in cases if c.split == "train" and c.family != "induction"]
    holdout = [c.with_cue(1-c.label) for c in cases
               if c.split == "test" and c.family == "induction"]
    if len(train) != 192 or len(holdout) != 16:
        raise AssertionError("Unexpected frozen family/split sizes")
    target, bpd = planted_bpd()
    pretrain = train_readout(target, bpd, train, updates=40, lr=.09)
    baseline_test = evaluate_accuracy(target, bpd, holdout)
    controls = select_probe_pairs(cases)
    effects = [signed_swap_row(target, bpd, x, y, role)
               for x, y, role in controls]
    # A row of output effects already includes the current readout weights.
    # Use independent pre-readout geometry for coefficient-identification
    # design, and keep observed causal effects as a separate diagnostic.
    geometry = [measure_pre_readout_geometry(target, bpd, x, y, row)
                for (x, y, _), row in zip(controls, effects)]
    aligned_only = two_column_certificate(
        [tuple(geometry[0].transport * q for q in geometry[0].activation_deltas)])
    design = select_geometry_basis(geometry, budget=2)
    response_design = select_identifying_evals(effects, budget=2)
    linear_residuals = check_joint_linear_response(
        geometry, tuple(float(v) for v in target.mix.detach()))
    if not design["identified"] or not response_design["identified"]:
        raise AssertionError("Training interventions failed mechanism separation")
    selected_roles = set(design["chosen_roles"])
    # The cue conflict evaluation adds verified-label contrast examples from
    # TRAIN roots only. Heldout family is never used for loss or selection.
    contrast_train = train + ([c.with_cue(1-c.label) for c in train]
                              if "cue_only" in selected_roles else [])
    if "cue_only" not in selected_roles:
        raise AssertionError("Selecting no cue-conflict arm would not test shortcut rejection")
    cue_row = next(r for r in effects if r.role == "cue_only")
    observed_cue_component = max(range(2), key=lambda c: abs(cue_row.signed_effects[c]))
    if abs(cue_row.signed_effects[observed_cue_component]) <= 1e-5:
        raise AssertionError("Causal component not observed in donor swap")
    saved_mix = target.mix.detach().clone()
    saved_bias = target.bias.detach().clone()
    # Each arm processes 384 item-passes per pass step and 90 steps, with the
    # same frozen starting head. The passive arm repeats natural items.
    baseline_losses = train_readout(target, bpd, train + train, updates=90, lr=.09)
    passive_test = evaluate_accuracy(target, bpd, holdout)
    passive_mix = [float(x) for x in target.mix.detach()]
    with torch.no_grad():
        target.mix.copy_(saved_mix)
        target.bias.copy_(saved_bias)
    # Input-level cue-conflict augmentation is an essential control:
    # in this planted toy, it can recover the same semantic behavior.
    augmentation_losses = train_readout(target, bpd, contrast_train,
                                        updates=90, lr=.09)
    augmented_test = evaluate_accuracy(target, bpd, holdout)
    augmented_mix = [float(x) for x in target.mix.detach()]
    with torch.no_grad():
        target.mix.copy_(saved_mix)
        target.bias.copy_(saved_bias)
    # Primary arm: the eval-selected BPD factor is actually swapped during
    # optimizer updates, and the host-verified graph label is the target.
    active_losses = train_interchange_readout(target, bpd, train,
                                              component=observed_cue_component,
                                              updates=90, lr=.09)
    active_test = evaluate_accuracy(target, bpd, holdout)
    active_mix = [float(x) for x in target.mix.detach()]
    post_effects = [signed_swap_row(target, bpd, x, y, role)
                    for x, y, role in controls]
    return {
        "schema": "EIM-01-v1",
        "source": "EvalMath BPD-LG-02 synthetic Lean source and host-only labels",
        "oracle": oracle,
        "counts": {"train_graphs": len(train), "sealed_fourth_family": len(holdout),
                   "active_training_records": len(contrast_train),
                   "passive_training_records": 2*len(train),
                   "interchange_training_records": 2*len(train)},
        "observed_probe_effects": [
            {"role": row.role, "signed_effects": list(row.signed_effects),
             "case_id": row.case_id, "donor_id": row.donor_id,
             "pass": row.intervention_pass, "next_readout": row.next_readout,
             "source_hash": row.origin_hash, "donor_hash": row.donor_hash,
             "model_sha256": row.model_hash}
            for row in effects],
        "post_training_probe_effects": [
            {"role": row.role, "signed_effects": list(row.signed_effects),
             "model_sha256": row.model_hash}
            for row in post_effects],
        "trained_interchange_component": observed_cue_component,
        "independent_linear_design": [
            {"role": g.observation.role,
             "activation_deltas": list(g.activation_deltas),
             "known_transport": g.transport,
             "observed_joint_logit": g.observed_joint_logit,
             "model_sha256": g.observation.model_hash}
            for g in geometry],
        "linear_design_residuals": linear_residuals,
        "observed_response_selection": response_design,
        "aligned_observability": aligned_only,
        "selected_interventions": design,
        "accuracy": {"pretrained_confounded": baseline_test,
                     "passive_equal_updates": passive_test,
                     "input_augmentation_control": augmented_test,
                     "active_eval_contrasts": active_test},
        "readout_weights": {"passive": passive_mix, "input_aug": augmented_mix,
                            "active": active_mix},
        "losses": {"pretrain_last": pretrain[-1],
                   "passive_last": baseline_losses[-1],
                   "input_aug_last": augmentation_losses[-1],
                   "active_last": active_losses[-1]},
        "claim_boundary": "Planted two-channel toy, supervised readout only; intervention training and input augmentation may be equivalent; fourth-family test reused during development, not fresh independent confirmation",
    }


if __name__ == "__main__":
    print(json.dumps(run_campaign(), indent=2, sort_keys=True))
