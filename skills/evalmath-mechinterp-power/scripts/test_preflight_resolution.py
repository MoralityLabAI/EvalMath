"""Regression tests for root-level mechanistic-resolution and zero-effect pilots."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('evalmath_mechinterp_preflight',Path(__file__).with_name('preflight.py'))
pf=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(pf)


def pilot(*,effects=None,shams=None,confirm=128, comparisons=3):
    effects=effects if effects is not None else ['0/1']*64
    shams=shams if shams is not None else ['1/128']*63 + ['24/128']
    return {'schema_version':1,'experiment_id':'BPD-AMM-03',
            'independent_unit':'trained physical model and factors root',
            'alpha':'1/20','scientific_min_effect':'1/10',
            'target_effect':'1/5','measurement_resolution':'1/128',
            'sham_quantile':'19/20','sham_confidence':'19/20',
            'planned_comparisons':comparisons,'confirm_units_planned':confirm,
            'pilot_from_development_only':True,'heldout_sealed':True,
            'units_independent':True,
            'pilot':[{'unit_id':f'root-{i}','paired_effect':effect,'sham_effects':[shams[i]]}
                     for i,effect in enumerate(effects)]}


class RootPowerGuardTests(unittest.TestCase):
    def test_amm03_all_zero_effect_is_not_confirmation_ready(self):
        out=pf.preflight(pilot())
        self.assertEqual(out['decision'],'REDESIGN_OR_PILOT_ONLY')
        self.assertEqual(out['mean_pilot_effect'],0.)
        self.assertEqual(out['mechanistic_variation_floor'],.1875)
        self.assertEqual(out['minimum_exact_sign_test_roots'],6)
        self.assertIsNone(out['approx_worlds_for_80pct_power'])
        self.assertIn('zero_variance_pilot_power_uninformative',out['reasons'])
        self.assertIn('pilot_effect_not_above_mechanistic_variation_floor',out['reasons'])

    def test_positive_pilot_with_root_variation_can_pass(self):
        effects=['1/4' if i%2 else '15/64' for i in range(64)]
        out=pf.preflight(pilot(effects=effects,shams=['1/128']*64))
        self.assertEqual(out['decision'],'READY_FOR_CONFIRMATION')
        self.assertGreater(out['mean_pilot_effect'],out['mechanistic_variation_floor'])
        self.assertGreaterEqual(out['approx_worlds_for_80pct_power'],6)

    def test_constant_positive_pilot_still_requires_exact_sign_roots(self):
        out=pf.preflight(pilot(effects=['1/4']*64,shams=['0']*64))
        self.assertEqual(out['decision'],'READY_FOR_CONFIRMATION')
        self.assertEqual(out['approx_worlds_for_80pct_power'],6)
        self.assertEqual(out['minimum_exact_sign_test_roots'],6)
        not_enough=pf.preflight(pilot(effects=['1/4']*64,shams=['0']*64,confirm=4))
        self.assertIn('confirmation_underpowered',not_enough['reasons'])

    def test_observed_pilot_below_floor_blocks_optimistic_target(self):
        p=pilot(effects=['5/128' if i%2 else '6/128' for i in range(64)],shams=['1/128']*64)
        out=pf.preflight(p)
        self.assertEqual(out['decision'],'REDESIGN_OR_PILOT_ONLY')
        self.assertIn('pilot_effect_not_above_mechanistic_variation_floor',out['reasons'])

    def test_insufficient_sham_roots_still_block(self):
        out=pf.preflight(pilot(effects=['1/4']*8,shams=['0']*8))
        self.assertEqual(out['decision'],'REDESIGN_OR_PILOT_ONLY')
        self.assertIn('sham_quantile_uncalibrated',out['reasons'])

    def test_duplicate_independent_root_rejected(self):
        p=pilot();p['pilot'][1]['unit_id']=p['pilot'][0]['unit_id']
        with self.assertRaises(ValueError):pf.preflight(p)


    def test_fsi01_positive_effect_floor_root_resolution_guard(self):
        p=pilot(effects=['1/4']*64,shams=['0']*64,confirm=128,comparisons=4)
        p['scientific_min_effect']='1/20'
        p['target_effect']='1/10'
        p['enforce_fsi01_floor']=True
        out=pf.preflight(p)
        self.assertEqual(out['fsi01_roots_at_target_for_effect_floor_resolution'],3506)
        self.assertEqual(out['fsi01_roots_at_observed_pilot_mean_for_effect_floor_resolution'],220)
        self.assertIn('fsi01_effect_floor_resolution_underpowered',out['reasons'])
        self.assertEqual(out['decision'],'REDESIGN_OR_PILOT_ONLY')
        p['enforce_fsi01_floor']=False
        old=pf.preflight(p)
        self.assertNotIn('fsi01_effect_floor_resolution_underpowered',old['reasons'])
        self.assertEqual(old['decision'],'READY_FOR_CONFIRMATION')

    def test_negative_effect_direction_is_explicit_and_signed(self):
        p=pilot(effects=['-3/8']*64,shams=['0']*64,confirm=256,comparisons=4)
        p['scientific_min_effect']='1/20'
        p['target_effect']='1/4'
        p['effect_direction']='decrease'
        p['enforce_fsi01_floor']=True
        out=pf.preflight(p)
        self.assertEqual(out['mean_pilot_effect'],0.375)
        self.assertEqual(out['effect_direction'],'decrease')
        self.assertEqual(out['fsi01_roots_at_target_for_effect_floor_resolution'],220)
        self.assertEqual(out['decision'],'READY_FOR_CONFIRMATION')
        p['effect_direction']='increase'
        opposite=pf.preflight(p)
        self.assertIn('pilot_effect_not_above_mechanistic_variation_floor',opposite['reasons'])

    def test_invalid_fsi_guard_and_direction_rejected(self):
        p=pilot()
        p['enforce_fsi01_floor']='yes'
        with self.assertRaisesRegex(ValueError,'boolean'):pf.preflight(p)
        del p['enforce_fsi01_floor']
        p['effect_direction']='two_sided'
        with self.assertRaisesRegex(ValueError,'effect_direction'):pf.preflight(p)


if __name__=='__main__':unittest.main()
