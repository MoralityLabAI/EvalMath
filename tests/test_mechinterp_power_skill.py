from fractions import Fraction as F
from importlib.util import spec_from_file_location,module_from_spec
from pathlib import Path
import pytest
p=Path(__file__).resolve().parents[1]/'skills/evalmath-mechinterp-power/scripts/preflight.py'
spec=spec_from_file_location('preflight',p);mod=module_from_spec(spec);spec.loader.exec_module(mod)

def fixture(n=64,target='0.30',floor='0.05',planned=128):
    return {'schema_version':1,'experiment_id':'toy','independent_unit':'world_seed',
    'alpha':'0.05','scientific_min_effect':floor,'target_effect':target,
    'measurement_resolution':'0.005','sham_quantile':'0.95','sham_confidence':'0.95',
    'planned_comparisons':2,'confirm_units_planned':planned,'heldout_sealed':True,
    'pilot_from_development_only':True,'units_independent':True,
    'pilot':[{'unit_id':str(i),'paired_effect':'0.20' if i%2 else '0.30',
              'sham_effects':['0.01','-0.02']} for i in range(n)]}

def test_upper_sham_quantile_requires_independent_worlds():
    assert mod.upper_quantile([F(1,50)]*8)==(None,None)
    assert mod.upper_quantile([F(1,50)]*64)==(F(1,50),64)

def test_ready_with_roots_and_shams():
    out=mod.preflight(fixture())
    assert out['decision']=='READY_FOR_CONFIRMATION'
    assert out['pilot_worlds']==64 and out['order_statistic_rank']==64

def test_eight_roots_stay_eight():
    out=mod.preflight(fixture(8,planned=8))
    assert out['pilot_worlds']==8
    assert 'sham_quantile_uncalibrated' in out['reasons']

def test_variation_exceeds_target():
    out=mod.preflight(fixture(target='0.01'))
    assert 'target_below_mechanistic_variation_floor' in out['reasons']

def test_external_floor_needs_source():
    v=fixture(8);v['external_sham_floor']='0.06'
    with pytest.raises(ValueError,match='source'):mod.preflight(v)
    v['external_sham_source']='calibration receipt SHA256:test'
    assert mod.preflight(v)['upper_sham_quantile']==0.06

def test_per_root_sham_max_not_pool():
    v=fixture()
    for x in v['pilot']:x['sham_effects']=['0.01']*200+['0.04']
    out=mod.preflight(v)
    assert out['pilot_worlds']==64 and out['upper_sham_quantile']==0.04

def test_duplicate_roots_and_floats_fail_closed():
    v=fixture();v['pilot'][1]['unit_id']=v['pilot'][0]['unit_id']
    with pytest.raises(ValueError,match='unique'):mod.preflight(v)
    v=fixture();v['scientific_min_effect']=.05
    with pytest.raises(ValueError):mod.preflight(v)

def test_unsealed_readout_blocks_confirmation():
    v=fixture();v['heldout_sealed']=False
    assert mod.preflight(v)['decision']=='REDESIGN_OR_PILOT_ONLY'
