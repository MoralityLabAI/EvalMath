"""Replay distinct residual certificates; report all occurrences and family preflight."""
from mic12 import *
from itertools import combinations


def audit(raw):
    distinct=occurrences=nonroot=0
    per_seed={s:0 for s in raw['seeds']}
    for row in raw['rows']:
        d=instance(row['family'],row['seed'],row['n'],row['kind']);cache=set()
        for name,a in row['arms'].items():
            assert valid(d,int(a['mask'],16)) and sum(d.w[i] for i in bits(int(a['mask'],16)))==a['value']
            assert a['normalizations']<=CAP and a['ve_cells']<=CELL_CAP and a['ve_scans']<=SCAN_CAP and a['ve_attempts']<=ATTEMPT_CAP
            assert sum(c['cells'] for c in a['ve_receipts'])==a['ve_cells']
            for c in a['ve_receipts']:
                occurrences+=1;nonroot+=int(c['active'],16)!=(1<<len(d.w))-1 or int(c['required'],16)!=0
                key=json.dumps(c,sort_keys=True)
                if key not in cache:
                    assert verify(d,c) and not verify(d,{**c,'value':-999})
                    cache.add(key);distinct+=1
            for seed in per_seed:
                if name==f'learned_{seed}':per_seed[seed]+=int(a['certified'])
    pilot=[]
    for f in FAMILIES:
        effects=[];shams=[]
        for r in raw['rows']:
            if r['family']!=f:continue
            a=r['arms'];w=r['total_weight'];base=F(a['periodic']['upper']-a['periodic']['value'],w)
            gaps=[F(a[f'learned_{s}']['upper']-a[f'learned_{s}']['value'],w) for s in raw['seeds']]
            effects.append(base-mean(gaps));shams.extend(abs(x-y) for x,y in combinations(gaps,2))
        pilot.append(dict(unit_id=f,paired_effect=str(mean(effects)),sham_effects=[str(max(shams))]))
    spec=dict(schema_version=1,experiment_id='MIC-12-public-gate',independent_unit='generator lineage (independence unverified)',alpha='1/20',scientific_min_effect='1/20',target_effect='1/10',measurement_resolution='0',sham_quantile='19/20',sham_confidence='19/20',planned_comparisons=1,confirm_units_planned=128,pilot_from_development_only=True,heldout_sealed=False,units_independent=False,pilot=pilot)
    return dict(schema='MIC-12/replay/v1',receipt_occurrences=occurrences,distinct_receipts_verified=distinct,nonroot_occurrences=nonroot,per_seed_certificates=per_seed,scope='Identical receipts on the same root replayed once; each distinct receipt and tampered objective checked. Not global frontier replay.'),spec

if __name__=='__main__':
    p=Path(__file__).parent;t=perf_counter();raw=json.loads((p/'results.json').read_text());a,s=audit(raw);a['elapsed_s']=perf_counter()-t
    (p/'audit_results.json').write_text(json.dumps(a,sort_keys=True,indent=2)+'\n');(p/'preflight_input.json').write_text(json.dumps(s,sort_keys=True,indent=2)+'\n');print(json.dumps(a,indent=2))
