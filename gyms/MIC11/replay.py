"""Replay each residual receipt independently and verify the public budget ledger."""
from mic11 import *
from fractions import Fraction as F
from statistics import mean


def replay(raw):
    counts={};replayed=0;infeasible=0;nonroot=0;baseline_matches=0
    for row in raw['rows']:
        d=instance(row['family'],row['seed'],row['n'],row['kind']);base=prior_solve(d,'both')
        assert all(base[k]==row['arms']['baseline'][k] for k in ('value','upper','mask','normalizations','expansions'))
        baseline_matches+=1
        for name,a in row['arms'].items():
            rec=a['ve_receipts'];counts[name]=counts.get(name,0)+len(rec)
            assert sum(c['cells'] for c in rec)==a['ve_cells']
            for c in rec:
                assert verify(d,c), (row['kind'],row['family'],row['n'],row['seed'],name,c)
                assert not verify(d,{**c,'value':-999})
                replayed+=1;infeasible+=c['value'] is None;nonroot+=int(c['active'],16)!=(1<<len(d.w))-1 or int(c['required'],16)!=0
    return dict(schema='MIC-11/independent-residual-replay/v1',replayed=replayed,by_arm=counts,infeasible=infeasible,nonroot=nonroot,baseline_matches=baseline_matches,scope='Independent replay of residual optima and infeasibility; not a replay of the entire B&B frontier')


def planner(raw):
    groups=[]
    for f in FAMILIES:
        rows=[r for r in raw['rows'] if r['family']==f]
        effects=[F(r['arms']['always']['value']-r['arms']['root']['value'],r['total_weight']) for r in rows]
        groups.append(dict(unit_id=f,paired_effect=str(mean(effects)),sham_effects=['0']))
    return dict(schema_version=1,experiment_id='MIC-11-public-structural',independent_unit='generator lineage (independence unverified)',alpha='1/20',scientific_min_effect='1/20',target_effect='1/10',measurement_resolution='0',sham_quantile='19/20',sham_confidence='19/20',planned_comparisons=1,confirm_units_planned=128,pilot_from_development_only=True,heldout_sealed=False,units_independent=False,pilot=groups)

if __name__=='__main__':
    t=perf_counter();p=Path(__file__).parent;raw=json.loads((p/'results.json').read_text());a=replay(raw);a['elapsed_s']=perf_counter()-t
    (p/'audit_results.json').write_text(json.dumps(a,sort_keys=True,indent=2)+'\n')
    (p/'preflight_input.json').write_text(json.dumps(planner(raw),sort_keys=True,indent=2)+'\n')
    print(json.dumps(a,indent=2))
