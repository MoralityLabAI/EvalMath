from copy import deepcopy
from spiral_ln.evaluation_hg09_session import analyze, MODELS, CONDITIONS
import pytest


def rows(seeds=(1,2)):
    return [{'task':'HG-02','seed':seed,'dimension':140,'horizon':5,'hidden_mode':bit,
             'model':m,'condition':c,'status':'complete','true_utility':'9' if m==MODELS[0] else '0',
             'safe_success':m==MODELS[0],'unsafe_release':False,
             'realized_oracle_gap':'0' if m==MODELS[0] else '9',
             'bellman_action_regret':'0' if m==MODELS[0] else '9'}
            for seed in seeds for bit in (0,1) for m in MODELS for c in CONDITIONS]


def test_modes_are_clustered_and_unsealed_blocks_confirmation():
    result=analyze({'episodes':rows()})
    assert result['n_units']==2
    assert result['n_balanced_model_episodes']==16
    comp=result['contrasts'][0]['completion_fsi01']
    assert comp['n_cases']==4 and comp['n_clusters']==2
    assert comp['test']=='exact_cluster_sign_flip'
    assert comp['verdict']!='confirmed'
    assert comp['accuracy_intervals'] is None
    assert result['planning']['single_accuracy_95_halfwidth_5pp_roots']==738


def test_partial_case_excluded_from_balanced_comparison():
    r=rows()
    r[-1]['status']='incomplete'
    result=analyze({'episodes':r})
    assert result['n_cases_completed']==15
    assert result['n_balanced_model_episodes']==8
    assert result['n_balanced_case_blocks']==2
    assert any(g['incomplete_episodes'] for g in result['groups'] if g['scope']=='available')


def test_missing_hidden_partner_preserves_data_but_blocks_paired_utility():
    result=analyze({'episodes':[r for r in rows((1,)) if r['hidden_mode']==0]})
    assert result['n_cases_completed']==4
    assert result['n_four_arm_complete_case_blocks']==1
    assert result['n_balanced_model_episodes']==0
    assert result['contrasts']==[]


def test_duplicate_attempt_never_selected_as_success():
    r=rows()
    with pytest.raises(ValueError):analyze({'episodes':r+[deepcopy(r[0])]})


def test_single_root_no_bootstrap_or_equivalence_claim():
    result=analyze({'episodes':rows((1,))})
    assert all(g['completion_uncertainty']['bootstrap_95_descriptive'] is None for g in result['groups'])
    assert all(c['completion_fsi01']['verdict']!='confirmed' for c in result['contrasts'])


def test_large_cluster_family_preserves_monte_carlo_p_value():
    result=analyze({'episodes':rows(tuple(range(1,20)))})
    contrast=result['contrasts'][0]
    assert contrast['completion_fsi01']['test']=='monte_carlo_cluster_sign_flip'
    assert contrast['holm40_family_uses_Monte_Carlo']
    from fractions import Fraction
    assert Fraction(contrast['holm40_completion_p_fraction'])<1
    assert contrast['completion_fsi01']['verdict']!='confirmed'
