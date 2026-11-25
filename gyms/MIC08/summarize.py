"""Summarize public development evidence, keeping unknown optima interval-valued."""
from run import root,FAMILIES,SEEDS
from fractions import Fraction as F
from itertools import combinations
from statistics import mean
from pathlib import Path
import json

def summarize(raw,audit):
    assert len(raw['rows'])==len(audit['rows'])
    rows=[]
    for a,b in zip(raw['rows'],audit['rows']):
        assert all(a[k]==b[k] for k in ('family','n','seed'))
        r={**a,'arms':{**a['arms'],**b['arms']},'pooled_lower':b['pooled_lower'],'pooled_upper':b['pooled_upper']}
        d=root(r['family'],r['seed'],r['n']);r['total']=sum(d.w);rows.append(r)
    pilot=[]
    for f in FAMILIES:
        group=[r for r in rows if r['family']==f];effects=[];sham=[]
        for r in group:
            a=r['arms'];w=r['total'];ls=[F(a[f'learned_{s}']['value'],w) for s in SEEDS]
            effects.append(mean(ls)-F(a['bound']['value'],w));sham.extend(abs(x-y) for x,y in combinations(ls,2))
        pilot.append(dict(unit_id=f,paired_effect=str(mean(effects)),sham_effects=[str(max(sham))]))
    spec=dict(schema_version=1,experiment_id='MIC-08-public-cpu',independent_unit='generator lineage (independence unverified)',alpha='1/20',scientific_min_effect='1/20',target_effect='1/10',measurement_resolution='0',sham_quantile='19/20',sham_confidence='19/20',planned_comparisons=1,confirm_units_planned=128,pilot_from_development_only=True,heldout_sealed=False,units_independent=False,pilot=pilot)
    return spec,rows
if __name__=='__main__':
    base=Path(__file__).parent
    spec,rows=summarize(json.loads((base/'results.json').read_text()),json.loads((base/'audit_results.json').read_text()))
    (base/'preflight_input.json').write_text(json.dumps(spec,sort_keys=True,indent=2)+'\n')
    for k in ('bound','loss','best_first','learned','timed_bound','timed_best_first','include512','timed_include'):
        vals=[(r,a) for r in rows for name,a in r['arms'].items() if name==k or k=='learned' and name.startswith('learned_')]
        print(k,'mean_vs_best_verified',float(mean(F(a['value'],max(1,r['pooled_lower'])) for r,a in vals)), 'mean_cert_gap',float(mean(F(a['upper']-a['value'],max(1,a['upper'])) for r,a in vals)), 'cert',sum(a['certified'] for _,a in vals),'n',len(vals),'ms',mean(a['ms'] for _,a in vals),'calls',mean(a['closure_calls'] for _,a in vals))
    print('timed soft deadline overruns',sum(r['arms']['timed_include']['ms']>r['learned_time_ms'] for r in rows), 'max ms overshoot',max(r['arms']['timed_include']['ms']-r['learned_time_ms'] for r in rows))
