"""Independent finite and executed BPD causal tests for EIM-01."""
from dataclasses import replace
import math

import pytest
import torch

from eim01.design import (EffectRow, coefficient_error_bound, select_identifying_evals,
                          two_column_certificate, validate_candidate_rows)
from eim01.gym import (source_cases, check_source_oracle, planted_bpd, select_probe_pairs,
                       signed_swap_row, run_campaign)


def fixture(role: str, pair: tuple[float,float], idx: str) -> EffectRow:
    return EffectRow(case_id=idx, donor_id="donor_"+idx, origin_hash="a", donor_hash="b",
        model_hash="frozen_model", split="train", family="exact", role=role,
        intervention_pass=2, next_readout=3, signed_effects=pair)


def test_finite_rank_and_noise_bound() -> None:
    assert two_column_certificate([(2.,2.)])["rank"] == 1
    cert = two_column_certificate([(1.,0.),(0.,1.)])
    assert cert["rank"] == 2 and cert["sigma_min"] == pytest.approx(1.)
    assert coefficient_error_bound([(1.,0.),(0.,1.)],0.1) == pytest.approx(math.sqrt(2)/10)
    assert math.isinf(coefficient_error_bound([(1.,1.),(2.,2.)],0.1))


def test_exact_eval_design_prefers_two_distinct_components() -> None:
    rows=[fixture("aligned",(1.,1.),"align"),
          fixture("cue_only",(0.,1.),"cue"),
          fixture("graph_only",(1.,0.),"graph")]
    answer=select_identifying_evals(rows,budget=2)
    assert answer["identified"]
    assert set(answer["chosen_roles"])=={"cue_only","graph_only"}
    assert answer["certificate"]["sigma_min"] == pytest.approx(1.)
    assert select_identifying_evals(rows[:1]+[fixture("aligned",(2.,2.),"align2")],
                                    budget=2)["identified"] is False


def test_sealed_eval_and_unobserved_route_are_rejected() -> None:
    row=fixture("cue_only",(0.,1.),"p")
    with pytest.raises(ValueError, match="training-split"):
        validate_candidate_rows([replace(row,split="test")])
    with pytest.raises(ValueError, match="unobserved route"):
        validate_candidate_rows([replace(row,route_observed=False)])
    with pytest.raises(ValueError, match="one frozen model"):
        validate_candidate_rows([row,replace(row,case_id="q",model_hash="other")])
    with pytest.raises(ValueError, match="Duplicate"):
        validate_candidate_rows([row,row])
    with pytest.raises(ValueError, match="certified"):
        validate_candidate_rows([replace(row,label_certified=False)])


def test_all_384_original_host_labels_survive_independent_graph_replay() -> None:
    cases=source_cases()
    assert len(cases)==384
    assert check_source_oracle(cases)=={"checked":384,"disagreements":0}
    assert len({c.alpha_hash for c in cases})==384
    train_root={c.root_group for c in cases if c.split=="train"}
    test_root={c.root_group for c in cases if c.split=="test"}
    assert train_root.isdisjoint(test_root)
    assert len([c for c in cases if c.family=="induction" and c.split=="test"])==16


def test_actual_bpd_swap_is_component_specific() -> None:
    torch.manual_seed(61017)
    target,bpd=planted_bpd()
    pairs=select_probe_pairs(source_cases())
    effects={role:signed_swap_row(target,bpd,x,y,role).signed_effects
             for x,y,role in pairs}
    # Causal specificity on actual same-pass BPD interventions, not feature correlations.
    assert abs(effects["cue_only"][0])<1e-6
    assert abs(effects["cue_only"][1])>0.05
    assert abs(effects["graph_only"][1])<1e-6
    assert abs(effects["graph_only"][0])>0.005
    cert=two_column_certificate([effects["cue_only"],effects["graph_only"]])
    assert cert["rank"]==2 and cert["sigma_min"]>0.005


def test_closed_eval_to_mechanism_loop_improves_sealed_family() -> None:
    report=run_campaign()
    assert report["oracle"]["disagreements"]==0
    assert report["counts"]=={"train_graphs":192,
                               "sealed_fourth_family":16,
                               "active_training_records":384}
    assert set(report["selected_interventions"]["chosen_roles"])=={"cue_only","graph_only"}
    scores=report["accuracy"]
    assert scores["pretrained_confounded"] <= 0.25
    assert scores["passive_equal_updates"] <= 0.5
    assert scores["active_eval_contrasts"] >= 0.875
    assert scores["active_eval_contrasts"] > scores["passive_equal_updates"]+0.3
    assert abs(report["readout_weights"]["active"][0]) > abs(report["readout_weights"]["active"][1])
